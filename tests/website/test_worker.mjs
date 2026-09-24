import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {webcrypto} from 'node:crypto';
import test from 'node:test';
import vm from 'node:vm';

test('browser worker returns exact, stable, locally verified demo records', async () => {
  const messages = [];
  const self = {postMessage: message => messages.push(message)};
  const context = {self, crypto: webcrypto, TextEncoder, setTimeout};
  const source = await readFile(new URL('../../website/worker.js', import.meta.url), 'utf8');
  vm.runInNewContext(source, context, {filename: 'worker.js'});

  await self.onmessage({data: {type: 'start', count: 3}});

  const records = messages.filter(message => message.type === 'batch').flatMap(message => message.records);
  assert.equal(messages.at(-1).type, 'done');
  assert.equal(messages.at(-1).completed, 3);
  assert.equal(records.length, 6);
  assert.ok(records.every(record => record.verified_locally === true));
  assert.ok(records.every(record => record.formal_proof === false));
  assert.equal(new Set(records.map(record => record.content_id)).size, records.length);
});

test('browser worker rejects a task outside its bounded budget', async () => {
  const messages = [];
  const self = {postMessage: message => messages.push(message)};
  const context = {self, crypto: webcrypto, TextEncoder, setTimeout};
  const source = await readFile(new URL('../../website/worker.js', import.meta.url), 'utf8');
  vm.runInNewContext(source, context, {filename: 'worker.js'});

  await self.onmessage({data: {type: 'start', count: 5001}});
  assert.equal(messages[0].type, 'error');
});
