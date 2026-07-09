import PixelIcon from './PixelIcon';

/**
 * PomodoroTimer - large SVG arc timer with controls.
 */
export default function PomodoroTimer({ timer, sessions, onSettingsClick }) {
  const { remaining, state, isBreak, progress } = timer;

  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;
  const timeStr = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  const size = 260;
  const strokeWidth = 7;
  const radius = (size - strokeWidth * 2) / 2 - 10;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - progress);

  const angle = -Math.PI / 2 + (1 - progress) * 2 * Math.PI;
  const dotX = size / 2 + radius * Math.cos(angle);
  const dotY = size / 2 + radius * Math.sin(angle);

  const arcColor = isBreak ? 'var(--blue)' : 'var(--accent)';
  const modeLabel = isBreak ? 'Break' : 'Focus';
  const status = state === 'idle'
    ? { text: 'Ready to focus', icon: 'star' }
    : state === 'paused'
      ? { text: 'Paused', icon: 'pause' }
      : isBreak
        ? { text: 'Relax and recharge', icon: 'coffee' }
        : { text: 'Stay on track', icon: 'fire' };

  return (
    <div className="pomodoro glass">
      <div className="pomodoro__header">
        <span className="pomodoro__title">
          <PixelIcon name="tomato" size="sm" />
          Pomodoro Timer
        </span>
        <button className="icon-btn" onClick={onSettingsClick} title="Timer settings" aria-label="Timer settings">
          <PixelIcon name="gear" size="sm" />
        </button>
      </div>

      <div className="pomodoro__arc-container">
        <svg className="pomodoro__svg" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <circle
            className="pomodoro__track"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
          />
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
      <span className="pomodoro__status">
        <PixelIcon name={status.icon} size="xs" />
        {status.text}
      </span>
      <span className="pomodoro__session">
        Session {sessions + 1} | {sessions} completed today
      </span>

      <div className="pomodoro__controls">
        <button
          className="btn-pill btn-pill--accent"
          onClick={timer.start}
          disabled={state !== 'idle'}
        >
          <PixelIcon name="play" size="xs" />
          Start
        </button>
        <button
          className="btn-pill btn-pill--ghost"
          onClick={state === 'paused' ? timer.resume : timer.pause}
          disabled={state === 'idle'}
        >
          <PixelIcon name={state === 'paused' ? 'play' : 'pause'} size="xs" />
          {state === 'paused' ? 'Resume' : 'Pause'}
        </button>
        <button
          className="btn-pill btn-pill--ghost"
          onClick={timer.reset}
        >
          <PixelIcon name="reset" size="xs" />
          Reset
        </button>
      </div>
    </div>
  );
}
