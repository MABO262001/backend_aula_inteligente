from ..extensions import db

class CursoParalelo(db.Model):
    __tablename__ = "curso_paralelo"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paralelo_id = db.Column(db.Integer, db.ForeignKey("paralelo.id"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id"), nullable=False)

    curso = db.relationship("Curso", backref="curso_paralelos", lazy=True)
    paralelo = db.relationship("Paralelo", backref="curso_paralelos", lazy=True)