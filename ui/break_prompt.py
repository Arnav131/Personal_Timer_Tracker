"""
Break Decision Prompt — modal overlay after Pomodoro session ends.

Three options:
1. Take a Break (10 min) — starts break countdown
2. Do a Micro Task — switches to Micro view
3. Continue Studying — starts next work session immediately
"""

import customtkinter as ctk


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


class BreakPrompt(ctk.CTkToplevel):
    """Modal overlay for the Break Decision Prompt."""

    def __init__(self, parent, data_manager, audio_manager, app):
        super().__init__(parent)

        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.app = app

        # ── Window Configuration ──
        self.title("Session Complete")
        self.geometry("440x340")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG)

        # Make modal — prevent interaction with main window
        self.transient(parent)
        self.grab_set()

        # Disable close
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        # Center on parent
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() - 440) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 340) // 2
        self.geometry(f"440x340+{px}+{py}")

        self._build_ui()

        # Force focus
        self.focus_force()
        self.lift()

    def _build_ui(self):
        """Build the prompt UI."""
        # Title
        ctk.CTkLabel(
            self,
            text="🎉  Session Complete!",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=Colors.ACCENT,
        ).pack(pady=(28, 4))

        ctk.CTkLabel(
            self,
            text="Great work! What's next?",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=Colors.TEXT_SEC,
        ).pack(pady=(0, 20))

        # ── Option Buttons ──

        # Take a Break
        break_btn = ctk.CTkButton(
            self,
            text="☕   Take a Break (10 min)",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=Colors.BLUE_MID,
            hover_color="#5a92c5",
            text_color="#ffffff",
            width=340,
            height=50,
            corner_radius=12,
            command=self._take_break,
        )
        break_btn.pack(pady=5)

        # Do a Micro Task
        micro_btn = ctk.CTkButton(
            self,
            text="⚡   Do a Micro Task",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=Colors.ACCENT_SOFT,
            hover_color="#b07f5a",
            text_color="#ffffff",
            width=340,
            height=50,
            corner_radius=12,
            command=self._do_micro,
        )
        micro_btn.pack(pady=5)

        # Continue Studying
        continue_btn = ctk.CTkButton(
            self,
            text="📖   Continue Studying",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=Colors.SUCCESS,
            hover_color="#69a584",
            text_color="#1e1e2e",
            width=340,
            height=50,
            corner_radius=12,
            command=self._continue_study,
        )
        continue_btn.pack(pady=5)

    def _take_break(self):
        """Start break countdown."""
        self.destroy()
        # Start break timer on the Pomodoro widget
        pomodoro = self.app.macro_view.pomodoro
        pomodoro.start_break_timer()

    def _do_micro(self):
        """Switch to Micro view."""
        self.destroy()
        self.app.switch_mode("micro")
        # The micro view will show a "Back to Study" button
        self.app.micro_view.show_back_to_study_button()

    def _continue_study(self):
        """Start next Pomodoro session immediately."""
        self.destroy()
        pomodoro = self.app.macro_view.pomodoro
        pomodoro.start_work_session()
