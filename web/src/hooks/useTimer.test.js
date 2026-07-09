import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateRemainingSeconds } from './useTimer.js';

test('timer remaining time is calculated from the wall clock', () => {
  const startedAt = 1_000_000;
  const deadline = startedAt + 30 * 60 * 1000;

  assert.equal(calculateRemainingSeconds(deadline, startedAt), 30 * 60);
  assert.equal(calculateRemainingSeconds(deadline, startedAt + 10 * 60 * 1000), 20 * 60);
  assert.equal(calculateRemainingSeconds(deadline, startedAt + 90 * 60 * 1000), 0);
});
