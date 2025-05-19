# app/seeders/user_seeder.py

from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash

def seed_users():
    if not User.query.first():
        users = [
            User(
                name="Miguel Angel Ballivian Ocampo",
                email="ballivian02@gmail.com",
                password=generate_password_hash("123456789"),
                photo_url=None,
                photo_storage=None,
                status=True,
                rol_id=1  # Asumiendo que el primer rol es Administrador
            ),
            User(
                name="Angel Ocampo",
                email="mabo2@mail.com",
                password=generate_password_hash("123456"),
                photo_url=None,
                photo_storage=None,
                status=False,
                rol_id=2  # Profesor
            ),
            User(
                name="Miguel Ballivian",
                email="miguel@mail.com",
                password=generate_password_hash("123456"),
                photo_url=None,
                photo_storage=None,
                status=True,
                rol_id=3  # Estudiante
            )
        ]
        db.session.add_all(users)
        db.session.commit()
        print("✅ Usuarios de prueba insertados.")
    else:
        print("ℹ️ Ya existen usuarios en la tabla.")
