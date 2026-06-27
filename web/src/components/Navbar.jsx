import { useState, useEffect } from 'react';

export default function Navbar({ onSettings, onPdf }) {
  const [time, setTime] = useState('');

  useEffect(() => {
    const update = () => {
      const now = new Date();
      const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      const date = now.toLocaleDateString('en-US', opts);
      const t = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      setTime(`${date}  •  ${t}`);
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <nav className="navbar">
      <span className="navbar__title">✦  Productivity Enforcer</span>
      <span className="navbar__time">{time}</span>
      <div className="navbar__actions">
        <button className="btn-pill btn-pill--accent btn-pill--sm" onClick={onPdf}>
          📥 PDF
        </button>
        <button className="icon-btn" onClick={onSettings} title="Settings">⚙</button>
      </div>
    </nav>
  );
}
