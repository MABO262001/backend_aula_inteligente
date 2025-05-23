from ..extensions import db

class Parentesco(db.Model):
    __tablename__ = "parentesco"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    apoderado_id = db.Column(db.Integer, db.ForeignKey("apoderado.id"), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiante.id"), nullable=False)

    apoderado = db.relationship("Apoderado", backref="parentesco_apoderado", lazy="joined")
    estudiante = db.relationship("Estudiante", backref="parentesco_estudiante", lazy="joined")