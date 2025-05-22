# app/seeders/paralelo_seeder.py

from app.models.paralelo import Paralelo
from app.extensions import db

def seed_paralelos():
    if not Paralelo.query.first():
        paralelos = [
            Paralelo(nombre="A"),
            Paralelo(nombre="B"),
            Paralelo(nombre="C")
        ]

        db.session.add_all(paralelos)
        db.session.commit()
        print("✅ Paralelos insertados.")
    else:
        print("ℹ️ Ya existen paralelos en la tabla.")