import os
import json
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from ..extensions import db
from ..models.user import User
from ..models.rol import Rol
from ..models.estudiante import Estudiante
from ..models.apoderado import Apoderado
from ..models.parentesco import Parentesco
from datetime import datetime

estudiante_bp = Blueprint('estudiante_bp', __name__)
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
    url = f"{base_url}/api/estudiantes/uploads/{role_name.lower()}/{safe_name}"
    return path, url

def serializar_estudiante(est, user):
    rol = Rol.query.get(user.rol_id)
    apoderados = []
    for par in Parentesco.query.filter_by(estudiante_id=est.id).all():
        apo = Apoderado.query.get(par.apoderado_id)
        if apo:
            apoderados.append({
                "nombre": par.nombre,
                "ci": apo.ci,
                "nombre_completo": f"{apo.nombre} {apo.apellido}"
            })
    return {
        "estudiante_id": est.id,
        "ci": est.ci,
        "nombre": est.nombre,
        "apellido": est.apellido,
        "sexo": est.sexo,
        "telefono": est.telefono,
        "users_id": est.users_id,
        "users_estudiante_id": est.users_estudiante_id,
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
        },
        "apoderados": apoderados
    }

@estudiante_bp.route('/guardar', methods=['POST'])
def guardar_estudiante():
    try:
        data = request.form.to_dict()
        parentescos_raw = data.get("parentescos")
        parentescos_info = json.loads(parentescos_raw) if parentescos_raw else []

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

        rol = Rol.query.filter_by(nombre="Estudiante").first()
        if not rol:
            rol = Rol(nombre="Estudiante")
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

        estudiante = Estudiante(
            ci=int(ci),
            nombre=nombre,
            apellido=apellido,
            sexo=sexo,
            telefono=int(telefono) if telefono and telefono.isdigit() else None,
            users_id=int(users_id),
            users_estudiante_id=new_user.id
        )
        db.session.add(estudiante)
        db.session.flush()

        for par in parentescos_info:
            ci_apo = par.get("ci")
            nombre_par = par.get("nombre")
            apoderado = Apoderado.query.filter_by(ci=ci_apo).first()
            if apoderado and nombre_par:
                db.session.add(Parentesco(
                    nombre=nombre_par,
                    apoderado_id=apoderado.id,
                    estudiante_id=estudiante.id
                ))

        db.session.commit()
        return jsonify({
            "message": "Estudiante creado correctamente",
            "estudiante": serializar_estudiante(estudiante, new_user)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al guardar estudiante: {str(e)}"}), 500

@estudiante_bp.route('/listar', methods=['GET'])
def listar_estudiantes():
    estudiantes = Estudiante.query.all()
    resultado = []
    for est in estudiantes:
        user = User.query.get(est.users_estudiante_id)
        if user:
            resultado.append(serializar_estudiante(est, user))
    return jsonify(resultado)

@estudiante_bp.route('/buscar', methods=['GET'])
def buscar_estudiante():
    args = request.args
    query = Estudiante.query
    if 'ci' in args: query = query.filter(Estudiante.ci == args.get('ci'))
    if 'nombre' in args: query = query.filter(Estudiante.nombre.ilike(f"%{args.get('nombre')}%"))
    if 'apellido' in args: query = query.filter(Estudiante.apellido.ilike(f"%{args.get('apellido')}%"))
    if 'telefono' in args: query = query.filter(Estudiante.telefono == args.get('telefono'))
    if 'users_estudiante_id' in args and args.get('users_estudiante_id').isdigit():
        query = query.filter(Estudiante.users_estudiante_id == int(args.get('users_estudiante_id')))

    results = []
    for est in query.all():
        user = User.query.get(est.users_estudiante_id)
        if user:
            results.append(serializar_estudiante(est, user))
    return jsonify(results)

@estudiante_bp.route('/actualizar/<int:estudiante_id>', methods=['PATCH'])
def actualizar_estudiante(estudiante_id):
    estudiante = Estudiante.query.get_or_404(estudiante_id)
    user = User.query.get_or_404(estudiante.users_estudiante_id)
    try:
        data = request.form.to_dict()

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
            estudiante.ci = int(data['ci'])
        if 'nombre' in data:
            estudiante.nombre = data['nombre'].strip()
        if 'apellido' in data:
            estudiante.apellido = data['apellido'].strip()
        if 'sexo' in data:
            estudiante.sexo = data['sexo'].strip()
        if 'telefono' in data and str(data['telefono']).isdigit():
            estudiante.telefono = int(data['telefono'])
        if 'users_id' in data and str(data['users_id']).isdigit():
            estudiante.users_id = int(data['users_id'])

        file = request.files.get('photo')
        if file and allowed_file(file.filename):
            if user.photo_storage and os.path.exists(user.photo_storage):
                os.remove(user.photo_storage)
            photo_storage, photo_url = save_user_photo(file, user.name, "Estudiante")
            user.photo_storage = photo_storage
            user.photo_url = photo_url

        db.session.commit()
        return jsonify({
            "message": "Estudiante actualizado correctamente",
            "estudiante": serializar_estudiante(estudiante, user)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar: {str(e)}"}), 500

@estudiante_bp.route('/eliminar/<int:estudiante_id>', methods=['DELETE'])
def eliminar_estudiante(estudiante_id):
    estudiante = Estudiante.query.get_or_404(estudiante_id)
    user = User.query.get_or_404(estudiante.users_estudiante_id)
    try:
        user.status = False
        db.session.commit()
        return jsonify({
            "message": "Estudiante desactivado correctamente",
            "estudiante": serializar_estudiante(estudiante, user)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo desactivar: {str(e)}"}), 500

@estudiante_bp.route('/eliminar_definitivamente/<int:estudiante_id>', methods=['DELETE'])
def eliminar_estudiante_definitivamente(estudiante_id):
    try:
        estudiante = Estudiante.query.get_or_404(estudiante_id)
        user = User.query.get_or_404(estudiante.users_estudiante_id)

        if user.photo_storage:
            photo_path = os.path.abspath(user.photo_storage)
            if os.path.exists(photo_path):
                os.remove(photo_path)

        db.session.query(Parentesco).filter_by(estudiante_id=estudiante.id).delete()
        db.session.delete(estudiante)
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "Estudiante eliminado correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo eliminar: {str(e)}"}), 500

@estudiante_bp.route('/uploads/<rol>/<filename>', methods=['GET'])
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
