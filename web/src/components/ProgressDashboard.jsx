/**
 * ProgressDashboard — dual SVG progress rings.
 */

function getColor(pct) {
  if (pct <= 33) return 'var(--accent)';
  if (pct <= 66) return 'var(--blue)';
  return 'var(--success)';
}

function ProgressRing({ pct, title, subtitle }) {
  const size = 110;
  const strokeWidth = 6;
  const radius = (size - strokeWidth * 2) / 2 - 4;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - pct / 100);
  const color = getColor(pct);

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
      <span className="progress-ring__pct" style={{ color }}>{Math.round(pct)}%</span>
      <span className="progress-ring__title">{title}</span>
      <span className="progress-ring__sub">{subtitle}</span>
    </div>
  );
}

export default function ProgressDashboard({ data, microConfig }) {
  // Macro progress: 50% tasks + 50% pomodoro (cap at 8)
  const tasks = data.macroTasks;
  const taskRatio = tasks.length > 0
    ? tasks.filter(t => t.done).length / tasks.length
    : 0;
  const sessionRatio = Math.min(data.pomodoroSessions / 8, 1);
  const macroPct = (taskRatio * 0.5 + sessionRatio * 0.5) * 100;

  // Micro progress
  const microTotal = microConfig.length;
  const microDone = microTotal > 0
    ? microConfig.filter(t => data.microStatus[t.id]).length
    : 0;
  const microPct = microTotal > 0 ? (microDone / microTotal) * 100 : 0;

  return (
    <div className="progress-dashboard glass">
      <ProgressRing pct={macroPct} title="Macro Progress" subtitle="Study & Tasks" />
      <div className="progress-divider" />
      <ProgressRing pct={microPct} title="Micro Progress" subtitle="Daily Habits" />
    </div>
  );
}
