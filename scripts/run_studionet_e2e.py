"""Run SpecLatch live E2E with two auxiliary wallets; never prints keys."""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

RPC="https://studio.genlayer.com/api"
EX="https://explorer-studio.genlayer.com"
COMMIT="0b8184b1d6ed9fba836222684fd082b32782d4ef"

def wallets():
    p=Path(__file__).resolve().parents[2]/"secrets"/"genlayer-test-wallets.env"
    for line in p.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k,v=line.split("=",1);os.environ.setdefault(k.strip(),v.strip().strip("'\"<>") )
    return create_account(os.environ["SERVICE_LEDGER_KEY_A"]),create_account(os.environ["SERVICE_LEDGER_KEY_B"])

def plain(v):
    if isinstance(v,dict):return {str(k):plain(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [plain(x) for x in v]
    return v if isinstance(v,(str,int,float,bool)) or v is None else str(v)

def signals(info):
    status=str(info.get("status_name") or info.get("status") or "UNKNOWN").upper()
    cons=str(info.get("result_name") or info.get("consensus_result_name") or "UNKNOWN").upper()
    vals=[];data=info.get("consensus_data")
    if isinstance(data,dict):
        # leader_receipt may also contain cancelled idle validator entries.
        # Only the actual leader and non-idle validator executions determine
        # whether the accepted transaction executed successfully.
        receipts=data.get("leader_receipt") or []
        if isinstance(receipts,dict):receipts=[receipts]
        vals += [str(x.get("execution_result") or "").upper() for x in receipts if isinstance(x,dict) and x.get("mode")=="leader"]
        vals += [str(x.get("execution_result") or "").upper() for x in (data.get("validators") or []) if isinstance(x,dict) and str(x.get("vote","")).lower() not in {"idle",""}]
    exe="ERROR" if any(any(t in x for t in("ERROR","FAIL","REVERT")) for x in vals) else "SUCCESS" if vals else "UNKNOWN"
    return status,exe,cons

def read(c,a,w,fn,args=None):return plain(c.read_contract(address=a,function_name=fn,args=args or [],account=w))

def send(c,a,w,fn,args,expected_error=False):
    tx=str(c.write_contract(address=a,function_name=fn,args=args,account=w,value=0))
    print(json.dumps({"submitted":fn,"tx":tx}),flush=True)
    for _ in range(240):
        try:
            info=plain(c.get_transaction(tx));status,exe,cons=signals(info)
        except Exception as error:
            print(json.dumps({"poll_retry":tx,"error":str(error)[:120]}),flush=True);time.sleep(3);continue
        if status=="FINALIZED":
            if (exe=="ERROR")!=expected_error:raise AssertionError(f"{fn}: expected_error={expected_error}, execution={exe}, tx={tx}")
            if not expected_error and cons not in {"MAJORITY_AGREE","UNKNOWN"}:raise RuntimeError(f"{fn}: consensus={cons}")
            return {"method":fn,"tx":tx,"status":status,"execution":exe,"consensus":cons,"expected_error":expected_error,"explorer":f"{EX}/tx/{tx}"}
        if status in {"FAILED","REJECTED","CANCELLED"}:raise RuntimeError(f"{fn}: {status}")
        time.sleep(3)
    raise TimeoutError(tx)

def main():
    if len(sys.argv)!=2:raise SystemExit("usage: run_studionet_e2e.py CONTRACT_ADDRESS")
    address=sys.argv[1];author,auditor=wallets();client=create_client(chain=studionet,account=author,endpoint=RPC)
    cfg=read(client,address,author,"get_config")
    expected={"version":"SPEC_LATCH_V1","architecture":"SEALED_MANIFEST_ITEM_RECEIPTS_DEPENDENCY_GATE","access":"PERMISSIONLESS_TWO_WALLET_PER_BUNDLE","decision_scope":"EIP_METADATA_ONLY_NOT_CONSUMER_MIGRATION"}
    for k,v in expected.items():
        if str(cfg.get(k))!=v:raise RuntimeError(f"wrong deployment {k}: {cfg}")
    proof={"network":"studionet","contract":address,"contract_explorer":f"{EX}/address/{address}","pinned_commit":COMMIT,"roles":{"bundle_author":author.address,"independent_auditor":auditor.address,"deployer_role":"NONE"},"initial_config":cfg,"transactions":[],"readbacks":{}}
    # Happy path: canonical Final Core EIPs with complete declared dependency set.
    before=int(cfg["bundle_count"]);happy=before+1
    proof["transactions"].append(send(client,address,author,"create_bundle",["London Core specification gate","Core",0]))
    for eip in (1559,2718,2930,2929):proof["transactions"].append(send(client,address,author,"add_requirement",[happy,eip,COMMIT]))
    proof["transactions"].append(send(client,address,author,"seal_bundle",[happy]))
    sealed=read(client,address,author,"get_bundle",[happy]);proof["readbacks"]["happy_sealed"]=sealed
    if sealed["state"]!="SEALED" or len(sealed["manifest_digest"])!=64:raise AssertionError(sealed)
    # Adversarial role separation: author cannot verify; state remains identical.
    proof["transactions"].append(send(client,address,author,"verify_requirement",[happy,0],True))
    if read(client,address,author,"get_bundle",[happy])!=sealed:raise AssertionError("self-check changed state")
    for slot in range(4):proof["transactions"].append(send(client,address,auditor,"verify_requirement",[happy,slot]))
    checked=[read(client,address,auditor,"get_requirement",[happy,i]) for i in range(4)];proof["readbacks"]["happy_requirements"]=checked
    if any(x["state"]!="VERIFIED" for x in checked):raise AssertionError(checked)
    proof["transactions"].append(send(client,address,auditor,"finalize_bundle",[happy]))
    final=read(client,address,auditor,"get_bundle",[happy]);proof["readbacks"]["happy_final"]=final
    if final["state"]!="SPEC_READY" or final["blocker_code"]!="ALL_SPEC_REQUIREMENTS_SATISFIED":raise AssertionError(final)
    # Terminal replay must fail and leave state unchanged.
    proof["transactions"].append(send(client,address,auditor,"finalize_bundle",[happy],True))
    if read(client,address,auditor,"get_bundle",[happy])!=final:raise AssertionError("terminal replay changed state")
    # Missing dependency path is deterministic and does not require another source fixture.
    missing=happy+1
    proof["transactions"].append(send(client,address,author,"create_bundle",["Missing dependency adversarial gate","Core",0]))
    proof["transactions"].append(send(client,address,author,"add_requirement",[missing,1559,COMMIT]))
    proof["transactions"].append(send(client,address,author,"seal_bundle",[missing]))
    proof["transactions"].append(send(client,address,auditor,"verify_requirement",[missing,0]))
    proof["transactions"].append(send(client,address,auditor,"finalize_bundle",[missing]))
    blocked=read(client,address,auditor,"get_bundle",[missing]);proof["readbacks"]["missing_dependency_final"]=blocked
    if blocked["state"]!="BLOCKED" or blocked["blocker_code"]!="MISSING_DEPENDENCY":raise AssertionError(blocked)
    proof["final_config"]=read(client,address,author,"get_config");proof["result"]="PASS"
    out=Path(__file__).resolve().parents[1]/"docs"/"studionet-e2e.json";out.write_text(json.dumps(proof,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"result":"PASS","happy_bundle":happy,"blocked_bundle":missing,"transactions":len(proof["transactions"]),"evidence":str(out)}),flush=True)

if __name__=="__main__":main()
