from ..extensions import db

class EstudianteParticipa(db.Model):
    __tablename__ = "estudiante_participa"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estado = db.Column(db.String(50), nullable=False)
    participacion_id = db.Column(db.Integer, db.ForeignKey("participacion.id"), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiante.id"), nullable=False)

    estudiante = db.relationship("Estudiante", backref="participacion_estudiante", lazy="joined")
    participacion = db.relationship("Participacion", backref="participacion_estudiante", lazy="joined")


