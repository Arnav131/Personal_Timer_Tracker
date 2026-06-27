import { useCallback, useEffect, useState } from 'react';
import { getLocalDateKey } from '../utils/localDate';

const REMINDER_KEY = 'pe_pdf_reminder_seen';

function reminderIsDue(now = new Date()) {
  return now.getHours() === 23 && now.getMinutes() >= 45;
}

export function useNightlyReminder() {
  const [showReminder, setShowReminder] = useState(false);
  const [permission, setPermission] = useState(
    typeof Notification === 'undefined' ? 'unsupported' : Notification.permission,
  );

  const dismissReminder = useCallback(() => {
    sessionStorage.setItem(REMINDER_KEY, getLocalDateKey());
    setShowReminder(false);
  }, []);

  const checkReminder = useCallback(() => {
    const today = getLocalDateKey();
    if (!reminderIsDue() || sessionStorage.getItem(REMINDER_KEY) === today) return;
    sessionStorage.setItem(REMINDER_KEY, today);
    setShowReminder(true);

    if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
      const notification = new Notification('Download today’s productivity report?', {
        body: 'It is 11:45 PM. Save your PDF before the daily reset at midnight.',
        icon: '/favicon.svg',
        tag: `productivity-report-${today}`,
      });
      notification.onclick = () => window.focus();
    }
  }, []);

  useEffect(() => {
    checkReminder();
    const interval = setInterval(checkReminder, 30000);
    window.addEventListener('focus', checkReminder);
    document.addEventListener('visibilitychange', checkReminder);
    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', checkReminder);
      document.removeEventListener('visibilitychange', checkReminder);
    };
  }, [checkReminder]);

  const requestPermission = useCallback(async () => {
    if (typeof Notification === 'undefined') {
      setPermission('unsupported');
      return 'unsupported';
    }
    const result = await Notification.requestPermission();
    setPermission(result);
    return result;
  }, []);

  return { showReminder, dismissReminder, permission, requestPermission };
}
