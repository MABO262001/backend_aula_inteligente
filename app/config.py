import os

class Config:
    DB_CHOICE = os.getenv("DB_CHOICE", "postgresql")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "262001")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "aula_inteligente")

    SQLALCHEMY_DATABASE_URI = (
        f"{DB_CHOICE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/app/uploads")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), 'uploads'))
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super_secret_key")
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = False  # o timedelta(minutes=30) para que expire