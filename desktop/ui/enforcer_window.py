"""
Enforcer Window — the un-closable "hostage" popup.

Glass-styled premium design with:
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


class EnforcerWindow(ctk.CTkToplevel):
    """The un-closable enforcer accountability window — glass themed."""

    MIN_CHARS = 15

    def __init__(self, parent, data_manager, audio_manager, on_submit, theme):
        super().__init__(parent)

        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.on_submit_callback = on_submit
        self.theme = theme
        self._shake_count = 0

        # ── Window Configuration ──
        self.title("Productivity Enforcer — Accountability Check")
        self.geometry("520x400")
        self.resizable(False, False)
        self.configure(fg_color=theme.bg)

        # Always on top
        self.attributes("-topmost", True)

        # Frameless
        self.overrideredirect(True)

        # Center on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 520) // 2
        y = (screen_h - 400) // 2
        self.geometry(f"520x400+{x}+{y}")

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
        """Build the glass-styled enforcer UI."""
        # Glass container
        container = ctk.CTkFrame(
            self,
            fg_color=self.theme.surface,
            corner_radius=18,
            border_width=1,
            border_color=self.theme.border,
        )
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # App icon/badge
        ctk.CTkLabel(
            container,
            text="✦",
            font=ctk.CTkFont(size=32),
            text_color=self.theme.accent,
            fg_color="transparent",
        ).pack(pady=(24, 4))

        # Time prompt
        now = datetime.now().strftime("%I:%M %p")
        ctk.CTkLabel(
            container,
            text=f"⏰  {now} — What did you accomplish\nthis past hour?",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.theme.text,
            fg_color="transparent",
            justify="center",
        ).pack(pady=(4, 14))

        # Text input
        self.text_frame = ctk.CTkFrame(
            container, fg_color="transparent"
        )
        self.text_frame.pack(fill="x", padx=28, pady=(0, 4))

        self.text_input = ctk.CTkTextbox(
            self.text_frame,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color=self.theme.bg,
            border_color=self.theme.border,
            text_color=self.theme.text,
            corner_radius=12,
            height=90,
            border_width=2,
            wrap="word",
        )
        self.text_input.pack(fill="x")
        self.text_input.bind("<KeyRelease>", self._on_text_change)

        # Character counter
        self.char_label = ctk.CTkLabel(
            container,
            text=f"0 / {self.MIN_CHARS} min",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.theme.text_sec,
            fg_color="transparent",
        )
        self.char_label.pack(pady=(0, 10))

        # Submit button (disabled initially)
        self.submit_btn = ctk.CTkButton(
            container,
            text="Submit Log",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=self.theme.border,
            hover_color=self.theme.border,
            text_color=self.theme.text_sec,
            width=220,
            height=46,
            corner_radius=23,
            command=self._submit,
            state="disabled",
        )
        self.submit_btn.pack(pady=(0, 24))

    def _on_text_change(self, event=None):
        """Update character counter and submit button state."""
        text = self.text_input.get("1.0", "end-1c")
        char_count = len(text.strip())

        self.char_label.configure(text=f"{char_count} / {self.MIN_CHARS} min")

        if char_count >= self.MIN_CHARS:
            self.submit_btn.configure(
                state="normal",
                fg_color=self.theme.accent,
                hover_color=self.theme.accent_soft,
                text_color="#0a0a14",
            )
            self.char_label.configure(text_color=self.theme.success)
        else:
            self.submit_btn.configure(
                state="disabled",
                fg_color=self.theme.border,
                hover_color=self.theme.border,
                text_color=self.theme.text_sec,
            )
            self.char_label.configure(text_color=self.theme.text_sec)

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
        self.text_input.configure(border_color=self.theme.danger)

        def shake():
            if self._shake_count >= 6:
                self.text_frame.place_forget()
                self.text_frame.pack(fill="x", padx=28, pady=(0, 4))
                self.after(500, lambda: self.text_input.configure(
                    border_color=self.theme.border
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
