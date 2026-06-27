import { useEffect, useState } from 'react';
import { getLocalDateKey, millisecondsUntilLocalMidnight } from '../utils/localDate';

const DAILY_DATA_KEY = 'pe_daily_data';
const POMODORO_SETTINGS_KEY = 'pe_pomodoro_settings';
const DEFAULT_WORK_MINUTES = 25;
const DEFAULT_BREAK_MINUTES = 10;

function validMinutes(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) && number >= 1 ? number : fallback;
}

function readPomodoroSettings() {
  try {
    const parsed = JSON.parse(localStorage.getItem(POMODORO_SETTINGS_KEY));
    return {
      workMin: validMinutes(parsed?.workMin, DEFAULT_WORK_MINUTES),
      breakMin: validMinutes(parsed?.breakMin, DEFAULT_BREAK_MINUTES),
    };
  } catch {
    return { workMin: DEFAULT_WORK_MINUTES, breakMin: DEFAULT_BREAK_MINUTES };
  }
}

function createFreshDailyData(date, previousData) {
  const savedSettings = readPomodoroSettings();
  return {
    date,
    macroTasks: [],
    pomodoroSessions: 0,
    pomodoroWorkMin: validMinutes(previousData?.pomodoroWorkMin, savedSettings.workMin),
    pomodoroBreakMin: validMinutes(previousData?.pomodoroBreakMin, savedSettings.breakMin),
    microStatus: {},
    enforcerLogs: [],
  };
}

function normalizeDailyData(data, date) {
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

function saveBackup(data) {
  if (!data || typeof data !== 'object') return;
  const date = typeof data.date === 'string' ? data.date : 'unknown-date';
  try {
    localStorage.setItem(`pe_backup_${date}`, JSON.stringify(data));
  } catch { /* A failed backup must not prevent the daily reset. */ }
}

/** Persists ordinary state in localStorage. */
export function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch { /* State remains available for the current session. */ }
  }, [key, value]);

  return [value, setValue];
}

/** Daily results reset at the user's local midnight. */
export function useDailyData() {
  const [data, setData] = useState(() => {
    const today = getLocalDateKey();
    try {
      const stored = localStorage.getItem(DAILY_DATA_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed?.date === today) return normalizeDailyData(parsed, today);
        saveBackup(parsed);
        return createFreshDailyData(today, parsed);
      }
    } catch { /* Invalid stored data is replaced with a clean day. */ }
    return createFreshDailyData(today);
  });

  useEffect(() => {
    try {
      localStorage.setItem(DAILY_DATA_KEY, JSON.stringify(data));
      localStorage.setItem(POMODORO_SETTINGS_KEY, JSON.stringify({
        workMin: data.pomodoroWorkMin,
        breakMin: data.pomodoroBreakMin,
      }));
    } catch { /* Daily state remains available for the current session. */ }
  }, [data]);

  useEffect(() => {
    let midnightTimer;

    const resetIfNeeded = () => {
      const today = getLocalDateKey();
      setData(current => {
        if (current.date === today) return current;
        saveBackup(current);
        return createFreshDailyData(today, current);
      });
    };

    const scheduleMidnight = () => {
      clearTimeout(midnightTimer);
      midnightTimer = setTimeout(() => {
        resetIfNeeded();
        scheduleMidnight();
      }, millisecondsUntilLocalMidnight() + 100);
    };

    const handleWake = () => {
      resetIfNeeded();
      scheduleMidnight();
    };
    const handleVisibility = () => {
      if (document.visibilityState === 'visible') handleWake();
    };

    resetIfNeeded();
    scheduleMidnight();
    const fallbackInterval = setInterval(resetIfNeeded, 60000);
    window.addEventListener('focus', handleWake);
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      clearTimeout(midnightTimer);
      clearInterval(fallbackInterval);
      window.removeEventListener('focus', handleWake);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, []);

  return [data, setData];
}

// Habit definitions persist; only their checked status is daily.
const DEFAULT_MICRO_TASKS = [
  { id: 1, text: 'Apply hair serum' },
  { id: 2, text: 'Polish shoes' },
  { id: 3, text: '20 pushups' },
  { id: 4, text: 'Wash face (morning)' },
  { id: 5, text: 'Wash face (night)' },
  { id: 6, text: 'Skincare routine' },
  { id: 7, text: 'Drink 2L water' },
];

export function useMicroConfig() {
  return useLocalStorage('pe_micro_config', DEFAULT_MICRO_TASKS);
}
