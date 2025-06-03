from ..extensions import db

class GestionCursoParalelo(db.Model):
    __tablename__ = "gestion_curso_paralelo"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    curso_paralelo_id = db.Column(db.Integer, db.ForeignKey("curso_paralelo.id"), nullable=False)
    gestion_id = db.Column(db.Integer, db.ForeignKey("gestion.id"), nullable=False)

    curso_paralelo = db.relationship("CursoParalelo", backref="gestion_curso_paralelo_rel", lazy="joined")
    gestion = db.relationship("Gestion", backref="gestion_curso_paralelo_rel", lazy="joined")

    materias_horario = db.relationship(
        "MateriaHorarioCursoParalelo",
        backref="gestion_curso_paralelo_rel",
        lazy="joined"
    )
