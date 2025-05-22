# app/seeders/materia_seeder.py

from app.models.materia import Materia
from app.extensions import db

def seed_materias():
    if not Materia.query.first():
        materias = [
            Materia(sigla="INF-101", nombre="Introducción a la Programación"),
            Materia(sigla="INF-102", nombre="Estructuras de Datos"),
            Materia(sigla="INF-103", nombre="Bases de Datos I"),
            Materia(sigla="INF-104", nombre="Sistemas Operativos"),
            Materia(sigla="INF-105", nombre="Redes de Computadoras"),
            Materia(sigla="INF-106", nombre="Ingeniería de Software I"),
            Materia(sigla="INF-107", nombre="Programación Orientada a Objetos"),
            Materia(sigla="INF-108", nombre="Arquitectura de Computadoras"),
            Materia(sigla="INF-109", nombre="Matemáticas Discretas"),
            Materia(sigla="INF-110", nombre="Cálculo I"),
            Materia(sigla="INF-111", nombre="Cálculo II"),
            Materia(sigla="INF-112", nombre="Álgebra Lineal"),
            Materia(sigla="INF-113", nombre="Probabilidad y Estadística"),
            Materia(sigla="INF-114", nombre="Bases de Datos II"),
            Materia(sigla="INF-115", nombre="Desarrollo Web"),
            Materia(sigla="INF-116", nombre="Inteligencia Artificial"),
            Materia(sigla="INF-117", nombre="Minería de Datos"),
            Materia(sigla="INF-118", nombre="Seguridad Informática"),
            Materia(sigla="INF-119", nombre="Gestión de Proyectos"),
            Materia(sigla="INF-120", nombre="Sistemas Distribuidos"),
            Materia(sigla="INF-121", nombre="Programación Funcional"),
            Materia(sigla="INF-122", nombre="Programación Paralela"),
            Materia(sigla="INF-123", nombre="Computación Gráfica"),
            Materia(sigla="INF-124", nombre="Teoría de la Computación"),
            Materia(sigla="INF-125", nombre="Compiladores"),
            Materia(sigla="INF-126", nombre="Métodos Numéricos"),
            Materia(sigla="INF-127", nombre="Modelado y Simulación"),
            Materia(sigla="INF-128", nombre="Sistemas de Información"),
            Materia(sigla="INF-129", nombre="Ingeniería de Software II"),
            Materia(sigla="INF-130", nombre="Administración de Redes"),
            Materia(sigla="INF-131", nombre="Ciberseguridad"),
            Materia(sigla="INF-132", nombre="Desarrollo de Aplicaciones Móviles"),
            Materia(sigla="INF-133", nombre="Desarrollo de Videojuegos"),
            Materia(sigla="INF-134", nombre="Big Data"),
            Materia(sigla="INF-135", nombre="Computación en la Nube"),
            Materia(sigla="INF-136", nombre="Robótica"),
            Materia(sigla="INF-137", nombre="Internet de las Cosas"),
            Materia(sigla="INF-138", nombre="Machine Learning"),
            Materia(sigla="INF-139", nombre="Procesamiento de Lenguaje Natural"),
            Materia(sigla="INF-140", nombre="Blockchain"),
            Materia(sigla="INF-141", nombre="Realidad Aumentada y Virtual"),
            Materia(sigla="INF-142", nombre="Emprendimiento Tecnológico"),
            Materia(sigla="INF-143", nombre="Ética Profesional"),
            Materia(sigla="INF-144", nombre="Taller de Grado"),
            Materia(sigla="INF-145", nombre="Prácticas Profesionales"),
            Materia(sigla="INF-146", nombre="Seminario de Investigación")
        ]

        db.session.add_all(materias)
        db.session.commit()
        print("✅ 48 materias insertadas.")
    else:
        print("ℹ️ Ya existen materias en la tabla.")