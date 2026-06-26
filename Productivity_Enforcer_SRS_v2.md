# Software Requirements Specification (SRS)
## Project: Local Productivity Enforcer — v2.0
**Author:** Arnav  
**Date:** June 2026  
**Status:** Updated — Major Feature Expansion

---

## 1. Introduction

### 1.1 Purpose
This document defines the software requirements for a locally deployed, aesthetic productivity desktop application. The application is divided into two primary modes — **Macro Tasks** (study sessions, major to-dos) and **Micro Tasks** (small daily habits like skincare, exercise, hygiene). It enforces accountability through a Pomodoro timer, an un-closable alarm-based enforcer, daily progress tracking with PDF export, and a 24-hour auto-reset database.

### 1.2 Scope
A standalone, lightweight desktop application running entirely on the local machine. No network connections, no cloud, no authentication. Features include:
- A **dual-mode interface**: Macro Task view and Micro Task view
- A **Pomodoro timer** with break decision prompts
- An **hourly Enforcer pop-up** (un-closable hostage window with soft alarm)
- **Progress tracking** with percentage indicators for both task types
- **PDF download** of daily progress
- **24-hour ephemeral database** with auto-backup before reset

### 1.3 Development Environment & Tools
- **AI Coding Assistant:** Google Antigravity powered by Claude Opus
- **Target Stack (choose one):**
  - **Python:** CustomTkinter (aesthetic frameless UI) + Pygame (audio) + ReportLab (PDF generation)
  - **Electron.js:** React/HTML/CSS (glassmorphism/dark theme UI) + Howler.js (audio) + jsPDF (PDF generation)
- **Database:** Local ephemeral JSON or CSV file (no external databases)
- **Audio:** Bundled `.mp3` file (soft lo-fi chime or gentle bell — not a system beep)

---

## 2. Overall Description

### 2.1 Product Perspective
A single-user, offline-first desktop productivity tool for personal daily use. Designed to be visually polished, classic, and atmospheric — with a warm or dark aesthetic (deep navy, charcoal, amber accents, or warm cream tones). It should feel like a premium personal assistant, not a generic productivity app.

### 2.2 User Characteristics
The user is Arnav — both the developer and the sole end-user. The application must support focus-heavy study sessions alongside small recurring daily habits that are easy to forget. The UI must be intuitive enough to use without documentation.

