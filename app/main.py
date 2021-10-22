from fastapi import FastAPI, Depends
from fastapi_users import FastAPIUsers
from fastapi_users.db import MongoDBUserDatabase
from beanie import init_beanie
import motor.motor_asyncio

from app import settings
from app.settings import DATABASES
from app.users.models import User, UserCreate, UserUpdate, UserDB
from app.users.auth import jwt_authentication
from app.users.routers import get_users_router
from app.users.managers import UserManager

from app.core.routers import get_core_router

app = FastAPI()


@app.on_event("startup")
async def app_init():
    MONGO_SETTINGS = DATABASES['mongodb']
    DB_NAME = MONGO_SETTINGS['database_name']
    DATABASE_URL = MONGO_SETTINGS['url'].format(**MONGO_SETTINGS)
    app.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(
        DATABASE_URL, uuidRepresentation="standard"
    )

    app.db = app.mongodb_client[DB_NAME]

    await init_beanie(database=app.mongodb_client[DB_NAME],
                      document_models=settings.BEANIE_DOCUMENTS)

    def get_user_db():
        yield MongoDBUserDatabase(UserDB, app.db['users'])

    app.get_user_db = get_user_db

    def get_user_manager(user_db=Depends(app.get_user_db)):
        yield UserManager(user_db)

    app.get_user_manager = get_user_manager

    app.fastapi_users = FastAPIUsers(
        get_user_manager,
        [jwt_authentication],
        User,
        UserCreate,
        UserUpdate,
        UserDB,
    )

    app.current_active_user = app.fastapi_users.current_user(active=True)

    app.include_router(get_users_router(app))
    app.include_router(get_core_router(app), prefix='/v1')


@app.on_event("shutdown")
async def shutdown_app():
    app.mongodb_client.close()
