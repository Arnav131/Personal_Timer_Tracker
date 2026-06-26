"""
Micro Task View — Daily Habits checklist.

Features:
- Habit cards with checkboxes
- Edit mode for renaming/deleting tasks
- Add Habit inline input
- Pre-loaded defaults on first launch
- "Back to Study" button when coming from Break Decision
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
    DANGER = "#c75050"


class MicroTaskCard(ctk.CTkFrame):
    """Individual micro task card with checkbox."""

    def __init__(self, parent, task, is_done, on_toggle, on_rename=None, on_delete=None, edit_mode=False):
        super().__init__(parent, fg_color=Colors.SURFACE, corner_radius=10, height=44)
        self.pack_propagate(False)

        self.task = task
        self.on_toggle = on_toggle

        if edit_mode:
            self._build_edit_mode(on_rename, on_delete)
        else:
            self._build_normal_mode(is_done)

    def _build_normal_mode(self, is_done):
        """Build the normal display with checkbox."""
        self.var = ctk.BooleanVar(value=is_done)
        self.checkbox = ctk.CTkCheckBox(
            self,
            text="",
            variable=self.var,
            width=24,
            height=24,
            checkbox_width=20,
            checkbox_height=20,
            fg_color=Colors.SUCCESS,
            hover_color=Colors.ACCENT_SOFT,
            border_color=Colors.BORDER,
            checkmark_color="#1e1e2e",
            command=self._toggle,
        )
        self.checkbox.pack(side="left", padx=(12, 8), pady=10)

        text_color = Colors.TEXT_SEC if is_done else Colors.TEXT
        font_style = ctk.CTkFont(
            family="Segoe UI", size=13, overstrike=is_done
        )
        self.text_label = ctk.CTkLabel(
            self,
            text=self.task["text"],
            font=font_style,
            text_color=text_color,
            fg_color="transparent",
            anchor="w",
        )
        self.text_label.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Status indicator
        if is_done:
            ctk.CTkLabel(
                self,
                text="✓",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=Colors.SUCCESS,
                fg_color="transparent",
            ).pack(side="right", padx=12)

    def _build_edit_mode(self, on_rename, on_delete):
        """Build the edit mode with rename and delete buttons."""
        # Task text (editable)
        self.edit_entry = ctk.CTkEntry(
            self,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=Colors.BG,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT,
            corner_radius=6,
            height=30,
        )
        self.edit_entry.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=7)
        self.edit_entry.insert(0, self.task["text"])

        # Save button
        save_btn = ctk.CTkButton(
            self,
            text="✓",
            font=ctk.CTkFont(size=13),
            fg_color=Colors.SUCCESS,
            hover_color="#69a584",
            text_color="#1e1e2e",
            width=30,
            height=28,
            corner_radius=6,
            command=lambda: on_rename(self.task["id"], self.edit_entry.get()),
        )
        save_btn.pack(side="right", padx=2, pady=7)

        # Delete button
        del_btn = ctk.CTkButton(
            self,
            text="✕",
            font=ctk.CTkFont(size=12),
            fg_color=Colors.DANGER,
            hover_color="#a04040",
            text_color="#ffffff",
            width=30,
            height=28,
            corner_radius=6,
            command=lambda: on_delete(self.task["id"]),
        )
        del_btn.pack(side="right", padx=(2, 4), pady=7)

    def _toggle(self):
        self.on_toggle(self.task["id"])
        done = self.var.get()
        text_color = Colors.TEXT_SEC if done else Colors.TEXT
        font_style = ctk.CTkFont(
            family="Segoe UI", size=13, overstrike=done
        )
        self.text_label.configure(text_color=text_color, font=font_style)


class MicroView(ctk.CTkFrame):
    """Micro task view for daily habits."""

    def __init__(self, parent, data_manager, app):
        super().__init__(parent, fg_color="transparent")
        self.data_manager = data_manager
        self.app = app
        self._edit_mode = False
        self._back_to_study_visible = False

        self._build_ui()

    def _build_ui(self):
        """Build the micro task list UI."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            header,
            text="⚡  Daily Habits",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=Colors.ACCENT,
            fg_color="transparent",
        ).pack(side="left")

        # Edit toggle button
        self.edit_btn = ctk.CTkButton(
            header,
            text="✏ Edit",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.HOVER,
            hover_color=Colors.BORDER,
            text_color=Colors.TEXT_SEC,
            width=70,
            height=30,
            corner_radius=8,
            command=self._toggle_edit_mode,
        )
        self.edit_btn.pack(side="right", padx=4)

        # Back to Study button (hidden by default)
        self.back_btn_frame = ctk.CTkFrame(self, fg_color="transparent", height=44)
        # Not packed yet — shown when coming from break prompt

        # Scrollable task list
        self.task_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Colors.BORDER,
            scrollbar_button_hover_color=Colors.TEXT_SEC,
        )
        self.task_scroll.pack(fill="both", expand=True)

        # Add habit input (at bottom)
        self.add_frame = ctk.CTkFrame(
            self, fg_color=Colors.SURFACE, corner_radius=10
        )
        self.add_frame.pack(fill="x", pady=(8, 0))

        self.add_entry = ctk.CTkEntry(
            self.add_frame,
            placeholder_text="Add a new habit...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=Colors.BG,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT,
            placeholder_text_color=Colors.TEXT_SEC,
            corner_radius=8,
            height=36,
        )
        self.add_entry.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        self.add_entry.bind("<Return>", lambda e: self._add_habit())

        add_btn = ctk.CTkButton(
            self.add_frame,
            text="+ Add Habit",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_SOFT,
            text_color="#1e1e2e",
            width=100,
            height=36,
            corner_radius=8,
            command=self._add_habit,
        )
        add_btn.pack(side="right", padx=(0, 8), pady=8)

        self._refresh_tasks()

    def _refresh_tasks(self):
        """Refresh the task list display."""
        for widget in self.task_scroll.winfo_children():
            widget.destroy()

        tasks = self.data_manager.get_micro_tasks_config()

        if not tasks:
            ctk.CTkLabel(
                self.task_scroll,
                text="No habits added yet. Add one below!",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=Colors.TEXT_SEC,
                fg_color="transparent",
            ).pack(pady=20)
            return

        for task in tasks:
            is_done = self.data_manager.get_micro_task_status(task["id"])
            card = MicroTaskCard(
                self.task_scroll,
                task,
                is_done=is_done,
                on_toggle=self._toggle_task,
                on_rename=self._rename_task if self._edit_mode else None,
                on_delete=self._delete_task if self._edit_mode else None,
                edit_mode=self._edit_mode,
            )
            card.pack(fill="x", pady=3)

    def _toggle_task(self, task_id):
        """Toggle micro task completion."""
        self.data_manager.toggle_micro_task_status(task_id)
        self.app.refresh_progress()

    def _add_habit(self):
        """Add a new habit."""
        text = self.add_entry.get().strip()
        if text:
            self.data_manager.add_micro_task(text)
            self.add_entry.delete(0, "end")
            self._refresh_tasks()
            self.app.refresh_progress()

    def _rename_task(self, task_id, new_text):
        """Rename a micro task."""
        new_text = new_text.strip()
        if new_text:
            self.data_manager.rename_micro_task(task_id, new_text)
            self._refresh_tasks()

    def _delete_task(self, task_id):
        """Delete a micro task."""
        self.data_manager.delete_micro_task(task_id)
        self._refresh_tasks()
        self.app.refresh_progress()

    def _toggle_edit_mode(self):
        """Toggle between normal and edit mode."""
        self._edit_mode = not self._edit_mode
        if self._edit_mode:
            self.edit_btn.configure(
                text="✓ Done",
                fg_color=Colors.ACCENT,
                text_color="#1e1e2e",
            )
        else:
            self.edit_btn.configure(
                text="✏ Edit",
                fg_color=Colors.HOVER,
                text_color=Colors.TEXT_SEC,
            )
        self._refresh_tasks()

    # ─── Back to Study Button ─────────────────────────

    def show_back_to_study_button(self):
        """Show the 'Back to Study' button when coming from break prompt."""
        if self._back_to_study_visible:
            return
        self._back_to_study_visible = True

        self.back_btn_frame.pack(fill="x", pady=(0, 8), before=self.task_scroll)

        back_btn = ctk.CTkButton(
            self.back_btn_frame,
            text="📖  Back to Study",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=Colors.SUCCESS,
            hover_color="#69a584",
            text_color="#1e1e2e",
            width=180,
            height=38,
            corner_radius=10,
            command=self._back_to_study,
        )
        back_btn.pack(pady=4)

    def _back_to_study(self):
        """Return to macro view and start next Pomodoro session."""
        self._back_to_study_visible = False
        # Clear the back button frame
        for widget in self.back_btn_frame.winfo_children():
            widget.destroy()
        self.back_btn_frame.pack_forget()

        # Switch back to macro view
        self.app.switch_mode("macro")
        # Start next work session
        self.app.macro_view.pomodoro.start_work_session()
