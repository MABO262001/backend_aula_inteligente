import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from ..extensions import db
from ..models.user import User
from ..models.rol import Rol
from ..models.estudiante import Estudiante
from ..models.parentesco import Parentesco
from ..models.apoderado import Apoderado

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
    url = f"{base_url}/api/estudiante/uploads/{role_name.lower()}/{safe_name}"
    return path, url

def to_int_if_str(val):
    if isinstance(val, int):
        return val
    if isinstance(val, str) and val.isdigit():
        return int(val)
    return None

def serializar_estudiante(estudiante, user):
    rol = Rol.query.get(user.rol_id)

    parentescos = estudiante.parentesco_estudiante
    apoderados = []
    for parentesco in parentescos:
        apo = parentesco.apoderado
        apo_user = User.query.get(apo.users_apoderado_id)
        apoderados.append({
            "tipo": parentesco.nombre,
            "apoderado": {
                "id": apo.id,
                "ci": apo.ci,
                "nombre": f"{apo.nombre} {apo.apellido}",
                "sexo": apo.sexo,
                "telefono": apo.telefono,
                "user": {
                    # "id": apo_user.id if apo_user else None,
                    # "name": apo_user.name if apo_user else None,
                    "email": apo_user.email if apo_user else None,
                    # "photo_url": apo_user.photo_url if apo_user else None,
                    # "status": apo_user.status if apo_user else None,
                }
            }
        })

    return {
        "estudiante_id": estudiante.id,
        "ci": estudiante.ci,
        "nombre": estudiante.nombre,
        "apellido": estudiante.apellido,
        "sexo": estudiante.sexo,
        "telefono": estudiante.telefono,
        "users_id": estudiante.users_id,
        "users_estudiante_id": estudiante.users_estudiante_id,
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

@estudiante_bp.route('/listar', methods=['GET'])
def listar_estudiantes():
    estudiantes = Estudiante.query.all()
    resultado = []

    for est in estudiantes:
        user = User.query.get(est.users_estudiante_id)
        if user:
            resultado.append(serializar_estudiante(est, user))

    return jsonify(resultado)

@estudiante_bp.route('/guardar_user', methods=['POST'])
def guardar_estudiante_user():
    try:
        data = request.form.to_dict()
        parentescos_raw = data.get("parentescos")
        parentescos = []
        if parentescos_raw:
            import json
            parentescos = json.loads(parentescos_raw)

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

        from werkzeug.security import generate_password_hash
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
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

        for p in parentescos:
            apo_ci = p.get("ci")
            tipo = p.get("tipo", "").strip()
            if not apo_ci or not tipo:
                continue
            apoderado = Apoderado.query.filter_by(ci=apo_ci).first()
            if apoderado:
                db.session.add(Parentesco(
                    nombre=tipo,
                    apoderado_id=apoderado.id,
                    estudiante_id=estudiante.id
                ))

        db.session.commit()

        return jsonify({
            "message": "Estudiante y usuario creados correctamente",
            "estudiante": serializar_estudiante(estudiante, new_user)
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad", "detail": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@estudiante_bp.route('/actualizar_user/<int:estudiante_id>', methods=['PATCH'])
def actualizar_estudiante_user(estudiante_id):
    estudiante = Estudiante.query.get_or_404(estudiante_id)
    user = User.query.get_or_404(estudiante.users_estudiante_id)

    try:
        data = request.form.to_dict()
        parentescos_raw = data.get("parentescos")
        parentescos = []
        if parentescos_raw:
            import json
            parentescos = json.loads(parentescos_raw)

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
            from werkzeug.security import generate_password_hash
            user.password = generate_password_hash(data['password'])

        file = request.files.get('photo')
        if file and allowed_file(file.filename):
            if user.photo_storage and os.path.exists(user.photo_storage):
                os.remove(user.photo_storage)
            photo_storage, photo_url = save_user_photo(file, user.name, "Estudiante")
            user.photo_storage = photo_storage
            user.photo_url = photo_url

        if 'ci' in data and data['ci'].isdigit():
            estudiante.ci = int(data['ci'])

        if 'nombre' in data:
            estudiante.nombre = data['nombre'].strip()

        if 'apellido' in data:
            estudiante.apellido = data['apellido'].strip()

        if 'sexo' in data:
            estudiante.sexo = data['sexo'].strip()

        if 'telefono' in data and data['telefono'].isdigit():
            estudiante.telefono = int(data['telefono'])

        if 'users_id' in data and data['users_id'].isdigit():
            estudiante.users_id = int(data['users_id'])

        if parentescos:

            Parentesco.query.filter_by(estudiante_id=estudiante.id).delete()
            for p in parentescos:
                apo_ci = p.get("ci")
                tipo = p.get("tipo", "").strip()
                if not apo_ci or not tipo:
                    continue
                apoderado = Apoderado.query.filter_by(ci=apo_ci).first()
                if apoderado:
                    db.session.add(Parentesco(
                        nombre=tipo,
                        apoderado_id=apoderado.id,
                        estudiante_id=estudiante.id
                    ))

        db.session.commit()

        return jsonify({
            "message": "Estudiante actualizado correctamente",
            "estudiante": serializar_estudiante(estudiante, user)
        })

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad", "detail": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@estudiante_bp.route('/desactivar_user/<int:estudiante_id>', methods=['DELETE'])
def desactivar_user_estudiante(estudiante_id):
    estudiante = Estudiante.query.get_or_404(estudiante_id)
    user = User.query.get_or_404(estudiante.users_estudiante_id)

    try:
        user.status = False
        db.session.commit()
        return jsonify({
            "message": "Estudiante y usuario desactivados correctamente",
            "estudiante_id": estudiante.id,
            "user_id": user.id,
            "ci": estudiante.ci,
            "nombre": estudiante.nombre,
            "apellido": estudiante.apellido,
            "sexo": estudiante.sexo,
            "telefono": estudiante.telefono,
            "status": user.status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo desactivar: {str(e)}"}), 500

@estudiante_bp.route('/eliminar_definitivamente/<int:estudiante_id>', methods=['DELETE'])
def eliminar_user_estudiante_definitivamente(estudiante_id):
    estudiante = Estudiante.query.get_or_404(estudiante_id)
    user = User.query.get_or_404(estudiante.users_estudiante_id)

    try:
        if user.photo_storage and os.path.exists(user.photo_storage):
            os.remove(user.photo_storage)

        Parentesco.query.filter_by(estudiante_id=estudiante.id).delete()
        db.session.delete(estudiante)
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            "message": "Estudiante y usuario eliminados permanentemente",
            "estudiante_id": estudiante_id
        })
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

@estudiante_bp.route('/buscar', methods=['GET'])
def buscar_estudiantes():
    args = request.args
    query = Estudiante.query

    if 'ci' in args and args['ci'].isdigit():
        query = query.filter(Estudiante.ci == int(args['ci']))
    if 'nombre' in args:
        query = query.filter(Estudiante.nombre.ilike(f"%{args['nombre']}%"))
    if 'apellido' in args:
        query = query.filter(Estudiante.apellido.ilike(f"%{args['apellido']}%"))
    if 'sexo' in args:
        query = query.filter(Estudiante.sexo.ilike(f"%{args['sexo']}%"))
    if 'telefono' in args and args['telefono'].isdigit():
        query = query.filter(Estudiante.telefono == int(args['telefono']))
    if 'users_id' in args and args['users_id'].isdigit():
        query = query.filter(Estudiante.users_id == int(args['users_id']))
    if 'users_estudiante_id' in args and args['users_estudiante_id'].isdigit():
        query = query.filter(Estudiante.users_estudiante_id == int(args['users_estudiante_id']))

    estudiantes = query.all()
    resultado = []

    for est in estudiantes:
        user = User.query.get(est.users_estudiante_id)
        if user:
            resultado.append(serializar_estudiante(est, user))

    return jsonify(resultado)
