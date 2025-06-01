from ..extensions import db
from app.models.gestion_curso_paralelo import GestionCursoParalelo
from app.models.estudiante import Estudiante
from app.models.user import User

class BoletaInscripcion(db.Model):
    __tablename__ = "boleta_inscripcion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hora = db.Column(db.Time, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiante.id"), nullable=False)
    gestion_curso_paralelo_id = db.Column(db.Integer, db.ForeignKey("gestion_curso_paralelo.id"), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    estudiante = db.relationship("Estudiante", backref="boletas", lazy="joined")
    gestion_curso_paralelo = db.relationship("GestionCursoParalelo", backref="boletas", lazy="joined")
    user = db.relationship("User", backref="boletas_registradas", lazy="joined")
