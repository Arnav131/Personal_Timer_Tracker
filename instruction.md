# Productivity Enforcer — Setup & Instructions

A premium productivity web application featuring a Pomodoro timer, macro/micro task management, glassmorphism UI with customizable pixel art backgrounds, and an hourly accountability enforcer.

## 🚀 Prerequisites

- **Node.js 18+** — Download from [nodejs.org](https://nodejs.org/)

## ⚙️ Installation

```bash
cd web
npm install
```

## ▶️ Running the Application

```bash
cd web
npm run dev
```

Then open **http://localhost:5173** in your browser.

## 🎨 Customizing Your Experience

**Changing Backgrounds & Themes:**
- Click the **⚙ (Gear Icon)** in the top right corner of the navigation bar to open Settings.
- Select from the bundled pixel art backgrounds (Ramen Shop, Cozy Study Room, Rainy Rooftop, Moonlit Garden).
- Or, click **"Load Custom Image"** to upload any `.png` or `.jpg` from your computer.
- The application automatically analyzes your chosen background and adapts its UI accent colors to match!

## 💡 How to Use the App

### 1. Macro Tasks (Study & Projects)
- Add tasks you want to accomplish in the To-Do List.
- Use the **Pomodoro Timer** (right side) to track your focus sessions.
- Click the ⚙ icon inside the Pomodoro panel to adjust Work and Break durations.

### 2. Micro Tasks (Daily Habits)
- Click the **⚡ Micro Tasks** toggle at the top to switch modes.
- Track recurring daily habits (drinking water, pushups, etc.).
- Click **✏ Edit** to rename, delete, or add new habits.

### 3. The Enforcer (Accountability)
- Every hour, an overlay will appear with an alarm.
- You must type at least 15 characters explaining what you worked on to dismiss it.

### 4. Progress & PDF Export
- Your progress is visualized in the dual rings at the top of the screen.
- Click **📥 PDF** in the navbar to download a daily productivity report.

## 📁 Where is my Data Saved?

All data is stored in your browser's **localStorage** — no server or cloud storage needed. Data persists across browser sessions and automatically resets daily (with backups).

## 🚀 Deploying for Public Use

Build a production bundle:
```bash
cd web
npm run build
```

This creates a `dist/` folder that can be deployed to:
- **GitHub Pages**
- **Vercel** (just connect your repo)
- **Netlify**
- Any static file hosting

## 📂 Old Desktop Version

The original Python/CustomTkinter desktop app is preserved in the `desktop/` folder for reference.
