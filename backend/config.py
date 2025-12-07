"""
from decouple import config
from dotenv import load_dotenv

load_dotenv()


DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT", cast=int)
DB_NAME = config("DB_NAME")

DB_USERNAME = config("DB_USERNAME")
DB_PASSWORD = config("DB_PASSWORD")

SECRET_KEY = config("SECRET_KEY")
JWT_EXPIRE_MINUTES = config("JWT_EXPIRE_MINUTES", cast=int, default=1440)
TG_BOT_TOKEN = config("TG_BOT_TOKEN")

"""

import os

from decouple import config
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "hackathon")


API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
