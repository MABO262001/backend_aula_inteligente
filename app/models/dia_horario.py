from ..extensions import db

class DiaHorario(db.Model):
    __tablename__ = "dia_horario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dia_id = db.Column(db.Integer, db.ForeignKey("dia.id"), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey("horario.id"), nullable=False)

    dia = db.relationship('Dia', backref='dia_horario_rel')
    horario = db.relationship('Horario', backref='dia_horario_rel')