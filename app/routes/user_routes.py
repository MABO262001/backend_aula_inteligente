import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from ..models.user import User
from ..models.rol import Rol
from ..extensions import db
from datetime import datetime

user_bp = Blueprint('user_bp', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_user_photo(file, user_name, role_name):
    folder_base = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    folder_rol = os.path.join(folder_base, role_name.lower())
    os.makedirs(folder_rol, exist_ok=True)
    ext = file.filename.rsplit('.', 1)[1].lower()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    safe_name = secure_filename(f"{user_name}_{timestamp}.{ext}")
    file_path = os.path.join(folder_rol, safe_name)
    file.save(file_path)
    base_url = current_app.config.get('BASE_URL', '')
    photo_url = f"{base_url}/api/users/uploads/{role_name.lower()}/{safe_name}" if base_url else f"/api/users/uploads/{role_name.lower()}/{safe_name}"
    return file_path, photo_url

def to_int_if_str(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None

def validate_email_simple(email: str) -> bool:
    return email and '@' in email

def validate_user_data(data, is_update=False):
    errors = []
    if not is_update or 'name' in data:
        name = data.get('name')
        if not name or len(name.strip()) < 3:
            errors.append("El campo 'name' es obligatorio y debe tener al menos 3 caracteres.")
    if not is_update or 'email' in data:
        email = data.get('email')
        if not validate_email_simple(email):
            errors.append("El campo 'email' es obligatorio y debe contener '@'.")
    if not is_update or 'password' in data:
        password = data.get('password')
        if not is_update and (not password or len(password) < 6):
            errors.append("El campo 'password' es obligatorio y debe tener al menos 6 caracteres.")
        elif is_update and password and len(password) < 6:
            errors.append("Si se envía contraseña, debe tener al menos 6 caracteres.")
    if not is_update or 'rol_id' in data:
        rol_id_raw = data.get('rol_id')
        if rol_id_raw is not None:
            rol_id = to_int_if_str(rol_id_raw)
            if rol_id is None:
                errors.append("El campo 'rol_id' debe ser numérico si se envía.")
    return errors

def serializar_usuario(user):
    rol = Rol.query.get(user.rol_id)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "photo_url": user.photo_url,
        "photo_storage": user.photo_storage,
        "status": user.status,
        "rol": {
            "id": rol.id if rol else None,
            "nombre": rol.nombre if rol else None
        }
    }

@user_bp.route('/uploads/<rol>/<filename>', methods=['GET'])
def servir_foto_por_rol(rol, filename):
    try:
        base_upload_folder = os.path.abspath(current_app.config.get('UPLOAD_FOLDER', 'uploads'))
        folder = os.path.join(base_upload_folder, rol)

        file_path = os.path.join(folder, filename)
        if not os.path.exists(file_path):
            return jsonify({
                "error": "Archivo no encontrado",
                "ruta": file_path
            }), 404

        return send_from_directory(folder, filename)
    except Exception as e:
        return jsonify({"error": f"Error al servir la imagen: {str(e)}"}), 500



@user_bp.route('/guardar', methods=['POST'])
def guardar_usuario():
    try:
        data = request.form.to_dict()
        errors = validate_user_data(data)
        if errors:
            return jsonify({"errors": errors}), 400

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()

        if User.query.filter_by(name=name).first():
            return jsonify({"error": "El nombre de usuario ya está registrado"}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "El email ya está registrado"}), 409

        rol_id_raw = data.get('rol_id')
        if rol_id_raw is not None:
            rol_id = to_int_if_str(rol_id_raw)
            rol = Rol.query.get(rol_id)
            if not rol:
                return jsonify({"error": "rol_id inválido"}), 400
        else:
            rol = Rol.query.filter_by(nombre="Administrador").first()
            if not rol:
                rol = Rol(nombre="Administrador")
                db.session.add(rol)
                db.session.flush()
            rol_id = rol.id

        password_hashed = generate_password_hash(data.get('password'))
        photo_url = None
        photo_storage = None
        file = request.files.get('photo')
        if file:
            if not allowed_file(file.filename):
                return jsonify({"error": "Formato de imagen no permitido"}), 400
            photo_storage, photo_url = save_user_photo(file, name, rol.nombre)

        user = User(
            name=name,
            email=email,
            password=password_hashed,
            photo_url=photo_url,
            photo_storage=photo_storage,
            status=True,
            rol_id=rol_id
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "Usuario creado exitosamente",
            "user": serializar_usuario(user)
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad en la base de datos"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@user_bp.route('/actualizar/<int:user_id>', methods=['PATCH'])
def actualizar_usuario(user_id):
    user = User.query.get_or_404(user_id)
    try:
        data = request.form.to_dict()
        errors = validate_user_data(data, is_update=True)
        if errors:
            return jsonify({"errors": errors}), 400

        if 'name' in data:
            name = data['name'].strip()
            existing = User.query.filter(User.name == name, User.id != user.id).first()
            if existing:
                return jsonify({"error": "El nombre de usuario ya existe"}), 409
            user.name = name

        if 'email' in data:
            email = data['email'].strip()
            existing = User.query.filter(User.email == email, User.id != user.id).first()
            if existing:
                return jsonify({"error": "El email ya está registrado"}), 409
            user.email = email

        if 'password' in data and data['password']:
            user.password = generate_password_hash(data['password'])

        rol_id_raw = data.get('rol_id')
        if rol_id_raw is not None:
            rol_id = to_int_if_str(rol_id_raw)
            rol = Rol.query.get(rol_id)
            if not rol:
                return jsonify({"error": "rol_id inválido"}), 400
            user.rol_id = rol_id
        else:
            rol = Rol.query.get(user.rol_id)

        file = request.files.get('photo')
        if file:
            if not allowed_file(file.filename):
                return jsonify({"error": "Formato de imagen no permitido"}), 400
            if user.photo_storage and os.path.exists(user.photo_storage):
                os.remove(user.photo_storage)
            photo_storage, photo_url = save_user_photo(file, user.name, rol.nombre)
            user.photo_storage = photo_storage
            user.photo_url = photo_url

        db.session.commit()
        return jsonify({
            "message": "Usuario actualizado correctamente",
            "user": serializar_usuario(user)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar usuario: {str(e)}"}), 500

@user_bp.route('/listar', methods=['GET'])
def listar_usuarios():
    users = User.query.filter_by(status=True).all()
    return jsonify([serializar_usuario(user) for user in users])

@user_bp.route('/buscar', methods=['GET'])
def buscar_usuarios():
    query_params = request.args
    query = User.query
    if 'status' in query_params:
        status_val = query_params.get('status').lower()
        if status_val == 'true':
            query = query.filter(User.status.is_(True))
        elif status_val == 'false':
            query = query.filter(User.status.is_(False))
    else:
        query = query.filter(User.status.is_(True))

    if 'id' in query_params and query_params.get('id').isdigit():
        query = query.filter(User.id == int(query_params.get('id')))
    if 'name' in query_params:
        query = query.filter(User.name.ilike(f"%{query_params.get('name')}%"))
    if 'email' in query_params:
        query = query.filter(User.email.ilike(f"%{query_params.get('email')}%"))
    if 'rol_id' in query_params:
        rol_id = to_int_if_str(query_params.get('rol_id'))
        if rol_id is not None:
            query = query.filter(User.rol_id == rol_id)

    users = query.all()
    return jsonify([serializar_usuario(user) for user in users])

@user_bp.route('/eliminar/<int:user_id>', methods=['DELETE'])
def eliminar_usuario(user_id):
    user = User.query.get_or_404(user_id)
    try:
        user.status = False
        db.session.commit()
        return jsonify({
            "message": "Usuario desactivado correctamente",
            "user": serializar_usuario(user)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo desactivar el usuario: {str(e)}"}), 500

@user_bp.route('/eliminar_definitivo/<int:user_id>', methods=['DELETE'])
def eliminar_usuario_definitivo(user_id):
    user = User.query.get_or_404(user_id)
    try:
        if user.photo_storage and os.path.exists(user.photo_storage):
            os.remove(user.photo_storage)
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            "message": "Usuario eliminado definitivamente",
            "user": serializar_usuario(user)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo eliminar el usuario: {str(e)}"}), 500

@user_bp.route('/listar_adminitrador', methods=['GET'])
def listar_usuarios_administrador():
    users = User.query.filter_by(status=True).all()
    result = []
    for user in users:
        rol = Rol.query.get(user.rol_id)
        if rol and rol.nombre == "Administrador":
            result.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "photo_url": user.photo_url,
                "status": user.status,

            })
    return jsonify(result)