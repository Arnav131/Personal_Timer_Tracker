# Productivity Enforcer — quick instructions

## Run locally

```powershell
Copy-Item .\web\.env.example .\web\.env.local
# Add the public Supabase URL and publishable key to web/.env.local
cd .\web
npm ci
npm run dev
```

Open `http://localhost:5173`.

## Use the app

- Add study/work items under **Macro Tasks**.
- Track and edit recurring habits under **Micro Tasks**.
- Configure work and break durations from the Pomodoro settings icon.
- Use the top-bar PDF button to download today's report.
- Use the main settings icon for backgrounds, panel transparency, browser reminder permission, and manual daily reset.

## Data behavior

- Guests use tab-scoped `sessionStorage`; task data disappears when the tab closes.
- Google users save today's state to the protected Supabase database.
- Daily tasks and progress reset at the user's local midnight. Habit definitions and timer durations remain.
- At 11:45 PM, an open page offers to download the PDF before reset.

## Complete production setup

1. Follow `GOOGLE_AUTH_SETUP.md` for Supabase, database security, and Google OAuth.
2. Follow `NETLIFY_DOCKER_GITHUB_ACTIONS.md` for Docker and automated Netlify deployments.
