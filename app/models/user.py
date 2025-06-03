from ..extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    photo_url = db.Column(db.Text, nullable=True)
    photo_storage = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Boolean, default=True)

    rol_id = db.Column(db.Integer, db.ForeignKey("rol.id"), nullable=False)
    rol = db.relationship("Rol", backref="users", lazy="joined")

    profesor = db.relationship("Profesor", uselist=False, backref="usuario", foreign_keys="[Profesor.users_profesor_id]")
    estudiante = db.relationship("Estudiante", uselist=False, backref="usuario", foreign_keys="[Estudiante.users_estudiante_id]")
    apoderado = db.relationship("Apoderado", uselist=False, backref="usuario", foreign_keys="[Apoderado.users_apoderado_id]")
