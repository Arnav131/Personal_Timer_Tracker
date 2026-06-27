# Productivity Enforcer web application

This directory contains the actively developed React/Vite browser application. It includes the glass UI, task and habit workflows, Pomodoro timer, focus music, PDF reporting, optional Google authentication, and Supabase persistence.

## Start the development server

```bash
npm ci
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Supabase configuration is optional; without it the application runs in guest mode.

## Validate a change

```bash
npm test
npm run lint
npm run build
```

## Documentation

- [Project overview](../README.md)
- [Complete local setup and troubleshooting](../LOCAL_SETUP.md)
- [Google sign-in and Supabase setup](../GOOGLE_AUTH_SETUP.md)
- [Docker and Netlify deployment](../NETLIFY_DOCKER_GITHUB_ACTIONS.md)

Dependencies are defined in `package.json` and locked by `package-lock.json`. The Python requirements under `../desktop/` do not apply to this web application.
