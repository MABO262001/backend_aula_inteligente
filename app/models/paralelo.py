from ..extensions import db

class Paralelo(db.Model):
    __tablename__ = "paralelo"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)