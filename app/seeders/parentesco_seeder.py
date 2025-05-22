import random
from app.models.parentesco import Parentesco
from app.models.apoderado import Apoderado
from app.models.estudiante import Estudiante
from app.extensions import db

def seed_parentescos():
    if Parentesco.query.first():
        print("ℹ️ Ya existen registros en la tabla parentesco.")
        return

    apoderados = Apoderado.query.all()
    estudiantes = Estudiante.query.all()

    if not apoderados or not estudiantes:
        print("❌ Faltan apoderados o estudiantes para crear parentescos.")
        return

    nombres_parentesco = [
        "Madre", "Padre", "Abuelo", "Abuela",
        "Tio", "Tia", "Primo", "Hermano",
        "Prima", "Hermana"
    ]

    parentescos = []
    estudiantes_disponibles = estudiantes.copy()
    random.shuffle(estudiantes_disponibles)

    for apoderado in apoderados:

        cantidad_asignar = random.randint(1, min(3, len(estudiantes_disponibles)))
        estudiantes_asignados = estudiantes_disponibles[:cantidad_asignar]
        estudiantes_disponibles = estudiantes_disponibles[cantidad_asignar:]

        for est in estudiantes_asignados:
            parentesco_nombre = random.choice(nombres_parentesco)
            parentesco = Parentesco(
                nombre=parentesco_nombre,
                apoderado_id=apoderado.id,
                estudiante_id=est.id
            )
            parentescos.append(parentesco)

        if not estudiantes_disponibles:
            break

    db.session.add_all(parentescos)
    db.session.commit()
    print(f"✅ Insertados {len(parentescos)} parentescos.")
