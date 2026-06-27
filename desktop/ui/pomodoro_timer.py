"""
Pomodoro Timer — Large, premium circular arc countdown.

Inspired by modern focus app designs with:
- 300px circular arc display (Canvas-drawn)
- Large 56pt MM:SS center text
- "Focus" / "Break" mode label
- Glass-panel card with subtle border glow
- Pill-shaped Start/Pause/Reset controls
- Session counter with refined typography
- Triggers Break Decision Prompt on completion
"""

import customtkinter as ctk
import tkinter as tk
import math
import threading
import time


class PomodoroTimer(ctk.CTkFrame):
    """Premium Pomodoro timer with large circular arc display."""

    # Timer states
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    BREAK = "break"

    def __init__(self, parent, data_manager, audio_manager, app, theme):
        super().__init__(
            parent,
            fg_color=theme.surface,
            corner_radius=16,
            border_width=1,
            border_color=theme.border,
        )
        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.app = app
        self.theme = theme

        # Timer state
        work_dur, break_dur = self.data_manager.get_pomodoro_durations()
        self.work_duration = work_dur * 60  # in seconds
        self.break_duration = break_dur * 60
        self.remaining = self.work_duration
        self.state = self.IDLE
        self._timer_thread = None
        self._stop_event = threading.Event()
        self._is_break_timer = False

        # Arc display size — large and premium
        self.arc_size = 300

        self._build_ui()

    def _build_ui(self):
        """Build the premium timer UI."""
        # Header with settings
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 0))

        ctk.CTkLabel(
            header,
            text="🍅  Pomodoro Timer",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=self.theme.accent,
            fg_color="transparent",
        ).pack(side="left")

        # Settings button
        settings_btn = ctk.CTkButton(
            header,
            text="⚙",
            font=ctk.CTkFont(size=17),
            fg_color="transparent",
            hover_color=self.theme.hover,
            text_color=self.theme.text_sec,
            width=36,
            height=36,
            corner_radius=10,
            command=self._show_settings,
        )
        settings_btn.pack(side="right")

        # Canvas for arc timer — large, centered, premium
        self.canvas = tk.Canvas(
            self,
            width=self.arc_size,
            height=self.arc_size,
            bg=self.theme.surface,
            highlightthickness=0,
        )
        self.canvas.pack(pady=(12, 4))

        # Mode label ("Focus" or "Break") — below canvas
        self.mode_label = ctk.CTkLabel(
            self,
            text="Focus",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.theme.text,
            fg_color="transparent",
        )
        self.mode_label.pack(pady=(0, 2))

        # Status label (subtle)
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready to focus",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.theme.text_sec,
            fg_color="transparent",
        )
        self.status_label.pack(pady=(0, 4))

        # Session counter
        sessions = self.data_manager.get_pomodoro_sessions()
        self.session_label = ctk.CTkLabel(
            self,
            text=f"Session {sessions + 1}  •  {sessions} completed today",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.theme.text_sec,
            fg_color="transparent",
        )
        self.session_label.pack(pady=(0, 10))

        # Controls — pill-shaped buttons
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(pady=(0, 20))

        self.start_btn = ctk.CTkButton(
            controls,
            text="▶  Start",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=self.theme.accent,
            hover_color=self.theme.accent_soft,
            text_color="#0a0a14",
            width=120,
            height=42,
            corner_radius=21,
            command=self._start,
        )
        self.start_btn.pack(side="left", padx=5)

        self.pause_btn = ctk.CTkButton(
            controls,
            text="⏸  Pause",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=self.theme.hover,
            hover_color=self.theme.border,
            text_color=self.theme.text,
            width=120,
            height=42,
            corner_radius=21,
            command=self._pause_resume,
            state="disabled",
        )
        self.pause_btn.pack(side="left", padx=5)

        self.reset_btn = ctk.CTkButton(
            controls,
            text="↺  Reset",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=self.theme.hover,
            hover_color=self.theme.border,
            text_color=self.theme.text_sec,
            width=110,
            height=42,
            corner_radius=21,
            command=self._reset,
        )
        self.reset_btn.pack(side="left", padx=5)

        # Initial draw
        self._draw_arc()

    def _format_time(self, seconds):
        """Format seconds as MM:SS."""
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"

    def _draw_arc(self):
        """Draw the large circular arc timer with centered time text."""
        self.canvas.delete("all")
        s = self.arc_size
        pad = 20
        lw = 6  # Thinner, more elegant line

        # Background track (subtle)
        self.canvas.create_arc(
            pad, pad, s - pad, s - pad,
            start=90, extent=-360,
            outline=self.theme.border,
            width=lw,
            style="arc",
        )

        # Progress arc
        if self._is_break_timer:
            total = self.break_duration
            color = self.theme.blue
        else:
            total = self.work_duration
            color = self.theme.accent

        if total > 0:
            pct = self.remaining / total
            extent = -pct * 360
            self.canvas.create_arc(
                pad, pad, s - pad, s - pad,
                start=90, extent=extent,
                outline=color,
                width=lw + 2,
                style="arc",
            )

        # Small glowing dot at the tip of the arc
        if total > 0 and self.remaining > 0:
            angle = math.radians(90 - (self.remaining / total) * 360)
            cx = s / 2
            cy = s / 2
            r = (s - 2 * pad) / 2
            dot_x = cx + r * math.cos(angle)
            dot_y = cy - r * math.sin(angle)
            dot_r = 5
            self.canvas.create_oval(
                dot_x - dot_r, dot_y - dot_r,
                dot_x + dot_r, dot_y + dot_r,
                fill=color, outline=color,
            )

        # Time text — large, centered, premium
        self.canvas.create_text(
            s // 2, s // 2,
            text=self._format_time(self.remaining),
            fill=self.theme.text,
            font=("Segoe UI", 52, "bold"),
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
            self.mode_label.configure(text="Focus")
            self.status_label.configure(text="🔥  Stay on track!")
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
        self.mode_label.configure(text="Break")
        self.status_label.configure(text="☕  Relax and recharge")
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
                self.status_label.configure(text="☕  Relax and recharge")
            else:
                self.status_label.configure(text="🔥  Stay on track!")
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
        self.mode_label.configure(text="Focus")
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
            self.mode_label.configure(text="Focus")
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
                text=f"Session {sessions + 1}  •  {sessions} completed today"
            )
            self.remaining = self.work_duration
            self._update_display()
            self.mode_label.configure(text="Focus")
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
        dialog.geometry("360x280")
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.theme.bg)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # Center on parent
        dialog.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + 350
        y = self.winfo_toplevel().winfo_y() + 200
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialog,
            text="⚙  Timer Settings",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.theme.accent,
        ).pack(pady=(20, 16))

        # Work duration
        work_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        work_frame.pack(fill="x", padx=28, pady=6)
        ctk.CTkLabel(
            work_frame, text="Work duration (min):",
            font=ctk.CTkFont(size=14), text_color=self.theme.text,
        ).pack(side="left")
        work_var = ctk.StringVar(value=str(self.work_duration // 60))
        work_entry = ctk.CTkEntry(
            work_frame, textvariable=work_var, width=70,
            fg_color=self.theme.surface, border_color=self.theme.border,
            text_color=self.theme.text, corner_radius=8,
        )
        work_entry.pack(side="right")

        # Break duration
        break_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        break_frame.pack(fill="x", padx=28, pady=6)
        ctk.CTkLabel(
            break_frame, text="Break duration (min):",
            font=ctk.CTkFont(size=14), text_color=self.theme.text,
        ).pack(side="left")
        break_var = ctk.StringVar(value=str(self.break_duration // 60))
        break_entry = ctk.CTkEntry(
            break_frame, textvariable=break_var, width=70,
            fg_color=self.theme.surface, border_color=self.theme.border,
            text_color=self.theme.text, corner_radius=8,
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
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.theme.accent,
            hover_color=self.theme.accent_soft,
            text_color="#0a0a14",
            width=140,
            height=40,
            corner_radius=20,
            command=save,
        ).pack(pady=20)
