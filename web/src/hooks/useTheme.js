import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { extractDominantColor } from '../utils/colorExtractor';
import { getCustomBackgrounds, saveCustomBackground } from '../utils/backgroundStore';

const BACKGROUNDS = [
  { id: 'bundled:ramen-shop', name: 'Ramen Shop', file: '/backgrounds/ramen_shop.png' },
  { id: 'bundled:cozy-study-room', name: 'Cozy Study Room', file: '/backgrounds/cozy_study_room.png' },
  { id: 'bundled:rainy-rooftop', name: 'Rainy Rooftop', file: '/backgrounds/rainy_rooftop.png' },
  { id: 'bundled:moonlit-garden', name: 'Moonlit Garden', file: '/backgrounds/moonlit_garden.png' },
];

const DEFAULT_BACKGROUND = BACKGROUNDS[0];

function createId() {
  const randomPart = globalThis.crypto?.randomUUID?.()
    || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `custom:${randomPart}`;
}

function loadImage(url) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = resolve;
    image.onerror = () => reject(new Error('The selected file is not a readable image.'));
    image.src = url;
  });
}

/**
 * Manages bundled/custom backgrounds, accent colors, and glass transparency.
 * Custom image blobs are persisted in IndexedDB to avoid localStorage quotas.
 */
