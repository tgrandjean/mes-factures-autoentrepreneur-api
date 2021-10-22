import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_PATH = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_PATH / '.dotenv')


DEBUG = True


APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')


CORS_SETTINGS = {
    "origins": [
        os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    ],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["*"]
}


SECRET = os.environ.get('SECRET', 'SECRET')


DATABASES = {
    'mongodb': {
        "host": os.environ.get('DATABASE.HOST', 'db'),
        "port": os.environ.get('DATABASE.PORT', '27017'),
        "user": os.environ.get('DATABASE.USER', 'admin'),
        "password": os.environ.get('DATABASE.PASSWORD', 'password'),
        "url": "mongodb://{user}:{password}@{host}:{port}",
        "database_name": "mes-factures-autoentrepreneur"
    }
}


BEANIE_DOCUMENTS = [
    "app.core.documents.Invoice"
]

JWT_TOKEN_LIFETIME = os.environ.get('JWT_TOKEN_LIFETIME', 10)

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")


SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_EMAIL_SEND_URL = os.environ.get("SENDGRID_EMAIL_SEND_URL")
SENDGRID_FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL")
