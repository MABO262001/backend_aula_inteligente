import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..models.user import User
from ..models.rol import Rol
from ..models.apoderado import Apoderado
from datetime import datetime

apoderado_bp = Blueprint('apoderado_bp', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_user_photo(file, username, role_name):
    folder_base = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    folder_rol = os.path.join(folder_base, role_name.lower())
    os.makedirs(folder_rol, exist_ok=True)
    ext = file.filename.rsplit('.', 1)[1].lower()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    safe_name = secure_filename(f"{username}_{timestamp}.{ext}")
    path = os.path.join(folder_rol, safe_name)
    file.save(path)
    base_url = current_app.config.get('BASE_URL', '')
    url = f"{base_url}/api/apoderados/uploads/{role_name.lower()}/{safe_name}"
    return path, url

def to_int_if_str(val):
    if isinstance(val, int):
        return val
    if isinstance(val, str) and val.isdigit():
        return int(val)
    return None

def serializar_apoderado(apoderado, user):
    rol = Rol.query.get(user.rol_id)
    return {
        "apoderado_id": apoderado.id,
        "ci": apoderado.ci,
        "nombre": apoderado.nombre,
        "apellido": apoderado.apellido,
        "sexo": apoderado.sexo,
        "telefono": apoderado.telefono,
        "users_id": apoderado.users_id,
        "users_apoderado_id": apoderado.users_apoderado_id,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "photo_url": user.photo_url,
            "status": user.status,
            "rol": {
                "id": rol.id if rol else None,
                "nombre": rol.nombre if rol else None
            }
        }
    }

