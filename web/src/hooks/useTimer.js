import { useState, useRef, useCallback, useEffect } from 'react';

export function calculateRemainingSeconds(deadlineMs, nowMs = Date.now()) {
  return Math.max(0, Math.ceil((deadlineMs - nowMs) / 1000));
}

/**
 * useTimer - Pomodoro countdown hook.
 * States: idle, running, paused
 */
export function useTimer(workMin = 25, breakMin = 10) {
  const [remaining, setRemaining] = useState(workMin * 60);
  const [state, setState] = useState('idle');
  const [isBreak, setIsBreak] = useState(false);

  const intervalRef = useRef(null);
  const deadlineRef = useRef(null);
  const onCompleteRef = useRef(null);
  const stateRef = useRef(state);
  const isBreakRef = useRef(isBreak);
  const remainingRef = useRef(remaining);

  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  useEffect(() => {
    isBreakRef.current = isBreak;
  }, [isBreak]);

  useEffect(() => {
    remainingRef.current = remaining;
  }, [remaining]);

  const clearTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const completeTimer = useCallback(() => {
    if (!deadlineRef.current) return;
    const completedBreak = isBreakRef.current;
    deadlineRef.current = null;
    clearTimer();
    remainingRef.current = 0;
    stateRef.current = 'idle';
    setRemaining(0);
    setState('idle');
    onCompleteRef.current?.(completedBreak);
  }, [clearTimer]);

  const syncRemainingToClock = useCallback(() => {
    if (!deadlineRef.current || stateRef.current !== 'running') return;
    const nextRemaining = calculateRemainingSeconds(deadlineRef.current);
    remainingRef.current = nextRemaining;
    setRemaining(current => (current === nextRemaining ? current : nextRemaining));
    if (nextRemaining <= 0) completeTimer();
  }, [completeTimer]);

  const beginSession = useCallback((durationSeconds, breakSession) => {
    const seconds = Math.max(1, Number(durationSeconds) || 1);
    deadlineRef.current = Date.now() + seconds * 1000;
    isBreakRef.current = breakSession;
    remainingRef.current = seconds;
    stateRef.current = 'running';
    setIsBreak(breakSession);
    setRemaining(seconds);
    setState('running');
  }, []);

  useEffect(() => {
    if (stateRef.current === 'idle' && !isBreakRef.current) {
      remainingRef.current = workMin * 60;
      setRemaining(workMin * 60);
    }
  }, [workMin]);

  const start = useCallback(() => {
    if (stateRef.current !== 'idle') return;
    beginSession(workMin * 60, false);
  }, [beginSession, workMin]);

  const startBreak = useCallback(() => {
    beginSession(breakMin * 60, true);
  }, [beginSession, breakMin]);

  const startWork = useCallback(() => {
    beginSession(workMin * 60, false);
  }, [beginSession, workMin]);

  const pause = useCallback(() => {
    if (stateRef.current !== 'running') return;
    const nextRemaining = deadlineRef.current
      ? calculateRemainingSeconds(deadlineRef.current)
      : remainingRef.current;
    deadlineRef.current = null;
    clearTimer();
    remainingRef.current = nextRemaining;
    stateRef.current = 'paused';
    setRemaining(nextRemaining);
    setState('paused');
  }, [clearTimer]);

  const resume = useCallback(() => {
    if (stateRef.current !== 'paused' || remainingRef.current <= 0) return;
    deadlineRef.current = Date.now() + remainingRef.current * 1000;
    stateRef.current = 'running';
    setState('running');
  }, []);

  const reset = useCallback(() => {
    deadlineRef.current = null;
    clearTimer();
    isBreakRef.current = false;
    remainingRef.current = workMin * 60;
    stateRef.current = 'idle';
    setIsBreak(false);
    setRemaining(workMin * 60);
    setState('idle');
  }, [clearTimer, workMin]);

  const onComplete = useCallback((fn) => {
    onCompleteRef.current = fn;
  }, []);

  useEffect(() => {
    clearTimer();

    if (state !== 'running') return clearTimer;

    syncRemainingToClock();
    intervalRef.current = setInterval(syncRemainingToClock, 250);

    const handleVisibility = () => {
      if (document.visibilityState === 'visible') syncRemainingToClock();
    };

    window.addEventListener('focus', syncRemainingToClock);
    window.addEventListener('pageshow', syncRemainingToClock);
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      clearTimer();
      window.removeEventListener('focus', syncRemainingToClock);
      window.removeEventListener('pageshow', syncRemainingToClock);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, [state, clearTimer, syncRemainingToClock]);

  const totalSeconds = isBreak ? breakMin * 60 : workMin * 60;
  const progress = totalSeconds > 0 ? remaining / totalSeconds : 0;

  return {
    remaining,
    state,
    isBreak,
    progress,
    totalSeconds,
    start,
    startBreak,
    startWork,
    pause,
    resume,
    reset,
    onComplete,
  };
}
