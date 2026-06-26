"""
Pomodoro Timer — circular arc countdown timer.

Features:
- Large circular arc display (Canvas-drawn)
- MM:SS center text
- Start/Pause/Resume/Reset controls
- Configurable durations via settings
- Session counter
- Triggers Break Decision Prompt on completion
"""

import customtkinter as ctk
import tkinter as tk
import math
import threading
import time


class Colors:
    BG = "#1e1e2e"
    SURFACE = "#2a2a3e"
    ACCENT = "#d4a853"
    ACCENT_SOFT = "#c8956c"
    TEXT = "#f0e9d6"
    TEXT_SEC = "#a0998a"
    SUCCESS = "#7cb899"
    BORDER = "#3a3a52"
    HOVER = "#353550"
    BLUE_MID = "#6ba3d6"


class PomodoroTimer(ctk.CTkFrame):
    """Pomodoro timer with circular arc display and session tracking."""

    # Timer states
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    BREAK = "break"

    def __init__(self, parent, data_manager, audio_manager, app):
        super().__init__(parent, fg_color=Colors.SURFACE, corner_radius=14)
        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.app = app

        # Timer state
        work_dur, break_dur = self.data_manager.get_pomodoro_durations()
        self.work_duration = work_dur * 60  # in seconds
        self.break_duration = break_dur * 60
        self.remaining = self.work_duration
        self.state = self.IDLE
        self._timer_thread = None
        self._stop_event = threading.Event()
        self._is_break_timer = False

        # Arc display size
        self.arc_size = 200

        self._build_ui()

    def _build_ui(self):
        """Build the timer UI."""
        # Header with settings
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 0))

        ctk.CTkLabel(
            header,
            text="🍅  Pomodoro Timer",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=Colors.ACCENT,
            fg_color="transparent",
        ).pack(side="left")

        # Settings button
        settings_btn = ctk.CTkButton(
            header,
            text="⚙",
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=Colors.HOVER,
            text_color=Colors.TEXT_SEC,
            width=32,
            height=32,
            corner_radius=8,
            command=self._show_settings,
        )
        settings_btn.pack(side="right")

        # Canvas for arc timer — we draw both the arc and the time text on this
        self.canvas = tk.Canvas(
            self,
            width=self.arc_size,
            height=self.arc_size,
            bg=Colors.SURFACE,
            highlightthickness=0,
        )
        self.canvas.pack(pady=(10, 4))

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready to focus",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Colors.TEXT_SEC,
            fg_color="transparent",
        )
        self.status_label.pack(pady=(0, 2))

        # Session counter
        sessions = self.data_manager.get_pomodoro_sessions()
        self.session_label = ctk.CTkLabel(
            self,
            text=f"Session {sessions + 1} today  •  {sessions} completed",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_SEC,
            fg_color="transparent",
        )
        self.session_label.pack(pady=(0, 8))

        # Controls
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(pady=(0, 16))

        self.start_btn = ctk.CTkButton(
            controls,
            text="▶  Start",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_SOFT,
            text_color="#1e1e2e",
            width=110,
            height=38,
            corner_radius=10,
            command=self._start,
        )
        self.start_btn.pack(side="left", padx=4)

        self.pause_btn = ctk.CTkButton(
            controls,
            text="⏸  Pause",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=Colors.HOVER,
            hover_color=Colors.BORDER,
            text_color=Colors.TEXT,
            width=110,
            height=38,
            corner_radius=10,
            command=self._pause_resume,
            state="disabled",
        )
        self.pause_btn.pack(side="left", padx=4)

        self.reset_btn = ctk.CTkButton(
            controls,
            text="↺  Reset",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=Colors.HOVER,
            hover_color=Colors.BORDER,
            text_color=Colors.TEXT_SEC,
            width=100,
            height=38,
            corner_radius=10,
            command=self._reset,
        )
        self.reset_btn.pack(side="left", padx=4)

        # Initial draw
        self._draw_arc()

    def _format_time(self, seconds):
        """Format seconds as MM:SS."""
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"

    def _draw_arc(self):
        """Draw the circular arc timer with centered time text."""
        self.canvas.delete("all")
        s = self.arc_size
        pad = 14
        lw = 10

        # Background track
        self.canvas.create_arc(
            pad, pad, s - pad, s - pad,
            start=90, extent=-360,
            outline=Colors.BORDER,
            width=lw,
            style="arc",
        )

        # Progress arc
        if self._is_break_timer:
            total = self.break_duration
            color = Colors.BLUE_MID
        else:
            total = self.work_duration
            color = Colors.ACCENT

        if total > 0:
            pct = self.remaining / total
            extent = -pct * 360
            self.canvas.create_arc(
                pad, pad, s - pad, s - pad,
                start=90, extent=extent,
                outline=color,
                width=lw + 1,
                style="arc",
            )

        # Time text in center of canvas
        self.canvas.create_text(
            s // 2, s // 2,
            text=self._format_time(self.remaining),
            fill=Colors.TEXT,
            font=("Consolas", 30, "bold"),
        )

    def _update_display(self):
        """Update the time display and arc."""
        self._draw_arc()

    # ─── Timer Controls ──────────────────────────────

    def _start(self):
        """Start the work timer."""
        if self.state == self.IDLE:
            self.state = self.RUNNING
            self._is_break_timer = False
            self.remaining = self.work_duration
            self._stop_event.clear()
            self.start_btn.configure(state="disabled")
            self.pause_btn.configure(state="normal")
            self.status_label.configure(text="🔥  Focus time — stay on track!")
            self._run_timer()

    def start_work_session(self):
        """Start a new work session (called from break prompt)."""
        self.state = self.IDLE
        self._is_break_timer = False
        self.remaining = self.work_duration
        self._start()

    def start_break_timer(self):
        """Start the break countdown."""
        self.state = self.RUNNING
        self._is_break_timer = True
        self.remaining = self.break_duration
        self._stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.status_label.configure(text="☕  Break time — relax!")
        self._run_timer()

    def _pause_resume(self):
        """Toggle pause/resume."""
        if self.state == self.RUNNING:
            self.state = self.PAUSED
            self._stop_event.set()
            self.pause_btn.configure(text="▶  Resume")
            self.status_label.configure(text="⏸  Paused")
        elif self.state == self.PAUSED:
            self.state = self.RUNNING
            self._stop_event.clear()
            self.pause_btn.configure(text="⏸  Pause")
            if self._is_break_timer:
                self.status_label.configure(text="☕  Break time — relax!")
            else:
                self.status_label.configure(text="🔥  Focus time — stay on track!")
            self._run_timer()

    def _reset(self):
        """Reset the timer without counting the session."""
        self._stop_event.set()
        self.state = self.IDLE
        self._is_break_timer = False
        self.remaining = self.work_duration
        self._update_display()
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸  Pause")
        self.status_label.configure(text="Ready to focus")

    def _run_timer(self):
        """Run the countdown in the main thread using after()."""
        if self._stop_event.is_set() or self.state != self.RUNNING:
            return

        if self.remaining <= 0:
            self._timer_complete()
            return

        self.remaining -= 1
        self._update_display()
        self.after(1000, self._run_timer)

    def _timer_complete(self):
        """Handle timer completion."""
        self.state = self.IDLE
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸  Pause")

        if self._is_break_timer:
            # Break ended
            self._is_break_timer = False
            self.remaining = self.work_duration
            self._update_display()
            self.status_label.configure(text="Break over! Ready for next session?")
            # Play chime once
            self.audio_manager.play_once()
            # Show break prompt to ask if ready
            self.app.show_break_prompt()
        else:
            # Work session ended
            self.data_manager.increment_pomodoro_session()
            sessions = self.data_manager.get_pomodoro_sessions()
            self.session_label.configure(
                text=f"Session {sessions + 1} today  •  {sessions} completed"
            )
            self.remaining = self.work_duration
            self._update_display()
            self.status_label.configure(text="Session complete! 🎉")
            self.app.refresh_progress()
            # Play chime once
            self.audio_manager.play_once()
            # Show Break Decision Prompt
            self.app.show_break_prompt()

    # ─── Settings ─────────────────────────────────────

    def _show_settings(self):
        """Show Pomodoro duration settings dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Pomodoro Settings")
        dialog.geometry("320x240")
        dialog.resizable(False, False)
        dialog.configure(fg_color=Colors.BG)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # Center on parent
        dialog.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + 300
        y = self.winfo_toplevel().winfo_y() + 200
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialog,
            text="⚙  Timer Settings",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=Colors.ACCENT,
        ).pack(pady=(16, 12))

        # Work duration
        work_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        work_frame.pack(fill="x", padx=24, pady=4)
        ctk.CTkLabel(
            work_frame, text="Work duration (min):",
            font=ctk.CTkFont(size=13), text_color=Colors.TEXT,
        ).pack(side="left")
        work_var = ctk.StringVar(value=str(self.work_duration // 60))
        work_entry = ctk.CTkEntry(
            work_frame, textvariable=work_var, width=60,
            fg_color=Colors.SURFACE, border_color=Colors.BORDER,
            text_color=Colors.TEXT,
        )
        work_entry.pack(side="right")

        # Break duration
        break_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        break_frame.pack(fill="x", padx=24, pady=4)
        ctk.CTkLabel(
            break_frame, text="Break duration (min):",
            font=ctk.CTkFont(size=13), text_color=Colors.TEXT,
        ).pack(side="left")
        break_var = ctk.StringVar(value=str(self.break_duration // 60))
        break_entry = ctk.CTkEntry(
            break_frame, textvariable=break_var, width=60,
            fg_color=Colors.SURFACE, border_color=Colors.BORDER,
            text_color=Colors.TEXT,
        )
        break_entry.pack(side="right")

        def save():
            try:
                w = int(work_var.get())
                b = int(break_var.get())
                if w > 0 and b > 0:
                    self.work_duration = w * 60
                    self.break_duration = b * 60
                    self.data_manager.set_pomodoro_durations(w, b)
                    if self.state == self.IDLE:
                        self.remaining = self.work_duration
                        self._update_display()
            except ValueError:
                pass
            dialog.destroy()

        ctk.CTkButton(
            dialog,
            text="Save",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_SOFT,
            text_color="#1e1e2e",
            width=120,
            height=36,
            corner_radius=10,
            command=save,
        ).pack(pady=16)
