"""
Main Application Window — Productivity Enforcer

Premium glassmorphism desktop app with:
- Full-bleed background image (pixel art)
- Frosted glass UI panels
- Custom drag region
- Mode toggle (Macro/Micro)
- Progress dashboard strip
- View switching with transitions
- Settings panel for background customization
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from PIL import ImageTk

from ui.theme_manager import ThemeManager
from ui.navbar import NavBar
from ui.progress_dashboard import ProgressDashboard
from ui.macro_view import MacroView
from ui.micro_view import MicroView
from ui.break_prompt import BreakPrompt
from ui.enforcer_window import EnforcerWindow


class App(ctk.CTk):
    """Main application window with background image and glass UI."""

    def __init__(self, data_manager, audio_manager):
        super().__init__()

        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.current_mode = "macro"  # "macro" or "micro"

        # ── Initialize Theme Manager ──
        self.theme = ThemeManager()

        # ── Window Configuration ──
        self.title("Productivity Enforcer")
        self.geometry("1100x750")
        self.minsize(1000, 700)
        self.configure(fg_color="#0a0a14")

        # Frameless window
        self.overrideredirect(True)

        # Center on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 1100) // 2
        y = (screen_h - 750) // 2
        self.geometry(f"1100x750+{x}+{y}")

        # Track window state
        self._is_maximized = False
        self._normal_geometry = f"1100x750+{x}+{y}"

        # ── Build UI ──
        self._build_ui()

        # ── Bind resize handles ──
        self._setup_resize()

        # ── Start periodic UI refresh ──
        self._start_clock()

        # ── Protocol for window close ──
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        # Reference to enforcer window (managed by daemon)
        self.enforcer_window = None

        # Reference to tray manager (set externally)
        self.tray_manager = None

        # ── Bind window resize to update background ──
        self.bind("<Configure>", self._on_resize)
        self._last_size = (0, 0)

    def _build_ui(self):
        """Build the entire UI layout with background canvas."""
        # ── Background Canvas (full-bleed image layer) ──
        self.bg_canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bd=0,
        )
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Render initial background
        self._update_background()

        # ── Main container (glass panels on top of background) ──
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # ── Navigation Bar ──
        self.navbar = NavBar(
            self.main_frame,
            on_minimize=self._minimize,
            on_maximize=self._toggle_maximize,
            on_close=self.minimize_to_tray,
            on_pdf=self._download_pdf,
            on_settings=self._open_settings,
            app=self,
            theme=self.theme,
        )
        self.navbar.pack(fill="x", padx=0, pady=0)

        # ── Mode Toggle ──
        self.toggle_frame = ctk.CTkFrame(
            self.main_frame, fg_color="transparent", height=54
        )
        self.toggle_frame.pack(fill="x", padx=28, pady=(10, 0))
        self.toggle_frame.pack_propagate(False)

        # Toggle container (glass pill)
        toggle_inner = ctk.CTkFrame(
            self.toggle_frame,
            fg_color=self.theme.surface,
            corner_radius=14,
            height=46,
            border_width=1,
            border_color=self.theme.border,
        )
        toggle_inner.pack(pady=4)

        self.macro_btn = ctk.CTkButton(
            toggle_inner,
            text="📚  Macro Tasks",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=self.theme.accent,
            hover_color=self.theme.accent_soft,
            text_color="#0a0a14",
            corner_radius=11,
            height=36,
            width=170,
            command=lambda: self.switch_mode("macro"),
        )
        self.macro_btn.pack(side="left", padx=5, pady=5)

        self.micro_btn = ctk.CTkButton(
            toggle_inner,
            text="⚡  Micro Tasks",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="transparent",
            hover_color=self.theme.hover,
            text_color=self.theme.text_sec,
            corner_radius=11,
            height=36,
            width=170,
            command=lambda: self.switch_mode("micro"),
        )
        self.micro_btn.pack(side="left", padx=5, pady=5)

        # ── Progress Dashboard ──
        self.progress_dashboard = ProgressDashboard(
            self.main_frame,
            data_manager=self.data_manager,
            theme=self.theme,
        )
        self.progress_dashboard.pack(fill="x", padx=28, pady=(10, 4))

        # ── Content Area ──
        self.content_frame = ctk.CTkFrame(
            self.main_frame, fg_color="transparent", corner_radius=0
        )
        self.content_frame.pack(fill="both", expand=True, padx=28, pady=(4, 20))

        # ── Macro View ──
        self.macro_view = MacroView(
            self.content_frame,
            data_manager=self.data_manager,
            audio_manager=self.audio_manager,
            app=self,
            theme=self.theme,
        )

        # ── Micro View ──
        self.micro_view = MicroView(
            self.content_frame,
            data_manager=self.data_manager,
            app=self,
            theme=self.theme,
        )

        # Show macro by default
        self.macro_view.pack(fill="both", expand=True)

    # ─── Background Management ───────────────────────

    def _update_background(self):
        """Render the background image on the canvas."""
        w = self.winfo_width() or 1100
        h = self.winfo_height() or 750

        photo = self.theme.get_background_photo(w, h)
        if photo:
            self.bg_canvas.delete("all")
            self.bg_canvas.create_image(0, 0, anchor="nw", image=photo)
            # Keep reference to prevent garbage collection
            self.bg_canvas._bg_photo = photo
        else:
            # Fallback: solid dark background
            self.bg_canvas.delete("all")
            self.bg_canvas.configure(bg="#0a0a14")

    def _on_resize(self, event=None):
        """Handle window resize — update background image."""
        if event and event.widget == self:
            w, h = event.width, event.height
            if (w, h) != self._last_size and w > 100 and h > 100:
                self._last_size = (w, h)
                # Debounce: update after brief delay
                if hasattr(self, '_resize_after_id'):
                    self.after_cancel(self._resize_after_id)
                self._resize_after_id = self.after(150, self._update_background)

    def refresh_background(self):
        """Force refresh the background (called after theme change)."""
        self._update_background()

    # ─── Settings ────────────────────────────────────

    def _open_settings(self):
        """Open the settings panel."""
        from ui.settings_panel import SettingsPanel
        SettingsPanel(self, theme=self.theme, app=self)

    def apply_theme_update(self):
        """Called after theme/background changes to refresh all UI elements."""
        self._update_background()
        # Update toggle buttons
        self.macro_btn.configure(
            fg_color=self.theme.accent if self.current_mode == "macro" else "transparent",
            hover_color=self.theme.accent_soft if self.current_mode == "macro" else self.theme.hover,
            text_color="#0a0a14" if self.current_mode == "macro" else self.theme.text_sec,
        )
        self.micro_btn.configure(
            fg_color=self.theme.accent if self.current_mode == "micro" else "transparent",
            hover_color=self.theme.accent_soft if self.current_mode == "micro" else self.theme.hover,
            text_color="#0a0a14" if self.current_mode == "micro" else self.theme.text_sec,
        )

    # ─── Mode Switching ──────────────────────────────

    def switch_mode(self, mode):
        """Switch between Macro and Micro views with animation."""
        if mode == self.current_mode:
            return

        self.current_mode = mode

        if mode == "macro":
            self.micro_view.pack_forget()
            self.macro_view.pack(fill="both", expand=True)
            # Update toggle styling
            self.macro_btn.configure(
                fg_color=self.theme.accent, text_color="#0a0a14",
                hover_color=self.theme.accent_soft,
            )
            self.micro_btn.configure(
                fg_color="transparent", text_color=self.theme.text_sec,
                hover_color=self.theme.hover,
            )
        else:
            self.macro_view.pack_forget()
            self.micro_view.pack(fill="both", expand=True)
            self.micro_btn.configure(
                fg_color=self.theme.accent, text_color="#0a0a14",
                hover_color=self.theme.accent_soft,
            )
            self.macro_btn.configure(
                fg_color="transparent", text_color=self.theme.text_sec,
                hover_color=self.theme.hover,
            )

        # Refresh progress
        self.refresh_progress()

    # ─── Progress Refresh ────────────────────────────

    def refresh_progress(self):
        """Update the progress dashboard with current data."""
        self.progress_dashboard.update_progress()

    # ─── Break Decision Prompt ───────────────────────

    def show_break_prompt(self):
        """Show the break decision modal overlay."""
        self.break_prompt = BreakPrompt(
            self,
            data_manager=self.data_manager,
            audio_manager=self.audio_manager,
            app=self,
            theme=self.theme,
        )

    # ─── Enforcer Window ─────────────────────────────

    def show_enforcer(self):
        """Show the enforcer hostage window."""
        if self.enforcer_window and self.enforcer_window.winfo_exists():
            self.enforcer_window.focus_force()
            return

        self.enforcer_window = EnforcerWindow(
            self,
            data_manager=self.data_manager,
            audio_manager=self.audio_manager,
            on_submit=self._on_enforcer_submit,
            theme=self.theme,
        )

    def _on_enforcer_submit(self):
        """Called when enforcer log is submitted."""
        self.enforcer_window = None
        # Reset the daemon timer (handled externally)
        if hasattr(self, 'enforcer_daemon') and self.enforcer_daemon:
            self.enforcer_daemon.reset_timer()

    # ─── Window Controls ─────────────────────────────

    def _minimize(self):
        """Minimize to taskbar."""
        self.overrideredirect(False)
        self.iconify()
        self.after(100, lambda: self.overrideredirect(True))

    def _toggle_maximize(self):
        """Toggle between maximized and normal state."""
        if self._is_maximized:
            self.geometry(self._normal_geometry)
            self._is_maximized = False
        else:
            self._normal_geometry = self.geometry()
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            self.geometry(f"{screen_w}x{screen_h}+0+0")
            self._is_maximized = True

    def minimize_to_tray(self):
        """Minimize to system tray."""
        self.withdraw()

    def show_from_tray(self):
        """Restore window from system tray."""
        self.deiconify()
        self.lift()
        self.focus_force()

    # ─── Window Dragging ──────────────────────────────

    def start_drag(self, event):
        """Start window drag."""
        self._drag_x = event.x
        self._drag_y = event.y

    def do_drag(self, event):
        """Continue window drag."""
        x = self.winfo_x() + event.x - self._drag_x
        y = self.winfo_y() + event.y - self._drag_y
        self.geometry(f"+{x}+{y}")

    # ─── Resize Handles ──────────────────────────────

    def _setup_resize(self):
        """Setup resize grips on window edges."""
        # Bottom-right resize grip
        grip = ctk.CTkLabel(
            self,
            text="⋮⋮",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.text_sec,
            fg_color="transparent",
            width=18,
            height=18,
            cursor="size_nw_se",
        )
        grip.place(relx=1.0, rely=1.0, anchor="se", x=-4, y=-4)
        grip.bind("<Button-1>", self._start_resize)
        grip.bind("<B1-Motion>", self._do_resize)

    def _start_resize(self, event):
        self._resize_x = event.x_root
        self._resize_y = event.y_root
        self._resize_w = self.winfo_width()
        self._resize_h = self.winfo_height()

    def _do_resize(self, event):
        new_w = max(1000, self._resize_w + (event.x_root - self._resize_x))
        new_h = max(700, self._resize_h + (event.y_root - self._resize_y))
        self.geometry(f"{new_w}x{new_h}")

    # ─── Clock ────────────────────────────────────────

    def _start_clock(self):
        """Periodically update the navbar clock."""
        self.navbar.update_time()
        self.after(1000, self._start_clock)

    # ─── PDF Download ─────────────────────────────────

    def _download_pdf(self):
        """Trigger PDF generation and download."""
        from services.pdf_generator import PDFGenerator
        generator = PDFGenerator(self.data_manager)
        generator.generate_and_save(self)
