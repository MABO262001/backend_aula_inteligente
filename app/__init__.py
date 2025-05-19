# app/__init__.py
from flask import Flask
from .config import Config
from .extensions import db, migrate
from .routes.user_routes import user_bp

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


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(user_bp, url_prefix='/api/users')

    return app
