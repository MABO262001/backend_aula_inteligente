import os

class Config:
    DB_CHOICE = os.getenv("DB_CHOICE", "postgresql")
    DB_USER = os.getenv("DB_USER", "user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "mydb")

    SQLALCHEMY_DATABASE_URI = (
        f"{DB_CHOICE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/app/uploads")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
