# Productivity Enforcer

A React productivity dashboard with macro tasks, editable daily habits, Pomodoro sessions, accountability prompts, PDF reports, Google sign-in, and optional cloud persistence.

## Persistence rules

- **Guest:** task and habit data uses `sessionStorage`, so it survives refreshes in the same tab but is removed when that tab is closed.
- **Signed in with Google:** today's state is saved in Supabase and can be reopened on another browser or device.
- **Midnight:** macro tasks, habit checks, Pomodoro session count, and accountability logs reset at the user's local midnight. Habit definitions and chosen timer durations remain.
- **Manual reset:** Settings includes a confirmation-protected **Reset today** button.
- **11:45 PM:** an open app displays a PDF reminder. If browser notifications were enabled in Settings, it also sends a system notification. Browsers cannot reliably schedule this notification after the page is completely closed.

## First-time setup

Follow both guides in order:

1. [Google sign-in and Supabase database setup](GOOGLE_AUTH_SETUP.md)
2. [Netlify deployment with Docker and GitHub Actions](NETLIFY_DOCKER_GITHUB_ACTIONS.md)

The database schema is in [`supabase/schema.sql`](supabase/schema.sql).

## Run locally

```powershell
Copy-Item .\web\.env.example .\web\.env.local
# Fill in the two public Supabase values in web/.env.local
cd .\web
npm ci
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Without the Supabase variables, the app still runs in guest mode and the Google button remains disabled.

## Verify

```powershell
cd .\web
npm test
npm run lint
npm run build
```

## Main project files

```text
Personal_Timer_Tracker/
├── .github/workflows/netlify.yml    # Test/build/deploy automation
├── supabase/schema.sql              # Protected per-user database table
├── netlify.toml                     # Netlify build and SPA routing
├── web/                             # React/Vite web application
│   ├── Dockerfile                   # Reproducible build and optional Nginx image
│   ├── .env.example                 # Safe configuration template
│   └── src/                         # Components, auth, storage, and utilities
├── GOOGLE_AUTH_SETUP.md
└── NETLIFY_DOCKER_GITHUB_ACTIONS.md
```

The preserved `desktop/` folder is the original Python desktop version; cloud authentication and Netlify deployment apply to the `web/` application.
