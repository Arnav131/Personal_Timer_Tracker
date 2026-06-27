import { useMemo } from 'react';

/**
 * PomodoroTimer — large SVG arc timer with controls.
 */
export default function PomodoroTimer({ timer, sessions, onSettingsClick }) {
  const { remaining, state, isBreak, progress } = timer;

  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;
  const timeStr = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  // SVG arc params
  const size = 260;
  const strokeWidth = 7;
  const radius = (size - strokeWidth * 2) / 2 - 10;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - progress);

  // Dot position on arc tip
  const angle = -Math.PI / 2 + (1 - progress) * 2 * Math.PI;
  const dotX = size / 2 + radius * Math.cos(angle);
  const dotY = size / 2 + radius * Math.sin(angle);

  const arcColor = isBreak ? 'var(--blue)' : 'var(--accent)';

  const modeLabel = isBreak ? 'Break' : 'Focus';
  const statusText = state === 'idle'
    ? 'Ready to focus'
    : state === 'paused'
      ? '⏸  Paused'
      : isBreak
        ? '☕  Relax and recharge'
        : '🔥  Stay on track!';

  return (
    <div className="pomodoro glass">
      <div className="pomodoro__header">
        <span className="pomodoro__title">🍅  Pomodoro Timer</span>
        <button className="icon-btn" onClick={onSettingsClick}>⚙</button>
      </div>

      <div className="pomodoro__arc-container">
        <svg className="pomodoro__svg" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {/* Track */}
          <circle
            className="pomodoro__track"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
          />
          {/* Progress arc */}
          <circle
            className="pomodoro__arc"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth + 1}
            stroke={arcColor}
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
          />
          {/* Glowing dot at tip */}
          {progress > 0 && progress < 1 && (
            <circle
              className="pomodoro__dot"
              cx={dotX}
              cy={dotY}
              r={5}
              fill={arcColor}
            />
          )}
        </svg>
        <span className="pomodoro__time">{timeStr}</span>
      </div>

      <span className="pomodoro__mode">{modeLabel}</span>
      <span className="pomodoro__status">{statusText}</span>
      <span className="pomodoro__session">
        Session {sessions + 1}  •  {sessions} completed today
      </span>

      <div className="pomodoro__controls">
        <button
          className="btn-pill btn-pill--accent"
          onClick={timer.start}
          disabled={state !== 'idle'}
        >
          ▶  Start
        </button>
        <button
          className="btn-pill btn-pill--ghost"
          onClick={state === 'paused' ? timer.resume : timer.pause}
          disabled={state === 'idle'}
        >
          {state === 'paused' ? '▶  Resume' : '⏸  Pause'}
        </button>
        <button
          className="btn-pill btn-pill--ghost"
          onClick={timer.reset}
        >
          ↺  Reset
        </button>
      </div>
    </div>
  );
}
