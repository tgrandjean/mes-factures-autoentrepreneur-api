import motor.motor_asyncio
from app.settings import DATABASES

MONGO_SETTINGS = DATABASES['mongodb']

DATABASE_URL = MONGO_SETTINGS['url'].format(**MONGO_SETTINGS)
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
