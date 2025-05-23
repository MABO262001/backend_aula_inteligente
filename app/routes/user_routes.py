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

def save_user_photo(file, user_name):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    model_folder = os.path.join(upload_folder, 'users')
    os.makedirs(model_folder, exist_ok=True)

    ext = file.filename.rsplit('.', 1)[1].lower()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_name = secure_filename(f"{user_name}_{timestamp}.{ext}")
    filepath = os.path.join(model_folder, safe_name)
    file.save(filepath)

    base_url = current_app.config.get('BASE_URL', '')
    public_url = f"{base_url}/api/users/uploads/{safe_name}" if base_url else f"/api/users/uploads/{safe_name}"

    return filepath, public_url

def validate_email_simple(email: str) -> bool:
    return email and '@' in email

def to_int_if_str(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None

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

@user_bp.route('/listar', methods=['GET'])
def listar_usuarios():
    users = User.query.filter_by(status=True).all()
    result = []
    for user in users:
        rol = Rol.query.get(user.rol_id)
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "photo_url": user.photo_url,
            "status": user.status,
            "rol": {
                "id": rol.id if rol else None,
                "nombre": rol.nombre if rol else None
            }
        })
    return jsonify(result)

@user_bp.route('/guardar', methods=['POST'])
def guardar_usuario():
    try:
        data = request.form.to_dict()
        errors = validate_user_data(data)
        if errors:
            return jsonify({"errors": errors}), 400

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()

        # Verificar que name y email no estén repetidos
        if User.query.filter_by(name=name).first():
            return jsonify({"error": "El nombre de usuario ya está registrado"}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "El email ya está registrado"}), 409

        # Usar rol_id enviado o por defecto Administrador
        rol_id_raw = data.get('rol_id')
        if rol_id_raw is not None:
            rol_id = to_int_if_str(rol_id_raw)
            rol = Rol.query.get(rol_id)
            if not rol:
                return jsonify({"error": "rol_id inválido"}), 400
        else:
            # Buscar rol administrador por defecto
            rol = Rol.query.filter_by(nombre="Administrador").first()
            if not rol:
                return jsonify({"error": "Rol 'Administrador' no encontrado"}), 500
            rol_id = rol.id

        password = data.get('password')
        password_hashed = generate_password_hash(password)

        photo_url = None
        photo_storage = None

        file = request.files.get('photo')
        if file:
            if not allowed_file(file.filename):
                return jsonify({"error": "Formato de imagen no permitido"}), 400
            photo_storage, photo_url = save_user_photo(file, name)
            current_app.logger.info(f"Foto guardada en: {photo_storage}")

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
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "photo_url": user.photo_url,
                "photo_storage": user.photo_storage,
                "status": user.status,
                "rol": {
                    "id": rol.id,
                    "nombre": rol.nombre
                }
            }
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad en la base de datos"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


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
    result = []
    for user in users:
        rol = Rol.query.get(user.rol_id)
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "photo_url": user.photo_url,
            "status": user.status,
            "rol": {
                "id": rol.id if rol else None,
                "nombre": rol.nombre if rol else None
            }
        })
    return jsonify(result)

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
            existing_user = User.query.filter(User.name == name, User.id != user_id).first()
            if existing_user:
                return jsonify({"error": "El nombre de usuario ya está registrado por otro usuario"}), 409
            user.name = name

        if 'email' in data:
            email = data['email'].strip()
            existing_user = User.query.filter(User.email == email, User.id != user_id).first()
            if existing_user:
                return jsonify({"error": "El email ya está registrado por otro usuario"}), 409
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

        file = request.files.get('photo')
        if file:
            if not allowed_file(file.filename):
                return jsonify({"error": "Formato de imagen no permitido"}), 400

            if user.photo_storage and os.path.exists(user.photo_storage):
                os.remove(user.photo_storage)

            photo_storage, photo_url = save_user_photo(file, user.name)
            user.photo_storage = photo_storage
            user.photo_url = photo_url

        db.session.commit()
        return jsonify({
            "message": "Usuario actualizado correctamente",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "photo_url": user.photo_url,
                "status": user.status
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar usuario: {str(e)}"}), 500

        
@user_bp.route('/eliminar/<int:user_id>', methods=['DELETE'])
def eliminar_usuario(user_id):
    user = User.query.get_or_404(user_id)
    try:
        user.status = False
        db.session.commit()
        return jsonify({"message": "Usuario desactivado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo desactivar el usuario: {str(e)}"}), 500

@user_bp.route('/uploads/<filename>', methods=['GET'])
def servir_foto_usuario(filename):
    folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'users')
    return send_from_directory(folder, filename)
