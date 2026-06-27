/**
 * colorExtractor — extracts the dominant saturated color from an image
 * using a hidden canvas element.
 */

function rgbToHsv(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  const d = max - min;
  let h = 0, s = max === 0 ? 0 : d / max, v = max;
  if (d !== 0) {
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }
  return [h, s, v];
}

function hsvToRgb(h, s, v) {
  let r, g, b;
  const i = Math.floor(h * 6);
  const f = h * 6 - i;
  const p = v * (1 - s);
  const q = v * (1 - f * s);
  const t = v * (1 - (1 - f) * s);
  switch (i % 6) {
    case 0: r = v; g = t; b = p; break;
    case 1: r = q; g = v; b = p; break;
    case 2: r = p; g = v; b = t; break;
    case 3: r = p; g = q; b = v; break;
    case 4: r = t; g = p; b = v; break;
    case 5: r = v; g = p; b = q; break;
  }
  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

/**
 * Extract the dominant saturated color from an image URL.
 * Returns { accent, accentSoft, accentRgb }.
 */
export function extractDominantColor(imageUrl) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    // Only set crossOrigin for non-data URLs to avoid tainted canvas issues
    if (!imageUrl.startsWith('data:')) {
      img.crossOrigin = 'anonymous';
    }
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        const size = 50;
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, size, size);
        const imageData = ctx.getImageData(0, 0, size, size);
        const pixels = imageData.data;

        let bestScore = 0;
        let bestR = 212, bestG = 168, bestB = 83; // Default amber

        for (let i = 0; i < pixels.length; i += 4) {
          const r = pixels[i], g = pixels[i + 1], b = pixels[i + 2];
          const [h, s, v] = rgbToHsv(r, g, b);
          const score = s * v;
          if (score > bestScore && v > 0.3 && s > 0.2) {
            bestScore = score;
            bestR = r; bestG = g; bestB = b;
          }
        }

        const accent = `#${bestR.toString(16).padStart(2, '0')}${bestG.toString(16).padStart(2, '0')}${bestB.toString(16).padStart(2, '0')}`;
        const accentRgb = `${bestR}, ${bestG}, ${bestB}`;

        // Softer variant
        const [h, s, v] = rgbToHsv(bestR, bestG, bestB);
        const [sr, sg, sb] = hsvToRgb(
          (h + 0.02) % 1.0,
          Math.max(0, s - 0.1),
          Math.max(0, v - 0.1)
        );
        const accentSoft = `#${sr.toString(16).padStart(2, '0')}${sg.toString(16).padStart(2, '0')}${sb.toString(16).padStart(2, '0')}`;

        resolve({ accent, accentSoft, accentRgb });
      } catch (e) {
        reject(e);
      }
    };
    img.onerror = reject;
    img.src = imageUrl;
  });
}
