"""
Productivity Enforcer — Main Entry Point

Initializes all managers and launches the application:
1. DataManager — handles all JSON persistence
2. AudioManager — handles audio playback
3. App — main CustomTkinter window
4. EnforcerDaemon — 60-minute background timer
5. TrayManager — system tray icon
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

from data.data_manager import DataManager
from audio.audio_manager import AudioManager
from ui.app import App
from services.enforcer_daemon import EnforcerDaemon
from services.tray_manager import TrayManager


def main():
    """Launch the Productivity Enforcer application."""

    # ── Configure CustomTkinter ──
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    # ── Initialize Data Manager ──
    data_manager = DataManager()

    # ── Initialize Audio Manager ──
    audio_manager = AudioManager()

    # ── Create Main App Window ──
    app = App(data_manager, audio_manager)

    # ── Start Enforcer Daemon ──
    enforcer_daemon = EnforcerDaemon(app)
    app.enforcer_daemon = enforcer_daemon

    # ── Start System Tray ──
    tray_manager = TrayManager(app)
    app.tray_manager = tray_manager
    tray_manager.start()

    # ── Run the App ──
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up
        enforcer_daemon.stop()
        audio_manager.cleanup()
        tray_manager.stop()


if __name__ == "__main__":
    main()