@apoderado_bp.route('/guardar', methods=['POST'])
def guardar_apoderado():
    try:
        data = request.form.to_dict()
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        ci = data.get("ci")
        nombre = data.get("nombre", "")
        apellido = data.get("apellido", "")
        sexo = data.get("sexo", "")
        telefono = data.get("telefono")
        users_id = data.get("users_id")

        errors = []
        if len(name) < 3: errors.append("Nombre de usuario muy corto.")
        if '@' not in email: errors.append("Email inválido.")
        if len(password) < 6: errors.append("Contraseña muy corta.")
        if not ci or not ci.isdigit(): errors.append("CI inválido.")
        if not nombre: errors.append("Nombre obligatorio.")
        if not apellido: errors.append("Apellido obligatorio.")
        if not sexo: errors.append("Sexo obligatorio.")
        if not users_id or not str(users_id).isdigit(): errors.append("users_id inválido.")

        if errors:
            return jsonify({"errors": errors}), 400

        if User.query.filter_by(name=name).first() or User.query.filter_by(email=email).first():
            return jsonify({"error": "Nombre o email ya registrados"}), 409

        rol = Rol.query.filter_by(nombre="Apoderado").first()
        if not rol:
            rol = Rol(nombre="Apoderado")
            db.session.add(rol)
            db.session.flush()

        file = request.files.get('photo')
        photo_storage, photo_url = (None, None)
        if file and allowed_file(file.filename):
            photo_storage, photo_url = save_user_photo(file, name, rol.nombre)

        hashed_pw = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_pw,
            photo_url=photo_url,
            photo_storage=photo_storage,
            status=True,
            rol_id=rol.id
        )
        db.session.add(new_user)
        db.session.flush()

        apoderado = Apoderado(
            ci=int(ci),
            nombre=nombre,
            apellido=apellido,
            sexo=sexo,
            telefono=int(telefono) if telefono and telefono.isdigit() else None,
            users_id=int(users_id),
            users_apoderado_id=new_user.id
        )
        db.session.add(apoderado)
        db.session.commit()

        return jsonify({
            "message": "Apoderado creado exitosamente",
            "apoderado": serializar_apoderado(apoderado, new_user)
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad", "detail": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@apoderado_bp.route('/listar', methods=['GET'])
def listar_apoderados():
    apoderados = Apoderado.query.all()
    resultado = []
    for apo in apoderados:
        user = User.query.get(apo.users_apoderado_id)
        if user:
            resultado.append(serializar_apoderado(apo, user))
    return jsonify(resultado)

@apoderado_bp.route('/buscar', methods=['GET'])
def buscar_apoderado():
    args = request.args
    query = Apoderado.query
    if 'ci' in args: query = query.filter(Apoderado.ci == args.get('ci'))
    if 'nombre' in args: query = query.filter(Apoderado.nombre.ilike(f"%{args.get('nombre')}%"))
    if 'apellido' in args: query = query.filter(Apoderado.apellido.ilike(f"%{args.get('apellido')}%"))
    if 'telefono' in args: query = query.filter(Apoderado.telefono == args.get('telefono'))
    if 'users_apoderado_id' in args and args.get('users_apoderado_id').isdigit():
        query = query.filter(Apoderado.users_apoderado_id == int(args.get('users_apoderado_id')))

    results = []
    for apo in query.all():
        user = User.query.get(apo.users_apoderado_id)
        if user:
            results.append(serializar_apoderado(apo, user))
    return jsonify(results)

@apoderado_bp.route('/actualizar/<int:apoderado_id>', methods=['PATCH'])
def actualizar_apoderado(apoderado_id):
    apoderado = Apoderado.query.get_or_404(apoderado_id)
    user = User.query.get_or_404(apoderado.users_apoderado_id)
    try:
        data = request.form.to_dict()

        # Solo actualiza si viene en los datos
        if 'name' in data:
            name = data['name'].strip()
            if User.query.filter(User.name == name, User.id != user.id).first():
                return jsonify({"error": "Nombre ya existe"}), 409
            user.name = name

        if 'email' in data:
            email = data['email'].strip()
            if User.query.filter(User.email == email, User.id != user.id).first():
                return jsonify({"error": "Email ya registrado"}), 409
            user.email = email

        if 'password' in data and data['password'].strip():
            user.password = generate_password_hash(data['password'])

        if 'ci' in data and str(data['ci']).isdigit():
            apoderado.ci = int(data['ci'])

        if 'nombre' in data:
            apoderado.nombre = data['nombre'].strip()

        if 'apellido' in data:
            apoderado.apellido = data['apellido'].strip()

        if 'sexo' in data:
            apoderado.sexo = data['sexo'].strip()

        if 'telefono' in data and str(data['telefono']).isdigit():
            apoderado.telefono = int(data['telefono'])

        if 'users_id' in data and str(data['users_id']).isdigit():
            apoderado.users_id = int(data['users_id'])

        file = request.files.get('photo')
        if file and allowed_file(file.filename):
            if user.photo_storage and os.path.exists(user.photo_storage):
                os.remove(user.photo_storage)
            photo_storage, photo_url = save_user_photo(file, user.name, "Apoderado")
            user.photo_storage = photo_storage
            user.photo_url = photo_url

        db.session.commit()
        return jsonify({
            "message": "Apoderado actualizado correctamente",
            "apoderado": serializar_apoderado(apoderado, user)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar: {str(e)}"}), 500

@apoderado_bp.route('/eliminar/<int:apoderado_id>', methods=['DELETE'])
def eliminar_apoderado(apoderado_id):
    apoderado = Apoderado.query.get_or_404(apoderado_id)
    user = User.query.get_or_404(apoderado.users_apoderado_id)
    try:
        user.status = False
        db.session.commit()
        return jsonify({
            "message": "Apoderado desactivado correctamente",
            "apoderado": serializar_apoderado(apoderado, user)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo desactivar: {str(e)}"}), 500

@apoderado_bp.route('/eliminar_definitivamente/<int:apoderado_id>', methods=['DELETE'])
def eliminar_apoderado_definitivamente(apoderado_id):
    try:
        apoderado = Apoderado.query.get_or_404(apoderado_id)

        user = None
        if apoderado.users_apoderado_id:
            user = User.query.get(apoderado.users_apoderado_id)

        # Eliminar foto si existe
        if user and user.photo_storage:
            photo_path = os.path.abspath(user.photo_storage)
            if os.path.exists(photo_path):
                os.remove(photo_path)
            else:
                current_app.logger.warning(f"Foto no encontrada en ruta: {photo_path}")

        # Eliminar registros
        db.session.delete(apoderado)
        if user:
            db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "Apoderado eliminado correctamente"})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar apoderado: {str(e)}")
        return jsonify({"error": f"No se pudo eliminar: {str(e)}"}), 500


@apoderado_bp.route('/uploads/<rol>/<filename>', methods=['GET'])
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


