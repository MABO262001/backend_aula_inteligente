from ..extensions import db

class Gestion(db.Model):
    __tablename__ = "gestion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)

    gestion_curso_paralelos = db.relationship("GestionCursoParalelo", backref="gestion_rel", lazy="joined")
