---
title: OAuth Providers
description: Set up GitHub, Google, or GitLab as OAuth providers for AuthGate.
---

AuthGate supports **GitHub**, **Google**, and **GitLab** out of the box. Enable any combination via the `connectors` section in `authgate.yaml`. Each connector needs a Client ID and Client Secret from the provider.

## GitHub

1. Go to **Settings → Developer settings → OAuth Apps → [New OAuth App](https://github.com/settings/applications/new)**
2. Fill in:
   - **Application name**: anything (e.g., `MyApp via AuthGate`)
   - **Homepage URL**: your AuthGate URL (e.g., `http://localhost:8000` for dev, `https://auth.example.com` for prod)
   - **Authorization callback URL**: `{BASE_URL}{GITHUB_REDIRECT_PATH}` (e.g. `http://localhost:8000/auth/github/callback`)
3. Click **Register application**
4. On the next page, note the **Client ID** and click **Generate a new client secret**
5. Add them to your environment:
   ```bash
   export GITHUB_CLIENT_ID=your_client_id
   export GITHUB_CLIENT_SECRET=your_client_secret
   ```

### YAML config

```yaml
connectors:
  - type: github
    id: github
    name: GitHub
    config:
      clientID: $GITHUB_CLIENT_ID
      clientSecret: $GITHUB_CLIENT_SECRET
      redirectPath: /auth/github/callback
```

### Scopes requested
AuthGate requests `read:user user:email` — just enough to read the user's profile and email. No repo access.

## Google

1. Go to the [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials) page
2. Click **Create Credentials → OAuth 2.0 Client ID** (if prompted, configure the consent screen first)
3. Choose **Web application**
4. Set:
   - **Name**: anything (e.g., `MyApp via AuthGate`)
   - **Authorized redirect URIs**: `{BASE_URL}{GOOGLE_REDIRECT_PATH}` (e.g. `http://localhost:8000/auth/google/callback`)
5. Click **Create**
6. Copy the **Client ID** and **Client secret** from the modal
7. Add them to your environment:
   ```bash
   export GOOGLE_CLIENT_ID=your_client_id
   export GOOGLE_CLIENT_SECRET=your_client_secret
   ```

### YAML config

```yaml
connectors:
  - type: google
    id: google
    name: Google
    config:
      clientID: $GOOGLE_CLIENT_ID
      clientSecret: $GOOGLE_CLIENT_SECRET
      redirectPath: /auth/google/callback
```

### Scopes requested
`openid email profile` — Google's standard OIDC scopes.

## GitLab

Works with **gitlab.com** (default) or self-hosted GitLab instances.

1. Go to **User Settings → [Applications](https://gitlab.com/-/user_settings/applications)** (or `/profile/applications` on self-hosted)
2. Fill in:
   - **Name**: anything (e.g., `MyApp via AuthGate`)
   - **Redirect URI**: `{BASE_URL}{GITLAB_REDIRECT_PATH}` (e.g. `http://localhost:8000/auth/gitlab/callback`)
   - **Scopes**: check only `read_user`
3. Click **Save application**
4. Copy the **Application ID** (Client ID) and **Secret** (Client Secret)
5. Add them to your environment:
   ```bash
   export GITLAB_CLIENT_ID=your_client_id
   export GITLAB_CLIENT_SECRET=your_client_secret
   ```

### YAML config

```yaml
connectors:
  - type: gitlab
    id: gitlab
    name: GitLab
    config:
      clientID: $GITLAB_CLIENT_ID
      clientSecret: $GITLAB_CLIENT_SECRET
      redirectPath: /auth/gitlab/callback
      baseUrl: https://gitlab.com       # change for self-hosted GitLab
```

### Self-hosted GitLab

Set `baseUrl` to your instance's URL:

```yaml
config:
  baseUrl: https://gitlab.yourcompany.com
```

## Auto-detection vs explicit enable

If you don't set `ENABLED_PROVIDERS`, AuthGate auto-detects providers based on whether their credentials are present. Only connectors with both `clientID` AND `clientSecret` populated appear on the login page.

To force a specific set regardless of credential presence, set:

```bash
ENABLED_PROVIDERS=github,google
```

This is useful if you want to temporarily disable a provider without removing its credentials.
