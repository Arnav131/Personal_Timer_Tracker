import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createFreshDailyData,
  normalizeDailyData,
  normalizeMicroConfig,
} from './dailyData.js';

test('a new day clears daily activity but preserves timer preferences', () => {
  const previous = {
    date: '2026-06-26',
    macroTasks: [{ id: 1, text: 'Old task', done: false }],
    microStatus: { 1: true },
    pomodoroSessions: 4,
    pomodoroWorkMin: 50,
    pomodoroBreakMin: 15,
    enforcerLogs: [{ timestamp: '10:00:00', text: 'old' }],
  };
  const fresh = createFreshDailyData('2026-06-27', previous);

  assert.equal(fresh.date, '2026-06-27');
  assert.deepEqual(fresh.macroTasks, []);
  assert.deepEqual(fresh.microStatus, {});
  assert.deepEqual(fresh.enforcerLogs, []);
  assert.equal(fresh.pomodoroSessions, 0);
  assert.equal(fresh.pomodoroWorkMin, 50);
  assert.equal(fresh.pomodoroBreakMin, 15);
});

test('normalization rejects stale daily content', () => {
  const result = normalizeDailyData({
    date: '2026-06-26',
    macroTasks: [{ id: 1, text: 'Old task' }],
  }, '2026-06-27');
  assert.deepEqual(result.macroTasks, []);
});

test('micro task configuration is sanitized', () => {
  assert.deepEqual(normalizeMicroConfig([
    { id: '2', text: '  Drink water  ' },
    { id: 'bad', text: 'discard' },
    { id: 3, text: '   ' },
  ]), [{ id: 2, text: 'Drink water' }]);
});

test('micro task configuration starts empty by default', () => {
  assert.deepEqual(normalizeMicroConfig(null), []);
});

test('legacy seeded micro tasks are removed from restored configuration', () => {
  assert.deepEqual(normalizeMicroConfig([
    { id: 1, text: 'Apply hair serum' },
    { id: 2, text: 'Polish shoes' },
    { id: 9, text: 'Meditate' },
  ]), [{ id: 9, text: 'Meditate' }]);
});
