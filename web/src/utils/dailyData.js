import { getLocalDateKey } from './localDate.js';

export const DEFAULT_WORK_MINUTES = 25;
export const DEFAULT_BREAK_MINUTES = 10;

export const DEFAULT_MICRO_TASKS = [
  { id: 1, text: 'Apply hair serum' },
  { id: 2, text: 'Polish shoes' },
  { id: 3, text: '20 pushups' },
  { id: 4, text: 'Wash face (morning)' },
  { id: 5, text: 'Wash face (night)' },
  { id: 6, text: 'Skincare routine' },
  { id: 7, text: 'Drink 2L water' },
];

function validMinutes(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) && number >= 1 ? number : fallback;
}

export function createFreshDailyData(date = getLocalDateKey(), previousData) {
  return {
    date,
    macroTasks: [],
    pomodoroSessions: 0,
    pomodoroWorkMin: validMinutes(previousData?.pomodoroWorkMin, DEFAULT_WORK_MINUTES),
    pomodoroBreakMin: validMinutes(previousData?.pomodoroBreakMin, DEFAULT_BREAK_MINUTES),
    microStatus: {},
    enforcerLogs: [],
  };
}

export function normalizeDailyData(data, date = getLocalDateKey()) {
  if (data?.date !== date) return createFreshDailyData(date, data);

  const fresh = createFreshDailyData(date, data);
  return {
    ...fresh,
    ...data,
    date,
    macroTasks: Array.isArray(data?.macroTasks) ? data.macroTasks : [],
    pomodoroSessions: Number.isFinite(Number(data?.pomodoroSessions))
      ? Math.max(0, Number(data.pomodoroSessions))
      : 0,
    pomodoroWorkMin: fresh.pomodoroWorkMin,
    pomodoroBreakMin: fresh.pomodoroBreakMin,
    microStatus: data?.microStatus && typeof data.microStatus === 'object'
      ? data.microStatus
      : {},
    enforcerLogs: Array.isArray(data?.enforcerLogs) ? data.enforcerLogs : [],
  };
}

export function normalizeMicroConfig(value) {
  if (!Array.isArray(value)) return DEFAULT_MICRO_TASKS;
  return value
    .filter(item => item && Number.isFinite(Number(item.id)) && typeof item.text === 'string')
    .map(item => ({ id: Number(item.id), text: item.text.trim() }))
    .filter(item => item.text);
}

export function createGuestState(date = getLocalDateKey()) {
  return {
    data: createFreshDailyData(date),
    microConfig: DEFAULT_MICRO_TASKS,
  };
}
