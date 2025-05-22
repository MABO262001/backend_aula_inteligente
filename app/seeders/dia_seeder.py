# app/seeders/dia_seeder.py

from app.models.dia import Dia
from app.extensions import db

def seed_dias():
    if not Dia.query.first():
        dias = [
            Dia(nombre="Lunes"),
            Dia(nombre="Martes"),
            Dia(nombre="Miércoles"),
            Dia(nombre="Jueves"),
            Dia(nombre="Viernes"),
            Dia(nombre="Sábado"),
            Dia(nombre="Domingo")
        ]
        db.session.add_all(dias)
        db.session.commit()
        print("✅ Días insertados.")
    else:
        print("ℹ️ Ya existen días en la tabla.")