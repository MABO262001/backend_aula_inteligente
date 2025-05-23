from ..extensions import db

class Profesor(db.Model):
    __tablename__ = "profesor"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ci = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    apellido = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.Integer, nullable=True)
    direccion = db.Column(db.String(255), nullable=False)

    users_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    users_profesor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    user_profesor = db.relationship('User', foreign_keys=[users_profesor_id])

    materias_profesor = db.relationship('MateriaProfesor', backref='profesor_rel', lazy='dynamic')
