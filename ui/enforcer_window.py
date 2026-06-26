"""
Enforcer Window — the un-closable "hostage" popup.

Features:
- Always on top, frameless, centered on screen
- Blocks Alt+F4, Escape, close events
- Cannot be minimized
- Loops alarm audio
- Text input with 15-char minimum validation
- Character counter
- Shake animation on invalid submit
- On valid submit: stop audio, save log, close window
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime


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
    DANGER = "#c75050"


class EnforcerWindow(ctk.CTkToplevel):
    """The un-closable enforcer accountability window."""

    MIN_CHARS = 15

    def __init__(self, parent, data_manager, audio_manager, on_submit):
        super().__init__(parent)

        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.on_submit_callback = on_submit
        self._shake_count = 0

        # ── Window Configuration ──
        self.title("Productivity Enforcer — Accountability Check")
        self.geometry("480x360")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG)

        # Always on top
        self.attributes("-topmost", True)

        # Frameless
        self.overrideredirect(True)

        # Center on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 480) // 2
        y = (screen_h - 360) // 2
        self.geometry(f"480x360+{x}+{y}")

        # Block close events
        self.protocol("WM_DELETE_WINDOW", self._block_close)
        self.bind("<Escape>", self._block_close)
        self.bind("<Alt-F4>", self._block_close)

        # Prevent minimization
        self.bind("<Unmap>", self._force_show)

        # ── Build UI ──
        self._build_ui()

        # ── Start audio loop ──
        self.audio_manager.play_loop()

        # Force focus
        self.focus_force()
        self.lift()

        # Keep forcing on top
        self._keep_on_top()

    def _build_ui(self):
        """Build the enforcer UI."""
        # Main container with rounded appearance
        container = ctk.CTkFrame(
            self, fg_color=Colors.SURFACE, corner_radius=16
        )
        container.pack(fill="both", expand=True, padx=8, pady=8)

        # App icon/badge
        ctk.CTkLabel(
            container,
            text="✦",
            font=ctk.CTkFont(size=28),
            text_color=Colors.ACCENT,
            fg_color="transparent",
        ).pack(pady=(20, 4))

        # Time prompt
        now = datetime.now().strftime("%I:%M %p")
        ctk.CTkLabel(
            container,
            text=f"⏰  {now} — What did you accomplish\nthis past hour?",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=Colors.TEXT,
            fg_color="transparent",
            justify="center",
        ).pack(pady=(4, 12))

        # Text input
        self.text_frame = ctk.CTkFrame(
            container, fg_color="transparent"
        )
        self.text_frame.pack(fill="x", padx=24, pady=(0, 4))

        self.text_input = ctk.CTkTextbox(
            self.text_frame,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=Colors.BG,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT,
            corner_radius=10,
            height=80,
            border_width=2,
            wrap="word",
        )
        self.text_input.pack(fill="x")
        self.text_input.bind("<KeyRelease>", self._on_text_change)

        # Character counter
        self.char_label = ctk.CTkLabel(
            container,
            text=f"0 / {self.MIN_CHARS} min",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_SEC,
            fg_color="transparent",
        )
        self.char_label.pack(pady=(0, 8))

        # Submit button (disabled initially)
        self.submit_btn = ctk.CTkButton(
            container,
            text="Submit Log",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=Colors.BORDER,
            hover_color=Colors.BORDER,
            text_color=Colors.TEXT_SEC,
            width=200,
            height=42,
            corner_radius=10,
            command=self._submit,
            state="disabled",
        )
        self.submit_btn.pack(pady=(0, 20))

    def _on_text_change(self, event=None):
        """Update character counter and submit button state."""
        text = self.text_input.get("1.0", "end-1c")
        char_count = len(text.strip())

        self.char_label.configure(text=f"{char_count} / {self.MIN_CHARS} min")

        if char_count >= self.MIN_CHARS:
            self.submit_btn.configure(
                state="normal",
                fg_color=Colors.ACCENT,
                hover_color=Colors.ACCENT_SOFT,
                text_color="#1e1e2e",
            )
            self.char_label.configure(text_color=Colors.SUCCESS)
        else:
            self.submit_btn.configure(
                state="disabled",
                fg_color=Colors.BORDER,
                hover_color=Colors.BORDER,
                text_color=Colors.TEXT_SEC,
            )
            self.char_label.configure(text_color=Colors.TEXT_SEC)

    def _submit(self):
        """Submit the enforcer log."""
        text = self.text_input.get("1.0", "end-1c").strip()

        if len(text) < self.MIN_CHARS:
            self._shake_input()
            return

        # Save log
        self.data_manager.add_enforcer_log(text)

        # Stop audio
        self.audio_manager.stop()

        # Callback
        self.on_submit_callback()

        # Close window
        self.destroy()

    def _shake_input(self):
        """Shake animation on the input field for invalid submission."""
        self._shake_count = 0
        original_x = self.text_frame.winfo_x()

        # Red border flash
        self.text_input.configure(border_color=Colors.DANGER)

        def shake():
            if self._shake_count >= 6:
                self.text_frame.place_forget()
                self.text_frame.pack(fill="x", padx=24, pady=(0, 4))
                self.after(500, lambda: self.text_input.configure(
                    border_color=Colors.BORDER
                ))
                return

            offset = 6 if self._shake_count % 2 == 0 else -6
            self.text_frame.place(
                x=original_x + offset,
                y=self.text_frame.winfo_y()
            )
            self._shake_count += 1
            self.after(50, shake)

        shake()

    def _block_close(self, event=None):
        """Block all close attempts."""
        self.focus_force()
        self.lift()
        return "break"

    def _force_show(self, event=None):
        """Force the window to stay visible."""
        self.after(100, lambda: self.deiconify())
        self.after(200, lambda: self.lift())
        self.after(300, lambda: self.focus_force())

    def _keep_on_top(self):
        """Periodically ensure the window stays on top."""
        if self.winfo_exists():
            self.attributes("-topmost", True)
            self.lift()
            self.after(2000, self._keep_on_top)
