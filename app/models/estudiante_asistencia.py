from ..extensions import db

class EstudianteAsistencia(db.Model):
    __tablename__ = "estudiante_asistencia"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estado = db.Column(db.String(50), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiante.id"), nullable=False)
    asistencia_id = db.Column(db.Integer, db.ForeignKey("asistencia.id"), nullable=False)

    estudiante = db.relationship("Estudiante", backref="asistencia_estudiante", lazy="joined")
    asistencia = db.relationship("Asistencia", backref="asistencia_estudiante", lazy="joined")