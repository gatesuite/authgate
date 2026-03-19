from datetime import datetime

from pydantic import BaseModel


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str
    provider: str
    created_at: datetime
    last_login_at: datetime


class TokenVerifyResponse(BaseModel):
    valid: bool
    user: UserInfo | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
