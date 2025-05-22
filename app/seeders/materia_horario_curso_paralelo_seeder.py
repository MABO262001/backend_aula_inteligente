import random
from app.models.gestion_curso_paralelo import GestionCursoParalelo
from app.models.materia_profesor_dia_horario import MateriaProfesorDiaHorario
from app.models.materia_profesor import MateriaProfesor
from app.models.materia_horario_curso_paralelo import MateriaHorarioCursoParalelo

from app.extensions import db


def seed_materia_horario_curso_paralelo():
    if MateriaHorarioCursoParalelo.query.first():
        print("ℹ️ Ya existen asignaciones en materia_horario_curso_paralelo.")
        return

    gestion_curso_paralelos = GestionCursoParalelo.query.all()
    materia_profesor_dia_horarios = MateriaProfesorDiaHorario.query.all()

    if not gestion_curso_paralelos or not materia_profesor_dia_horarios:
        print("❌ No hay datos suficientes para asignar materia_horario_curso_paralelo.")
        return

    asignaciones = []

    for gcp in gestion_curso_paralelos:
        # Para esta gestion_curso_paralelo asignamos de 3 a 6 materias diferentes (random)
        cantidad_asignar = random.randint(3, 6)

        # Para no repetir materias, trackeamos los materia_profesor_id ya asignados
        materia_ids_asignados = set()
        dia_horario_ids_asignados = set()

        # Filtramos las materias disponibles para asignar, shuffle para aleatorizar
        random.shuffle(materia_profesor_dia_horarios)

        for mpdh in materia_profesor_dia_horarios:
            materia_id = mpdh.materia_profesor_id
            dia_horario_id = mpdh.dia_horario_id

            # Solo asignar si no choca materia ni horario
            if (materia_id not in materia_ids_asignados and
                    dia_horario_id not in dia_horario_ids_asignados):

                asignacion = MateriaHorarioCursoParalelo(
                    gestion_curso_paralelo_id=gcp.id,
                    materia_profesor_dia_horario_id=mpdh.id
                )
                asignaciones.append(asignacion)

                materia_ids_asignados.add(materia_id)
                dia_horario_ids_asignados.add(dia_horario_id)

                if len(materia_ids_asignados) >= cantidad_asignar:
                    break

    db.session.add_all(asignaciones)
    db.session.commit()
    print(f"✅ Asignadas {len(asignaciones)} materias con horarios a cursos por gestión.")
