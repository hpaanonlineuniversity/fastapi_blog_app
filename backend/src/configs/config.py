import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DBNAME = os.getenv("MONGO_DBNAME")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
JWT_SECRET = os.getenv("JWT_SECRET")

USERNAME = os.getenv("USERNAME")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")