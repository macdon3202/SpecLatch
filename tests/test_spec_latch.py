from pathlib import Path
import pytest

CONTRACT = Path(__file__).parents[1] / "contracts" / "spec_latch.py"
DEPLOYER = bytes.fromhex("11" * 20)
AUTHOR = bytes.fromhex("22" * 20)
AUDITOR = bytes.fromhex("33" * 20)
OUTSIDER = bytes.fromhex("44" * 20)
COMMIT = "a" * 40


def deploy(vm, direct_deploy):
    vm.strict_mocks = True
    vm.check_pickling = True
    with vm.prank(DEPLOYER):
        return direct_deploy(CONTRACT, sdk_version="v0.2.16")


def fact(eip, status="Final", category="Core", requires="", binding="MATCH"):
    return {
        "source_binding": binding,
        "title": f"Fixture EIP {eip}",
        "status": status,
        "eip_type": "Standards Track",
        "category": category,
        "requires_csv": requires,
    }


def mock(vm, eip, model=None, primary="canonical page", fallback="pinned canonical markdown"):
    vm.mock_web(rf"eips\.ethereum\.org/EIPS/eip-{eip}$", {"method":"GET", "status":200, "body":primary})
    vm.mock_web(rf"raw\.githubusercontent\.com/ethereum/EIPs/.*/EIPS/eip-{eip}\.md$", {"method":"GET", "status":200, "body":fallback})
    vm.mock_llm("SPEC_LATCH_FACT_V1", model or fact(eip))


def create(c, vm, name="Cancun Core Gate"):
    with vm.prank(AUTHOR):
        return c.create_bundle(name, "Core", 0)


def add(c, vm, bundle_id, eip):
    with vm.prank(AUTHOR):
        c.add_requirement(bundle_id, eip, COMMIT)


def seal(c, vm, bundle_id):
    with vm.prank(AUTHOR):
        return c.seal_bundle(bundle_id)


