import { useState, useEffect, useCallback } from 'react';

/**
 * useLocalStorage — persists React state to localStorage.
 * Handles daily reset for ephemeral data.
 */
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
    } catch {
      // localStorage full or unavailable
    }
  }, [key, value]);

  return [value, setValue];
}

/**
 * useDailyData — ephemeral daily data that resets at midnight.
 * Returns [data, setData] where data auto-resets if the date changes.
 */
export function useDailyData() {
  const today = new Date().toISOString().slice(0, 10);

  const getFresh = () => ({
    date: today,
    macroTasks: [],
    pomodoroSessions: 0,
    pomodoroWorkMin: 25,
    pomodoroBreakMin: 10,
    microStatus: {},
    enforcerLogs: [],
  });

  const [data, setData] = useState(() => {
    try {
      const stored = localStorage.getItem('pe_daily_data');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.date === today) return parsed;
        // Different day — backup and reset
        localStorage.setItem(`pe_backup_${parsed.date}`, stored);
      }
    } catch { /* ignore */ }
    return getFresh();
  });

  // Persist on every change
  useEffect(() => {
    localStorage.setItem('pe_daily_data', JSON.stringify(data));
  }, [data]);

  // Check for date change periodically
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date().toISOString().slice(0, 10);
      if (now !== data.date) {
        localStorage.setItem(`pe_backup_${data.date}`, JSON.stringify(data));
        setData(getFresh());
      }
    }, 60000); // check every minute
    return () => clearInterval(interval);
  }, [data.date]);

  return [data, setData];
}

/**
 * useMicroConfig — persistent micro task definitions.
 */
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
