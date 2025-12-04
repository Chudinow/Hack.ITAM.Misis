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
