"""
Main Application Window — Productivity Enforcer

Frameless, dark-themed CustomTkinter window with:
- Custom drag region
- Mode toggle (Macro/Micro)
- Progress dashboard strip
- View switching with transitions
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime

from ui.navbar import NavBar
from ui.progress_dashboard import ProgressDashboard
from ui.macro_view import MacroView
from ui.micro_view import MicroView
from ui.break_prompt import BreakPrompt
from ui.enforcer_window import EnforcerWindow


# ─── Color Palette ───────────────────────────────────
class Colors:
    BG = "#1e1e2e"
    SURFACE = "#2a2a3e"
    ACCENT = "#d4a853"
    ACCENT_SOFT = "#c8956c"
    TEXT = "#f0e9d6"
    TEXT_SEC = "#a0998a"
    SUCCESS = "#7cb899"
    WARNING = "#d4a853"
    BORDER = "#3a3a52"
    HOVER = "#353550"
    DANGER = "#c75050"
    BLUE_MID = "#6ba3d6"


class App(ctk.CTk):
    """Main application window."""

    def __init__(self, data_manager, audio_manager):
        super().__init__()

        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.current_mode = "macro"  # "macro" or "micro"

        # ── Window Configuration ──
        self.title("Productivity Enforcer")
        self.geometry("960x700")
        self.minsize(900, 650)
        self.configure(fg_color=Colors.BG)

        # Frameless window
        self.overrideredirect(True)

        # Center on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 960) // 2
        y = (screen_h - 700) // 2
        self.geometry(f"960x700+{x}+{y}")

        # Track window state
        self._is_maximized = False
        self._normal_geometry = f"960x700+{x}+{y}"

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

    def _build_ui(self):
        """Build the entire UI layout."""
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color=Colors.BG, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # ── Navigation Bar ──
        self.navbar = NavBar(
            self.main_frame,
            on_minimize=self._minimize,
            on_maximize=self._toggle_maximize,
            on_close=self.minimize_to_tray,
            on_pdf=self._download_pdf,
            app=self,
        )
        self.navbar.pack(fill="x", padx=0, pady=0)

        # ── Mode Toggle ──
        self.toggle_frame = ctk.CTkFrame(
            self.main_frame, fg_color=Colors.BG, height=50
        )
        self.toggle_frame.pack(fill="x", padx=24, pady=(8, 0))
        self.toggle_frame.pack_propagate(False)

        # Toggle container
        toggle_inner = ctk.CTkFrame(
            self.toggle_frame, fg_color=Colors.SURFACE, corner_radius=12, height=42
        )
        toggle_inner.pack(pady=4)

        self.macro_btn = ctk.CTkButton(
            toggle_inner,
            text="📚  Macro Tasks",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_SOFT,
            text_color="#1e1e2e",
            corner_radius=10,
            height=34,
            width=160,
            command=lambda: self.switch_mode("macro"),
        )
        self.macro_btn.pack(side="left", padx=4, pady=4)

        self.micro_btn = ctk.CTkButton(
            toggle_inner,
            text="⚡  Micro Tasks",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="transparent",
            hover_color=Colors.HOVER,
            text_color=Colors.TEXT_SEC,
            corner_radius=10,
            height=34,
            width=160,
            command=lambda: self.switch_mode("micro"),
        )
        self.micro_btn.pack(side="left", padx=4, pady=4)

        # ── Progress Dashboard ──
        self.progress_dashboard = ProgressDashboard(
            self.main_frame, data_manager=self.data_manager
        )
        self.progress_dashboard.pack(fill="x", padx=24, pady=(10, 4))

        # ── Content Area ──
        self.content_frame = ctk.CTkFrame(
            self.main_frame, fg_color=Colors.BG, corner_radius=0
        )
        self.content_frame.pack(fill="both", expand=True, padx=24, pady=(4, 16))

        # ── Macro View ──
        self.macro_view = MacroView(
            self.content_frame,
            data_manager=self.data_manager,
            audio_manager=self.audio_manager,
            app=self,
        )

        # ── Micro View ──
        self.micro_view = MicroView(
            self.content_frame,
            data_manager=self.data_manager,
            app=self,
        )

        # Show macro by default
        self.macro_view.pack(fill="both", expand=True)

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
                fg_color=Colors.ACCENT, text_color="#1e1e2e"
            )
            self.micro_btn.configure(
                fg_color="transparent", text_color=Colors.TEXT_SEC
            )
        else:
            self.macro_view.pack_forget()
            self.micro_view.pack(fill="both", expand=True)
            self.micro_btn.configure(
                fg_color=Colors.ACCENT, text_color="#1e1e2e"
            )
            self.macro_btn.configure(
                fg_color="transparent", text_color=Colors.TEXT_SEC
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
            self.main_frame,
            text="⋮⋮",
            font=ctk.CTkFont(size=10),
            text_color=Colors.TEXT_SEC,
            fg_color="transparent",
            width=16,
            height=16,
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
        new_w = max(900, self._resize_w + (event.x_root - self._resize_x))
        new_h = max(650, self._resize_h + (event.y_root - self._resize_y))
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
