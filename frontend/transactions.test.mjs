import test from'node:test';import assert from'node:assert/strict';import{normalizeHash,receiptState}from'./src/transactions.js';
test('normalizes valid hash',()=>assert.equal(normalizeHash({txId:'0x'+'a'.repeat(64)}),'0x'+'a'.repeat(64)));
test('rejects invalid wallet response',()=>assert.throws(()=>normalizeHash({hash:'bad'})));
test('FINALIZED alone is not success when execution errored',()=>{const s=receiptState({statusName:'FINALIZED',consensus_data:{leader_receipt:[{execution_result:'ERROR',result:{payload:'boom'}}]}});assert.equal(s.accepted,false);assert.equal(s.failed,true)});
test('accepts finalized successful receipt',()=>assert.equal(receiptState({statusName:'FINALIZED',consensus_data:{leader_receipt:[{execution_result:'SUCCESS'}]}}).accepted,true));
test('ignores idle validator cancellation after a successful leader receipt',()=>assert.equal(receiptState({statusName:'FINALIZED',consensus_data:{leader_receipt:[{mode:'leader',execution_result:'SUCCESS'},{mode:'validator',vote:'idle',execution_result:'ERROR'}]}}).accepted,true));
