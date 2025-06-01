import json
from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash
import random

def generate_unique_email(name, existing_emails):
    base_email = name.lower().replace(" ", ".")
    email = f"{base_email}@gmail.com"
    counter = 1

    while email in existing_emails:
        email = f"{base_email}{counter:02}@gmail.com"
        counter += 1

    existing_emails.add(email)
    return email

def seed_users():
    if not User.query.first():
        users = []
        existing_emails = set()
        user_counter = 1

        with open('fakerApi.json', 'r', encoding='utf-8') as file:
            names_data = json.load(file)

        predefined_users = [
            {
                "name": "MABO262001",
                "email": "ballivian02@gmail.com",
                "password": "123456789",
                "status": True,
                "rol_id": 1
            },
            {
                "name": "Antonio Bravo Vieira",
                "email": "bravo02@gmail.com",
                "password": "123456789",
                "status": True,
                "rol_id": 1
            },
            {
                "name": "Helen Baldelomar",
                "email": "helendiyhana03@gmail.com",
                "password": "123456789",
                "status": False,
                "rol_id": 1
            },
            {
                "name": "Briyidt Araceli",
                "email": "Araceli@mail.com",
                "password": "123456",
                "status": True,
                "rol_id": 3
            }
        ]

        for user_data in predefined_users:
            users.append(User(
                name=user_data["name"],
                email=user_data["email"],
                password=generate_password_hash(user_data["password"]),
                photo_url=None,
                photo_storage=None,
                status=user_data["status"],
                rol_id=user_data["rol_id"]
            ))
            existing_emails.add(user_data["email"])

        roles = {
            1: 7,    # Administradores
            2: 5,   # Profesores
            3: 400, # Estudiantes
            4: 13   # Apoderados
        }

        for rol_id, count in roles.items():
            for _ in range(count):

                name_data = names_data[(user_counter - 1) % len(names_data)]
                name = f"{name_data['first_name']} {name_data['last_name']}_{user_counter}"
                email = generate_unique_email(name, existing_emails)
                users.append(User(
                    name=name,
                    email=email,
                    password=generate_password_hash("123456789"),
                    photo_url=None,
                    photo_storage=None,
                    status=True,
                    rol_id=rol_id
                ))
                user_counter += 1

                if len(users) >= 500:
                    db.session.add_all(users)
                    db.session.commit()
                    users = []

        if users:
            db.session.add_all(users)
            db.session.commit()

        print("✅ Usuarios de prueba y generados al azar insertados.")
    else:
        print("ℹ️ Ya existen usuarios en la tabla.")