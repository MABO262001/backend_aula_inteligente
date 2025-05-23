from ..extensions import db

class MateriaProfesor(db.Model):
    __tablename__ = "materia_profesor"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    materia_id = db.Column(db.Integer, db.ForeignKey("materia.id"), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey("profesor.id"), nullable=False)

    materia = db.relationship('Materia', backref='materia_profesor')
    profesor = db.relationship('Profesor', backref='materia_profesor')
    materia_profesor_dia_horario = db.relationship('MateriaProfesorDiaHorario', backref='materia_profesor_rel')
