from ..extensions import db

class Horario(db.Model):
    __tablename__ = "horario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_final = db.Column(db.Time, nullable=False)