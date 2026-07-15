import { getLocalDateKey } from './localDate.js';

export const DEFAULT_WORK_MINUTES = 25;
export const DEFAULT_BREAK_MINUTES = 10;

const LEGACY_DEFAULT_MICRO_TASKS = [
  { id: 1, text: 'Apply hair serum' },
  { id: 2, text: 'Polish shoes' },
  { id: 3, text: '20 pushups' },
  { id: 4, text: 'Wash face (morning)' },
  { id: 5, text: 'Wash face (night)' },
  { id: 6, text: 'Skincare routine' },
  { id: 7, text: 'Drink 2L water' },
];

const LEGACY_DEFAULT_MICRO_TEXT = new Set(
  LEGACY_DEFAULT_MICRO_TASKS.map(task => task.text.toLowerCase()),
);

export const DEFAULT_MICRO_TASKS = [];

function validMinutes(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) && number >= 1 ? number : fallback;
}

function normalizeTaskList(value) {
  if (!Array.isArray(value)) return [];
  return value
    .filter(item => item && Number.isFinite(Number(item.id)) && typeof item.text === 'string')
    .map(item => ({
      id: Number(item.id),
      text: item.text.trim(),
      done: Boolean(item.done),
    }))
    .filter(item => item.text);
}

function microConfigToTasks(config, status = {}) {
  return normalizeMicroConfig(config).map(task => ({
    ...task,
    done: Boolean(status?.[task.id]),
  }));
}

export function createFreshDailyData(date = getLocalDateKey(), previousData) {
  return {
    date,
    macroTasks: [],
    microTasks: [],
    pomodoroSessions: 0,
    pomodoroWorkMin: validMinutes(previousData?.pomodoroWorkMin, DEFAULT_WORK_MINUTES),
    pomodoroBreakMin: validMinutes(previousData?.pomodoroBreakMin, DEFAULT_BREAK_MINUTES),
  };
}

export function normalizeDailyData(data, date = getLocalDateKey(), legacyMicroConfig = []) {
  if (data?.date !== date) {
    const fresh = createFreshDailyData(date, data);
    return data?.date
      ? fresh
      : { ...fresh, microTasks: microConfigToTasks(legacyMicroConfig, data?.microStatus) };
  }

  const fresh = createFreshDailyData(date, data);
  return {
    date,
    macroTasks: normalizeTaskList(data?.macroTasks),
    microTasks: Array.isArray(data?.microTasks)
      ? normalizeTaskList(data.microTasks)
      : microConfigToTasks(legacyMicroConfig, data?.microStatus),
    pomodoroSessions: Number.isFinite(Number(data?.pomodoroSessions))
      ? Math.max(0, Number(data.pomodoroSessions))
      : 0,
    pomodoroWorkMin: fresh.pomodoroWorkMin,
    pomodoroBreakMin: fresh.pomodoroBreakMin,
  };
}

export function normalizeMicroConfig(value) {
  if (!Array.isArray(value)) return DEFAULT_MICRO_TASKS;
  return value
    .filter(item => item && Number.isFinite(Number(item.id)) && typeof item.text === 'string')
    .map(item => ({ id: Number(item.id), text: item.text.trim() }))
    .filter(item => item.text)
    .filter(item => !LEGACY_DEFAULT_MICRO_TEXT.has(item.text.toLowerCase()));
}

export function createGuestState(date = getLocalDateKey()) {
  return {
    data: createFreshDailyData(date),
    microConfig: DEFAULT_MICRO_TASKS,
  };
}
