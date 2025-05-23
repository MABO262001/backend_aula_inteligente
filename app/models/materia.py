from ..extensions import db

class Materia(db.Model):
    __tablename__ = "materia"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sigla = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)

