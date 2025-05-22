import random
from app.models.materia_profesor_dia_horario import MateriaProfesorDiaHorario
from app.models.materia_profesor import MateriaProfesor
from app.models.dia_horario import DiaHorario
from app.extensions import db

def seed_materia_profesor_dia_horario():
    if MateriaProfesorDiaHorario.query.first():
        print("ℹ️ Ya existen asignaciones en materia_profesor_dia_horario.")
        return

    materia_profesores = MateriaProfesor.query.all()
    dia_horarios = DiaHorario.query.all()

    if not materia_profesores or not dia_horarios:
        print("❌ No hay materia_profesor o dia_horario para asignar.")
        return

    asignaciones = []

    for mp in materia_profesores:
        cantidad_asignar = random.randint(1, 3)

        dias_asignados = random.sample(dia_horarios, k=min(cantidad_asignar, len(dia_horarios)))

        for dia in dias_asignados:
            asignacion = MateriaProfesorDiaHorario(
                materia_profesor_id=mp.id,
                dia_horario_id=dia.id
            )
            asignaciones.append(asignacion)

    db.session.add_all(asignaciones)
    db.session.commit()
    print(f"✅ Asignadas {len(asignaciones)} dia_horarios a materia_profesor.")
