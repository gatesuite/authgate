from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class OAuthUser:
    id: str
    email: str
    name: str
    avatar_url: str


class OAuthProvider(ABC):
    @abstractmethod
    def get_authorize_url(self, state: str, redirect_uri: str) -> str: ...

    @abstractmethod
    async def get_token(self, code: str, redirect_uri: str) -> str: ...

    @abstractmethod
    async def get_user(self, token: str) -> OAuthUser: ...
