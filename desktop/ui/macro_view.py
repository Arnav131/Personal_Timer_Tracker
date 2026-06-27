"""
Macro Task View — To-Do List + Pomodoro Timer side by side.

Premium glass-panel design:
- Left panel: Task list with glass card styling
- Right panel: Large Pomodoro timer with glass styling
- Themed colors from ThemeManager
"""

import customtkinter as ctk
import tkinter as tk


class TaskCard(ctk.CTkFrame):
    """Individual task card with checkbox and delete button — glass styled."""

    def __init__(self, parent, task, on_toggle, on_delete, theme):
        super().__init__(
            parent,
            fg_color=theme.surface,
            corner_radius=12,
            height=48,
            border_width=1,
            border_color=theme.border,
        )
        self.pack_propagate(False)
        self.theme = theme

        self.task = task
        self.on_toggle = on_toggle
        self.on_delete = on_delete

        # Checkbox
        self.var = ctk.BooleanVar(value=task.get("done", False))
        self.checkbox = ctk.CTkCheckBox(
            self,
            text="",
            variable=self.var,
            width=24,
            height=24,
            checkbox_width=22,
            checkbox_height=22,
            fg_color=theme.accent,
            hover_color=theme.accent_soft,
            border_color=theme.border,
            checkmark_color="#0a0a14",
            command=self._toggle,
        )
        self.checkbox.pack(side="left", padx=(14, 10), pady=10)

        # Delete button
        del_btn = ctk.CTkButton(
            self,
            text="✕",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=theme.danger,
            text_color=theme.text_sec,
            width=30,
            height=30,
            corner_radius=8,
            command=lambda: self.on_delete(self.task["id"]),
        )
        del_btn.pack(side="right", padx=10)

        # Task text
        text_color = theme.text_sec if task.get("done") else theme.text
        font_style = ctk.CTkFont(
            family="Segoe UI", size=14,
            overstrike=task.get("done", False)
        )
        self.text_label = ctk.CTkLabel(
            self,
            text=task["text"],
            font=font_style,
            text_color=text_color,
            fg_color="transparent",
            anchor="w",
        )
        self.text_label.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def _toggle(self):
        self.on_toggle(self.task["id"])
        done = self.var.get()
        text_color = self.theme.text_sec if done else self.theme.text
        font_style = ctk.CTkFont(
            family="Segoe UI", size=14, overstrike=done
        )
        self.text_label.configure(text_color=text_color, font=font_style)


class MacroView(ctk.CTkFrame):
    """Macro task view with glass panels for to-do list and Pomodoro timer."""

    def __init__(self, parent, data_manager, audio_manager, app, theme):
        super().__init__(parent, fg_color="transparent")
        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.app = app
        self.theme = theme

        # Split layout: left = tasks, right = pomodoro
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self._build_task_list()
        self._build_pomodoro()

    def _build_task_list(self):
        """Build the to-do list panel with glass styling."""
        # Glass container
        task_container = ctk.CTkFrame(
            self.left_frame,
            fg_color=self.theme.surface,
            corner_radius=16,
            border_width=1,
            border_color=self.theme.border,
        )
        task_container.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(task_container, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 8))

        ctk.CTkLabel(
            header,
            text="📝  To-Do List",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=self.theme.accent,
            fg_color="transparent",
        ).pack(side="left")

        # Input area
        input_frame = ctk.CTkFrame(
            task_container, fg_color="transparent"
        )
        input_frame.pack(fill="x", padx=18, pady=(0, 8))

        self.task_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Add a new task...",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color=self.theme.bg,
            border_color=self.theme.border,
            text_color=self.theme.text,
            placeholder_text_color=self.theme.text_sec,
            corner_radius=10,
            height=40,
        )
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.task_entry.bind("<Return>", lambda e: self._add_task())

        add_btn = ctk.CTkButton(
            input_frame,
            text="+",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color=self.theme.accent,
            hover_color=self.theme.accent_soft,
            text_color="#0a0a14",
            width=44,
            height=40,
            corner_radius=10,
            command=self._add_task,
        )
        add_btn.pack(side="right")

        # Scrollable task list
        self.task_scroll = ctk.CTkScrollableFrame(
            task_container,
            fg_color="transparent",
            scrollbar_button_color=self.theme.border,
            scrollbar_button_hover_color=self.theme.text_sec,
        )
        self.task_scroll.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self._refresh_tasks()

    def _add_task(self):
        """Add a new task from the input field."""
        text = self.task_entry.get().strip()
        if text:
            self.data_manager.add_macro_task(text)
            self.task_entry.delete(0, "end")
            self._refresh_tasks()
            self.app.refresh_progress()

    def _toggle_task(self, task_id):
        """Toggle task completion status."""
        self.data_manager.toggle_macro_task(task_id)
        self.app.refresh_progress()

    def _delete_task(self, task_id):
        """Delete a task."""
        self.data_manager.delete_macro_task(task_id)
        self._refresh_tasks()
        self.app.refresh_progress()

    def _refresh_tasks(self):
        """Refresh the task list display."""
        for widget in self.task_scroll.winfo_children():
            widget.destroy()

        tasks = self.data_manager.get_macro_tasks()

        if not tasks:
            ctk.CTkLabel(
                self.task_scroll,
                text="No tasks yet. Add one above!",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=self.theme.text_sec,
                fg_color="transparent",
            ).pack(pady=24)
            return

        for task in tasks:
            card = TaskCard(
                self.task_scroll,
                task,
                on_toggle=self._toggle_task,
                on_delete=self._delete_task,
                theme=self.theme,
            )
            card.pack(fill="x", pady=3)

    def _build_pomodoro(self):
        """Build the Pomodoro timer panel."""
        from ui.pomodoro_timer import PomodoroTimer

        self.pomodoro = PomodoroTimer(
            self.right_frame,
            data_manager=self.data_manager,
            audio_manager=self.audio_manager,
            app=self.app,
            theme=self.theme,
        )
        self.pomodoro.pack(fill="both", expand=True)
