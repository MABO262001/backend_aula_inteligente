import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from ..models.user import User
from ..models.rol import Rol
from ..models.profesor import Profesor
from ..extensions import db
from datetime import datetime

profesor_bp = Blueprint('profesor_bp', __name__)

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
    public_url = f"{base_url}/api/profesores/uploads/{safe_name}" if base_url else f"/api/profesores/uploads/{safe_name}"

    return filepath, public_url


@profesor_bp.route('/guardar', methods=['POST'])
def guardar_profesor():
    try:
        data = request.form.to_dict()

        # Campos obligatorios para usuario y profesor
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        ci = data.get('ci')
        nombre_prof = data.get('nombre_prof', '').strip()
        apellido_prof = data.get('apellido_prof', '').strip()
        telefono = data.get('telefono')
        direccion = data.get('direccion', '').strip()
        users_id = data.get('users_id')  # Usuario que crea/atiende al profesor

        # Validaciones básicas
        errors = []
        if len(name) < 3:
            errors.append("El campo 'name' es obligatorio y debe tener al menos 3 caracteres.")
        if '@' not in email:
            errors.append("El campo 'email' es obligatorio y debe contener '@'.")
        if len(password) < 6:
            errors.append("El campo 'password' es obligatorio y debe tener al menos 6 caracteres.")
        if not ci or not ci.isdigit():
            errors.append("El campo 'ci' es obligatorio y debe ser numérico.")
        if len(nombre_prof) == 0:
            errors.append("El campo 'nombre_prof' es obligatorio.")
        if len(apellido_prof) == 0:
            errors.append("El campo 'apellido_prof' es obligatorio.")
        if not users_id or not users_id.isdigit():
            errors.append("El campo 'users_id' es obligatorio y debe ser numérico.")
        if len(direccion) == 0:
            errors.append("El campo 'direccion' es obligatorio.")
        if errors:
            return jsonify({"errors": errors}), 400

        # Verificar que no existan duplicados name/email en usuarios
        if User.query.filter_by(name=name).first():
            return jsonify({"error": "El nombre de usuario ya está registrado"}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "El email ya está registrado"}), 409

        # Obtener rol "Profesor"
        rol_profesor = Rol.query.filter_by(nombre="Profesor").first()
        if not rol_profesor:
            return jsonify({"error": "Rol 'Profesor' no encontrado en base de datos"}), 500

        # Procesar foto (opcional)
        photo_url = None
        photo_storage = None
        file = request.files.get('photo')
        if file:
            if not allowed_file(file.filename):
                return jsonify({"error": "Formato de imagen no permitido"}), 400
            photo_storage, photo_url = save_user_photo(file, name)
            current_app.logger.info(f"Foto guardada en: {photo_storage}")

        # Crear usuario con rol Profesor
        password_hashed = generate_password_hash(password)
        user_profesor = User(
            name=name,
            email=email,
            password=password_hashed,
            photo_url=photo_url,
            photo_storage=photo_storage,
            status=True,
            rol_id=rol_profesor.id
        )
        db.session.add(user_profesor)
        db.session.flush()  # para obtener user_profesor.id antes del commit

        # Crear registro en tabla Profesor
        profesor = Profesor(
            ci=int(ci),
            nombre=nombre_prof,
            apellido=apellido_prof,
            telefono=int(telefono) if telefono and telefono.isdigit() else None,
            direccion=direccion,
            users_id=int(users_id),
            users_profesor_id=user_profesor.id
        )
        db.session.add(profesor)
        db.session.commit()

        return jsonify({
            "message": "Profesor y usuario creados exitosamente",
            "user": {
                "id": user_profesor.id,
                "name": user_profesor.name,
                "email": user_profesor.email,
                "photo_url": user_profesor.photo_url,
                "status": user_profesor.status,
                "rol": {"id": rol_profesor.id, "nombre": rol_profesor.nombre}
            },
            "profesor": {
                "id": profesor.id,
                "ci": profesor.ci,
                "nombre": profesor.nombre,
                "apellido": profesor.apellido,
                "telefono": profesor.telefono,
                "direccion": profesor.direccion,
                "users_id": profesor.users_id,
                "users_profesor_id": profesor.users_profesor_id
            }
        }
        ), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad en la base de datos", "detail": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error guardando profesor: {str(e)}")
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@profesor_bp.route('/actualizar/<int:profesor_id>', methods=['PUT'])
def actualizar_profesor(profesor_id):
    profesor = Profesor.query.get_or_404(profesor_id)
    user = User.query.get_or_404(profesor.users_profesor_id)
    try:
        data = request.form.to_dict()

        errors = []
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        ci = data.get('ci')
        nombre_prof = data.get('nombre_prof')
        apellido_prof = data.get('apellido_prof')
        telefono = data.get('telefono')
        direccion = data.get('direccion')
        users_id = data.get('users_id')

        if name:
            name = name.strip()
            exist = User.query.filter(User.name == name, User.id != user.id).first()
            if exist:
                errors.append("El nombre de usuario ya está registrado por otro usuario.")
            else:
                user.name = name

        if email:
            email = email.strip()
            exist = User.query.filter(User.email == email, User.id != user.id).first()
            if exist:
                errors.append("El email ya está registrado por otro usuario.")
            else:
                user.email = email

        if password:
            if len(password) < 6:
                errors.append("La contraseña debe tener al menos 6 caracteres.")
            else:
                user.password = generate_password_hash(password)

        if ci:
            if not ci.isdigit():
                errors.append("El campo 'ci' debe ser numérico.")
            else:
                profesor.ci = int(ci)

        if nombre_prof:
            profesor.nombre = nombre_prof.strip()
        if apellido_prof:
            profesor.apellido = apellido_prof.strip()
        if telefono:
            if telefono.isdigit():
                profesor.telefono = int(telefono)
            else:
                errors.append("El campo 'telefono' debe ser numérico o vacío.")
        if direccion:
            profesor.direccion = direccion.strip()
        if users_id:
            if users_id.isdigit():
                profesor.users_id = int(users_id)
            else:
                errors.append("El campo 'users_id' debe ser numérico.")

        if errors:
            return jsonify({"errors": errors}), 400

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
        return jsonify({"message": "Profesor y usuario actualizados correctamente"})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al actualizar profesor: {str(e)}")
        return jsonify({"error": f"Error al actualizar: {str(e)}"}), 500


