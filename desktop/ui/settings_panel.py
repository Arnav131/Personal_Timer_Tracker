"""
Settings Panel — Background picker and theme customization.

Features:
- Thumbnail grid of available background images
- "Load Custom Image" button (file dialog)
- Live preview — background changes instantly
- Active indicator on selected background
- Glass-styled modal
"""

import customtkinter as ctk
from tkinter import filedialog
import shutil
from pathlib import Path
from PIL import ImageTk


class SettingsPanel(ctk.CTkToplevel):
    """Modal settings panel for background and theme customization."""

    def __init__(self, parent, theme, app):
        super().__init__(parent)

        self.theme = theme
        self.app = app
        self._thumbnails = []  # Keep references to prevent GC

        # ── Window Configuration ──
        self.title("Settings")
        self.geometry("560x480")
        self.resizable(False, False)
        self.configure(fg_color=theme.bg)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() - 560) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 480) // 2
        self.geometry(f"560x480+{px}+{py}")

        self._build_ui()

        # Force focus
        self.focus_force()
        self.lift()

    def _build_ui(self):
        """Build the settings UI."""
        # Container
        container = ctk.CTkFrame(
            self,
            fg_color=self.theme.surface,
            corner_radius=16,
            border_width=1,
            border_color=self.theme.border,
        )
        container.pack(fill="both", expand=True, padx=12, pady=12)

        # Title
        ctk.CTkLabel(
            container,
            text="⚙  Settings",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=self.theme.accent,
        ).pack(pady=(20, 4))

        ctk.CTkLabel(
            container,
            text="Choose a background to set the mood",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.theme.text_sec,
        ).pack(pady=(0, 16))

        # ── Background Grid ──
        bg_section = ctk.CTkLabel(
            container,
            text="🖼  Backgrounds",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=self.theme.text,
            fg_color="transparent",
            anchor="w",
        )
        bg_section.pack(fill="x", padx=24, pady=(0, 8))

        # Scrollable grid for backgrounds
        self.grid_frame = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            height=240,
            scrollbar_button_color=self.theme.border,
            scrollbar_button_hover_color=self.theme.text_sec,
        )
        self.grid_frame.pack(fill="x", padx=20, pady=(0, 12))

        self._populate_backgrounds()

        # ── Load Custom Image Button ──
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(4, 8))

        load_btn = ctk.CTkButton(
            btn_frame,
            text="📁  Load Custom Image",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=self.theme.accent,
            hover_color=self.theme.accent_soft,
            text_color="#0a0a14",
            width=220,
            height=40,
            corner_radius=20,
            command=self._load_custom_image,
        )
        load_btn.pack(side="left")

        # Close button
        close_btn = ctk.CTkButton(
            btn_frame,
            text="Close",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=self.theme.hover,
            hover_color=self.theme.border,
            text_color=self.theme.text,
            width=100,
            height=40,
            corner_radius=20,
            command=self.destroy,
        )
        close_btn.pack(side="right")

    def _populate_backgrounds(self):
        """Populate the thumbnail grid with available backgrounds."""
        # Clear existing
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self._thumbnails.clear()

        backgrounds = self.theme.get_available_backgrounds()
        current_path = self.theme.get_background_path()
        # Normalize for comparison
        current_norm = str(Path(current_path).resolve()) if current_path else ""

        # Create a row frame for grid layout
        row_frame = None
        for i, (name, path) in enumerate(backgrounds):
            if i % 3 == 0:
                row_frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=4)

            is_active = str(Path(path).resolve()) == current_norm
            self._create_thumbnail_card(row_frame, name, path, is_active)

    def _create_thumbnail_card(self, parent, name, path, is_active):
        """Create a single background thumbnail card."""
        # Card container
        border_color = self.theme.accent if is_active else self.theme.border
        border_width = 3 if is_active else 1

        card = ctk.CTkFrame(
            parent,
            fg_color=self.theme.bg,
            corner_radius=12,
            border_width=border_width,
            border_color=border_color,
            width=155,
            height=120,
        )
        card.pack(side="left", padx=6, pady=4)
        card.pack_propagate(False)

        # Thumbnail image
        thumb = self.theme.get_thumbnail(path, size=(140, 78))
        if thumb:
            self._thumbnails.append(thumb)  # Prevent GC
            thumb_label = ctk.CTkLabel(
                card,
                text="",
                image=ctk.CTkImage(
                    light_image=self._load_pil_thumb(path),
                    size=(140, 78),
                ),
                fg_color="transparent",
            )
            thumb_label.pack(padx=6, pady=(6, 2))
            thumb_label.bind("<Button-1>", lambda e, p=path: self._select_background(p))

        # Name label
        label = ctk.CTkLabel(
            card,
            text=name,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.theme.accent if is_active else self.theme.text_sec,
            fg_color="transparent",
        )
        label.pack(pady=(0, 4))
        label.bind("<Button-1>", lambda e, p=path: self._select_background(p))

        # Make whole card clickable
        card.bind("<Button-1>", lambda e, p=path: self._select_background(p))

    def _load_pil_thumb(self, path):
        """Load PIL Image for CTkImage."""
        try:
            from PIL import Image
            img = Image.open(path)
            img = img.convert("RGB")
            # Cover fit
            img_w, img_h = img.size
            scale = max(140 / img_w, 78 / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            resized = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - 140) // 2
            top = (new_h - 78) // 2
            return resized.crop((left, top, left + 140, top + 78))
        except Exception:
            from PIL import Image
            return Image.new("RGB", (140, 78), (30, 30, 46))

    def _select_background(self, path):
        """Select a background and apply it."""
        self.theme.set_background(path)
        self.app.apply_theme_update()
        # Refresh the grid to update active indicator
        self._populate_backgrounds()

    def _load_custom_image(self):
        """Open file dialog to load a custom background image."""
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Choose a Background Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp *.bmp"),
                ("All files", "*.*"),
            ],
        )

        if not file_path:
            return

        # Copy to backgrounds directory
        src = Path(file_path)
        dest_dir = Path(self.theme._backgrounds_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Create a clean filename
        dest = dest_dir / src.name
        counter = 1
        while dest.exists():
            dest = dest_dir / f"{src.stem}_{counter}{src.suffix}"
            counter += 1

        try:
            shutil.copy2(str(src), str(dest))
            # Select the new background
            self._select_background(str(dest))
        except Exception:
            pass
