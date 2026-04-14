---
title: API Reference
description: AuthGate HTTP endpoints — verify, userinfo, JWKS, login, logout, health.
---

## Endpoints at a glance

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/login` | `GET` | Branded login page (pass `?redirect_url=...`) |
| `/auth/{provider}` | `GET` | Start OAuth flow (`github`, `google`, `gitlab`) |
| `{PROVIDER_REDIRECT_PATH}` | `GET` | OAuth callback — path set per connector in config |
| `/api/verify` | `GET` | Verify JWT — always `200 OK`, returns `{ valid, user }` |
| `/api/userinfo` | `GET` | Get authenticated user profile — `401` if invalid/missing token |
| `/.well-known/jwks.json` | `GET` | Public keys for local JWT verification |
| `/logout` | `GET` | Clear auth cookie, redirect to `?redirect_url=...` |
| `/health` | `GET` | Health check |

**Authentication**: Pass token as `Authorization: Bearer <token>` header OR via the `authgate_token` cookie. Most endpoints accept either.

## `/login`

Renders the branded login page. Supports these query params:

| Param | Purpose |
|---|---|
| `redirect_url` | Where to redirect after successful auth (must match `allowedRedirects`) |
| `theme` | `light` or `dark` — overrides `app.defaultTheme` for this request |
| `error` | Error code to display (set by AuthGate on failure redirects) |

## `/auth/{provider}`

Starts the OAuth flow for the given provider. Supported values: `github`, `google`, `gitlab` (only enabled ones work).

Optional query params:
- `redirect_url` — propagated through OAuth state so the final redirect hits your app

This endpoint issues a redirect to the provider's authorization URL. It's invoked by the login page's provider buttons — you normally don't call it directly.

## `/api/verify`

Validates a JWT and returns the user profile (if valid).

**Request:**

```bash
curl -H "Authorization: Bearer eyJhbG..." https://auth.example.com/api/verify
```

**Success (HTTP `200 OK`):**

```json
{
  "valid": true,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "Jane Doe",
    "avatar_url": "https://avatars.githubusercontent.com/u/12345",
    "providers": ["github", "google"],
    "created_at": "2026-04-01T12:34:56+00:00",
    "last_login_at": "2026-04-10T09:15:22+00:00"
  }
}
```

**Failure** (missing, expired, tampered token, or user disabled) — also `200 OK`:

```json
{ "valid": false, "user": null }
```

:::note
`/api/verify` **always returns `200 OK`** — check the `valid` boolean, not the status code. Verification is a read, not an auth-gated action, so status codes carry no auth signal. Use `/api/userinfo` if you want a true auth-gated endpoint that returns `401` on failure.
:::

### `user.providers` — most-recently-linked first

The `providers` array lists all OAuth identities linked to this user, **ordered by most recently used**. Example: `["github", "google"]` means the user last signed in with GitHub, but also linked Google previously.

## `/api/userinfo`

Returns the authenticated user's profile. Auth-gated — returns `401 Unauthorized` on failure.

**Request:**

```bash
curl -H "Authorization: Bearer eyJhbG..." https://auth.example.com/api/userinfo
```

**Success (HTTP `200 OK`):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "Jane Doe",
  "avatar_url": "https://avatars.githubusercontent.com/u/12345",
  "providers": ["github"],
  "created_at": "2026-04-01T12:34:56+00:00",
  "last_login_at": "2026-04-10T09:15:22+00:00"
}
```

**Failure** (HTTP `401 Unauthorized`):

```json
{ "detail": "Not authenticated" }
```

```json
{ "detail": "Invalid token" }
```

```json
{ "detail": "User not found" }
```

## `/.well-known/jwks.json`

Returns the public JWKS (JSON Web Key Set) for local JWT verification.

**Request:**

```bash
curl https://auth.example.com/.well-known/jwks.json
```

**Response:**

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "abc123...",
      "n": "<base64url-encoded modulus>",
      "e": "AQAB"
    }
  ]
}
```

Use your language's JWT library to verify tokens locally without calling AuthGate per request. See the [Integration Guide](/authgate/integration/#option-b-validate-locally-using-jwks) for language-specific examples.

## `/logout`

Clears the `authgate_token` cookie and redirects to the URL in `?redirect_url=...`.

```
GET https://auth.example.com/logout?redirect_url=https://app.example.com
```

Returns a `302` redirect. Your app should also clear any session cookies it set independently.

## `/health`

Simple health check for Kubernetes liveness/readiness probes and monitoring.

```bash
curl https://auth.example.com/health
```

```json
{
  "status": "ok",
  "service": "AuthGate",
  "version": "1.0.0"
}
```

Always returns `200 OK` if the process is running. Doesn't verify database connectivity — use a dedicated readiness check if you need that guarantee.

## OAuth flow failure errors

When OAuth flow fails, AuthGate redirects to `/login?error=<code>` and the login page renders a friendly alert. Possible codes:

| `?error=` | When |
|---|---|
| `invalid_provider` | Provider not enabled in config |
| `missing_redirect_path` | Connector is enabled but `redirectPath` is missing |
| `invalid_redirect` | `redirect_url` doesn't match any `allowedRedirects` pattern |
| `missing_params` | OAuth callback arrived without `code` or `state` |
| `invalid_state` | State token expired (10 min TTL) or tampered |
| `provider_error` | OAuth token or user fetch failed |
| `no_email` | Provider didn't return an email address |
| `access_denied` | User clicked "deny" on the consent screen |
| `account_disabled` | User account is disabled (`is_active = false`) |
