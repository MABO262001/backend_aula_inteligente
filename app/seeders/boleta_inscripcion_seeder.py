import random
from datetime import datetime, time, timedelta
from app.models.boleta_inscripcion import BoletaInscripcion
from app.models.estudiante import Estudiante
from app.models.gestion_curso_paralelo import GestionCursoParalelo
from app.models.matricula import Matricula
from app.extensions import db

def seed_boleta_inscripcion():
    if BoletaInscripcion.query.first():
        print("ℹ️ Ya existen boletas de inscripción en la tabla.")
        return

    boletas = []

    estudiantes = Estudiante.query.all()
    gestiones_curso_paralelo = GestionCursoParalelo.query.all()

    # Mapeo para saber en qué gestiones está matriculado cada estudiante
    matriculas = Matricula.query.all()
    estudiante_matriculas = {}
    for m in matriculas:
        estudiante_matriculas.setdefault(m.parentesco.estudiante_id, []).append(m.subgestion.gestion_curso_paralelo.gestion_id if hasattr(m.subgestion, 'gestion_curso_paralelo') else None)

    # Ordenamos las gestiones por año para la lógica de ascenso
    gestiones_curso_paralelo.sort(key=lambda gcp: (gcp.gestion.nombre, gcp.curso_paralelo.curso.nombre if hasattr(gcp, 'curso_paralelo') and hasattr(gcp.curso_paralelo, 'curso') else ''))

    for estudiante in estudiantes:
        gestiones_del_estudiante = sorted(set(estudiante_matriculas.get(estudiante.id, [])))
        if not gestiones_del_estudiante:
            continue  # Estudiante sin matrículas, ignorar

        # Cantidad de gestiones en las que estuvo matriculado (usamos para saber curso)
        gestiones_count = len(gestiones_del_estudiante)

        for i, gestion_id in enumerate(gestiones_del_estudiante):
            # Buscar cursos para esa gestion
            gestiones_curso = [gcp for gcp in gestiones_curso_paralelo if gcp.gestion_id == gestion_id]
            if not gestiones_curso:
                continue

            # Calcular el índice del curso para el estudiante en esta gestión (subiendo cursos)
            curso_index = i  # la posición de la gestión representa el curso que debería cursar

            # Si supera el número de cursos, repetir último curso
            if curso_index >= len(gestiones_curso):
                curso_index = len(gestiones_curso) - 1

            gcp_asignado = gestiones_curso[curso_index]

            # Validar que no se inscriba más de una vez en la misma gestion y curso
            existe_boleta = BoletaInscripcion.query.filter_by(
                estudiante_id=estudiante.id,
                gestion_curso_paralelo_id=gcp_asignado.id
            ).first()

            if existe_boleta:
                continue

            # Fecha aleatoria dentro de la gestion (usamos fecha inicio y fin de la gestion)
            fecha_inicio = gcp_asignado.gestion.fecha_inicio if hasattr(gcp_asignado.gestion, 'fecha_inicio') else datetime.strptime(gcp_asignado.gestion.nombre + '-01-01', '%Y-%m-%d')
            fecha_final = gcp_asignado.gestion.fecha_final if hasattr(gcp_asignado.gestion, 'fecha_final') else datetime.strptime(gcp_asignado.gestion.nombre + '-12-31', '%Y-%m-%d')

            fecha_random = fecha_inicio + timedelta(days=random.randint(0, (fecha_final - fecha_inicio).days))

            # Hora random entre 8am y 5pm
            hora_random = time(hour=random.randint(8, 17), minute=random.choice([0, 15, 30, 45]))

            # El usuario admin que inscribe
            user_admin = estudiante.users_id

            boleta = BoletaInscripcion(
                hora=hora_random,
                fecha=fecha_random,
                estudiante_id=estudiante.id,
                gestion_curso_paralelo_id=gcp_asignado.id,
                users_id=user_admin
            )
            boletas.append(boleta)

    db.session.add_all(boletas)
    db.session.commit()
    print(f"✅ {len(boletas)} boletas de inscripción insertadas.")
