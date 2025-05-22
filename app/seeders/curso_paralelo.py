# app/seeders/curso_paralelo.py

from app.models.curso import Curso
from app.models.paralelo import Paralelo
from app.models.curso_paralelo import CursoParalelo
from app.extensions import db

def seed_curso_paralelo():
    if not CursoParalelo.query.first():
        curso_paralelo = []

        cursos = Curso.query.all()
        paralelos = Paralelo.query.all()

        for curso in cursos:
            if "Primaria" in curso.nombre:
                for paralelo in paralelos:
                    if paralelo.nombre in ["A", "B", "C"]:
                        curso_paralelo.append(CursoParalelo(curso_id=curso.id, paralelo_id=paralelo.id))
            elif "Secundaria" in curso.nombre:
                for paralelo in paralelos:
                    if paralelo.nombre in ["A", "B"]:
                        curso_paralelo.append(CursoParalelo(curso_id=curso.id, paralelo_id=paralelo.id))

        db.session.add_all(curso_paralelo)
        db.session.commit()
        print("✅ Relaciones Curso-Paralelo insertadas.")
    else:
        print("ℹ️ Ya existen relaciones Curso-Paralelo en la tabla.")