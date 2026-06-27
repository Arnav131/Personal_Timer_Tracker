import { useRef, useState } from 'react';

/**
 * SettingsPanel — Background picker with thumbnails, custom upload, and panel transparency slider.
 */
export default function SettingsPanel({
  bgUrl,
  allBackgrounds,
  setBackground,
  addCustomBackground,
  panelTransparency,
  setPanelTransparency,
  onResetDay,
  notificationPermission,
  onEnableNotifications,
  user,
  onClose,
}) {
  const fileRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError('');
    try {
      const name = file.name.replace(/\.[^.]+$/, '').replace(/[_-]/g, ' ');
      await addCustomBackground(name, file);
    } catch (error) {
      setUploadError(error?.message || 'The image could not be saved.');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-card glass-surface" onClick={e => e.stopPropagation()}>
        <div className="settings-card__title">⚙  Settings</div>
        <div className="settings-card__subtitle">Choose a background to set the mood</div>

        <div className="settings-card__section">🖼  Backgrounds</div>

        <div className="settings-grid">
          {allBackgrounds.map((bg, i) => (
            <div
              key={i}
              className={`settings-thumb ${bg.file === bgUrl ? 'settings-thumb--active' : ''}`}
              onClick={() => setBackground(bg.file)}
            >
              <img src={bg.file} alt={bg.name} loading="lazy" />
              <div className="settings-thumb__name">{bg.name}</div>
            </div>
          ))}
        </div>

        {/* Panel Transparency Slider */}
        <div className="settings-card__section">🔲  Panel Transparency</div>
        <div className="transparency-slider">
          <div className="transparency-slider__header">
            <span className="transparency-slider__label">Background visibility</span>
            <span className="transparency-slider__value">{panelTransparency}%</span>
          </div>
          <div className="transparency-slider__track-wrapper">
            <input
              type="range"
              min="0"
              max="100"
              step="1"
              value={panelTransparency}
              onChange={(e) => setPanelTransparency(Number(e.target.value))}
              className="transparency-slider__input"
              style={{
                '--slider-pct': `${panelTransparency}%`,
              }}
            />
            <div className="transparency-slider__labels">
              <span>Opaque</span>
              <span>Transparent</span>
            </div>
          </div>
        </div>

        <div className="settings-card__section">Account & daily data</div>
        <div className="settings-data-card">
          <div>
            <strong>{user ? 'Cloud saving is on' : 'Guest session'}</strong>
            <p>
              {user
                ? `Signed in as ${user.email}. Today’s work follows you across devices.`
                : 'Tasks are kept only in this browser tab. Sign in from the top bar for cloud saving.'}
            </p>
          </div>
          <button className="btn-pill btn-pill--danger btn-pill--sm" onClick={onResetDay}>
            Reset today
          </button>
        </div>

        <div className="settings-card__section">11:45 PM report reminder</div>
        <div className="settings-data-card">
          <div>
            <strong>Browser notification: {notificationPermission}</strong>
            <p>An in-app reminder appears at 11:45 PM whenever this page is open.</p>
          </div>
          {notificationPermission !== 'granted' && notificationPermission !== 'unsupported' && (
            <button className="btn-pill btn-pill--ghost btn-pill--sm" onClick={onEnableNotifications}>
              Enable alerts
            </button>
          )}
        </div>

        <div className="settings-actions">
          <button
            className="btn-pill btn-pill--accent"
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? 'Saving image…' : '📁  Load Custom Image'}
          </button>
          <button className="btn-pill btn-pill--ghost" onClick={onClose}>
            Close
          </button>
        </div>

        {uploadError && <div className="settings-upload-error" role="alert">{uploadError}</div>}

        <input
          ref={fileRef}
          type="file"
          accept="image/png,image/jpeg,image/webp"
          style={{ display: 'none' }}
          onChange={handleUpload}
        />
      </div>
    </div>
  );
}