export function useTheme() {
  const [bgUrl, setBgUrl] = useState(() => {
    const legacyUrl = localStorage.getItem('pe_bg_url');
    return BACKGROUNDS.some(background => background.file === legacyUrl)
      ? legacyUrl
      : DEFAULT_BACKGROUND.file;
  });
  const [selectedId, setSelectedId] = useState(() => {
    const storedId = localStorage.getItem('pe_background_selection');
    if (storedId) return storedId;
    const legacyUrl = localStorage.getItem('pe_bg_url');
    return BACKGROUNDS.find(background => background.file === legacyUrl)?.id
      || DEFAULT_BACKGROUND.id;
  });
  const [customBgs, setCustomBgs] = useState([]);
  const [panelTransparency, setPanelTransparency] = useState(() => {
    const stored = localStorage.getItem('pe_panel_transparency');
    const parsed = stored !== null ? Number(stored) : 35;
    return Number.isFinite(parsed) ? Math.min(100, Math.max(0, parsed)) : 35;
  });
  const objectUrls = useRef(new Set());

  const applyAccentFromImage = useCallback((url) => {
    extractDominantColor(url).then(({ accent, accentSoft, accentRgb }) => {
      document.documentElement.style.setProperty('--accent', accent);
      document.documentElement.style.setProperty('--accent-soft', accentSoft);
      document.documentElement.style.setProperty('--accent-rgb', accentRgb);
    }).catch(() => {
      document.documentElement.style.setProperty('--accent', '#d4a853');
      document.documentElement.style.setProperty('--accent-soft', '#c8956c');
      document.documentElement.style.setProperty('--accent-rgb', '212, 168, 83');
    });
  }, []);

  // Restore custom images and migrate images saved by the old base64 implementation.
  useEffect(() => {
    let cancelled = false;
    const urls = objectUrls.current;

    const hydrate = async () => {
      try {
        const rows = await getCustomBackgrounds();
        if (cancelled) return;
        const legacyJson = localStorage.getItem('pe_custom_bgs');
        const legacySelectedUrl = localStorage.getItem('pe_bg_url');
        let migratedSelection = null;
        let legacyBackgrounds = [];

        if (legacyJson) {
          try {
            const parsed = JSON.parse(legacyJson);
            if (Array.isArray(parsed)) legacyBackgrounds = parsed;
          } catch {
            // A damaged gallery should not prevent valid IndexedDB images loading.
          }
        }

        // The old implementation could save the active image and then run out of
        // localStorage space before saving the gallery. Recover that image too.
        if (
          legacySelectedUrl?.startsWith('data:image/')
          && !legacyBackgrounds.some(background => background?.file === legacySelectedUrl)
        ) {
          legacyBackgrounds.push({ name: 'Custom background', file: legacySelectedUrl });
        }

        if (legacyBackgrounds.length > 0) {
          for (const background of legacyBackgrounds) {
            if (!background?.file?.startsWith('data:image/')) continue;
            const blob = await fetch(background.file).then(response => response.blob());
            const row = {
              id: createId(),
              name: background.name || 'Custom background',
              blob,
              createdAt: Date.now(),
            };
            await saveCustomBackground(row);
            rows.push(row);
            if (background.file === legacySelectedUrl) migratedSelection = row.id;
          }

          localStorage.removeItem('pe_custom_bgs');
          localStorage.removeItem('pe_bg_url');
          if (migratedSelection) {
            localStorage.setItem('pe_background_selection', migratedSelection);
            setSelectedId(migratedSelection);
          }
        } else if (legacyJson) {
          // Discard only invalid legacy data after IndexedDB has loaded safely.
          localStorage.removeItem('pe_custom_bgs');
        }

        if (cancelled) return;
        const hydrated = rows.map(row => {
          const file = URL.createObjectURL(row.blob);
          urls.add(file);
          return { id: row.id, name: row.name, file };
        });
        setCustomBgs(hydrated);

        const storedSelection = migratedSelection
          || localStorage.getItem('pe_background_selection');
        const active = hydrated.find(background => background.id === storedSelection);
        if (active) setBgUrl(active.file);
      } catch (error) {
        console.error('Could not restore custom backgrounds:', error);
      }
    };

    hydrate();
    return () => {
      cancelled = true;
      urls.forEach(url => URL.revokeObjectURL(url));
      urls.clear();
    };
  }, []);

  useEffect(() => {
    // 0% transparency is solid; 100% is clear, unblurred glass.
    const opacity = 1 - panelTransparency / 100;
    const blur = opacity * 24;
    document.documentElement.style.setProperty(
      '--glass-bg',
      `rgba(18, 18, 36, ${opacity.toFixed(3)})`,
    );
    document.documentElement.style.setProperty(
      '--glass-surface',
      `rgba(26, 26, 46, ${opacity.toFixed(3)})`,
    );
    document.documentElement.style.setProperty('--blur', `${blur.toFixed(1)}px`);
    try {
      localStorage.setItem('pe_panel_transparency', String(panelTransparency));
    } catch { /* The live setting still works if storage is unavailable. */ }
  }, [panelTransparency]);

  useEffect(() => {
    applyAccentFromImage(bgUrl);
  }, [bgUrl, applyAccentFromImage]);

  useEffect(() => {
    try {
      localStorage.setItem('pe_background_selection', selectedId);
    } catch { /* The live setting still works if storage is unavailable. */ }
  }, [selectedId]);

  const setBackground = useCallback((url) => {
    const background = [...BACKGROUNDS, ...customBgs].find(item => item.file === url);
    if (!background) return;
    setSelectedId(background.id);
    setBgUrl(url);
  }, [customBgs]);

  const addCustomBackground = useCallback(async (name, fileBlob) => {
    if (!fileBlob?.type?.startsWith('image/')) {
      throw new Error('Please choose a PNG, JPEG, or WebP image.');
    }

    const previewUrl = URL.createObjectURL(fileBlob);
    try {
      await loadImage(previewUrl);
      const stored = {
        id: createId(),
        name,
        blob: fileBlob,
        createdAt: Date.now(),
      };
      await saveCustomBackground(stored);

      objectUrls.current.add(previewUrl);
      const custom = { id: stored.id, name, file: previewUrl };
      setCustomBgs(previous => [...previous, custom]);
      setSelectedId(stored.id);
      setBgUrl(previewUrl);
    } catch (error) {
      URL.revokeObjectURL(previewUrl);
      throw error;
    }
  }, []);

  const allBackgrounds = useMemo(() => [...BACKGROUNDS, ...customBgs], [customBgs]);

  return {
    bgUrl,
    allBackgrounds,
    setBackground,
    addCustomBackground,
    panelTransparency,
    setPanelTransparency,
  };
}
