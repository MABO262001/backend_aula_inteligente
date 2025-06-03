from ..extensions import db

class Estudiante(db.Model):
    __tablename__ = "estudiante"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ci = db.Column(db.Integer, nullable=False, unique=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellido = db.Column(db.String(255), nullable=False)
    sexo = db.Column(db.String(10), nullable=False)
    telefono = db.Column(db.Integer, nullable=True)

    users_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    users_estudiante_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    user_estudiante = db.relationship('User', foreign_keys=[users_estudiante_id])
