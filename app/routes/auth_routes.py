from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies
)
from ..models.user import User
from ..models.rol import Rol
from ..extensions import db

auth_bp = Blueprint("auth_bp", __name__)

def validate_email_simple(email: str) -> bool:
    return email and "@" in email

def get_user_data(user: User) -> dict:
    rol = Rol.query.get(user.rol_id)
    if not rol:
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "photo_url": user.photo_url,
            "status": user.status,
            "rol": None
        }

    rol_nombre = rol.nombre
    base_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "photo_url": user.photo_url,
        "photo_storage": user.photo_storage,
        "status": user.status,
        "rol": {
            "id": rol.id,
            "nombre": rol_nombre
        }
    }

    if rol_nombre == "Administrador":
        return base_data

    elif rol_nombre == "Profesor":
        profesor = getattr(user, "profesor", None)
        if profesor:
            base_data["profesor"] = {
                "id": profesor.id,
                "ci": profesor.ci,
                "nombre": profesor.nombre,
                "apellido": profesor.apellido,
                "telefono": profesor.telefono
            }

    elif rol_nombre == "Estudiante":
        estudiante = getattr(user, "estudiante", None)
        if estudiante:
            base_data["estudiante"] = {
                "id": estudiante.id,
                "ci": estudiante.ci,
                "nombre": estudiante.nombre,
                "apellido": estudiante.apellido,
                "sexo": estudiante.sexo,
                "telefono": estudiante.telefono
            }

    elif rol_nombre == "Apoderado":
        apoderado = getattr(user, "apoderado", None)
        if apoderado:
            base_data["apoderado"] = {
                "id": apoderado.id,
                "ci": apoderado.ci,
                "nombre": apoderado.nombre,
                "apellido": apoderado.apellido,
                "telefono": apoderado.telefono
            }

    return base_data

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email:
        return jsonify({"error": "Correo es obligatorio"}), 400

    if not validate_email_simple(email):
        return jsonify({"error": "Correo inválido"}), 400

    if not password:
        return jsonify({"error": "Contraseña es obligatoria"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Correo inválido"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"error": "Contraseña inválida"}), 401

    if not user.status:
        return jsonify({"error": "Usuario inactivo, contacte al administrador"}), 403

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": access_token,
        "user": get_user_data(user)
    }), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Sesión cerrada correctamente"})
    unset_jwt_cookies(response)
    return response, 200

@auth_bp.route('/protegido', methods=['GET'])
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Token inválido"}), 401

    user = User.query.get(user_id_int)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if not user.status:
        return jsonify({"error": "Usuario inactivo"}), 403

    return jsonify({
        "message": f"Bienvenido usuario {user_id_int}",
        "user": get_user_data(user)
    })

@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify(get_user_data(user)), 200
