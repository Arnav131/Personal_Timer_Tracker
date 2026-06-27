import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * useTimer — Pomodoro countdown hook.
 * States: idle, running, paused, break
 */
export function useTimer(workMin = 25, breakMin = 10) {
  const [remaining, setRemaining] = useState(workMin * 60);
  const [state, setState] = useState('idle'); // idle | running | paused
  const [isBreak, setIsBreak] = useState(false);
  const intervalRef = useRef(null);
  const onCompleteRef = useRef(null);

  // Update durations when they change (only when idle)
  useEffect(() => {
    if (state === 'idle' && !isBreak) {
      setRemaining(workMin * 60);
    }
  }, [workMin]);

  const clearTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const start = useCallback(() => {
    if (state !== 'idle') return;
    setIsBreak(false);
    setRemaining(workMin * 60);
    setState('running');
  }, [state, workMin]);

  const startBreak = useCallback(() => {
    setIsBreak(true);
    setRemaining(breakMin * 60);
    setState('running');
  }, [breakMin]);

  const startWork = useCallback(() => {
    setIsBreak(false);
    setRemaining(workMin * 60);
    setState('running');
  }, [workMin]);

  const pause = useCallback(() => {
    if (state === 'running') {
      setState('paused');
    }
  }, [state]);

  const resume = useCallback(() => {
    if (state === 'paused') {
      setState('running');
    }
  }, [state]);

  const reset = useCallback(() => {
    clearTimer();
    setIsBreak(false);
    setRemaining(workMin * 60);
    setState('idle');
  }, [clearTimer, workMin]);

  // Set completion callback
  const onComplete = useCallback((fn) => {
    onCompleteRef.current = fn;
  }, []);

  // Timer tick
  useEffect(() => {
    clearTimer();
    if (state === 'running') {
      intervalRef.current = setInterval(() => {
        setRemaining(prev => {
          if (prev <= 1) {
            clearTimer();
            setState('idle');
            if (onCompleteRef.current) {
              onCompleteRef.current(isBreak);
            }
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return clearTimer;
  }, [state, clearTimer, isBreak]);

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
