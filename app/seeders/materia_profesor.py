import random
from app.models.materia_profesor import MateriaProfesor
from app.models.materia import Materia
from app.models.profesor import Profesor
from app.extensions import db

def seed_materia_profesor():
    if MateriaProfesor.query.first():
        print("ℹ️ Ya existen asignaciones en la tabla materia_profesor.")
        return

    profesores = Profesor.query.all()
    materias = Materia.query.all()

    if not profesores or not materias:
        print("❌ No hay profesores o materias para asignar.")
        return

    asignaciones = []

    for materia in materias:
        profesor = random.choice(profesores)
        asignaciones.append(MateriaProfesor(
            materia_id=materia.id,
            profesor_id=profesor.id
        ))

    for profesor in profesores:

        materias_asignadas = [mp for mp in asignaciones if mp.profesor_id == profesor.id]
        cantidad_actual = len(materias_asignadas)
        cantidad_nueva = random.randint(1, 4)

        materias_no_asignadas = [m for m in materias if m.id not in [mp.materia_id for mp in materias_asignadas]]

        nuevas_materias = random.sample(materias_no_asignadas, k=min(cantidad_nueva, len(materias_no_asignadas)))

        for materia in nuevas_materias:
            asignaciones.append(MateriaProfesor(
                materia_id=materia.id,
                profesor_id=profesor.id
            ))

    db.session.add_all(asignaciones)
    db.session.commit()
    print(f"✅ Asignadas {len(asignaciones)} materias a profesores.")
