# Local browser setup and personalization

This guide takes a new contributor from an empty machine to a working local copy of Productivity Enforcer. It covers the quickest guest setup, optional Google/Supabase integration, production-style testing, Docker, personalization, validation, and common installation problems.

## 1. Prerequisites

Install the following tools:

- **Git** for cloning and version control.
- **Node.js 22.x**, which includes npm.
- A current version of Chrome, Edge, Firefox, or Safari.

Optional tools:

- **Docker Desktop** for a containerized production build.
- A **Supabase** project and **Google Cloud** account for optional sign-in and cloud sync.

Verify the required tools in PowerShell, Command Prompt, or a terminal:

```bash
git --version
node --version
npm --version
```

The Node.js command should report version `22.x`. Download it from [nodejs.org](https://nodejs.org/) if the command is unavailable.

## 2. Clone the repository

```bash
git clone https://github.com/Arnav131/Personal_Timer_Tracker.git
cd Personal_Timer_Tracker
```

If you already have the project, update your current branch instead:

```bash
git pull
```

Check `git status` before pulling when you have uncommitted local work.

## 3. Install the browser-app dependencies

The active application is inside `web/`:

```bash
cd web
npm ci
```

`npm ci` reads `web/package-lock.json` and installs the exact tested dependency versions. A Python `requirements.txt` is not needed for the web application. The separate `desktop/requirements.txt` belongs only to the preserved Python desktop version.

Use `npm install` instead of `npm ci` only when intentionally adding or upgrading a package.

## 4. Run immediately in guest mode

No account, database, or environment file is required for guest mode:

```bash
npm run dev
```

Vite prints a local address, normally:

```text
http://localhost:5173
```

Open it in your browser. File changes under `web/src/` refresh automatically. Press `Ctrl+C` in the terminal to stop the development server.

### Guest-mode behavior

- Productivity data survives refreshes in the same browser tab.
- Closing that tab removes guest tasks, habit status, sessions, and logs.
- Theme selection, transparency, music volume, custom images, and custom tracks use longer-lived browser storage.
- The Google sign-in button remains disabled until Supabase is configured.

## 5. Optional: enable Google sign-in and cloud persistence

The full setup is documented in [GOOGLE_AUTH_SETUP.md](GOOGLE_AUTH_SETUP.md). Complete that guide when you want productivity data to follow a signed-in user across browsers or devices.

After creating the Supabase project and applying `supabase/schema.sql`, create a local environment file.

### Windows PowerShell

Run from the repository root:

```powershell
Copy-Item .\web\.env.example .\web\.env.local
```

### macOS, Linux, or Git Bash

Run from the repository root:

```bash
cp web/.env.example web/.env.local
```

Edit `web/.env.local`:

```env
VITE_SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_REPLACE_ME
```

Important security rules:

- The Supabase URL and publishable key are designed for browser use.
- Never place a Supabase `service_role` key in this project.
- Never place the Google OAuth client secret in a Vite environment variable.
- `.env.local` is ignored by Git and must not be committed.

Restart `npm run dev` after changing environment variables. Vite reads them when the server starts.

## 6. Personalize the glass interface

Once the application is open:

1. Select the settings button in the navigation bar.
2. Choose one of the bundled backgrounds or upload a PNG, JPEG, or WebP image.
3. Move **Panel Transparency** between opaque and transparent.
4. The app extracts an accent color from the selected image and updates highlights automatically.
5. Use the focus player to select a bundled track or add local MP3 files.

Custom images and MP3 files are saved in browser IndexedDB. They are intentionally not uploaded to Supabase and will not automatically appear on another device, browser profile, hostname, or port.

### Comparing local and deployed glass effects

Browser rendering determines `backdrop-filter`, transparency, and shadows; the hosting server does not render those effects. For a meaningful comparison:

- Use the same browser, window size, display scaling, and 100% browser zoom.
- Select the same background and transparency value.
- Compare against a local production preview, not only the development server.
- Remember that `localhost` and the deployed domain have separate browser storage.

## 7. Test the production build locally

Run from `web/`:

```bash
npm run build
npm run preview
```

Open the URL printed by Vite, normally [http://localhost:4173](http://localhost:4173). This uses the optimized files from `web/dist/` and is the closest local comparison to the static site deployed on Netlify.

Stop the preview server with `Ctrl+C`.

## 8. Run all quality checks

Before committing a change, run:

```bash
npm test
npm run lint
npm run build
```

What each command checks:

| Command | Check |
| --- | --- |
| `npm test` | Daily reset, stale-state rejection, and habit-data normalization |
| `npm run lint` | JavaScript and React static analysis with Oxlint |
| `npm run build` | Full optimized Vite production compilation |

These are the same core checks used by GitHub Actions before a production deployment.

## 9. Optional: run with Docker

Docker builds the app with Node.js and serves it through Nginx with single-page application routing.

From the repository root:

```bash
docker build -t productivity-enforcer ./web
docker run --rm -p 8080:80 productivity-enforcer
```

Open [http://localhost:8080](http://localhost:8080). This build runs in guest mode when no Supabase build arguments are supplied.

To include browser-safe Supabase configuration, pass the values during the build:

```bash
docker build --build-arg VITE_SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co --build-arg VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_REPLACE_ME -t productivity-enforcer ./web
docker run --rm -p 8080:80 productivity-enforcer
```

Because Vite embeds public environment values at build time, changing them requires rebuilding the image.

## 10. Useful development commands

Run these from `web/`:

| Command | Description |
| --- | --- |
| `npm ci` | Clean, reproducible dependency installation |
| `npm run dev` | Development server with hot module replacement |
| `npm run dev -- --host` | Expose the development server to other devices on the local network |
| `npm run dev -- --port 5174` | Use a different development port |
| `npm test` | Automated data tests |
| `npm run lint` | Static analysis |
| `npm run build` | Optimized build in `dist/` |
| `npm run preview` | Local server for the optimized build |

## 11. Browser storage reference

Local development and production are different web origins, so each keeps separate storage.

| Storage | Contents | Lifetime |
| --- | --- | --- |
| `sessionStorage` | Guest productivity state and reminder status | Current browser tab/session |
| `localStorage` | Background selection, transparency, and music volume | Until browser data is cleared |
| IndexedDB | Custom backgrounds and uploaded MP3 files | Until browser data is cleared |
| Supabase | Signed-in daily state and habit configuration | Until deleted from the account/database |

Clearing site data in browser developer tools resets local personalization and guest data for that origin.

## 12. Troubleshooting

### `node` or `npm` is not recognized

Install Node.js 22, close and reopen the terminal, then run:

```bash
node --version
npm --version
```

### Dependencies fail to install

Confirm that the terminal is inside `Personal_Timer_Tracker/web`, then retry:

```bash
npm ci
```

If the existing installation is damaged, remove `web/node_modules` using your file manager and run `npm ci` again. Do not delete `package-lock.json` during normal setup.

### Port 5173 is already in use

```bash
npm run dev -- --port 5174
```

Then open `http://localhost:5174`.

### Google sign-in is disabled

This is expected in guest mode. Confirm that `web/.env.local` exists, both values are filled in, and the dev server was restarted. Then follow the redirect URL checks in [GOOGLE_AUTH_SETUP.md](GOOGLE_AUTH_SETUP.md).

### Cloud data reports an RLS or table error

Run the complete [Supabase schema](supabase/schema.sql) in the Supabase SQL Editor and verify that the signed-in user is authenticated. The schema enables Row Level Security and creates owner-only policies.

### Custom music does not start automatically

Browsers block unprompted audio. Select the play button once to grant playback through a user interaction. Only MP3 uploads are accepted by the current player.

### Notifications do not appear

Enable notifications from the application settings and allow the browser permission prompt. The 11:45 PM system notification requires the page to be open; browsers cannot reliably schedule it after the site is fully closed.

### The local theme differs from production

Ensure both pages use the same background, transparency value, viewport, zoom, and browser. Use `npm run build` followed by `npm run preview` for a production-style comparison. Localhost and the deployed domain do not share saved theme preferences.

### A route returns 404 in a custom server

The app is a client-side single-page application. Configure the server to return `index.html` for unknown routes. Netlify uses `netlify.toml`/`web/public/_redirects`, while the included Nginx configuration uses `try_files`.

## 13. Updating your local copy

From the repository root:

```bash
git pull
cd web
npm ci
npm run dev
```

Review local changes with `git status` before pulling. When dependencies have not changed, `npm ci` can be skipped, but running it is the safest way to match the current lockfile.

## Next steps

- Read the [main project overview](README.md).
- Configure [Google sign-in and Supabase](GOOGLE_AUTH_SETUP.md).
- Learn the [Netlify and GitHub Actions deployment flow](NETLIFY_DOCKER_GITHUB_ACTIONS.md).
