# app/seeders/rol_seeder.py

from app.models.rol import Rol
from app.extensions import db

def seed_roles():
    if not Rol.query.first():
        roles = [
            Rol(nombre="Administrador"),
            Rol(nombre="Profesor"),
            Rol(nombre="Estudiante"),
            Rol(nombre="Apoderado")
        ]
        db.session.add_all(roles)
        db.session.commit()
        print("✅ Roles insertados.")
    else:
        print("ℹ️ Ya existen roles en la tabla.")
