function pad(value) {
  return String(value).padStart(2, '0');
}

/** Returns YYYY-MM-DD using the user's local calendar, not UTC. */
export function getLocalDateKey(date = new Date()) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

/** Returns HH:MM:SS using the user's local clock. */
export function getLocalTimeKey(date = new Date()) {
  return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

/** Milliseconds until the next local midnight, including DST changes. */
export function millisecondsUntilLocalMidnight(date = new Date()) {
  const midnight = new Date(
    date.getFullYear(),
    date.getMonth(),
    date.getDate() + 1,
  );
  return Math.max(0, midnight.getTime() - date.getTime());
}
