import { useCallback, useEffect, useRef, useState } from 'react';
import { supabase } from '../lib/supabase';
import { getLocalDateKey, millisecondsUntilLocalMidnight } from '../utils/localDate';
import {
  createFreshDailyData,
  createGuestState,
  normalizeDailyData,
  normalizeMicroConfig,
} from '../utils/dailyData';

const GUEST_STATE_KEY = 'pe_guest_session';
const LEGACY_DAILY_KEY = 'pe_daily_data';
const LEGACY_MICRO_KEY = 'pe_micro_config';

function readGuestState() {
  const today = getLocalDateKey();
  try {
    const sessionValue = sessionStorage.getItem(GUEST_STATE_KEY);
    if (!sessionValue) {
      const legacyDaily = localStorage.getItem(LEGACY_DAILY_KEY);
      const legacyMicro = localStorage.getItem(LEGACY_MICRO_KEY);
      if (legacyDaily || legacyMicro) {
        const migrated = {
          data: normalizeDailyData(legacyDaily ? JSON.parse(legacyDaily) : null, today),
          microConfig: normalizeMicroConfig(legacyMicro ? JSON.parse(legacyMicro) : null),
        };
        saveGuestState(migrated.data, migrated.microConfig);
        localStorage.removeItem(LEGACY_DAILY_KEY);
        localStorage.removeItem(LEGACY_MICRO_KEY);
        localStorage.removeItem('pe_pomodoro_settings');
        return migrated;
      }
    }
    const stored = JSON.parse(sessionValue);
    return {
      data: normalizeDailyData(stored?.data, today),
      microConfig: normalizeMicroConfig(stored?.microConfig),
    };
  } catch {
    return createGuestState(today);
  }
}

function saveGuestState(data, microConfig) {
  try {
    sessionStorage.setItem(GUEST_STATE_KEY, JSON.stringify({ data, microConfig }));
  } catch {
    // The React state still keeps the guest's work for this open tab.
  }
}

function toDatabaseRow(userId, data, microConfig) {
  return {
    user_id: userId,
    daily_date: data.date,
    daily_data: data,
    micro_config: microConfig,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    updated_at: new Date().toISOString(),
  };
}

export function useProductivityData(user, authLoading) {
  const guest = useRef(readGuestState());
  const [data, setData] = useState(guest.current.data);
  const [microConfig, setMicroConfig] = useState(guest.current.microConfig);
  const [loading, setLoading] = useState(true);
  const [syncStatus, setSyncStatus] = useState('Loading…');
  const [syncError, setSyncError] = useState('');
  const loadedOwner = useRef(null);
  const saveSequence = useRef(0);

  useEffect(() => {
    if (authLoading) return;
    let cancelled = false;
    const owner = user?.id || 'guest';
    loadedOwner.current = null;
    setLoading(true);
    setSyncError('');

    const load = async () => {
      if (!user || !supabase) {
        const next = readGuestState();
        if (cancelled) return;
        setData(next.data);
        setMicroConfig(next.microConfig);
        loadedOwner.current = 'guest';
        setSyncStatus('Guest · this tab only');
        setLoading(false);
        return;
      }

      setSyncStatus('Loading cloud data…');
      const { data: row, error } = await supabase
        .from('user_productivity_state')
        .select('daily_date,daily_data,micro_config')
        .eq('user_id', user.id)
        .maybeSingle();

      if (cancelled) return;
      if (error) {
        setSyncError(error.message);
        setSyncStatus('Cloud sync error');
        setLoading(false);
        return;
      }

      const today = getLocalDateKey();
      let nextData;
      let nextMicro;

      if (row) {
        nextData = row.daily_date === today
          ? normalizeDailyData(row.daily_data, today)
          : createFreshDailyData(today, row.daily_data);
        nextMicro = normalizeMicroConfig(row.micro_config);
      } else {
        // First sign-in keeps work already entered in this tab.
        const currentGuest = readGuestState();
        nextData = normalizeDailyData(currentGuest.data, today);
        nextMicro = normalizeMicroConfig(currentGuest.microConfig);
      }

      setData(nextData);
      setMicroConfig(nextMicro);
      loadedOwner.current = owner;

      const { error: saveError } = await supabase
        .from('user_productivity_state')
        .upsert(toDatabaseRow(user.id, nextData, nextMicro), { onConflict: 'user_id' });

      if (cancelled) return;
      if (!saveError) sessionStorage.removeItem(GUEST_STATE_KEY);
      setSyncError(saveError?.message || '');
      setSyncStatus(saveError ? 'Cloud sync error' : 'Saved to cloud');
      setLoading(false);
    };

    load();
    return () => { cancelled = true; };
  }, [user, authLoading]);

  useEffect(() => {
    if (loading || loadedOwner.current !== (user?.id || 'guest')) return;

    if (!user || !supabase) {
      saveGuestState(data, microConfig);
      setSyncStatus('Guest · this tab only');
      return;
    }

    const sequence = ++saveSequence.current;
    setSyncStatus('Saving…');
    const timer = setTimeout(async () => {
      const { error } = await supabase
        .from('user_productivity_state')
        .upsert(toDatabaseRow(user.id, data, microConfig), { onConflict: 'user_id' });
      if (sequence !== saveSequence.current) return;
      setSyncError(error?.message || '');
      setSyncStatus(error ? 'Cloud sync error' : 'Saved to cloud');
    }, 450);

    return () => clearTimeout(timer);
  }, [data, microConfig, user, loading]);

  const resetDay = useCallback(() => {
    setData(current => createFreshDailyData(getLocalDateKey(), current));
    setMicroConfig(normalizeMicroConfig(null));
  }, []);

  useEffect(() => {
    if (loading) return;
    let midnightTimer;

    const resetIfNeeded = () => {
      const today = getLocalDateKey();
      setData(current => current.date === today
        ? current
        : createFreshDailyData(today, current));
    };
    const schedule = () => {
      clearTimeout(midnightTimer);
      midnightTimer = setTimeout(() => {
        resetIfNeeded();
        schedule();
      }, millisecondsUntilLocalMidnight() + 250);
    };
    const handleVisibility = () => {
      if (document.visibilityState === 'visible') resetIfNeeded();
    };

    resetIfNeeded();
    schedule();
    const interval = setInterval(resetIfNeeded, 60000);
    window.addEventListener('focus', resetIfNeeded);
    document.addEventListener('visibilitychange', handleVisibility);
    return () => {
      clearTimeout(midnightTimer);
      clearInterval(interval);
      window.removeEventListener('focus', resetIfNeeded);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, [loading]);

  return {
    data,
    setData,
    microConfig,
    setMicroConfig,
    loading,
    syncStatus,
    syncError,
    resetDay,
  };
}
