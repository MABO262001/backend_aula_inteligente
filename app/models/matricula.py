from ..extensions import db

class Matricula(db.Model):
    __tablename__ = "matricula"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    parentesco_id = db.Column(db.Integer, db.ForeignKey("parentesco.id"), nullable=False)
    subgestion_id = db.Column(db.Integer, db.ForeignKey("subgestion.id"), nullable=False)

    users_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)