import test from 'node:test';
import assert from 'node:assert/strict';
import {compareReceipt, validateReceipt, summaryMarkdown} from '../site/core.mjs';

const hash = 'a'.repeat(64), changed = 'b'.repeat(64);
const make = () => ({schema_version:1,command:['python','-m','unittest'],started_at:'2026-10-05T12:00:00Z',duration_seconds:1,exit_code:0,check_status:'passed',before:{'src/app.py':hash},after:{'src/app.py':hash}});
test('matching bytes preserve a passing command result', () => assert.equal(compareReceipt(make(), {'src/app.py':hash}).state,'current_passed'));
test('changed bytes invalidate a passing result', () => assert.equal(compareReceipt(make(), {'src/app.py':changed}).state,'changed_since_check'));
test('missing watched file invalidates a passing result', () => assert.deepEqual(compareReceipt(make(), {}).changes,['src/app.py']));
test('failed command remains failed with matching files', () => {const r=make();r.check_status='failed';r.exit_code=1;assert.equal(compareReceipt(r,{'src/app.py':hash}).state,'current_failed');});
test('check modifying its inputs is not a current pass', () => {const r=make();r.after['src/app.py']=changed;assert.equal(compareReceipt(r,{'src/app.py':changed}).state,'changed_during_check');});
test('missing after snapshot is explicitly unknown', () => {const r=make();r.after=null;assert.equal(compareReceipt(r,{'src/app.py':hash}).state,'snapshot_unavailable');});
test('invalid receipts and inconsistent success are rejected', () => {for(const r of [null,[],{}, {...make(),exit_code:1}, {...make(),command:'python'}, {...make(),duration_seconds:-1}]) assert.throws(()=>validateReceipt(r));});
test('traversal and absolute paths are rejected', () => {for(const p of ['../x','/etc/passwd','a/../x','C:/secret','a\\b']) {const r=make();r.before={[p]:hash};r.after={[p]:hash};assert.throws(()=>validateReceipt(r));}});
test('after snapshot cannot silently omit watched files', () => {const r=make();r.after={};assert.throws(()=>validateReceipt(r));});
test('invalid digests are rejected', () => {const r=make();r.before['src/app.py']='not-a-hash';assert.throws(()=>validateReceipt(r));});
test('export names its scope and staleness limits', () => {const r=make();const text=summaryMarkdown(r,compareReceipt(r,{}));assert.match(text,/Result is out of date/);assert.match(text,/unsigned records/);assert.match(text,/src\/app.py/);});
test('example exports cannot masquerade as a live check', () => {const r=make();assert.match(summaryMarkdown(r,compareReceipt(r,{'src/app.py':hash}),true),/Saved demonstration snapshot/);});
