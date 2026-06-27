# Coding Agent Prompt — Local Productivity Enforcer

## This is to help you through production of app. 

## Your Role
You are building a **personal desktop productivity application** for a single user named Arnav. This is a fully local, offline application — no cloud, no network, no authentication. You will implement every feature described below exactly as specified. Do not simplify, stub out, or defer any feature. This is the complete spec.

---

## What You Are Building

A desktop app called **"Productivity Enforcer"** with two primary modes — **Macro Tasks** and **Micro Tasks** — plus an hourly accountability enforcer, a Pomodoro timer, real-time progress tracking, PDF export, and a 24-hour auto-resetting local database.

---

## Stack Decision (Pick One & Commit)

**Option A — Python (Recommended for simplicity):**
- `CustomTkinter` — frameless, rounded, dark-themed UI
- `Pygame` — audio playback (looping mp3)
- `ReportLab` or `fpdf2` — PDF generation
- `pystray` + `Pillow` — system tray icon
- `threading` + `time` — background timer daemon
- Storage: local `data.json` in `~/ProductivityEnforcer/`

**Option B — Electron.js + React:**
- React for UI, Tailwind CSS for styling
- `Howler.js` for audio
- `jsPDF` or `PDFKit` for PDF generation
- `electron-tray` for system tray
- `electron-store` or local JSON file for storage

**Whichever you pick, do not mix frameworks. Build it completely.**

---

## Visual Design Requirements (NON-NEGOTIABLE)

This app must look **premium, classic, and aesthetic**. It must feel handcrafted — not like a default UI kit output.

### Color Palette (Warm Dark — recommended)
```
Background:     #1e1e2e  (deep charcoal)
Surface cards:  #2a2a3e  (slightly lighter charcoal)
Accent primary: #d4a853  (warm amber/gold)
Accent soft:    #c8956c  (muted terracotta)
Text primary:   #f0e9d6  (warm cream)
Text secondary: #a0998a  (muted warm grey)
Success:        #7cb899  (soft sage green)
Warning:        #d4a853  (amber — same as accent)
Border/divider: #3a3a52  (subtle)
```

### Typography
- Headings: `Inter Bold` or `Nunito ExtraBold` (or system fallback `Segoe UI` / `SF Pro`)
- Body: `Inter Regular` or `Nunito Regular`
- Timer display: large monospaced or geometric font for the countdown numerals

### Window
- Fully frameless (no OS title bar)
- Rounded corners (12–16px radius)
- Soft box shadow (especially for enforcer pop-up)
- Custom drag region at top of window for moving
- Min size: 900×650px

### Animations
- View transitions between Macro and Micro: fade (150ms) or horizontal slide (200ms)
- Progress bar/ring updates: smooth animated fill, not instant jump
- Hover states on all buttons: subtle brightness or scale change
- Enforcer pop-up: fade-in on appear

---

## Feature 1 — Application Layout

The main window has:
1. A **top navigation bar** (app name left, current date+time right, tray/minimize button far right)
2. A **mode toggle** (prominent button or tab): `[📚 Macro]` ↔ `[⚡ Micro]`
3. A **progress dashboard strip** always visible below nav — shows both Macro % and Micro % simultaneously
4. The main content area below — switches between Macro and Micro views

---

## Feature 2 — Macro Task View

### 2A — To-Do List
- Input field at top: type task and press Enter or click `+` to add
- Each task renders as a card with: checkbox | task text | delete (×) button
- Checking checkbox marks task done (strikethrough text, muted color)
- Tasks persist in today's `data.json`

### 2B — Pomodoro Timer
Place below or beside the to-do list.

**Timer Display:**
- Large circular arc timer (SVG or canvas-drawn) showing remaining time
- Center text: `MM:SS` in large clean font
- Arc fills/drains as time passes
- Below arc: "Session X today" label

**Controls:**
- `Start` — begins work session countdown
- `Pause` / `Resume` — toggles mid-session
- `Reset` — resets current session without counting it
- Configurable durations via small settings icon (default: 25 min work, 10 min break)

**Session End Behaviour:**
When work timer hits 00:00:
1. Play soft chime (single, non-looping)
2. Show the **Break Decision Prompt** (see Feature 3)
3. Increment today's session counter

---

## Feature 3 — Break Decision Prompt

Appears as a modal overlay (not a separate window) when a Pomodoro session ends.

**Title:** "Session complete! What's next?"

**Three buttons — large, clearly distinct:**

