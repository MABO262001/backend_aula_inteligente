from ..extensions import db

class Participacion(db.Model):
    __tablename__ = "participacion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(255), nullable=False)
    hora = db.Column(db.Time, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    # materia_horario_curso_paralelo_id = db.Column(db.Integer, db.ForeignKey("materia_horario_curso_paralelo.id"), nullable=False)
    gestion_curso_paralelo_id = db.Column(db.Integer, db.ForeignKey("gestion_curso_paralelo.id"), nullable=False)
    materia_profesor_id = db.Column(db.Integer, db.ForeignKey("materia_profesor.id"), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey("profesor.id"), nullable=False)

    profesor = db.relationship("Profesor", backref="participaciones", lazy="joined")
    materia_profesor = db.relationship("MateriaProfesor", backref="participaciones", lazy="joined")
    gestion_curso_paralelo = db.relationship("GestionCursoParalelo", backref="participaciones", lazy="joined")