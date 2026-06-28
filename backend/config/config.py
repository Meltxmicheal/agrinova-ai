import os
import datetime
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "agrinova-secret-key")
    JWT_SECRET_KEY = os.getenv("SECRET_KEY", "agrinova-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Max upload size: 16MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024