from urllib.parse import urlencode

import httpx

from app.config import settings
from app.oauth.base import OAuthProvider, OAuthUser


class GitHubOAuth(OAuthProvider):
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_URL = "https://api.github.com/user"
    EMAILS_URL = "https://api.github.com/user/emails"

    def get_authorize_url(self, state: str, redirect_uri: str) -> str:
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "user:email",
            "state": state,
        }
        return f"{self.AUTHORIZE_URL}?{urlencode(params)}"

    async def get_token(self, code: str, redirect_uri: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            return resp.json()["access_token"]

    async def get_user(self, token: str) -> OAuthUser:
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.USER_URL, headers=headers)
            data = resp.json()

            email = data.get("email")
            if not email:
                emails_resp = await client.get(self.EMAILS_URL, headers=headers)
                emails = emails_resp.json()
                primary = next(
                    (e for e in emails if e.get("primary")),
                    emails[0] if emails else None,
                )
                email = primary["email"] if primary else ""

            return OAuthUser(
                id=str(data["id"]),
                email=email,
                name=data.get("name") or data.get("login", ""),
                avatar_url=data.get("avatar_url", ""),
            )
