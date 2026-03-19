from urllib.parse import urlencode

import httpx

from app.config import settings
from app.oauth.base import OAuthProvider, OAuthUser


class GitLabOAuth(OAuthProvider):
    def __init__(self):
        base = settings.GITLAB_BASE_URL.rstrip("/")
        self.authorize_url = f"{base}/oauth/authorize"
        self.token_url = f"{base}/oauth/token"
        self.user_url = f"{base}/api/v4/user"

    def get_authorize_url(self, state: str, redirect_uri: str) -> str:
        params = {
            "client_id": settings.GITLAB_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "read_user",
            "state": state,
        }
        return f"{self.authorize_url}?{urlencode(params)}"

    async def get_token(self, code: str, redirect_uri: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.token_url,
                data={
                    "client_id": settings.GITLAB_CLIENT_ID,
                    "client_secret": settings.GITLAB_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
            )
            return resp.json()["access_token"]

    async def get_user(self, token: str) -> OAuthUser:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self.user_url, headers={"Authorization": f"Bearer {token}"}
            )
            data = resp.json()
            return OAuthUser(
                id=str(data["id"]),
                email=data.get("email", ""),
                name=data.get("name") or data.get("username", ""),
                avatar_url=data.get("avatar_url", ""),
            )
