from ..extensions import db

class Nota(db.Model):
    __tablename__ = "nota"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    promedio_final = db.Column(db.Float, nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiante.id"), nullable=False)
    gestion_curso_paralelo_id = db.Column(db.Integer, db.ForeignKey("gestion_curso_paralelo.id"), nullable=False)
    materia_profesor_id = db.Column(db.Integer, db.ForeignKey("materia_profesor.id"), nullable=False)

    estudiante = db.relationship("Estudiante", backref="notas", lazy="joined")

