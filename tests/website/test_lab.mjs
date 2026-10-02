import assert from 'node:assert/strict';
import test from 'node:test';
import {FIELD_META, fieldVector, mulberry32} from '../../website/src/lab.js';

test('gerador visual é determinístico para a mesma semente', () => {
  const first = mulberry32(42), second = mulberry32(42);
  assert.deepEqual(Array.from({length: 8}, first), Array.from({length: 8}, second));
});

test('todos os campos retornam vetores finitos e metadados', () => {
  for (const mode of Object.keys(FIELD_META)) {
    const vector = fieldVector(mode, .25, -.4, 1.2);
    assert.equal(Number.isFinite(vector.x), true); assert.equal(Number.isFinite(vector.y), true);
    assert.ok(FIELD_META[mode].name); assert.ok(FIELD_META[mode].equation);
  }
});

test('campo orbital permanece regular na origem', () => {
  assert.deepEqual(fieldVector('orbit', 0, 0), {x: 0, y: 0});
});
