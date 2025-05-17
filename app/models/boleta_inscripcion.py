from ..extensions import db

class BoletaInscripcion(db.Model):
    __tablename__ = "boleta_inscripcion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hora = db.Column(db.Time, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiante.id"), nullable=False)
    gestion_curso_paralelo_id = db.Column(db.Integer, db.ForeignKey("gestion_curso_paralelo.id"), nullable=False)