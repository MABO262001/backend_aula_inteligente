from ..extensions import db

class MateriaProfesor(db.Model):
    __tablename__ = "materia_profesor"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    materia_id = db.Column(db.Integer, db.ForeignKey("materia.id"), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey("profesor.id"), nullable=False)