### 2.3 Design Philosophy
- **Classic & aesthetic** — avoid bright neon or default OS widgets. Think warm dark tones (charcoal #1e1e2e, amber #d4a853, cream #f5efe6) or a deep moody palette.
- **No default title bars or rigid borders** — fully custom frameless window.
- Soft drop shadows, rounded corners, clean serif or geometric sans-serif typography.
- Smooth transitions between views (fade or slide).
- **Completely distinct** from standard web Pomodoro timers — this is a desktop-native, personal experience.

---

## 3. System Features

---

### 3.1 Dual-Mode Interface

The main window contains two primary views switchable via a prominent toggle/button:

#### 3.1.A — Macro Task View (Default View)
The primary workspace for study and major to-dos. Contains two sub-components:

**3.1.A.1 — To-Do List (Major Tasks)**
- User can add, edit, and delete major task items (e.g., "Complete KNN chapter," "Solve 5 LeetCode problems").
- Each task has a checkbox. Checking it marks it complete and contributes to the Macro Task progress percentage.
- Tasks persist for the current 24-hour day and are wiped at midnight reset.

**3.1.A.2 — Pomodoro Timer**
- Default session: **25 minutes work / 10 minute break** (user can customise durations before starting).
- Multiple sessions allowed per day — no daily session cap.
- Large, elegant circular or arc-style timer display (not a plain digital clock).
- States: **Idle → Running → Break Decision → Break → Resume.**
- At the end of each work session, a **Break Decision Prompt** appears (see Section 3.2).
- Session count displayed (e.g., "Session 3 of today").
- Sessions completed contribute to Macro Task progress percentage.

---

#### 3.1.B — Micro Task View (Habit Panel)
Accessed via a clearly visible switch button in the Macro view (e.g., a floating icon or a side-panel toggle).

- Displays a **user-curated checklist** of small daily habits. Default example tasks (fully editable by user):
  - Apply hair serum
  - Polish shoes
  - 20 pushups
  - Wash face (morning)
  - Wash face (night)
  - Skincare routine
  - Drink 2L water
- User can **add, rename, or delete** micro-tasks from a settings/edit panel.
- Each micro-task has a checkbox. Checking it marks complete for the day.
- All micro-tasks reset at midnight.
- Micro-task completion contributes to the **Micro Task progress percentage** (separate from Macro).

---

### 3.2 Break Decision Prompt

Triggered automatically when a Pomodoro work session ends (timer hits zero).

Displays three clearly styled action buttons:

| Button | Action |
|---|---|
| **Take Break (10 min)** | Starts a 10-minute break countdown. After break ends, prompts to resume. |
| **Do Micro Task** | Switches view to Micro Task panel. After user checks off a task, a "Resume Study" button returns to Pomodoro. |
| **Continue Study Session** | Immediately starts the next Pomodoro session without a break. |

- The prompt is modal but not hostile — it appears as an elegant overlay.
- A soft chime plays when this prompt appears (same audio asset as the enforcer alarm, played once — not looping).

---

### 3.3 Background Daemon (Hourly Enforcer Timer)

- A persistent background process that tracks elapsed time since the last enforcer log or app launch.
- **Exactly 60 minutes** after launch or last valid log, triggers the Enforcer UI (Section 3.4).
- Timer resets to 0 only after a valid log submission.
- Handles system sleep/wake: on wake, calculates actual elapsed time to avoid instant multi-triggering.
- Runs with minimal CPU/RAM footprint (background thread or async loop).

---

### 3.4 The Enforcer UI (Hostage Window)

A frameless, always-on-top pop-up that cannot be dismissed without submitting a valid log.

**Requirements:**
- Forces itself to the front of all windows (`Always on Top`).
- Intercepts and blocks all standard close events: `Alt+F4`, window close button, `Cmd+W`.
- Displays:
  - Time of trigger (e.g., "It's 3:00 PM — what have you been doing?")
  - A text input field with placeholder ("Describe your last hour...")
  - A **Submit** button (disabled until input passes validation — see Section 3.5)
- Aesthetic matches the main app — same color palette, soft shadows, rounded corners.
- **Audio alarm** plays in a loop from the moment this window renders (see Section 3.6).

---

### 3.5 Input Validation (Enforcer)

- Submit button is **disabled** until the text input contains **≥ 15 characters**.
- On invalid submit attempt: subtle shake animation or red outline on the input field.
- On valid submit: log is saved, audio stops, window closes, and timer resets.

---

### 3.6 Continuous Audio Alarm

- A **pleasant, soft audio file** (lo-fi chime, gentle bell, or calm ambient tone) bundled with the app as a `.mp3` file.
- Plays the moment the Enforcer UI renders.
- Loops infinitely without stuttering (use Pygame mixer or Howler.js loop mode).
- Stops **only** on valid form submission — not on click-away or escape.
- The same audio file is used (played once, non-looping) as a notification sound for the Pomodoro Break Decision Prompt.

---

### 3.7 Progress Dashboard

Displayed prominently in the main window — visible in both Macro and Micro views.

**Two separate progress indicators:**

| Indicator | What it tracks |
|---|---|
| **Macro Progress %** | (Tasks checked / Total tasks added) + (Pomodoro sessions completed today) — weighted or simple ratio, developer's choice. |
| **Micro Progress %** | (Micro tasks checked / Total micro tasks defined by user) × 100 |

- Visual style: circular progress rings, gradient arc bars, or elegant horizontal bars — avoid plain grey bars.
- Both percentages displayed simultaneously (e.g., side by side or stacked).
- Update in real-time as tasks are checked.
- Color cues: low progress = warm amber, mid = soft blue, high = calm green (no harsh reds).

---

### 3.8 Ephemeral Storage & Daily Reset

**3.8.1 — Data Stored Per Day (local JSON/CSV):**
- All macro to-do items and their completion status
- Number of Pomodoro sessions completed
- All micro-task items and their completion status
- All hourly enforcer logs (timestamp + text)

**3.8.2 — Midnight Reset:**
- On each app wake/launch, compare current date to last entry date.
- If date has advanced past midnight: trigger backup routine, then wipe the primary log.
- Reset all task checkboxes and session counters to zero.

**3.8.3 — Auto-Backup Failsafe:**
- Before wiping, copy yesterday's data to a local `auto_backups/` folder as a dated file (e.g., `backup_2026-06-25.json`).
- Automatically purge backups older than **7 days**.

**3.8.4 — Manual PDF Export:**
- A clearly visible **"Download PDF"** button in the main UI (always accessible, not buried in menus).
- On click: generates and immediately downloads/saves a PDF report of the **current day's** data.
- PDF contents (see Section 3.9).
- After 24 hours, data resets regardless of whether the user downloaded the PDF.

---

### 3.9 PDF Daily Progress Report

Generated on demand via the Download PDF button.

**PDF Contents:**
- Header: App name, date, user name ("Arnav's Daily Report — June 26, 2026")
- **Macro Task Summary:** list of all tasks with ✓/✗ status + total % completion
- **Pomodoro Summary:** total sessions completed today, total focused minutes
- **Micro Task Summary:** list of all micro-tasks with ✓/✗ status + total % completion
- **Hourly Log:** table of all enforcer submissions (time | log text)
- Footer: "Generated by Local Productivity Enforcer"
- Clean, styled layout — not a raw data dump. Use appropriate fonts, spacing, and section headers.

---

### 3.10 System Tray Icon

- App minimises to system tray (not taskbar) when the main window is closed.
- Tray icon right-click menu:
  - Open App
  - Download PDF (triggers export directly)
  - Quit

---

## 4. Non-Functional Requirements

### 4.1 Aesthetics & UI/UX
- **Theme:** Warm dark (recommended: charcoal backgrounds, amber/gold accents, cream text) or deep moody cool tones (dark navy, soft gold, off-white). No bright default OS widgets.
- **Typography:** Clean geometric sans-serif (e.g., Inter, Nunito, or similar) or a tasteful serif for headings.
- Fully custom frameless window with soft drop shadows and rounded corners.
- Smooth view transitions (fade or slide animations between Macro and Micro views).
- Responsive to window resize within reasonable desktop bounds (min 800×600).
- All interactive elements have hover states and subtle feedback animations.

### 4.2 Performance & Reliability
- Background daemon uses minimal resources — target < 1% CPU, < 30 MB RAM at idle.
- App must handle system sleep/wake gracefully (no instant alarm spam on wake).
- All file I/O (read/write logs, PDF generation) must complete within 2 seconds on average hardware.
- No crash on corrupted or missing local data files — app recreates them silently.

### 4.3 Data & Privacy
- Fully offline. No data leaves the local machine ever.
- No telemetry, no analytics, no network requests.
- All data stored in a clearly named local folder (e.g., `~/ProductivityEnforcer/` or `AppData` on Windows).

---

## 5. Data Model (Reference)

```json
{
  "date": "2026-06-26",
  "macro_tasks": [
    { "id": 1, "text": "Complete KNN chapter", "done": true },
    { "id": 2, "text": "LeetCode - 3 problems", "done": false }
  ],
  "pomodoro_sessions_completed": 4,
  "pomodoro_session_duration_minutes": 25,
  "micro_tasks": [
    { "id": 1, "text": "Apply hair serum", "done": true },
    { "id": 2, "text": "20 pushups", "done": false },
    { "id": 3, "text": "Wash face", "done": true }
  ],
  "enforcer_logs": [
    { "timestamp": "2026-06-26T10:00:00", "text": "Finished KNN theory notes, started coding lab" },
    { "timestamp": "2026-06-26T11:00:00", "text": "Did 2 LeetCode problems, took a short break" }
  ]
}
```

---

## 6. Out of Scope
- Cloud sync or multi-device support
- User accounts or login
- Mobile version
- Integration with external calendars or task managers
- Speech-to-text input (future consideration)

---

## 7. Revision History

| Version | Date | Changes |
|---|---|---|
| 1.0 | Original | Initial SRS — hourly enforcer, basic logging, ephemeral DB |
| 2.0 | June 2026 | Added dual-mode (Macro/Micro), Pomodoro timer, break decision flow, progress dashboard, PDF export, micro-task management, tray icon, full aesthetic spec |
