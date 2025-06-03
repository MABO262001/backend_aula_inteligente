# app/__init__.py
from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt

# ⚠️ Importar los modelos explícitamente para que se registren en SQLAlchemy
# 1 No depende De Nadie
from .models.rol import  Rol
from .models.user import User
from .models.profesor import Profesor
from .models.materia import Materia
from .models.dia import Dia
from .models.horario import Horario
from .models.curso import Curso
from .models.paralelo import Paralelo
from .models.gestion import Gestion
from .models.subgestion import Subgestion
from .models.apoderado import Apoderado
from .models.estudiante import Estudiante

# 2 Depende de Otros Modelos
from .models.dia_horario import DiaHorario
from .models.materia_profesor import MateriaProfesor
from .models.curso_paralelo import CursoParalelo
from .models.parentesco import Parentesco

# 3 Depende del #2
from .models.matricula import Matricula
from .models.gestion_curso_paralelo import GestionCursoParalelo
from .models.materia_profesor_dia_horario import MateriaProfesorDiaHorario

# 4 Depende del #3
from .models.boleta_inscripcion import BoletaInscripcion
from .models.materia_horario_curso_paralelo import MateriaHorarioCursoParalelo

# 5 Depende del #4
from .models.nota import Nota
from .models.asistencia import Asistencia
from .models.participacion import Participacion

# 6 Depende del #5
from .models.estudiante_asistencia import EstudianteAsistencia
from .models.estudiante_participa import EstudianteParticipa

from .routes.user_routes import user_bp
from .routes.auth_routes import auth_bp
from .routes.user_profesor_routes import profesor_bp
from .routes.rol_routes import rol_bp
from .routes.dia_routes import dia_bp
from .routes.horario_routes import horario_bp
from .routes.materia_routes import materia_bp
from .routes.gestion_routes import gestion_bp
from .routes.user_apoderados import apoderado_bp
from .routes.user_estudiante_routes import estudiante_bp
from .routes.pagos_matriculas_routes import pagos_matriculas_bp
from .routes.inscripcion_routes import boleta_bp
from .routes.gestion_notas_routes import gestion_notas_bp
from .routes.gestionar_asistencias_routes import gestionar_asistencias_bp
from .routes.gestionar_participacion_routes import gestionar_participaciones_bp
from .routes.gestionar_apis_movil_routes import apimovil_pb


from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

    print("[DEBUG] UPLOAD_FOLDER:", app.config['UPLOAD_FOLDER'])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(rol_bp, url_prefix='/api/roles')
    app.register_blueprint(profesor_bp, url_prefix='/api/profesores')
    app.register_blueprint(dia_bp, url_prefix='/api/dias')
    app.register_blueprint(horario_bp, url_prefix='/api/horario')
    app.register_blueprint(materia_bp, url_prefix='/api/materias')
    app.register_blueprint(gestion_bp, url_prefix='/api/gestion')
    app.register_blueprint(apoderado_bp, url_prefix='/api/apoderados')
    app.register_blueprint(estudiante_bp, url_prefix='/api/estudiante')
    app.register_blueprint(pagos_matriculas_bp, url_prefix='/api/pagos_matriculas')
    app.register_blueprint(boleta_bp, url_prefix='/api/boleta')
    app.register_blueprint(gestion_notas_bp, url_prefix='/api/gestion_notas')
    app.register_blueprint(gestionar_asistencias_bp, url_prefix='/api/asistencias')
    app.register_blueprint(gestionar_participaciones_bp, url_prefix='/api/participacion')
    app.register_blueprint(apimovil_pb, url_prefix='/api/movil')

    return app