def test_deployer_has_no_admin_role_and_any_two_wallets_can_run_flow(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    cfg = c.get_config()
    assert cfg["access"] == "PERMISSIONLESS_TWO_WALLET_PER_BUNDLE"
    assert cfg["decision_scope"] == "EIP_METADATA_ONLY_NOT_CONSUMER_MIGRATION"
    bid = create(c, direct_vm)
    assert c.get_bundle(bid).creator == "0x" + "22" * 20


def test_happy_path_final_metadata_and_dependencies(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    bid = create(c, direct_vm)
    for eip in (1559, 2718, 2930, 2929):
        add(c, direct_vm, bid, eip)
    digest = seal(c, direct_vm, bid)
    assert len(digest) == 64
    for slot, eip, requires in ((0,1559,"2718,2930"),(1,2718,""),(2,2930,"2718,2929"),(3,2929,"")):
        mock(direct_vm, eip, fact(eip, requires=requires))
        with direct_vm.prank(AUDITOR):
            assert c.verify_requirement(bid, slot) == "VERIFIED"
    with direct_vm.prank(AUDITOR):
        assert c.finalize_bundle(bid) == "SPEC_READY"
    bundle = c.get_bundle(bid)
    assert bundle.blocker_code == "ALL_SPEC_REQUIREMENTS_SATISFIED"
    assert bundle.finalizer == "0x" + "33" * 20


def test_withdrawn_eip_blocks_gate(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    bid = create(c, direct_vm); add(c, direct_vm, bid, 7701); seal(c, direct_vm, bid)
    mock(direct_vm, 7701, fact(7701, status="Withdrawn"))
    with direct_vm.prank(AUDITOR):
        c.verify_requirement(bid, 0)
        assert c.finalize_bundle(bid) == "BLOCKED"
    assert c.get_bundle(bid).blocker_code == "NON_FINAL_EIP"


def test_missing_dependency_is_deterministically_blocked(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    bid = create(c, direct_vm); add(c, direct_vm, bid, 1559); seal(c, direct_vm, bid)
    mock(direct_vm, 1559, fact(1559, requires="2718,2930"))
    with direct_vm.prank(AUDITOR):
        c.verify_requirement(bid, 0)
        assert c.finalize_bundle(bid) == "BLOCKED"
    assert c.get_bundle(bid).blocker_code == "MISSING_DEPENDENCY"


def test_source_conflict_blocks_and_preserves_receipt(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    bid = create(c, direct_vm); add(c, direct_vm, bid, 1559); seal(c, direct_vm, bid)
    mock(direct_vm, 1559, fact(1559, binding="CONFLICT"))
    with direct_vm.prank(AUDITOR):
        assert c.verify_requirement(bid, 0) == "CONFLICT"
        assert c.finalize_bundle(bid) == "BLOCKED"
    receipt = c.get_receipt(bid, 0, 1)
    assert receipt.source_binding == "CONFLICT"
    assert c.get_bundle(bid).blocker_code == "SOURCE_CONFLICT"


def test_unavailable_can_retry_with_append_only_receipts(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    bid = create(c, direct_vm); add(c, direct_vm, bid, 2718); seal(c, direct_vm, bid)
    direct_vm.mock_web(r"eips\.ethereum\.org/", {"method":"GET", "status":503, "body":"offline"})
    with direct_vm.prank(AUDITOR):
        assert c.verify_requirement(bid, 0) == "SOURCE_UNAVAILABLE"
    mock(direct_vm, 2718)
    with direct_vm.prank(AUDITOR):
        assert c.verify_requirement(bid, 0) == "VERIFIED"
    assert c.get_requirement(bid, 0).revision == 2
    assert c.get_receipt(bid, 0, 1).reason_code == "SOURCE_OR_MODEL_UNAVAILABLE"
    assert c.get_receipt(bid, 0, 2).reason_code == "CANONICAL_FACTS_MATCH"


def test_role_separation_and_sealed_immutability(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    bid = create(c, direct_vm); add(c, direct_vm, bid, 1559); seal(c, direct_vm, bid)
    with direct_vm.prank(AUTHOR), direct_vm.expect_revert("BUNDLE_IMMUTABLE"):
        c.add_requirement(bid, 2718, COMMIT)
    mock(direct_vm, 1559)
    with direct_vm.prank(AUTHOR), direct_vm.expect_revert("INDEPENDENT_CHECKER_REQUIRED"):
        c.verify_requirement(bid, 0)


def test_input_bounds_duplicate_and_invalid_commit(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); bid = create(c, direct_vm)
    add(c, direct_vm, bid, 1559)
    with direct_vm.prank(AUTHOR), direct_vm.expect_revert("DUPLICATE_EIP"):
        c.add_requirement(bid, 1559, COMMIT)
    with direct_vm.prank(AUTHOR), direct_vm.expect_revert("INVALID_COMMIT"):
        c.add_requirement(bid, 2718, "main")


def test_cannot_finalize_unchecked_or_replay_terminal(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    bid = create(c, direct_vm); add(c, direct_vm, bid, 2718); seal(c, direct_vm, bid)
    with direct_vm.prank(AUDITOR), direct_vm.expect_revert("NOT_FINALIZABLE"):
        c.finalize_bundle(bid)
    mock(direct_vm, 2718)
    with direct_vm.prank(AUDITOR):
        c.verify_requirement(bid, 0)
        c.finalize_bundle(bid)
    before = c.get_bundle(bid)
    with direct_vm.prank(OUTSIDER), direct_vm.expect_revert("NOT_FINALIZABLE"):
        c.finalize_bundle(bid)
    assert c.get_bundle(bid) == before


@pytest.mark.parametrize("bad", [
    {"source_binding":"MATCH"},
    fact(1559, requires="2930,2718"),
    fact(1559, category="Unbounded"),
])
def test_malformed_model_output_fails_closed(direct_vm, direct_deploy, bad):
    c = deploy(direct_vm, direct_deploy)
    bid = create(c, direct_vm); add(c, direct_vm, bid, 1559); seal(c, direct_vm, bid)
    mock(direct_vm, 1559, bad)
    with direct_vm.prank(AUDITOR):
        assert c.verify_requirement(bid, 0) == "SOURCE_UNAVAILABLE"
    assert c.get_requirement(bid, 0).state == "SOURCE_UNAVAILABLE"
