from app.models.materia import Materia
from app.extensions import db

def seed_materias():
    if not Materia.query.first():
        materias = [
            # Primaria
            Materia(sigla="PRI-101", nombre="Lenguaje y Comunicación"),
            Materia(sigla="PRI-102", nombre="Matemáticas"),
            Materia(sigla="PRI-103", nombre="Ciencias Naturales"),
            Materia(sigla="PRI-104", nombre="Ciencias Sociales"),
            Materia(sigla="PRI-105", nombre="Educación Física"),
            Materia(sigla="PRI-106", nombre="Educación Artística"),
            Materia(sigla="PRI-107", nombre="Educación Cívica"),
            Materia(sigla="PRI-108", nombre="Tecnología"),
            Materia(sigla="PRI-109", nombre="Educación Musical"),
            Materia(sigla="PRI-110", nombre="Valores"),

            # Secundaria
            Materia(sigla="SEC-201", nombre="Lengua y Literatura"),
            Materia(sigla="SEC-202", nombre="Matemática"),
            Materia(sigla="SEC-203", nombre="Física"),
            Materia(sigla="SEC-204", nombre="Química"),
            Materia(sigla="SEC-205", nombre="Biología"),
            Materia(sigla="SEC-206", nombre="Historia"),
            Materia(sigla="SEC-207", nombre="Geografía"),
            Materia(sigla="SEC-208", nombre="Educación Física"),
            Materia(sigla="SEC-209", nombre="Educación Artística"),
            Materia(sigla="SEC-210", nombre="Filosofía"),
            Materia(sigla="SEC-211", nombre="Psicología"),
            Materia(sigla="SEC-212", nombre="Sociología"),
            Materia(sigla="SEC-213", nombre="Tecnología"),
            Materia(sigla="SEC-214", nombre="Inglés"),
            Materia(sigla="SEC-215", nombre="Computación")
        ]

        db.session.add_all(materias)
        db.session.commit()
        print("✅ Materias de primaria y secundaria insertadas.")
    else:
        print("ℹ️ Ya existen materias en la tabla.")
