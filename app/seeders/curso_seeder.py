# app/seeders/curso_seeder.py

from app.models.curso import Curso
from app.extensions import db

def seed_cursos():
    if not Curso.query.first():
        cursos = []

        # Cursos de primaria
        for i in range(1, 7):
            cursos.append(Curso(nombre=f"{i}° de Primaria"))

        # Cursos de secundaria
        for i in range(1, 7):
            cursos.append(Curso(nombre=f"{i}° de Secundaria"))

        db.session.add_all(cursos)
        db.session.commit()
        print("✅ Cursos insertados.")
    else:
        print("ℹ️ Ya existen cursos en la tabla.")