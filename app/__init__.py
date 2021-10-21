from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from beanie import init_beanie

from app import settings
from app.db import client
from app.users.routers import fastapi_users
from app.users.auth_methods import jwt_authentication


MONGO_SETTINGS = settings.DATABASES['mongodb']

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_SETTINGS['origins'],
    allow_methods=settings.CORS_SETTINGS['allow_methods'],
    allow_headers=settings.CORS_SETTINGS['allow_headers'],
    expose_headers=settings.CORS_SETTINGS['expose_headers']
)


@app.get('/')
async def root():
    """Home"""
    docs_url = settings.APP_URL + '/docs/'
    msg = "Hello check out the docs %s" % docs_url
    return {"message": msg}


app.include_router(
    fastapi_users.get_auth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(),
    prefix="/users",
    tags=["users"]
)


@app.on_event("startup")
async def app_init():
    await init_beanie(database=client[MONGO_SETTINGS['database_name']],
                      document_models=settings.BEANIE_DOCUMENTS)
