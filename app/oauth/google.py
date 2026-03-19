from urllib.parse import urlencode

import httpx

from app.config import settings
from app.oauth.base import OAuthProvider, OAuthUser


class GoogleOAuth(OAuthProvider):
    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def get_authorize_url(self, state: str, redirect_uri: str) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{self.AUTHORIZE_URL}?{urlencode(params)}"

    async def get_token(self, code: str, redirect_uri: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
            )
            return resp.json()["access_token"]

    async def get_user(self, token: str) -> OAuthUser:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self.USER_URL, headers={"Authorization": f"Bearer {token}"}
            )
            data = resp.json()
            return OAuthUser(
                id=data["id"],
                email=data["email"],
                name=data.get("name", ""),
                avatar_url=data.get("picture", ""),
            )
