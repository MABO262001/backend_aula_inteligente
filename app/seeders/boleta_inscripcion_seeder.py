import random
from datetime import datetime, timedelta, time
from app.extensions import db
from app.models.boleta_inscripcion import BoletaInscripcion
from app.models.estudiante import Estudiante
from app.models.gestion import Gestion
from app.models.curso import Curso
from app.models.paralelo import Paralelo
from app.models.curso_paralelo import CursoParalelo
from app.models.gestion_curso_paralelo import GestionCursoParalelo
from app.models.user import User
from app.models.rol import Rol

def seed_boletas_inscripcion():
    if BoletaInscripcion.query.first():
        print("ℹ️ Ya existen boletas de inscripción en la tabla.")
        return

    estudiantes = Estudiante.query.all()
    gestiones = sorted(Gestion.query.all(), key=lambda g: int(g.nombre))
    cursos_primaria = sorted([c for c in Curso.query.all() if "Primaria" in c.nombre], key=lambda c: int(c.nombre.split('°')[0]))
    cursos_secundaria = sorted([c for c in Curso.query.all() if "Secundaria" in c.nombre], key=lambda c: int(c.nombre.split('°')[0]))
    paralelos = Paralelo.query.all()
    rol_admin = Rol.query.filter_by(nombre="Administrador").first()
    usuarios_admin = User.query.filter_by(rol_id=rol_admin.id).all()

    if not all([estudiantes, gestiones, cursos_primaria, cursos_secundaria, paralelos, usuarios_admin]):
        print("❌ Faltan datos esenciales (estudiantes, gestiones, cursos, paralelos, o admin).")
        return

    mitad = len(estudiantes) // 2
    estudiantes_primaria = estudiantes[:mitad]
    estudiantes_secundaria = estudiantes[mitad:]

    boletas = []
    fecha_base = datetime.now().date()
    hora_base = time(8, 0)

    def generar_boletas(estudiantes, cursos_base):
        for estudiante in estudiantes:
            gestion_inicio_idx = random.randint(0, len(gestiones) - 4)
            gestiones_seleccionadas = gestiones[gestion_inicio_idx:gestion_inicio_idx + random.randint(3, 5)]
            curso_inicio_idx = 0

            for i, gestion in enumerate(gestiones_seleccionadas):
                curso_actual = cursos_base[min(curso_inicio_idx + i, len(cursos_base) - 1)]
                paralelo = random.choice(paralelos)

                ya_inscrito = db.session.query(BoletaInscripcion).join(GestionCursoParalelo).filter(
                    BoletaInscripcion.estudiante_id == estudiante.id,
                    GestionCursoParalelo.gestion_id == gestion.id
                ).first()

                if ya_inscrito:
                    continue

                curso_paralelo = CursoParalelo.query.filter_by(
                    curso_id=curso_actual.id,
                    paralelo_id=paralelo.id
                ).first()

                if not curso_paralelo:
                    continue

                gestion_cp = GestionCursoParalelo.query.filter_by(
                    gestion_id=gestion.id,
                    curso_paralelo_id=curso_paralelo.id
                ).first()

                if not gestion_cp:
                    continue

                usuario_admin = random.choice(usuarios_admin)

                boleta = BoletaInscripcion(
                    fecha=gestion.nombre + '-02-15',
                    hora=(datetime.combine(fecha_base, hora_base) + timedelta(minutes=random.randint(0, 200))).time(),
                    estudiante_id=estudiante.id,
                    gestion_curso_paralelo_id=gestion_cp.id,
                    users_id=usuario_admin.id
                )
                boletas.append(boleta)

    generar_boletas(estudiantes_primaria, cursos_primaria)
    generar_boletas(estudiantes_secundaria, cursos_secundaria)

    db.session.add_all(boletas)
    db.session.commit()
    print(f"✅ Se generaron {len(boletas)} boletas de inscripción distribuidas entre primaria y secundaria.")
