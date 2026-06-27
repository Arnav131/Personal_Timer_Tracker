"""
Theme Manager — background images, color extraction, glass effects.

Handles:
- Background image loading and resizing (cover fit)
- Dominant color extraction from background for adaptive accents
- Glass-panel tint color generation
- Settings persistence (background choice)
"""

import os
import json
import colorsys
from pathlib import Path
from PIL import Image, ImageFilter, ImageTk, ImageDraw, ImageStat


class ThemeManager:
    """Manages background images, accent colors, and glass-panel theming."""

    # Fallback colors if no image loaded
    DEFAULT_ACCENT = "#d4a853"
    DEFAULT_ACCENT_SOFT = "#c8956c"

    # Glass panel colors (constant — light frosted glass over dark backgrounds)
    GLASS_BG = "#1a1a2e"          # Dark base for glass panels
    GLASS_SURFACE = "#22223a"     # Slightly lighter glass surface
    GLASS_BORDER = "#3a3a5c"      # Subtle border for glass panels
    GLASS_HOVER = "#2e2e4a"       # Hover state for glass elements
    GLASS_TEXT = "#f0eadc"        # Warm white text
    GLASS_TEXT_SEC = "#a8a098"    # Secondary text
    GLASS_SUCCESS = "#7cb899"
    GLASS_DANGER = "#c75050"
    GLASS_BLUE = "#6ba3d6"

    def __init__(self, settings_path=None):
        """Initialize the theme manager."""
        self._project_root = Path(__file__).parent.parent
        self._backgrounds_dir = self._project_root / "assets" / "backgrounds"
        self._settings_path = settings_path or (
            Path.home() / "ProductivityEnforcer" / "settings.json"
        )

        # Current state
        self._bg_image_path = None
        self._bg_pil_image = None   # Original PIL image
        self._bg_photo = None       # Current ImageTk.PhotoImage (sized to window)
        self._accent = self.DEFAULT_ACCENT
        self._accent_soft = self.DEFAULT_ACCENT_SOFT

        # Load saved settings
        self._load_settings()

    # ─── Settings Persistence ─────────────────────────

    def _load_settings(self):
        """Load user settings from JSON."""
        try:
            if self._settings_path.exists():
                with open(self._settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                bg_path = settings.get("background_path", "")
                if bg_path and Path(bg_path).exists():
                    self._bg_image_path = Path(bg_path)
                    return
        except (json.JSONDecodeError, OSError):
            pass

        # Default to ramen_shop.png if it exists
        default = self._backgrounds_dir / "ramen_shop.png"
        if default.exists():
            self._bg_image_path = default

    def save_settings(self):
        """Persist current settings to JSON."""
        settings = {
            "background_path": str(self._bg_image_path) if self._bg_image_path else "",
        }
        try:
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except OSError:
            pass

    # ─── Background Image ────────────────────────────

    def get_available_backgrounds(self):
        """Return list of (name, path) for bundled backgrounds."""
        results = []
        if self._backgrounds_dir.exists():
            for f in sorted(self._backgrounds_dir.iterdir()):
                if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                    # Convert filename to display name
                    name = f.stem.replace("_", " ").title()
                    results.append((name, str(f)))
        return results

    def set_background(self, image_path):
        """Set a new background image path and extract colors."""
        path = Path(image_path)
        if path.exists():
            self._bg_image_path = path
            self._bg_pil_image = None  # Force reload
            self._bg_photo = None
            self._extract_accent_colors()
            self.save_settings()

    def get_background_path(self):
        """Return current background image path or None."""
        return str(self._bg_image_path) if self._bg_image_path else None

    def load_background_image(self):
        """Load the background PIL image (lazy, cached)."""
        if self._bg_pil_image is None and self._bg_image_path:
            try:
                self._bg_pil_image = Image.open(str(self._bg_image_path))
                self._bg_pil_image = self._bg_pil_image.convert("RGB")
                self._extract_accent_colors()
            except Exception:
                self._bg_pil_image = None
        return self._bg_pil_image

    def get_background_photo(self, width, height):
        """
        Return an ImageTk.PhotoImage sized to cover the given dimensions.
        Uses 'cover' scaling (fills entirely, may crop edges).
        """
        img = self.load_background_image()
        if img is None:
            return None

        # Cover fit: scale to fill, then center-crop
        img_w, img_h = img.size
        scale = max(width / img_w, height / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # Center crop to exact dimensions
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        cropped = resized.crop((left, top, left + width, top + height))

        # Apply a very subtle dark overlay to make glass panels pop
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 40))
        cropped_rgba = cropped.convert("RGBA")
        composited = Image.alpha_composite(cropped_rgba, overlay)

        self._bg_photo = ImageTk.PhotoImage(composited)
        return self._bg_photo

    def get_thumbnail(self, image_path, size=(120, 80)):
        """Generate a thumbnail for the settings panel."""
        try:
            img = Image.open(image_path)
            img = img.convert("RGB")
            # Cover fit for thumbnail
            img_w, img_h = img.size
            scale = max(size[0] / img_w, size[1] / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            resized = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - size[0]) // 2
            top = (new_h - size[1]) // 2
            cropped = resized.crop((left, top, left + size[0], top + size[1]))
            # Round corners
            return ImageTk.PhotoImage(cropped)
        except Exception:
            return None

    # ─── Color Extraction ────────────────────────────

    def _extract_accent_colors(self):
        """Extract dominant warm color from the background image."""
        img = self.load_background_image()
        if img is None:
            return

        try:
            # Downscale for speed
            small = img.resize((50, 50), Image.LANCZOS)

            # Sample all pixels and find the most saturated warm color
            pixels = list(small.getdata())

            best_sat = 0
            best_rgb = (212, 168, 83)  # Default amber

            for r, g, b in pixels:
                h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                # Prefer warm, saturated, reasonably bright colors
                score = s * v
                if score > best_sat and v > 0.3 and s > 0.2:
                    best_sat = score
                    best_rgb = (r, g, b)

            r, g, b = best_rgb
            self._accent = f"#{r:02x}{g:02x}{b:02x}"

            # Create a softer/darker variant
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            # Shift hue slightly warmer, reduce saturation
            sr, sg, sb = colorsys.hsv_to_rgb(
                (h + 0.02) % 1.0, max(0, s - 0.1), max(0, v - 0.1)
            )
            self._accent_soft = f"#{int(sr*255):02x}{int(sg*255):02x}{int(sb*255):02x}"

        except Exception:
            self._accent = self.DEFAULT_ACCENT
            self._accent_soft = self.DEFAULT_ACCENT_SOFT

    # ─── Theme Colors (Dynamic) ──────────────────────

    @property
    def accent(self):
        return self._accent

    @property
    def accent_soft(self):
        return self._accent_soft

    @property
    def bg(self):
        return self.GLASS_BG

    @property
    def surface(self):
        return self.GLASS_SURFACE

    @property
    def border(self):
        return self.GLASS_BORDER

    @property
    def hover(self):
        return self.GLASS_HOVER

    @property
    def text(self):
        return self.GLASS_TEXT

    @property
    def text_sec(self):
        return self.GLASS_TEXT_SEC

    @property
    def success(self):
        return self.GLASS_SUCCESS

    @property
    def danger(self):
        return self.GLASS_DANGER

    @property
    def blue(self):
        return self.GLASS_BLUE
