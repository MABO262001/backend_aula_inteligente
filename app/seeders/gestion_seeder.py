# app/seeders/gestion_seeder.py
from app.models.gestion import Gestion
from app.extensions import db

DEFAULT_DESDE = 2020
DEFAULT_HASTA = 2025

def seed_gestion(desde=DEFAULT_DESDE, hasta=DEFAULT_HASTA):
    if not Gestion.query.first():
        gestiones = []

        for anio in range(desde, hasta + 1):
            gestiones.append(Gestion(nombre=str(anio)))

        db.session.add_all(gestiones)
        db.session.commit()
        print(f"✅ Gestiones desde {desde} hasta {hasta} insertadas.")
    else:
        print("ℹ️ Ya existen gestiones en la tabla.")