"""
PDF Generator — styled daily progress report.

Generates a clean, formatted PDF with:
- Header: App name, date, user name
- Macro Task Summary with ✓/✗ status
- Pomodoro Summary with session count and focused minutes
- Micro Task Summary with ✓/✗ status
- Hourly Enforcer Logs table
- Footer
"""

import os
from datetime import datetime
from pathlib import Path
from tkinter import filedialog

from fpdf import FPDF


class Colors:
    # RGB tuples for PDF
    BG = (30, 30, 46)
    SURFACE = (42, 42, 62)
    ACCENT = (212, 168, 83)
    TEXT = (240, 233, 214)
    TEXT_SEC = (160, 153, 138)
    SUCCESS = (124, 184, 153)
    DANGER = (199, 80, 80)
    BORDER = (58, 58, 82)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


class PDFGenerator:
    """Generates styled PDF daily progress reports."""

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def generate_and_save(self, parent_window=None):
        """Generate the PDF and prompt user for save location."""
        today = datetime.now().strftime("%Y-%m-%d")
        default_name = f"productivity_report_{today}.pdf"

        # Show save dialog
        file_path = filedialog.asksaveasfilename(
            parent=parent_window,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_name,
            title="Save Daily Progress Report",
        )

        if not file_path:
            return  # User cancelled

        # Generate the PDF
        pdf = self._create_pdf()
        pdf.output(file_path)

    def _create_pdf(self):
        """Create the styled PDF document."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        data = self.data_manager.get_full_data()
        micro_config = self.data_manager.get_micro_tasks_config()
        today = datetime.now()

        # ── Header ──
        pdf.set_fill_color(*Colors.ACCENT)
        pdf.rect(10, 10, 190, 1.5, "F")

        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(*Colors.BLACK)
        pdf.ln(8)
        pdf.cell(0, 12, "PRODUCTIVITY ENFORCER", ln=True, align="C")

        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, "Daily Progress Report", ln=True, align="C")

        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(80, 80, 80)
        date_str = today.strftime("%B %d, %Y")
        pdf.cell(0, 8, f"Arnav  |  {date_str}", ln=True, align="C")

        pdf.set_fill_color(*Colors.ACCENT)
        pdf.rect(10, pdf.get_y() + 2, 190, 1, "F")
        pdf.ln(8)

        # ── Macro Task Summary ──
        macro_pct = self.data_manager.get_macro_progress()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*Colors.BLACK)
        pdf.cell(0, 10, f"MACRO PROGRESS - {int(macro_pct)}%", ln=True)

        # Pomodoro summary
        sessions = data.get("pomodoro_sessions_completed", 0)
        work_dur = data.get("pomodoro_work_duration_minutes", 25)
        total_min = sessions * work_dur

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 7, f"    Pomodoro Sessions: {sessions} completed ({total_min} mins focused)", ln=True)
        pdf.ln(2)

        # Task list
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 7, "    To-Do List:", ln=True)

        macro_tasks = data.get("macro_tasks", [])
        if macro_tasks:
            for task in macro_tasks:
                icon = "+" if task.get("done") else "-"
                status_text = "DONE" if task.get("done") else "TODO"
                pdf.set_font("Helvetica", "", 10)
                if task.get("done"):
                    pdf.set_text_color(124, 184, 153)  # Green
                else:
                    pdf.set_text_color(199, 80, 80)  # Red
                pdf.cell(0, 6, f"      [{status_text}]  {task['text']}", ln=True)
        else:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 6, "      No tasks added today", ln=True)

        pdf.ln(6)

        # ── Micro Task Summary ──
        micro_pct = self.data_manager.get_micro_progress()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*Colors.BLACK)
        pdf.cell(0, 10, f"MICRO PROGRESS - {int(micro_pct)}%", ln=True)

        micro_status = data.get("micro_task_status", {})
        if micro_config:
            for task in micro_config:
                done = micro_status.get(str(task["id"]), False)
                status_text = "DONE" if done else "TODO"
                pdf.set_font("Helvetica", "", 10)
                if done:
                    pdf.set_text_color(124, 184, 153)
                else:
                    pdf.set_text_color(199, 80, 80)
                pdf.cell(0, 6, f"      [{status_text}]  {task['text']}", ln=True)
        else:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 6, "      No habits configured", ln=True)

        pdf.ln(6)

        # ── Hourly Logs ──
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*Colors.BLACK)
        pdf.cell(0, 10, "HOURLY LOGS", ln=True)

        logs = data.get("enforcer_logs", [])
        if logs:
            # Table header
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(40, 7, "Time", border=1, fill=True)
            pdf.cell(0, 7, "Log Entry", border=1, ln=True, fill=True)

            pdf.set_font("Helvetica", "", 10)
            for log in logs:
                try:
                    ts = datetime.fromisoformat(log["timestamp"])
                    time_str = ts.strftime("%I:%M %p")
                except (ValueError, KeyError):
                    time_str = "Unknown"

                pdf.set_text_color(60, 60, 60)
                pdf.cell(40, 7, f"  {time_str}", border=1)

                # Truncate long text
                text = log.get("text", "")
                if len(text) > 80:
                    text = text[:77] + "..."
                pdf.cell(0, 7, f"  {text}", border=1, ln=True)
        else:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 6, "      No hourly logs recorded today", ln=True)

        # ── Footer ──
        pdf.ln(10)
        pdf.set_fill_color(*Colors.ACCENT)
        pdf.rect(10, pdf.get_y(), 190, 0.5, "F")
        pdf.ln(4)

        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 8, "Generated by Local Productivity Enforcer", ln=True, align="C")

        return pdf
