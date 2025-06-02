from ..extensions import db

class Subgestion(db.Model):
    __tablename__ = "subgestion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_final = db.Column(db.Date, nullable=False)

    gestion_id = db.Column(db.Integer, db.ForeignKey("gestion.id"), nullable=False)

