# app/seeders/gestion_curso_paralelo.py

from app.models.gestion import Gestion
from app.models.curso_paralelo import CursoParalelo
from app.models.gestion_curso_paralelo import GestionCursoParalelo
from app.extensions import db

def seed_gestion_curso_paralelo():
    if not GestionCursoParalelo.query.first():
        gestion_curso_paralelo = []

        gestiones = Gestion.query.all()
        cursos_paralelo = CursoParalelo.query.all()

        for gestion in gestiones:
            for curso_paralelo in cursos_paralelo:
                gestion_curso_paralelo.append(
                    GestionCursoParalelo(
                        gestion_id=gestion.id,
                        curso_paralelo_id=curso_paralelo.id
                    )
                )

        db.session.add_all(gestion_curso_paralelo)
        db.session.commit()
        print("✅ Relaciones Gestión-Curso-Paralelo insertadas.")
    else:
        print("ℹ️ Ya existen relaciones Gestión-Curso-Paralelo en la tabla.")