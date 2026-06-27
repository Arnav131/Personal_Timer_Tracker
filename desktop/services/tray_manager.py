"""
System Tray Manager — minimizes app to tray with right-click menu.

Menu options:
- Open Productivity Enforcer
- Download Today's PDF
- Quit
"""

import threading
from pathlib import Path

try:
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False


class TrayManager:
    """Manages the system tray icon and menu."""

    def __init__(self, app):
        self.app = app
        self._icon = None

        if not PYSTRAY_AVAILABLE:
            return

        # Create tray icon image (a simple gold circle)
        self._image = self._create_icon()

        # Create tray menu
        menu = pystray.Menu(
            pystray.MenuItem("Open Productivity Enforcer", self._open_app, default=True),
            pystray.MenuItem("Download Today's PDF", self._download_pdf),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._quit),
        )

        self._icon = pystray.Icon(
            "ProductivityEnforcer",
            self._image,
            "Productivity Enforcer",
            menu,
        )

    def _create_icon(self):
        """Create a simple tray icon image."""
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background circle
        draw.ellipse(
            [4, 4, size - 4, size - 4],
            fill=(30, 30, 46),
            outline=(212, 168, 83),
            width=3,
        )

        # Inner accent dot
        center = size // 2
        r = 12
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=(212, 168, 83),
        )

        return img

    def start(self):
        """Start the tray icon in a daemon thread."""
        if not PYSTRAY_AVAILABLE or not self._icon:
            return

        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _open_app(self, icon=None, item=None):
        """Open/restore the main application window."""
        self.app.after(0, self.app.show_from_tray)

    def _download_pdf(self, icon=None, item=None):
        """Trigger PDF download."""
        self.app.after(0, self.app._download_pdf)

    def _quit(self, icon=None, item=None):
        """Quit the application completely."""
        self.stop()
        self.app.after(0, self._do_quit)

    def _do_quit(self):
        """Perform the actual quit on the main thread."""
        # Clean up
        if hasattr(self.app, 'enforcer_daemon') and self.app.enforcer_daemon:
            self.app.enforcer_daemon.stop()
        if hasattr(self.app, 'audio_manager') and self.app.audio_manager:
            self.app.audio_manager.cleanup()
        self.app.destroy()
