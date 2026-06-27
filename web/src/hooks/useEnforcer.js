import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * useEnforcer — 60-minute timer that triggers the accountability modal.
 */
export function useEnforcer() {
  const ENFORCER_INTERVAL = 60 * 60 * 1000; // 60 minutes
  const [showEnforcer, setShowEnforcer] = useState(false);
  const timerRef = useRef(null);

  const startTimer = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      setShowEnforcer(true);
    }, ENFORCER_INTERVAL);
  }, []);

  const resetTimer = useCallback(() => {
    setShowEnforcer(false);
    startTimer();
  }, [startTimer]);

  // Start on mount
  useEffect(() => {
    startTimer();
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [startTimer]);

  return {
    showEnforcer,
    setShowEnforcer,
    resetTimer,
  };
}
