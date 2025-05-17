from ..extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    photo_url = db.Column(db.Text, nullable=True)        # URL pública
    photo_storage = db.Column(db.String(255), nullable=True)  # Ruta en el servidor
    status = db.Column(db.Boolean, default=True)
