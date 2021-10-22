from typing import Optional
from fastapi import Request
from fastapi_users import BaseUserManager
from app import settings
from .models import UserCreate, UserDB
from .background_tasks import send_mail


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET

    async def on_after_register(self,
                                user: UserDB,
                                request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} forgot password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        print(f"Verification {user.id}. Verification token: {token}")
        content = f'Token:\n {token}'
        if not settings.DEBUG:
            await send_mail(user.email, "Vérification d'adress email", content)
