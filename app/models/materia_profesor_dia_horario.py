from ..extensions import db

class MateriaProfesorDiaHorario(db.Model):
    __tablename__ = "materia_profesor_dia_horario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    materia_profesor_id = db.Column(db.Integer, db.ForeignKey("materia_profesor.id"), nullable=False)
    dia_horario_id = db.Column(db.Integer, db.ForeignKey("dia_horario.id"), nullable=False)

    dia_horario = db.relationship('DiaHorario', backref='materia_profesor_dia_horario_rel')
    materia_profesor = db.relationship('MateriaProfesor', backref='materia_profesor_dia_horario_rel')