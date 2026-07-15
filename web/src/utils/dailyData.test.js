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
    macroTasks: [{ id: 1, text: 'Old macro task', done: false }],
    microTasks: [{ id: 1, text: 'Old micro task', done: true }],
    pomodoroSessions: 4,
    pomodoroWorkMin: 50,
    pomodoroBreakMin: 15,
  };
  const fresh = createFreshDailyData('2026-06-27', previous);

  assert.equal(fresh.date, '2026-06-27');
  assert.deepEqual(fresh.macroTasks, []);
  assert.deepEqual(fresh.microTasks, []);
  assert.equal(fresh.pomodoroSessions, 0);
  assert.equal(fresh.pomodoroWorkMin, 50);
  assert.equal(fresh.pomodoroBreakMin, 15);
});

test('normalization rejects stale daily content', () => {
  const result = normalizeDailyData({
    date: '2026-06-26',
    macroTasks: [{ id: 1, text: 'Old task' }],
    microTasks: [{ id: 2, text: 'Old micro task' }],
  }, '2026-06-27');

  assert.deepEqual(result.macroTasks, []);
  assert.deepEqual(result.microTasks, []);
});

test('normalization sanitizes macro and micro task lists', () => {
  const result = normalizeDailyData({
    date: '2026-06-27',
    macroTasks: [
      { id: '1', text: '  Write report  ', done: 1 },
      { id: 'bad', text: 'discard' },
    ],
    microTasks: [
      { id: '2', text: '  Clear desk  ', done: 0 },
      { id: 3, text: '   ' },
    ],
  }, '2026-06-27');

  assert.deepEqual(result.macroTasks, [{ id: 1, text: 'Write report', done: true }]);
  assert.deepEqual(result.microTasks, [{ id: 2, text: 'Clear desk', done: false }]);
});

test('legacy micro task configuration migrates to daily micro tasks', () => {
  const result = normalizeDailyData({
    date: '2026-06-27',
    microStatus: { 2: true },
  }, '2026-06-27', [
    { id: '2', text: '  Drink water  ' },
  ]);

  assert.deepEqual(result.microTasks, [{ id: 2, text: 'Drink water', done: true }]);
});
test('legacy micro task configuration can migrate without legacy daily data', () => {
  const result = normalizeDailyData(null, '2026-06-27', [
    { id: '2', text: '  Drink water  ' },
  ]);

  assert.deepEqual(result.microTasks, [{ id: 2, text: 'Drink water', done: false }]);
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
