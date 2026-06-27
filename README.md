# Productivity Enforcer

## Run the application

Open a terminal in the project directory and run these commands:

```powershell
cd .\web
npm install
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173) in your browser. Keep the terminal open while the application is running. Press `Ctrl+C` to stop it.

## About

Productivity Enforcer is a focused productivity dashboard that combines task management, daily habits, Pomodoro sessions, progress tracking, and accountability reminders in a customizable glass-style interface.

## Features

- Macro task management for study, work, and project goals
- Configurable Pomodoro work and break sessions
- Daily micro-task and habit tracking
- Visual progress dashboard
- Hourly accountability prompts
- PDF productivity report export
- Bundled and custom background images
- Smooth panel transparency and blur controls
- Automatic accent colors based on the selected background
- Local, persistent data with no account or cloud service required

## Data and privacy

Application data stays on your device:

- Tasks, settings, and daily progress are stored in browser `localStorage`.
- Custom background images are stored in browser IndexedDB to support larger files reliably.
- Daily activity resets automatically, with previous-day data backed up locally.

Clearing this site's browser storage will remove the saved application data and custom backgrounds.

## Requirements

- [Node.js](https://nodejs.org/) 18 or newer
- npm (included with Node.js)
- A modern browser with IndexedDB support

## Available commands

Run these commands from the `web` directory:

```powershell
npm run dev      # Start the development server
npm run build    # Create a production build
npm run preview  # Preview the production build
npm run lint     # Check the source code
```

## Project structure

```text
Personal_Timer_Tracker/
├── assets/          # Shared images and audio
├── desktop/         # Preserved Python desktop version
└── web/             # React web application
    ├── public/      # Bundled backgrounds and static assets
    └── src/         # Components, hooks, styles, and utilities
```

## Production build

```powershell
cd .\web
npm install
npm run build
```

The optimized application will be generated in `web/dist`. It can be hosted on services such as GitHub Pages, Netlify, or Vercel, or on any static web server.

## Technology

- React 19
- Vite
- CSS glassmorphism design system
- IndexedDB and localStorage
- jsPDF

