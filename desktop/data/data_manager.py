"""
Data Manager — handles all JSON persistence for the Productivity Enforcer.

Manages:
- data.json: Today's ephemeral data (tasks, sessions, logs)
- micro_tasks_config.json: Permanent micro-task definitions
- auto_backups/: Dated backups of previous days' data
"""

import json
import os
import shutil
import threading
from datetime import datetime, timedelta
from pathlib import Path


class DataManager:
    """Thread-safe manager for all application data persistence."""

    # Default micro tasks loaded on first launch
    DEFAULT_MICRO_TASKS = [
        {"id": 1, "text": "Apply hair serum"},
        {"id": 2, "text": "Polish shoes"},
        {"id": 3, "text": "20 pushups"},
        {"id": 4, "text": "Wash face (morning)"},
        {"id": 5, "text": "Wash face (night)"},
        {"id": 6, "text": "Skincare routine"},
        {"id": 7, "text": "Drink 2L water"},
    ]

    def __init__(self):
        """Initialize the data manager and ensure all files/dirs exist."""
        self._lock = threading.Lock()

        # Data directory: ~/ProductivityEnforcer/
        self.base_dir = Path.home() / "ProductivityEnforcer"
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.data_file = self.base_dir / "data.json"
        self.micro_config_file = self.base_dir / "micro_tasks_config.json"
        self.backup_dir = self.base_dir / "auto_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Ensure micro_tasks_config.json exists with defaults
        self._init_micro_config()

        # Check date and handle daily reset
        self._check_daily_reset()

    # ──────────────────────────────────────────────
    # Initialization
    # ──────────────────────────────────────────────

    def _init_micro_config(self):
        """Create micro_tasks_config.json with defaults if it doesn't exist."""
        if not self.micro_config_file.exists():
            config = {"tasks": list(self.DEFAULT_MICRO_TASKS)}
            self._write_json(self.micro_config_file, config)

    def _get_fresh_data(self):
        """Return a fresh data.json template for today."""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "macro_tasks": [],
            "pomodoro_sessions_completed": 0,
            "pomodoro_work_duration_minutes": 25,
            "pomodoro_break_duration_minutes": 10,
            "micro_task_status": {},
            "enforcer_logs": [],
        }

    def _check_daily_reset(self):
        """Check if a new day has started and reset data if needed."""
        today = datetime.now().strftime("%Y-%m-%d")

        if self.data_file.exists():
            try:
                data = self._read_json(self.data_file)
                if data.get("date") == today:
                    # Same day — load normally
                    self._data = data
                    return
                else:
                    # New day — backup old data, then reset
                    self._backup_old_data(data)
            except (json.JSONDecodeError, KeyError):
                # Corrupted file — just reset
                pass

        # Create fresh data for today
        self._data = self._get_fresh_data()
        self._save_data()

    def _backup_old_data(self, old_data):
        """Backup yesterday's data and purge old backups."""
        old_date = old_data.get("date", "unknown")
        backup_file = self.backup_dir / f"backup_{old_date}.json"
        self._write_json(backup_file, old_data)

        # Purge backups older than 7 days
        cutoff = datetime.now() - timedelta(days=7)
        for f in self.backup_dir.iterdir():
            if f.suffix == ".json" and f.name.startswith("backup_"):
                try:
                    date_str = f.stem.replace("backup_", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if file_date < cutoff:
                        f.unlink()
                except ValueError:
                    pass

    # ──────────────────────────────────────────────
    # File I/O (thread-safe)
    # ──────────────────────────────────────────────

    def _read_json(self, path):
        """Read and parse a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path, data):
        """Write data to a JSON file atomically."""
        temp_path = str(path) + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Atomic rename (best-effort on Windows)
        shutil.move(temp_path, str(path))

    def _save_data(self):
        """Persist current data to data.json."""
        self._write_json(self.data_file, self._data)

    # ──────────────────────────────────────────────
    # Macro Tasks
    # ──────────────────────────────────────────────

    def get_macro_tasks(self):
        """Return list of macro tasks."""
        with self._lock:
            return list(self._data.get("macro_tasks", []))

    def add_macro_task(self, text):
        """Add a new macro task. Returns the new task dict."""
        with self._lock:
            tasks = self._data.get("macro_tasks", [])
            new_id = max((t["id"] for t in tasks), default=0) + 1
            task = {"id": new_id, "text": text, "done": False}
            tasks.append(task)
            self._data["macro_tasks"] = tasks
            self._save_data()
            return task

    def toggle_macro_task(self, task_id):
        """Toggle the done status of a macro task."""
        with self._lock:
            for task in self._data.get("macro_tasks", []):
                if task["id"] == task_id:
                    task["done"] = not task["done"]
                    break
            self._save_data()

    def delete_macro_task(self, task_id):
        """Delete a macro task by ID."""
        with self._lock:
            self._data["macro_tasks"] = [
                t for t in self._data.get("macro_tasks", []) if t["id"] != task_id
            ]
            self._save_data()

    # ──────────────────────────────────────────────
    # Pomodoro
    # ──────────────────────────────────────────────

    def get_pomodoro_sessions(self):
        """Return the number of completed Pomodoro sessions today."""
        with self._lock:
            return self._data.get("pomodoro_sessions_completed", 0)

    def increment_pomodoro_session(self):
        """Increment the Pomodoro session counter."""
        with self._lock:
            self._data["pomodoro_sessions_completed"] = (
                self._data.get("pomodoro_sessions_completed", 0) + 1
            )
            self._save_data()

    def get_pomodoro_durations(self):
        """Return (work_minutes, break_minutes)."""
        with self._lock:
            return (
                self._data.get("pomodoro_work_duration_minutes", 25),
                self._data.get("pomodoro_break_duration_minutes", 10),
            )

    def set_pomodoro_durations(self, work_min, break_min):
        """Update Pomodoro durations."""
        with self._lock:
            self._data["pomodoro_work_duration_minutes"] = work_min
            self._data["pomodoro_break_duration_minutes"] = break_min
            self._save_data()

    # ──────────────────────────────────────────────
    # Micro Tasks
    # ──────────────────────────────────────────────

    def get_micro_tasks_config(self):
        """Return the list of micro task definitions."""
        try:
            config = self._read_json(self.micro_config_file)
            return config.get("tasks", [])
        except (json.JSONDecodeError, FileNotFoundError):
            self._init_micro_config()
            return list(self.DEFAULT_MICRO_TASKS)

    def save_micro_tasks_config(self, tasks):
        """Save updated micro task definitions."""
        self._write_json(self.micro_config_file, {"tasks": tasks})

    def add_micro_task(self, text):
        """Add a new micro task definition. Returns the new task."""
        tasks = self.get_micro_tasks_config()
        new_id = max((t["id"] for t in tasks), default=0) + 1
        task = {"id": new_id, "text": text}
        tasks.append(task)
        self.save_micro_tasks_config(tasks)
        return task

    def rename_micro_task(self, task_id, new_text):
        """Rename a micro task definition."""
        tasks = self.get_micro_tasks_config()
        for task in tasks:
            if task["id"] == task_id:
                task["text"] = new_text
                break
        self.save_micro_tasks_config(tasks)

    def delete_micro_task(self, task_id):
        """Delete a micro task definition and its status."""
        tasks = [t for t in self.get_micro_tasks_config() if t["id"] != task_id]
        self.save_micro_tasks_config(tasks)
        with self._lock:
            self._data.get("micro_task_status", {}).pop(str(task_id), None)
            self._save_data()

    def get_micro_task_status(self, task_id):
        """Return whether a micro task is completed today."""
        with self._lock:
            return self._data.get("micro_task_status", {}).get(str(task_id), False)

    def toggle_micro_task_status(self, task_id):
        """Toggle the completion status of a micro task for today."""
        with self._lock:
            status = self._data.get("micro_task_status", {})
            key = str(task_id)
            status[key] = not status.get(key, False)
            self._data["micro_task_status"] = status
            self._save_data()

    # ──────────────────────────────────────────────
    # Enforcer Logs
    # ──────────────────────────────────────────────

    def get_enforcer_logs(self):
        """Return list of enforcer log entries."""
        with self._lock:
            return list(self._data.get("enforcer_logs", []))

    def add_enforcer_log(self, text):
        """Add a new enforcer log entry with current timestamp."""
        with self._lock:
            logs = self._data.get("enforcer_logs", [])
            entry = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "text": text,
            }
            logs.append(entry)
            self._data["enforcer_logs"] = logs
            self._save_data()
            return entry

    # ──────────────────────────────────────────────
    # Progress Calculations
    # ──────────────────────────────────────────────

    def get_macro_progress(self):
        """
        Macro Progress % formula:
        (checked_macro_tasks / total_macro_tasks) * 0.5 + (pomodoro_sessions / 8) * 0.5
        Cap Pomodoro contribution at 8 sessions. If no tasks, that half = 0.
        """
        with self._lock:
            tasks = self._data.get("macro_tasks", [])
            total_tasks = len(tasks)
            checked_tasks = sum(1 for t in tasks if t.get("done"))
            task_ratio = (checked_tasks / total_tasks) if total_tasks > 0 else 0.0

            sessions = self._data.get("pomodoro_sessions_completed", 0)
            session_ratio = min(sessions / 8, 1.0)

            return (task_ratio * 0.5 + session_ratio * 0.5) * 100

    def get_micro_progress(self):
        """
        Micro Progress % formula:
        (checked_micro_tasks / total_micro_tasks) * 100
        """
        tasks = self.get_micro_tasks_config()
        total = len(tasks)
        if total == 0:
            return 0.0
        with self._lock:
            status = self._data.get("micro_task_status", {})
            checked = sum(1 for t in tasks if status.get(str(t["id"]), False))
            return (checked / total) * 100

    # ──────────────────────────────────────────────
    # Full Data Access (for PDF generation)
    # ──────────────────────────────────────────────

    def get_full_data(self):
        """Return a copy of the full current data dict."""
        with self._lock:
            return dict(self._data)

    def get_today_date(self):
        """Return today's date string."""
        with self._lock:
            return self._data.get("date", datetime.now().strftime("%Y-%m-%d"))
