from fastapi import APIRouter
from .auth import jwt_authentication


def get_users_router(app):
    users_router = APIRouter()

    users_router.include_router(
        app.fastapi_users.get_auth_router(jwt_authentication),
        prefix='/auth/jwt',
        tags=['auth']
    )

    users_router.include_router(
        app.fastapi_users.get_register_router(),
        prefix='/auth', tags=['auth']
    )

    users_router.include_router(
        app.fastapi_users.get_reset_password_router(),
        prefix="/auth", tags=['auth']
    )

    users_router.include_router(
        app.fastapi_users.get_verify_router(),
        prefix="/auth", tags=['auth']
    )

    users_router.include_router(
        app.fastapi_users.get_users_router(),
        prefix="/users",
        tags=['users']
    )

    return users_router
# current_active_user = fastapi_users.current_user(active=True)
