# Automated Netlify deployment with Docker and GitHub Actions

**This repository builds the React site inside Docker, verifies it, exports the static `dist` files, and uses GitHub Actions to upload those files to Netlify. Netlify hosts static files; it does not run the Nginx Docker container. The container remains useful for reproducible builds and local production testing.**

Complete [`GOOGLE_AUTH_SETUP.md`](GOOGLE_AUTH_SETUP.md) first, or at minimum create the Supabase project and copy its project URL and publishable key.

## 1. Install the local tools

Install and verify:

```powershell
git --version
node --version
npm --version
docker --version
```

Recommended versions are Node.js 22 and a current Docker Desktop release. Start Docker Desktop before running Docker commands.

## 2. Verify the project locally

From the repository root:

```powershell
cd .\web
npm ci
npm test
npm run lint
npm run build
cd ..
```

All commands must succeed. A bundle-size warning is informational.

Optionally verify the production container:

```powershell
docker build `
  --build-arg VITE_SUPABASE_URL="https://YOUR_PROJECT_REF.supabase.co" `
  --build-arg VITE_SUPABASE_PUBLISHABLE_KEY="sb_publishable_REPLACE_ME" `
  -t productivity-enforcer .\web

docker run --rm -p 8080:80 productivity-enforcer
```

Open `http://localhost:8080`. Press `Ctrl+C` to stop it. Values passed to `VITE_*` are compiled into the public JavaScript bundle, so only use the Supabase publishable key—never a secret or `service_role` key.

## 3. Create and push the GitHub repository

1. Sign in to GitHub and create a new repository.
2. Do not add another README, `.gitignore`, or license when the local repository already contains them.
3. Copy the repository HTTPS URL.
4. In PowerShell at the project root, inspect changes and commit them:

   ```powershell
   git status
   git add .
   git commit -m "Add Google auth, cloud persistence, and automated deployment"
   ```

5. Make sure the production branch is named `main`:

   ```powershell
   git branch -M main
   ```

6. Add the GitHub remote if one is not already configured, then push:

   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   git push -u origin main
   ```

If `origin` already exists, inspect it with `git remote -v` and do not add it again.

## 4. Create an empty Netlify site

1. Sign in at [app.netlify.com](https://app.netlify.com/).
2. Select **Add new project**.
3. Choose the manual/deploy-without-Git option. The exact label can change in the Netlify UI.
4. Drop any small placeholder folder if Netlify requires a first manual deploy. The GitHub workflow will replace it.
5. Open **Project configuration > General > Project information**.
6. Set a clear project name. This determines the default `https://NAME.netlify.app` URL.
7. Copy the **Project ID** (older screens call it **Site ID** or **API ID**). It is a UUID, not the site name.
8. Do not separately connect Netlify's Git-based continuous deployment when using this repository's GitHub Actions workflow; otherwise a push can start two deployments.

## 5. Create a Netlify personal access token

1. In Netlify, open the user/avatar menu.
2. Open **User settings > Applications > Personal access tokens**.
3. Select **New access token**.
4. Name it `GitHub Actions - Productivity Enforcer`.
5. Create it and immediately copy the token. Netlify will not show the complete value again.
6. Treat it as a password. Never place it in `.env`, workflow YAML, chat, screenshots, or source code.

## 6. Add the four GitHub Actions secrets

1. Open the GitHub repository.
2. Go to **Settings > Secrets and variables > Actions**.
3. Select **New repository secret** for each item below. Secret names are case-sensitive.

| Secret name | Value |
| --- | --- |
| `NETLIFY_AUTH_TOKEN` | Netlify personal access token from step 5 |
| `NETLIFY_SITE_ID` | Netlify Project/Site/API ID from step 4 |
| `VITE_SUPABASE_URL` | `https://YOUR_PROJECT_REF.supabase.co` |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Supabase key beginning with `sb_publishable_` |

4. Reopen the Actions secrets list and confirm all four names exist. GitHub intentionally will not reveal their values.

The publishable key is designed for browser use, but keeping build configuration in GitHub secrets avoids hard-coding project-specific values. The Netlify token is truly sensitive.

## 7. Understand the included automation

The workflow is [`.github/workflows/netlify.yml`](.github/workflows/netlify.yml). It does the following:

