from ..extensions import db

class MateriaHorarioCursoParalelo(db.Model):
    __tablename__ = "materia_horario_curso_paralelo"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gestion_curso_paralelo_id = db.Column(db.Integer, db.ForeignKey("gestion_curso_paralelo.id"), nullable=False)
    materia_profesor_dia_horario_id = db.Column(db.Integer, db.ForeignKey("materia_profesor_dia_horario.id"), nullable=False)