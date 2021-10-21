from fastapi_users import FastAPIUsers
from .dependencies import get_user_manager
from .models import User, UserCreate, UserUpdate, UserDB
from .auth_methods import jwt_authentication

fastapi_users = FastAPIUsers(
    get_user_manager,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

current_active_user = fastapi_users.current_user(active=True)
