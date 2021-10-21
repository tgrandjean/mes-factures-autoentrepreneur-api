from fastapi import Depends
from fastapi_users.db import MongoDBUserDatabase

from app import settings
from app.db import client
from .models import UserDB
from .managers import UserManager


MONGO_SETTINGS = settings.DATABASES['mongodb']

db = client[MONGO_SETTINGS['database_name']]
collection = db['users']


def get_user_db():
    yield MongoDBUserDatabase(UserDB, collection)


def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
