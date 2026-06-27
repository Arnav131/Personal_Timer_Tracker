"""
Enforcer Daemon — Background thread that fires the enforcer every 60 minutes.

Features:
- 60-minute countdown in a daemon thread
- Timer resets only after valid log submission
- Sleep/wake handling: calculates elapsed time on resume
- Triggers enforcer window through the main app
"""

import threading
import time
from datetime import datetime


class EnforcerDaemon:
    """Background daemon that triggers the hourly enforcer."""

    INTERVAL = 60 * 60  # 60 minutes in seconds

    def __init__(self, app):
        self.app = app
        self._remaining = self.INTERVAL
        self._last_tick = time.time()
        self._running = True
        self._lock = threading.Lock()

        # Start the daemon thread
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        """Main daemon loop — ticks every second."""
        while self._running:
            time.sleep(1)

            with self._lock:
                now = time.time()
                elapsed = now - self._last_tick
                self._last_tick = now

                # Handle sleep/wake: if elapsed > 2 seconds,
                # system was probably sleeping
                if elapsed > 2:
                    # Subtract actual elapsed time
                    self._remaining -= elapsed
                else:
                    self._remaining -= 1

                if self._remaining <= 0:
                    self._remaining = 0
                    # Trigger enforcer on the main thread
                    self._trigger_enforcer()

    def _trigger_enforcer(self):
        """Schedule the enforcer window to open on the main thread."""
        try:
            self.app.after(0, self.app.show_enforcer)
        except Exception:
            pass  # App may be closing

    def reset_timer(self):
        """Reset the 60-minute timer after a valid log submission."""
        with self._lock:
            self._remaining = self.INTERVAL
            self._last_tick = time.time()

    def get_remaining(self):
        """Return remaining seconds until next enforcer trigger."""
        with self._lock:
            return max(0, int(self._remaining))

    def stop(self):
        """Stop the daemon thread."""
        self._running = False