| Button | Icon | Action |
|--------|------|--------|
| Take a Break (10 min) | ☕ | Start break countdown; at end of break, show "Ready to start next session?" prompt |
| Do a Micro Task | ⚡ | Switch main view to Micro Task panel. After user checks a task, show "Back to Study" button |
| Continue Studying | 📖 | Immediately start next Pomodoro work session |

- Prompt has a subtle background overlay (semi-transparent dark)
- Dismiss is only possible by choosing one of the three actions — no click-away dismiss

---

## Feature 4 — Micro Task View

Accessed by the mode toggle or the "Do a Micro Task" button.

**Layout:**
- Header: "Daily Habits" with a small `Edit` button
- List of micro-tasks as cards with checkboxes
- Each checked task shows in muted/strikethrough style
- `+ Add Habit` button at bottom opens inline input to add a new task
- Edit mode (pencil icon): allows renaming or deleting tasks permanently

**Default micro-tasks pre-loaded on first launch:**
1. Apply hair serum
2. Polish shoes
3. 20 pushups
4. Wash face (morning)
5. Wash face (night)
6. Skincare routine
7. Drink 2L water

**These are saved in a separate `micro_tasks_config.json`** (task definitions persist across days; only completion status resets daily).

---

## Feature 5 — Progress Dashboard

Always visible strip between nav and content area.

**Two rings or arc indicators side by side:**

```
[  Macro Progress  ]    [  Micro Progress  ]
       68%                     43%
  Study & Tasks              Daily Habits
```

**Macro Progress % formula:**
```
( checked_macro_tasks / total_macro_tasks ) * 0.5 + ( pomodoro_sessions_today / 8 ) * 0.5
```
(Cap Pomodoro contribution at 8 sessions = 100%. If no tasks added, use 0 for that half.)

**Micro Progress % formula:**
```
( checked_micro_tasks / total_micro_tasks ) * 100
```

- Rings animate smoothly on update
- Color changes: 0–33% amber, 34–66% soft blue, 67–100% sage green
- Display percentage number in center of ring

---

## Feature 6 — Hourly Enforcer (Background Daemon)

**Timer Logic:**
- On app launch: start a 60-minute countdown in a background thread
- Timer resets to 60:00 only after a valid enforcer log is submitted
- On system sleep: record sleep time; on wake, subtract elapsed sleep from remaining timer if less than 60 min has passed (prevent instant spam)
- If >60 min has passed while sleeping: trigger enforcer immediately on wake

**Trigger:**
When 60 minutes elapse, launch the Enforcer Window (Feature 7).

---

## Feature 7 — Enforcer Window (Hostage Pop-up)

A separate, small frameless window. This is not a modal — it is a real window that floats above everything.

**Behaviour:**
- `Always on Top` flag set
- Intercepts: `Alt+F4`, window close event, `Cmd+W`, `Escape` — none of these should close it
- Cannot be minimised
- Size: approximately 480×320px, centered on screen
- Plays looping soft alarm MP3 immediately on render

**Content:**
- Small app logo or icon at top
- Text: `"⏰ [Current time] — What did you accomplish this past hour?"`
- Multi-line text input (min 3 rows)
- Submit button (disabled until input ≥ 15 characters)
- Character count indicator: `"12 / 15 min"`

**On Valid Submit (≥15 chars):**
1. Stop audio
2. Save log entry to `data.json` with timestamp
3. Close the enforcer window
4. Reset the 60-min background timer

**Validation Feedback:**
- Submit button stays disabled + greyed until threshold met
- On attempt to submit with <15 chars: subtle red outline shake animation on the input

---

## Feature 8 — Audio

Bundle a single soft audio file (`alarm.mp3`) with the application. This should be a gentle lo-fi chime, soft bell, or calm ambient tone — NOT a system beep.

**Usage:**
| Context | Behaviour |
|--------|-----------|
| Enforcer appears | Loop indefinitely until submission |
| Pomodoro session ends | Play once (no loop) |
| Break timer ends | Play once (no loop) |

If the user doesn't have an MP3 bundled, fall back gracefully (silence — never crash).

**Implementation:**
- Python: `pygame.mixer.music.load()` + `pygame.mixer.music.play(-1)` for loop
- Electron: `Howler.js` with `loop: true` / `loop: false`

---

## Feature 9 — PDF Daily Progress Report

Triggered by a `📥 Download PDF` button always visible in the main UI (top right or bottom of window, never buried).

