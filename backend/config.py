import os
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from .env if present

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    JWT_SECRET = os.getenv("JWT_SECRET", "default_jwt_secret")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/nomad_db")

config = Config()
