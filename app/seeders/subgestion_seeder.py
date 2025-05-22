# app/seeders/subgestion_seeder.py

from app.models.subgestion import Subgestion
from app.models.gestion import Gestion
from app.extensions import db
from datetime import date

def seed_subgestiones():
    if not Subgestion.query.first():
        subgestiones = []

        gestiones = Gestion.query.all()

        for gestion in gestiones:
            anio = int(gestion.nombre)

            if anio % 2 == 0:
                subgestiones.append(Subgestion(
                    nombre="1er Trimestre",
                    fecha_inicio=date(anio, 1, 1),
                    fecha_final=date(anio, 3, 31),
                    gestion_id=gestion.id
                ))
                subgestiones.append(Subgestion(
                    nombre="2do Trimestre",
                    fecha_inicio=date(anio, 4, 1),
                    fecha_final=date(anio, 6, 30),
                    gestion_id=gestion.id
                ))
                subgestiones.append(Subgestion(
                    nombre="3er Trimestre",
                    fecha_inicio=date(anio, 7, 1),
                    fecha_final=date(anio, 9, 30),
                    gestion_id=gestion.id
                ))
            else:
                subgestiones.append(Subgestion(
                    nombre="1er Semestre",
                    fecha_inicio=date(anio, 1, 1),
                    fecha_final=date(anio, 6, 30),
                    gestion_id=gestion.id
                ))
                subgestiones.append(Subgestion(
                    nombre="2do Semestre",
                    fecha_inicio=date(anio, 7, 1),
                    fecha_final=date(anio, 12, 31),
                    gestion_id=gestion.id
                ))

        db.session.add_all(subgestiones)
        db.session.commit()
        print("✅ Subgestiones insertadas.")
    else:
        print("ℹ️ Ya existen subgestiones en la tabla.")