**PDF Contents (styled, not raw data):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PRODUCTIVITY ENFORCER — DAILY REPORT
  Arnav  |  June 26, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 MACRO PROGRESS — 68%
  Pomodoro Sessions: 4 completed (100 mins focused)

  To-Do List:
  ✓ Complete KNN chapter
  ✓ LeetCode – 3 problems
  ✗ Read PyTorch docs

⚡ MICRO PROGRESS — 43%
  ✓ Apply hair serum
  ✓ Wash face (morning)
  ✗ 20 pushups
  ✗ Polish shoes

🕐 HOURLY LOGS
  10:00 AM — "Finished KNN theory, started coding lab"
  11:00 AM — "Did 2 LeetCode problems, short break"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Generated by Local Productivity Enforcer
```

**File naming:** `productivity_report_2026-06-26.pdf`
**Save location:** Native file save dialog (user picks location)

---

## Feature 10 — 24-Hour Database Reset

**On every app launch or wake:**
1. Read `data.json` and check `"date"` field
2. If `"date"` ≠ today's date:
   a. Copy `data.json` → `auto_backups/backup_YYYY-MM-DD.json`
   b. Delete backups older than 7 days from `auto_backups/`
   c. Reset `data.json` to a fresh template for today
   d. Reset all task checkboxes and session count to 0
   e. Keep `micro_tasks_config.json` intact (task definitions don't reset)
3. If date matches: load normally, restore previous state

---

## Feature 11 — System Tray

App minimises to system tray when main window is closed.

**Tray icon right-click menu:**
- Open Productivity Enforcer
- Download Today's PDF
- Quit

The enforcer window must still be able to fire even when the main window is minimised to tray.

---

## Data Files & Folder Structure

```
~/ProductivityEnforcer/
├── data.json                  ← Today's ephemeral data
├── micro_tasks_config.json    ← User's permanent micro-task list
├── auto_backups/
│   ├── backup_2026-06-25.json
│   ├── backup_2026-06-24.json
│   └── ...
└── assets/
    └── alarm.mp3              ← Bundled soft chime audio
```

**data.json schema:**
```json
{
  "date": "2026-06-26",
  "macro_tasks": [
    { "id": 1, "text": "Complete KNN chapter", "done": true },
    { "id": 2, "text": "LeetCode – 3 problems", "done": false }
  ],
  "pomodoro_sessions_completed": 4,
  "pomodoro_work_duration_minutes": 25,
  "pomodoro_break_duration_minutes": 10,
  "micro_task_status": {
    "1": true,
    "2": false,
    "3": true
  },
  "enforcer_logs": [
    { "timestamp": "2026-06-26T10:00:00", "text": "Finished KNN theory, started coding" }
  ]
}
```

**micro_tasks_config.json schema:**
```json
{
  "tasks": [
    { "id": 1, "text": "Apply hair serum" },
    { "id": 2, "text": "Polish shoes" },
    { "id": 3, "text": "20 pushups" },
    { "id": 4, "text": "Wash face (morning)" },
    { "id": 5, "text": "Wash face (night)" },
    { "id": 6, "text": "Skincare routine" },
    { "id": 7, "text": "Drink 2L water" }
  ]
}
```

---

## What NOT to Do

- Do NOT use default OS title bars or window chrome
- Do NOT use bright neon colors or generic Bootstrap/Material styling
- Do NOT make the enforcer window dismissable without a valid log
- Do NOT connect to the internet for any reason
- Do NOT use a harsh system beep for audio — use the bundled MP3
- Do NOT skip any feature listed above — build all of them
- Do NOT make the UI look like the reference Pomodoro web app (https://onlinealarmkur.com/timer/en/) — this must be a completely distinct, desktop-native design
- Do NOT reset `micro_tasks_config.json` at midnight — only reset daily completion status

---

## Acceptance Criteria

The app is complete when ALL of the following work:

- [ ] App launches with warm dark aesthetic, frameless custom window
- [ ] Macro view shows to-do list + Pomodoro timer with arc display
- [ ] Micro view shows habit checklist, switchable via toggle
- [ ] Pomodoro ends → Break Decision Prompt with 3 working buttons
- [ ] Progress rings update live for both Macro and Micro %
- [ ] Hourly enforcer fires reliably, loops audio, blocks closure until 15-char log
- [ ] PDF downloads correctly with all sections populated
- [ ] Midnight reset wipes data.json, backs up to auto_backups/, preserves micro_tasks_config.json
- [ ] System tray works with open/PDF/quit options
- [ ] App handles system sleep/wake without spamming the enforcer
