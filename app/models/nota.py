from ..extensions import db

class Nota(db.Model):
    __tablename__ = "nota"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    promedio_final = db.Column(db.Float, nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiante.id"), nullable=False)
    materia_horario_curso_paralelo_id = db.Column(db.Integer, db.ForeignKey("materia_horario_curso_paralelo.id"), nullable=False)

    estudiante = db.relationship("Estudiante", backref="notas", lazy="joined")
    materia_horario_curso_paralelo = db.relationship("MateriaHorarioCursoParalelo", backref="notas", lazy="joined")

