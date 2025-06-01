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
