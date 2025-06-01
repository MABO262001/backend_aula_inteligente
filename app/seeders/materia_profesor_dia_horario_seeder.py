import random
from collections import defaultdict
from app.models.materia_profesor_dia_horario import MateriaProfesorDiaHorario
from app.models.materia_profesor import MateriaProfesor
from app.models.dia_horario import DiaHorario
from app.models.materia import Materia
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

    # Agrupar los dia_horarios por intervalo horario (hora_inicio y hora_final)
    bloques = defaultdict(list)
    for dh in dia_horarios:
        clave = (dh.horario.hora_inicio, dh.horario.hora_final)
        bloques[clave].append(dh)

    asignaciones = []

    for mp in materia_profesores:
        # Elegir un bloque de horario al azar (mismo horario, distintos días)
        bloque_elegido = random.choice(list(bloques.values()))
        # Seleccionar entre 2 y 3 días distintos de ese bloque
        dias_seleccionados = random.sample(bloque_elegido, k=min(len(bloque_elegido), random.randint(2, 3)))

        for dia in dias_seleccionados:
            asignacion = MateriaProfesorDiaHorario(
                materia_profesor_id=mp.id,
                dia_horario_id=dia.id
            )
            asignaciones.append(asignacion)

    db.session.add_all(asignaciones)
    db.session.commit()
    print(f"✅ Asignadas {len(asignaciones)} dia_horarios a materia_profesor.")
