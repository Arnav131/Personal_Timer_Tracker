import { useState, useEffect } from 'react';
import PixelIcon from './PixelIcon';

export default function Navbar({ onSettings, onPdf, auth, syncStatus }) {
  const [time, setTime] = useState('');

  useEffect(() => {
    const update = () => {
      const now = new Date();
      const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      const date = now.toLocaleDateString('en-US', opts);
      const t = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      setTime(`${date} | ${t}`);
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <nav className="navbar">
      <span className="navbar__title">
        <PixelIcon name="star" size="sm" />
        Productivity Enforcer
      </span>
      <span className="navbar__time">{time}</span>
      <div className="navbar__actions">
        <span className="navbar__sync" title={syncStatus}>{syncStatus}</span>
        {auth.user ? (
          <div className="account-chip" title={auth.user.email || 'Signed in'}>
            {auth.user.user_metadata?.avatar_url && (
              <img src={auth.user.user_metadata.avatar_url} alt="" referrerPolicy="no-referrer" />
            )}
            <span>{auth.user.user_metadata?.full_name?.split(' ')[0] || 'Account'}</span>
            <button onClick={auth.signOut} title="Sign out">Sign out</button>
          </div>
        ) : (
          <button
            className="btn-pill btn-pill--ghost btn-pill--sm"
            onClick={auth.signInWithGoogle}
            disabled={!auth.configured}
            title={auth.configured ? 'Save tasks with your Google account' : 'Configure Supabase to enable sign-in'}
          >
            <span className="google-mark">G</span> Sign in
          </button>
        )}
        <button className="btn-pill btn-pill--accent btn-pill--sm" onClick={onPdf}>
          <PixelIcon name="download" size="xs" />
          PDF
        </button>
        <button
          className="icon-btn icon-btn--settings-main"
          onClick={onSettings}
          title="Settings"
          aria-label="Settings"
        >
          <PixelIcon name="gear" size="lg" />
        </button>
      </div>
    </nav>
  );
}
