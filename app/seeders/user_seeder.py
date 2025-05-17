from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash

def seed_users():
    if not User.query.first():
        users = [
            User(
                name="MABO262001",
                email="ballivian02@gmail.com",
                password=generate_password_hash("123456789"),
                photo_url=None,
                photo_storage=None,
                status=True
            ),
            User(
                name="MABO",
                email="mabo2@mail.com",
                password=generate_password_hash("123456"),
                photo_url=None,
                photo_storage=None,
                status=False
            ),
            User(
                name="migueldev",
                email="miguel@mail.com",
                password=generate_password_hash("123456"),
                photo_url=None,
                photo_storage=None,
                status=True
            )
        ]
        db.session.add_all(users)
        db.session.commit()
        print("✅ Usuarios de prueba insertados.")
    else:
        print("ℹ️ Ya existen usuarios en la tabla.")
