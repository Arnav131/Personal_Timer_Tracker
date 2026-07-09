import { useState, useEffect } from 'react';
import { playLoop, stopLoop } from '../utils/audioManager';
import PixelIcon from './PixelIcon';

/**
 * EnforcerModal - un-dismissable accountability popup.
 */
export default function EnforcerModal({ onSubmit }) {
  const [text, setText] = useState('');
  const [error, setError] = useState(false);
  const MIN_CHARS = 15;

  const now = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  const charCount = text.trim().length;
  const isValid = charCount >= MIN_CHARS;

  useEffect(() => {
    playLoop();
    return () => stopLoop();
  }, []);

  const handleSubmit = () => {
    if (!isValid) {
      setError(true);
      setTimeout(() => setError(false), 500);
      return;
    }
    stopLoop();
    onSubmit(text.trim());
  };

  return (
    <div className="modal-overlay" style={{ zIndex: 200 }}>
      <div className="modal-card glass-surface" style={{ maxWidth: 520 }}>
        <div className="enforcer-pixel">
          <PixelIcon name="star" size="xl" />
        </div>
        <div className="modal-card__title" style={{ fontSize: 18 }}>
          {now} - What did you accomplish this past hour?
        </div>
        <div className="modal-card__subtitle">
          Write at least {MIN_CHARS} characters to dismiss this window.
        </div>

        <textarea
          className={`enforcer-textarea ${error ? 'enforcer-textarea--error' : ''}`}
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="What were you working on? Be specific..."
          autoFocus
        />

        <div className={`enforcer-charcount ${isValid ? 'enforcer-charcount--valid' : ''}`}>
          {charCount} / {MIN_CHARS} min
        </div>

        <button
          className={`btn-pill ${isValid ? 'btn-pill--accent' : 'btn-pill--ghost'}`}
          onClick={handleSubmit}
          disabled={!isValid}
          style={{ width: '100%', height: 48 }}
        >
          Submit Log
        </button>
      </div>
    </div>
  );
}