@profesor_bp.route('/listar', methods=['GET'])
def listar_profesores():
    profesores = Profesor.query.all()
    result = []
    for p in profesores:
        user = User.query.get(p.users_profesor_id)
        rol = Rol.query.get(user.rol_id) if user else None
        result.append({
            "profesor_id": p.id,
            "ci": p.ci,
            "nombre_profesor": p.nombre,
            "apellido_profesor": p.apellido,
            "telefono": p.telefono,
            "direccion": p.direccion,
            "users_id": p.users_id,
            "users_profesor_id": p.users_profesor_id,
            "user": {
                "id": user.id if user else None,
                "name": user.name if user else None,
                "email": user.email if user else None,
                "photo_url": user.photo_url if user else None,
                "status": user.status if user else None,
                "rol": {
                    "id": rol.id if rol else None,
                    "nombre": rol.nombre if rol else None
                } if rol else None
            }
        }
        )
    return jsonify(result)


@profesor_bp.route('/buscar', methods=['GET'])
def buscar_profesores():
    query_params = request.args
    query = Profesor.query

    # Filtros para Profesor
    if 'id' in query_params and query_params.get('id').isdigit():
        query = query.filter(Profesor.id == int(query_params.get('id')))
    if 'ci' in query_params and query_params.get('ci').isdigit():
        query = query.filter(Profesor.ci == int(query_params.get('ci')))
    if 'nombre' in query_params:
        query = query.filter(Profesor.nombre.ilike(f"%{query_params.get('nombre')}%"))
    if 'apellido' in query_params:
        query = query.filter(Profesor.apellido.ilike(f"%{query_params.get('apellido')}%"))
    if 'telefono' in query_params and query_params.get('telefono').isdigit():
        query = query.filter(Profesor.telefono == int(query_params.get('telefono')))
    if 'direccion' in query_params:
        query = query.filter(Profesor.direccion.ilike(f"%{query_params.get('direccion')}%"))
    if 'users_profesor_id' in query_params and query_params.get('users_profesor_id').isdigit():
        query = query.filter(Profesor.users_profesor_id == int(query_params.get('users_profesor_id')))
    if 'users_id' in query_params and query_params.get('users_id').isdigit():
        query = query.filter(Profesor.users_id == int(query_params.get('users_id')))

    # Filtros para User
    if 'name' in query_params:
        query = query.join(User, User.id == Profesor.users_profesor_id).filter(User.name.ilike(f"%{query_params.get('name')}%"))
    if 'email' in query_params:
        query = query.join(User, User.id == Profesor.users_profesor_id).filter(User.email.ilike(f"%{query_params.get('email')}%"))

    profesores = query.all()
    result = []
    for p in profesores:
        user = User.query.get(p.users_profesor_id)
        rol = Rol.query.get(user.rol_id) if user else None
        result.append({
            "profesor_id": p.id,
            "ci": p.ci,
            "nombre_profesor": p.nombre,
            "apellido": p.apellido,
            "telefono": p.telefono,
            "direccion": p.direccion,
            "users_id": p.users_id,
            "users_profesor_id": p.users_profesor_id,
            "user": {
                "id": user.id if user else None,
                "name": user.name if user else None,
                "email": user.email if user else None,
                "photo_url": user.photo_url if user else None,
                "status": user.status if user else None,
                "rol": {
                    "id": rol.id if rol else None,
                    "nombre": rol.nombre if rol else None
                } if rol else None
            }
        })
    return jsonify(result)


@profesor_bp.route('/eliminar/<int:profesor_id>', methods=['DELETE'])
def eliminar_profesor(profesor_id):
    profesor = Profesor.query.get_or_404(profesor_id)
    user = User.query.get_or_404(profesor.users_profesor_id)
    try:
        user.status = False
        db.session.commit()
        return jsonify({"message": "Profesor y usuario desactivados correctamente"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error eliminando profesor: {str(e)}")
        return jsonify({"error": f"No se pudo eliminar: {str(e)}"}), 500


@profesor_bp.route('/uploads/<filename>', methods=['GET'])
def servir_foto_profesor(filename):
    folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'users')
    return send_from_directory(folder, filename)
