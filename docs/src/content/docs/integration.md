---
title: Integration Guide
description: Wire AuthGate into your existing app's auth flow.
---

AuthGate is a **sidecar auth service**. Your app stays auth-unaware — it just checks for a JWT on incoming requests and redirects to AuthGate when missing.

## How it works

```
┌────────────┐     1. redirect     ┌────────────┐
│  Your App  │ ──────────────────→ │  AuthGate  │
│            │                     │            │
│            │  4. redirect back   │  /login    │
│            │ ←────────────────── │  (branded) │
│            │    with JWT token   │            │
└────────────┘                     └──────┬─────┘
                                          │ 2. OAuth
                                          ↓
                                    ┌───────────┐
                                    │  GitHub / │
                                    │  Google / │
                                    │  GitLab   │
                                    └───────────┘
                                    3. callback
```

1. User visits your app without a session.
2. Your app redirects them to `auth.example.com/login?redirect_url=...`.
3. User picks a provider, completes OAuth consent.
4. AuthGate issues a JWT and redirects back to your `redirect_url` with `?token=...`.
5. Your app verifies the JWT (via `/api/verify` or local JWKS) and treats the request as authenticated.

## Step 1: Redirect unauthenticated users

When a user visits your app without a valid session, redirect them:

```
https://auth.example.com/login?redirect_url=https://app.example.com/dashboard
```

**Important**: the `redirect_url` must match one of the glob patterns in `server.allowedRedirects`. If it doesn't, AuthGate redirects to `/login?error=invalid_redirect` — a security feature to prevent open redirects.

### Per-request theme preference

Append `?theme=light` or `?theme=dark` to sync the login page with your app's current theme:

```javascript
const theme = document.documentElement.getAttribute("data-theme") === "dark"
  ? "dark"
  : "light";
const authUrl = `https://auth.example.com/login?redirect_url=${encodeURIComponent(currentUrl)}&theme=${theme}`;
window.location.href = authUrl;
```

## Step 2: Receive the token

After authentication, AuthGate redirects back to your `redirect_url` with the JWT appended:

```
https://app.example.com/dashboard?token=eyJhbG...
```

If this is the user's **first sign-in**, AuthGate additionally appends `&new_user=true`:

```
https://app.example.com/dashboard?token=eyJhbG...&new_user=true
```

This lets your app trigger first-time flows — onboarding wizards, welcome emails, analytics events — exactly once. The param is absent on subsequent logins.

:::note
`new_user=true` is a **UX signal**, not a security claim. It's not cryptographically signed. Use it for things like "show the welcome banner", not for security-critical logic.
:::

AuthGate also sets an HttpOnly cookie named `authgate_token` — useful when your app and AuthGate share a domain (e.g., both under `*.example.com`).

## Step 3: Verify the token

Two options. Pick based on whether you want network round-trips.

### Option A: Call `/api/verify`

Simplest for low-traffic apps.

```bash
curl -H "Authorization: Bearer <token>" https://auth.example.com/api/verify
```

Always returns `200 OK` with a JSON body:

```json
{ "valid": true, "user": { "email": "jane@example.com", ... } }
```

or

```json
{ "valid": false, "user": null }
```

See [API Reference](/authgate/api-reference/) for the full response schema.

### Option B: Validate locally using JWKS

Faster — no network call per request. Fetch the public keys once, cache them, verify tokens locally.

```bash
curl https://auth.example.com/.well-known/jwks.json
```

Returns:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "abc123...",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

Use your language's JWT library with JWKS support to verify. Examples:

**Node.js** (using `jose`):

```javascript
import { createRemoteJWKSet, jwtVerify } from 'jose';

const JWKS = createRemoteJWKSet(new URL('https://auth.example.com/.well-known/jwks.json'));

async function verifyToken(token) {
  const { payload } = await jwtVerify(token, JWKS, {
    issuer: 'authgate',
  });
  return payload; // { sub, email, name, provider, iat, exp, iss }
}
```

**Python** (using `pyjwt`):

```python
import jwt
from jwt import PyJWKClient

jwks_client = PyJWKClient("https://auth.example.com/.well-known/jwks.json")

def verify_token(token: str) -> dict:
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer="authgate",
    )
```

**Go** (using `github.com/lestrrat-go/jwx`):

```go
import "github.com/lestrrat-go/jwx/v2/jwk"
import "github.com/lestrrat-go/jwx/v2/jwt"

jwks, _ := jwk.Fetch(ctx, "https://auth.example.com/.well-known/jwks.json")
parsedToken, err := jwt.ParseString(token,
    jwt.WithKeySet(jwks),
    jwt.WithIssuer("authgate"),
)
```

### Which option to pick?

| | **Option A (`/api/verify`)** | **Option B (JWKS)** |
|---|---|---|
| **Latency** | +1 network RTT per request | ~0 (local verify) |
| **Correctness** | Always reflects latest user state (disabled users blocked immediately) | Cached keys — disabled users still valid until token expires |
| **Dependency** | App must reach AuthGate per request | App only needs JWKS refreshed occasionally |
| **Scaling** | AuthGate load scales with app traffic | AuthGate load is minimal |

**Recommendation:** use **Option B** for most apps — it's faster and more resilient. Use **Option A** only if you need immediate propagation of user-state changes (e.g., disabling a user should lock them out right away).

## Sign out

To sign a user out, clear your own session cookie AND clear AuthGate's cookie:

```
https://auth.example.com/logout?redirect_url=https://app.example.com
```

AuthGate clears the `authgate_token` cookie and redirects to the URL you specify.
