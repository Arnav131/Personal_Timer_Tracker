/**
 * ProgressDashboard - task progress rings plus Pomodoro count.
 */

import FocusMusicPlayer from './FocusMusicPlayer';

function getColor(pct) {
  if (pct <= 33) return 'var(--accent)';
  if (pct <= 66) return 'var(--blue)';
  return 'var(--success)';
}

function ProgressRing({ pct, title, subtitle }) {
  const safePct = Math.max(0, Math.min(100, pct));
  const size = 110;
  const strokeWidth = 6;
  const radius = (size - strokeWidth * 2) / 2 - 4;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - safePct / 100);
  const color = getColor(safePct);

  return (
    <div className="progress-ring">
      <svg className="progress-ring__svg" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          className="progress-ring__track"
          cx={size / 2} cy={size / 2} r={radius}
          strokeWidth={strokeWidth}
        />
        <circle
          className="progress-ring__fill"
          cx={size / 2} cy={size / 2} r={radius}
          strokeWidth={strokeWidth + 1}
          stroke={color}
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
        />
      </svg>
      <span className="progress-ring__pct" style={{ color }}>{Math.round(safePct)}%</span>
      <span className="progress-ring__title">{title}</span>
      <span className="progress-ring__sub">{subtitle}</span>
    </div>
  );
}

function PomodoroCount({ count }) {
  return (
    <div className="progress-count" aria-label={`${count} Pomodoro sessions completed today`}>
      <span className="progress-count__value">{count}</span>
      <span className="progress-ring__title">Pomodoros</span>
      <span className="progress-ring__sub">completed today</span>
    </div>
  );
}

export default function ProgressDashboard({ data, musicPauseSignal }) {
  const macroTasks = data.macroTasks || [];
  const macroDone = macroTasks.filter(t => t.done).length;
  const macroPct = macroTasks.length > 0 ? (macroDone / macroTasks.length) * 100 : 0;

  const microTasks = data.microTasks || [];
  const microDone = microTasks.filter(t => t.done).length;
  const microPct = microTasks.length > 0 ? (microDone / microTasks.length) * 100 : 0;

  const pomodoroCount = Math.max(0, Number(data.pomodoroSessions) || 0);

  return (
    <div className="progress-dashboard glass">
      <div className="progress-dashboard__metrics">
        <ProgressRing pct={macroPct} title="Macro Progress" subtitle="Task completion" />
        <div className="progress-divider" />
        <PomodoroCount count={pomodoroCount} />
        <div className="progress-divider" />
        <ProgressRing pct={microPct} title="Micro Progress" subtitle="Small actions" />
      </div>
      <div className="progress-dashboard__section-divider" />
      <FocusMusicPlayer pauseSignal={musicPauseSignal} />
    </div>
  );
}
