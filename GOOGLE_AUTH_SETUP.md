# Google sign-in and Supabase database setup

**This guide starts from an empty Supabase/Google configuration. Complete it in order. The app uses Supabase because one small service can provide both Google authentication and the database. Netlify only hosts the compiled website.**

## 1. Create the Supabase project

1. Open [supabase.com](https://supabase.com) and sign in.
2. Select **New project**.
3. Choose or create an organization.
4. Enter a project name such as `productivity-enforcer`.
5. Generate and safely store the database password. The browser app never needs this password.
6. Select a region near the expected users.
7. Select **Create new project** and wait until provisioning finishes.
8. Copy the project reference from the project URL. For `https://abcdefgh.supabase.co`, the reference is `abcdefgh`.

## 2. Create the protected data table

1. In the Supabase project, open **SQL Editor**.
2. Select **New query**.
3. Open [`supabase/schema.sql`](supabase/schema.sql) from this repository.
4. Copy the complete file into the query editor.
5. Select **Run**.
6. Open **Table Editor** and confirm that `user_productivity_state` exists.
7. In **Authentication > Policies** or the table's policy view, confirm that Row Level Security is enabled and four policies exist.

The policies are essential. They ensure the signed-in user can access only the row whose `user_id` matches their authentication token. Never replace the browser key with a Supabase secret or `service_role` key.

## 3. Copy the safe browser connection values

1. In Supabase, select **Connect**, or open **Project Settings > API Keys**.
2. Copy the **Project URL**, for example `https://abcdefgh.supabase.co`.
3. Copy the **Publishable key** beginning with `sb_publishable_`.
4. Do not copy a secret key. A secret key bypasses Row Level Security and must never be included in a Vite/browser build.

Keep the URL and publishable key ready for local setup and GitHub secrets later.

## 4. Create a Google Cloud project and consent screen

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Use the project picker at the top and select **New project**.
3. Name it, for example, `Productivity Enforcer Auth`, then select **Create**.
4. Make sure the new project is selected.
5. Open **Google Auth Platform**. In older console layouts, use **APIs & Services > OAuth consent screen**.
6. Complete **Branding**:
   - App name: `Productivity Enforcer`
   - User support email: an email you monitor
   - App logo: optional
   - Authorized domain: add the custom production domain if one is used
   - Developer contact email: an email you monitor
7. In **Audience**, choose **External** unless every user belongs to one Google Workspace organization.
8. While testing, leave publishing status as **Testing** and add every friend's Google address under **Test users**. A user not on this list cannot sign in while the app is in testing mode.
9. In **Data Access/Scopes**, keep only the standard identity scopes needed for sign-in: `openid`, email, and profile.

Google may rename or regroup these pages, but the required values remain the app identity, an External audience, test users, and the three basic identity scopes.

## 5. Create the Google OAuth web client

1. In **Google Auth Platform > Clients**, select **Create client**.
2. Choose **Web application**.
3. Name it `Productivity Enforcer Web`.
4. Under **Authorized JavaScript origins**, add each origin that will run the app:
   - `http://localhost:5173`
   - `https://YOUR-NETLIFY-SITE.netlify.app`
   - `https://YOUR-CUSTOM-DOMAIN.com` if applicable
5. Under **Authorized redirect URIs**, add the Supabase callback, not the Netlify address:

   ```text
   https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback
   ```

6. Select **Create**.
7. Copy the generated **Client ID** and **Client secret**. The client secret belongs only in Supabase, never in this repository, Netlify build variables, or Vite variables.

The redirect chain is Google → Supabase callback → the allowed app URL. Confusing those two redirects is the most common setup failure.

## 6. Enable Google inside Supabase

1. Return to the Supabase dashboard.
2. Open **Authentication > Sign In / Providers**.
3. Select **Google**.
4. Turn **Enable Sign in with Google** on.
5. Paste the Google **Client ID**.
6. Paste the Google **Client secret**.
7. Save the provider settings.
8. Copy the callback URL shown by Supabase and compare it character-for-character with the URI entered in Google Cloud.

## 7. Configure Supabase redirect URLs

1. In Supabase, open **Authentication > URL Configuration**.
2. Set **Site URL** to the final production URL, including `https://`, for example:

   ```text
   https://YOUR-NETLIFY-SITE.netlify.app/
   ```

3. Add these **Redirect URLs**:

   ```text
   http://localhost:5173/**
   https://YOUR-NETLIFY-SITE.netlify.app/**
   ```

4. If Netlify Deploy Previews will be tested with login, also add the preview pattern documented by Supabase:

   ```text
   https://**--YOUR-NETLIFY-SITE.netlify.app/**
   ```

5. If a custom domain is used, add its exact URL as well.
6. Save the URL configuration.

Use exact production URLs. Broad wildcards should be limited to localhost and trusted preview subdomains.

## 8. Configure and run the app locally

From the repository root in PowerShell:

```powershell
Copy-Item .\web\.env.example .\web\.env.local
notepad .\web\.env.local
```

Replace the placeholders:

```dotenv
VITE_SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_REPLACE_ME
```

Then run:

```powershell
cd .\web
npm ci
npm run dev
```

Open `http://localhost:5173`, select **Sign in**, and complete Google consent. `.env.local` is ignored by Git and must not be committed.

## 9. Verify every data rule

Use these checks before deployment:

1. Without signing in, add a macro task and edit/check a micro task.
2. Refresh the same tab: the guest work should remain.
3. Close the tab, open a new tab, and revisit the app: guest work should be gone.
4. Add another guest task, then sign in: on the first sign-in, that tab's work should be copied to the new cloud row.
5. Wait for the top bar to say **Saved to cloud**.
6. Close the browser completely and reopen the app: the Google session and today's cloud work should return.
7. Sign into the same Google account on another browser/device: today's state should load there.
8. Sign into a different Google account: the first account's data must not appear.
9. Open **Settings > Reset today**, confirm, and verify that daily tasks, checks, sessions, and logs clear. Habit definitions and timer durations intentionally remain.
10. To test the date change without waiting until midnight, temporarily change the computer date in a disposable browser profile, reload, and restore the correct date immediately afterward.
11. At 11:45 PM local time, the open page should show the PDF reminder. Browser notifications also appear if the user enabled them in Settings.

## 10. Move Google OAuth from testing to production

Google's Testing mode is enough for explicitly listed friends. For broader public access:

1. Return to **Google Auth Platform > Audience**.
2. Review the app name, support email, domains, privacy policy, and scopes.
3. Select **Publish app**.
4. Complete Google's verification process if Google requests it. Basic sign-in scopes normally require less review than sensitive scopes.
5. Remove obsolete test origins and redirect URLs after production is stable.

## Troubleshooting

- **Sign-in button is disabled:** the two `VITE_SUPABASE_*` values were absent when Vite built the app. Restart the dev server after editing `.env.local`, or rerun the GitHub workflow after adding secrets.
- **`redirect_uri_mismatch`:** the Google Authorized redirect URI must be the exact Supabase `/auth/v1/callback` URL.
- **Returned to the wrong website:** correct Supabase **Site URL** and **Redirect URLs**.
- **Google says access is blocked:** add the address as a Google OAuth test user or publish the consent screen.
- **`relation user_productivity_state does not exist`:** run `supabase/schema.sql` in the correct project.
- **`new row violates row-level security policy`:** run the complete schema, confirm the user is signed in, and confirm the browser uses the publishable key from the same Supabase project.
- **Cloud sync error in the top bar:** inspect the browser Network/Console panels and the Supabase logs; do not disable RLS as a shortcut.

Official references: [Supabase Google login](https://supabase.com/docs/guides/auth/social-login/auth-google), [Supabase redirect URLs](https://supabase.com/docs/guides/auth/redirect-urls), and [Supabase API key safety](https://supabase.com/docs/guides/getting-started/api-keys).
