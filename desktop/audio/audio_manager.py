"""
Audio Manager — handles MP3 playback for the Productivity Enforcer.

Uses pygame.mixer for:
- Looping alarm playback (enforcer window)
- One-shot chime playback (Pomodoro session end, break end)
- Graceful fallback if audio file is missing
"""

import os
import threading
from pathlib import Path


class AudioManager:
    """Manages audio playback using pygame.mixer."""

    def __init__(self):
        """Initialize the audio system."""
        self._initialized = False
        self._lock = threading.Lock()

        # Locate the alarm audio asset (prefer .mp3, fallback to .wav)
        project_root = Path(__file__).parent.parent
        mp3_path = project_root / "assets" / "alarm.mp3"
        wav_path = project_root / "assets" / "alarm.wav"
        if mp3_path.exists():
            self._alarm_path = mp3_path
        else:
            self._alarm_path = wav_path

        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            self._pygame = pygame
            self._initialized = True
        except Exception:
            self._initialized = False

    def play_loop(self):
        """Play the alarm sound in an infinite loop (for enforcer window)."""
        if not self._initialized:
            return
        with self._lock:
            try:
                if self._alarm_path.exists():
                    self._pygame.mixer.music.load(str(self._alarm_path))
                    self._pygame.mixer.music.set_volume(0.5)
                    self._pygame.mixer.music.play(-1)  # -1 = infinite loop
            except Exception:
                pass  # Graceful fallback — no crash

    def play_once(self):
        """Play the alarm sound once (for Pomodoro/break chime)."""
        if not self._initialized:
            return
        with self._lock:
            try:
                if self._alarm_path.exists():
                    self._pygame.mixer.music.load(str(self._alarm_path))
                    self._pygame.mixer.music.set_volume(0.4)
                    self._pygame.mixer.music.play(0)  # 0 = play once
            except Exception:
                pass

    def stop(self):
        """Stop all audio playback."""
        if not self._initialized:
            return
        with self._lock:
            try:
                self._pygame.mixer.music.stop()
            except Exception:
                pass

    def is_playing(self):
        """Check if audio is currently playing."""
        if not self._initialized:
            return False
        try:
            return self._pygame.mixer.music.get_busy()
        except Exception:
            return False

    def cleanup(self):
        """Clean up audio resources."""
        self.stop()
        if self._initialized:
            try:
                self._pygame.mixer.quit()
            except Exception:
                pass
