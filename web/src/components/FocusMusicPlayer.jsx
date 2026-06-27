import { useEffect, useRef, useState } from 'react';
import { deleteTrack, getTracks, saveTrack } from '../utils/musicStore';

const DEFAULT_TRACKS = [
  {
    id: 'bundled:downtown-glow',
    name: 'Downtown Glow',
    url: '/audio/downtown-glow.mp3',
    bundled: true,
  },
  {
    id: 'bundled:colorful-flowers',
    name: 'Colorful Flowers',
    url: '/audio/colorful-flowers.mp3',
    bundled: true,
  },
];

function createId() {
  return globalThis.crypto?.randomUUID?.()
    || `track-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function cleanTrackName(filename) {
  return filename
    .replace(/\.mp3$/i, '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim() || 'Untitled track';
}

function PreviousIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M6 5v14M18 6l-9 6 9 6z" />
    </svg>
  );
}

function NextIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M18 5v14M6 6l9 6-9 6z" />
    </svg>
  );
}

function PlaybackIcon({ paused }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      {paused
        ? <path d="M8 5v14l11-7z" />
        : <path d="M7 5h4v14H7zM14 5h4v14h-4z" />}
    </svg>
  );
}

export default function FocusMusicPlayer({ pauseSignal = 0 }) {
  const fileInputRef = useRef(null);
  const audioRef = useRef(null);
  const objectUrlsRef = useRef(new Set());
  const [tracks, setTracks] = useState(DEFAULT_TRACKS);
  const [activeIndex, setActiveIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [volume, setVolume] = useState(() => {
    const savedVolume = localStorage.getItem('pe_music_volume');
    const stored = savedVolume === null ? Number.NaN : Number(savedVolume);
    return Number.isFinite(stored) ? Math.min(1, Math.max(0, stored)) : 0.65;
  });

  const activeTrack = tracks[activeIndex] || null;

  useEffect(() => {
    let cancelled = false;
    const urls = objectUrlsRef.current;
    const audio = audioRef.current;

    getTracks()
      .then(rows => {
        if (cancelled) return;
        const hydrated = rows
          .sort((a, b) => a.createdAt - b.createdAt)
          .map(row => {
            const url = URL.createObjectURL(row.blob);
            urls.add(url);
            return { ...row, url };
          });
        setTracks([...DEFAULT_TRACKS, ...hydrated]);
      })
      .catch(error => {
        if (!cancelled) {
          setTracks(DEFAULT_TRACKS);
          setUploadError(error?.message || 'Saved music could not be loaded.');
        }
      });

    return () => {
      cancelled = true;
      audio?.pause();
      urls.forEach(url => URL.revokeObjectURL(url));
      urls.clear();
    };
  }, []);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.volume = volume;
    try {
      localStorage.setItem('pe_music_volume', String(volume));
    } catch { /* Volume still works when browser storage is unavailable. */ }
  }, [volume]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (!isPlaying || !activeTrack) {
      audio.pause();
      return;
    }

    audio.play().catch(() => setIsPlaying(false));
  }, [activeTrack, isPlaying]);

  useEffect(() => {
    if (pauseSignal > 0) setIsPlaying(false);
  }, [pauseSignal]);

  const handleUpload = async (event) => {
    const selected = Array.from(event.target.files || []);
    event.target.value = '';
    if (selected.length === 0) return;

    const mp3Files = selected.filter(file => (
      file.type === 'audio/mpeg' || file.name.toLowerCase().endsWith('.mp3')
    ));

    setUploadError(mp3Files.length === selected.length ? '' : 'Only MP3 files can be added.');

    const added = [];
    for (const file of mp3Files) {
      const stored = {
        id: createId(),
        name: cleanTrackName(file.name),
        blob: file,
        createdAt: Date.now() + added.length,
      };

      try {
        await saveTrack(stored);
        const url = URL.createObjectURL(file);
        objectUrlsRef.current.add(url);
        added.push({ ...stored, url });
      } catch (error) {
        setUploadError(error?.message || 'One or more tracks could not be saved.');
        break;
      }
    }

    if (added.length > 0) setTracks(previous => [...previous, ...added]);
  };

  const togglePlayback = () => {
    if (!activeTrack) {
      fileInputRef.current?.click();
      return;
    }
    setIsPlaying(previous => !previous);
  };

  const changeTrack = (direction) => {
    if (tracks.length < 2) return;
    setActiveIndex(previous => (previous + direction + tracks.length) % tracks.length);
  };

  const removeActiveTrack = async () => {
    if (!activeTrack) return;
    const removedIndex = activeIndex;
    const removed = activeTrack;
    setIsPlaying(false);

    try {
      await deleteTrack(removed.id);
      objectUrlsRef.current.delete(removed.url);
      URL.revokeObjectURL(removed.url);
      setTracks(previous => previous.filter(track => track.id !== removed.id));
      setActiveIndex(Math.max(0, Math.min(removedIndex, tracks.length - 2)));
      setUploadError('');
    } catch (error) {
      setUploadError(error?.message || 'This track could not be removed.');
    }
  };

  return (
    <section className="music-player" aria-label="Focus music player">
      <div className="music-player__header">
        <div>
          <span className="music-player__eyebrow">FOCUS MUSIC</span>
          <span className="music-player__count">
            {tracks.length ? `${activeIndex + 1} / ${tracks.length}` : 'Your MP3s'}
          </span>
        </div>
        <div className="music-player__actions">
          {activeTrack && !activeTrack.bundled && (
            <button type="button" className="music-player__small-btn" onClick={removeActiveTrack}
              title="Remove current track" aria-label="Remove current track">
              &minus;
            </button>
          )}
          <button type="button" className="music-player__add-btn"
            onClick={() => fileInputRef.current?.click()} title="Add MP3 files" aria-label="Add MP3 files">
            +
          </button>
        </div>
      </div>

      <div className="music-player__main">
        <div className="music-player__controls">
          <button type="button" className="music-player__skip" onClick={() => changeTrack(-1)}
            disabled={tracks.length < 2} title="Previous track" aria-label="Previous track">
            <PreviousIcon />
          </button>

          <button type="button" className={`music-player__play ${isPlaying ? 'music-player__play--active' : ''}`}
            onClick={togglePlayback}
            aria-label={isPlaying ? 'Pause music' : activeTrack ? 'Play music' : 'Add MP3 files'}>
            <PlaybackIcon paused={!isPlaying} />
          </button>

          <button type="button" className="music-player__skip" onClick={() => changeTrack(1)}
            disabled={tracks.length < 2} title="Next track" aria-label="Next track">
            <NextIcon />
          </button>
        </div>

        <div className="music-player__track">
          <div className="music-player__name" title={activeTrack?.name || ''}>
            {activeTrack?.name || 'Add your focus track'}
          </div>
        </div>
      </div>

      <div className="music-player__volume">
        <span className="music-player__volume-icon" aria-hidden="true">{volume === 0 ? '×' : '♪'}</span>
        <label htmlFor="focus-music-volume">Volume</label>
        <input id="focus-music-volume" type="range" min="0" max="1" step="0.01" value={volume}
          onChange={event => setVolume(Number(event.target.value))}
          style={{ '--volume-pct': `${volume * 100}%` }}
          aria-valuetext={`${Math.round(volume * 100)} percent`} />
        <span className="music-player__volume-value">{Math.round(volume * 100)}%</span>
      </div>

      {uploadError && <div className="music-player__error" role="alert">{uploadError}</div>}
      <input ref={fileInputRef} className="music-player__file-input" type="file"
        accept="audio/mpeg,.mp3" multiple onChange={handleUpload} />
      <audio ref={audioRef} src={activeTrack?.url || undefined} loop />
    </section>
  );
}
