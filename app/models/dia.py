from ..extensions import db

class Dia(db.Model):
    __tablename__ = "dia"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)