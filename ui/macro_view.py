"""
Macro Task View — To-Do List + Pomodoro Timer side by side.

Left panel: Task list with add/check/delete functionality.
Right panel: Pomodoro timer with arc display.
"""

import customtkinter as ctk
import tkinter as tk


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


class TaskCard(ctk.CTkFrame):
    """Individual task card with checkbox and delete button."""

    def __init__(self, parent, task, on_toggle, on_delete):
        super().__init__(parent, fg_color=Colors.SURFACE, corner_radius=10, height=44)
        self.pack_propagate(False)

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
            checkbox_width=20,
            checkbox_height=20,
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_SOFT,
            border_color=Colors.BORDER,
            checkmark_color="#1e1e2e",
            command=self._toggle,
        )
        self.checkbox.pack(side="left", padx=(12, 8), pady=10)

        # Delete button
        del_btn = ctk.CTkButton(
            self,
            text="✕",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=Colors.DANGER,
            text_color=Colors.TEXT_SEC,
            width=28,
            height=28,
            corner_radius=6,
            command=lambda: self.on_delete(self.task["id"]),
        )
        del_btn.pack(side="right", padx=8)

        # Task text
        text_color = Colors.TEXT_SEC if task.get("done") else Colors.TEXT
        font_style = ctk.CTkFont(
            family="Segoe UI", size=13,
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
        text_color = Colors.TEXT_SEC if done else Colors.TEXT
        font_style = ctk.CTkFont(
            family="Segoe UI", size=13, overstrike=done
        )
        self.text_label.configure(text_color=text_color, font=font_style)


class MacroView(ctk.CTkFrame):
    """Macro task view with to-do list and Pomodoro timer."""

    def __init__(self, parent, data_manager, audio_manager, app):
        super().__init__(parent, fg_color="transparent")
        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.app = app

        # Split layout: left = tasks, right = pomodoro
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(8, 0))

        self._build_task_list()
        self._build_pomodoro()

    def _build_task_list(self):
        """Build the to-do list panel."""
        # Header
        header = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            header,
            text="📝  To-Do List",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=Colors.ACCENT,
            fg_color="transparent",
        ).pack(side="left")

        # Input area
        input_frame = ctk.CTkFrame(
            self.left_frame, fg_color=Colors.SURFACE, corner_radius=10
        )
        input_frame.pack(fill="x", pady=(0, 8))

        self.task_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Add a new task...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=Colors.BG,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT,
            placeholder_text_color=Colors.TEXT_SEC,
            corner_radius=8,
            height=36,
        )
        self.task_entry.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        self.task_entry.bind("<Return>", lambda e: self._add_task())

        add_btn = ctk.CTkButton(
            input_frame,
            text="+",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_SOFT,
            text_color="#1e1e2e",
            width=40,
            height=36,
            corner_radius=8,
            command=self._add_task,
        )
        add_btn.pack(side="right", padx=(0, 8), pady=8)

        # Scrollable task list
        self.task_scroll = ctk.CTkScrollableFrame(
            self.left_frame,
            fg_color="transparent",
            scrollbar_button_color=Colors.BORDER,
            scrollbar_button_hover_color=Colors.TEXT_SEC,
        )
        self.task_scroll.pack(fill="both", expand=True)

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
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=Colors.TEXT_SEC,
                fg_color="transparent",
            ).pack(pady=20)
            return

        for task in tasks:
            card = TaskCard(
                self.task_scroll,
                task,
                on_toggle=self._toggle_task,
                on_delete=self._delete_task,
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
        )
        self.pomodoro.pack(fill="both", expand=True)