1. Runs on every pull request, every push to `main`, or a manual dispatch.
2. Installs exact locked dependencies with `npm ci`.
3. Runs tests and lint checks.
4. For non-pull-request runs, builds the export stage in [`web/Dockerfile`](web/Dockerfile).
5. Passes only the public Supabase build values to Vite.
6. Exports `/app/dist` from Docker to `web/dist` on the GitHub runner.
7. Deploys that folder to the existing Netlify site with Netlify CLI.
8. Cancels an older in-progress deployment for the same branch when a newer commit arrives.

Pull requests verify code but deliberately do not receive production tokens or deploy to production.

## 8. Run the first automated deployment

1. Push a commit to `main`, or open **GitHub > Actions > Test and deploy to Netlify** and select **Run workflow**.
2. Open the workflow run.
3. Wait for the `verify` job and then the `deploy` job to turn green.
4. Expand **Deploy production files to Netlify** and copy the production URL if needed.
5. Open **Netlify > Deploys** and confirm a new published deploy exists.
6. Open the site in a private browser window and confirm the page loads.

If Actions shows no workflow, confirm the file exists at exactly `.github/workflows/netlify.yml` on the default branch and that GitHub Actions is enabled under repository settings.

## 9. Finish OAuth URLs after the Netlify name is final

1. Copy the exact Netlify production origin, for example `https://productivity-enforcer.netlify.app`.
2. In Google Cloud's OAuth web client, add that value under **Authorized JavaScript origins**.
3. In Supabase **Authentication > URL Configuration**:
   - Set **Site URL** to the Netlify URL with a trailing `/`.
   - Add `https://YOUR-NETLIFY-SITE.netlify.app/**` to Redirect URLs.
4. Keep Google's Authorized redirect URI pointing to Supabase:

   ```text
   https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback
   ```

5. Wait a few minutes for Google configuration changes to propagate, then test sign-in on the deployed site.

## 10. Verify the deployed behavior

1. Open the production URL without signing in and add a task.
2. Refresh: it remains in the same tab.
3. Close the tab and open a new one: guest data is gone.
4. Sign in with an allowed Google account, add a task, and wait for **Saved to cloud**.
5. Close and reopen the browser: today's cloud data returns.
6. Open the same account on a second device: the same daily data loads.
7. Test **Settings > Reset today**.
8. Enable browser alerts in Settings and allow notifications when the browser asks.
9. Confirm PDF download works.
10. In Supabase Table Editor, verify that the row's `user_id` matches the signed-in user under **Authentication > Users**.

## 11. Normal future release process

For each update:

```powershell
git status
git add .
git commit -m "Describe the update"
git push origin main
```

GitHub Actions automatically tests, builds in Docker, and deploys. Do not manually upload `web/dist`, commit `.env.local`, or commit generated `dist`/`node_modules` folders.

## Optional: custom domain and HTTPS

1. In Netlify, open **Domain management**.
2. Select **Add a domain** and follow Netlify's DNS instructions.
3. Wait for DNS propagation and Netlify's TLS certificate.
4. Add the custom origin to Google Authorized JavaScript origins.
5. Change Supabase Site URL to the custom HTTPS URL and add it to Redirect URLs.
6. Retest Google sign-in in a private window.

## Troubleshooting the workflow

- **`Input required and not supplied` / empty variable:** verify all four GitHub secret names exactly.
- **`Site not found` or `Not authorized`:** `NETLIFY_SITE_ID` or the token is wrong, or the token owner cannot access that site.
- **Docker build cannot find files:** run it from the repository root with `./web` as the build context.
- **The deployed Sign in button is disabled:** the Supabase GitHub secrets were absent during the build. Add them and rerun the complete workflow.
- **The site loads but direct paths return 404:** `web/public/_redirects` and `netlify.toml` already provide the SPA fallback; confirm `_redirects` exists in the deployed output.
- **Two deploys happen for one push:** disconnect Netlify's native Git deployment or stop using the custom GitHub workflow. Keep one deployment owner.
- **Token leaked:** revoke it immediately in Netlify, generate another, and replace `NETLIFY_AUTH_TOKEN` in GitHub.
- **A dependency install changes unexpectedly:** commit `web/package-lock.json`; the Docker and CI builds use `npm ci` for reproducibility.

Official references: [Netlify deploys and CLI](https://docs.netlify.com/deploy/create-deploys/), [Netlify CLI production deploy](https://docs.netlify.com/api-and-cli-guides/cli-guides/get-started-with-cli/), and [GitHub Actions secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions).
