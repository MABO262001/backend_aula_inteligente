import json
import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from ..models.user import User
from ..models.rol import Rol
from ..extensions import db
from datetime import datetime
from ..models.dia import Dia
from ..models.horario import Horario
from ..models.profesor import Profesor
from ..models.materia_profesor import MateriaProfesor
from ..models.materia_profesor_dia_horario import MateriaProfesorDiaHorario
from ..models.dia_horario import DiaHorario
from ..models.materia import Materia



profesor_bp = Blueprint('profesor_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_or_create_dia_horario(dia_nombre, hora_inicio, hora_final):
    dia = Dia.query.filter_by(nombre=dia_nombre).first()
    if not dia:
        dia = Dia(nombre=dia_nombre)
        db.session.add(dia)
        db.session.flush()

    horario = Horario.query.filter_by(hora_inicio=hora_inicio, hora_final=hora_final).first()
    if not horario:
        horario = Horario(hora_inicio=hora_inicio, hora_final=hora_final)
        db.session.add(horario)
        db.session.flush()

    dia_horario = DiaHorario.query.filter_by(dia_id=dia.id, horario_id=horario.id).first()
    if not dia_horario:
        dia_horario = DiaHorario(dia_id=dia.id, horario_id=horario.id)
        db.session.add(dia_horario)
        db.session.flush()

    return dia_horario.id

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_user_photo_by_role(file, user_name, role_name):
    upload_folder = os.path.abspath(current_app.config.get('UPLOAD_FOLDER', 'uploads'))
    model_folder = os.path.join(upload_folder, role_name.lower())
    os.makedirs(model_folder, exist_ok=True)

    ext = file.filename.rsplit('.', 1)[1].lower()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_name = secure_filename(f"{user_name}_{timestamp}.{ext}")
    filepath = os.path.join(model_folder, safe_name)
    file.save(filepath)

    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    public_url = f"{base_url}/api/profesores/uploads/{role_name.lower()}/{safe_name}"

    return filepath, public_url

@profesor_bp.route('/guardar', methods=['POST'])
def guardar_profesor():
    try:
        data = request.form.to_dict()
        materias_raw = data.get("materias")
        materias_info = json.loads(materias_raw) if materias_raw else []

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        ci = data.get('ci')
        nombre_prof = data.get('nombre_prof', '').strip()
        apellido_prof = data.get('apellido_prof', '').strip()
        telefono = data.get('telefono')
        direccion = data.get('direccion', '').strip()
        users_id = data.get('users_id')

        errors = []
        if len(name) < 3:
            errors.append("El campo 'name' debe tener al menos 3 caracteres.")
        if '@' not in email:
            errors.append("El campo 'email' debe contener '@'.")
        if len(password) < 6:
            errors.append("La contraseña debe tener al menos 6 caracteres.")
        if not ci or not ci.isdigit():
            errors.append("El campo 'ci' debe ser numérico.")
        if not users_id or not str(users_id).isdigit():
            errors.append("El campo 'users_id' es obligatorio y numérico.")
        if len(nombre_prof) == 0:
            errors.append("El campo 'nombre_prof' es obligatorio.")
        if len(apellido_prof) == 0:
            errors.append("El campo 'apellido_prof' es obligatorio.")
        if len(direccion) == 0:
            errors.append("El campo 'direccion' es obligatorio.")
        if errors:
            return jsonify({"errors": errors}), 400

        if User.query.filter_by(name=name).first():
            return jsonify({"error": "El nombre de usuario ya existe"}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "El email ya está registrado"}), 409

        rol_profesor = Rol.query.filter_by(nombre="Profesor").first()
        if not rol_profesor:
            return jsonify({"error": "Rol 'Profesor' no encontrado"}), 500

        photo_url = None
        photo_storage = None
        file = request.files.get('photo')
        if file:
            if not allowed_file(file.filename):
                return jsonify({"error": "Formato de imagen no permitido"}), 400
            photo_storage, photo_url = save_user_photo_by_role(file, name, rol_profesor.nombre)

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
        db.session.flush()

        profesor = Profesor(
            ci=int(ci),
            nombre=nombre_prof,
            apellido=apellido_prof,
            telefono=int(telefono) if telefono and str(telefono).isdigit() else None,
            direccion=direccion,
            users_id=int(users_id),
            users_profesor_id=user_profesor.id
        )
        db.session.add(profesor)
        db.session.flush()

        materias_resultado = []

        for materia_data in materias_info:
            materia_id = materia_data.get("materia_id")
            horario_id = materia_data.get("horario_id")
            dias = materia_data.get("dias", [])

            if not materia_id or not horario_id or not dias:
                continue

            materia_profesor = MateriaProfesor(
                materia_id=materia_id,
                profesor_id=profesor.id
            )
            db.session.add(materia_profesor)
            db.session.flush()

            dias_horarios_resultado = []

            for dia_nombre in dias:
                dia = Dia.query.filter_by(nombre=dia_nombre).first()
                if not dia:
                    continue

                dia_horario = DiaHorario.query.filter_by(horario_id=horario_id, dia_id=dia.id).first()
                if not dia_horario:
                    continue

                db.session.add(MateriaProfesorDiaHorario(
                    materia_profesor_id=materia_profesor.id,
                    dia_horario_id=dia_horario.id
                ))

                dias_horarios_resultado.append({
                    "dias_horarios_id": dia_horario.id,
                    "dia_id": dia.id,
                    "dias": dia.nombre,
                    "horario_id": dia_horario.horario.id,
                    "hora_inicio": dia_horario.horario.hora_inicio.strftime("%H:%M:%S"),
                    "hora_final": dia_horario.horario.hora_final.strftime("%H:%M:%S")
                })

            materia = Materia.query.get(materia_id)
            materias_resultado.append({
                "materia_id": materia.id,
                "materia_nombre": materia.nombre,
                "dias_horarios": dias_horarios_resultado
            })

        db.session.commit()

        return jsonify({
            "message": "Profesor registrado exitosamente",
            "user": {
                "id": user_profesor.id,
                "name": user_profesor.name,
                "email": user_profesor.email,
                "photo_url": user_profesor.photo_url,
                "status": user_profesor.status
            },
            "profesor": {
                "id": profesor.id,
                "ci": profesor.ci,
                "nombre_profesor": profesor.nombre,
                "apellido_profesor": profesor.apellido,
                "telefono": profesor.telefono,
                "direccion": profesor.direccion,
                "users_id": profesor.users_id,
                "users_profesor_id": profesor.users_profesor_id
            },
            "materias": materias_resultado
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad en la base de datos", "detail": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error guardando profesor: {str(e)}")
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@profesor_bp.route('/actualizar/<int:profesor_id>', methods=['PATCH'])
def actualizar_profesor(profesor_id):
    profesor = Profesor.query.get_or_404(profesor_id)
    user = User.query.get_or_404(profesor.users_profesor_id)

    try:
        data = request.form.to_dict()
        materias_raw = data.get("materias")

        name = data.get('name', user.name).strip()
        email = data.get('email', user.email).strip()
        password = data.get('password', '')
        ci = data.get('ci', str(profesor.ci))
        nombre_prof = data.get('nombre_prof', profesor.nombre).strip()
        apellido_prof = data.get('apellido_prof', profesor.apellido).strip()
        telefono = data.get('telefono', str(profesor.telefono) if profesor.telefono else '')
        direccion = data.get('direccion', profesor.direccion).strip()
        users_id = data.get('users_id', str(profesor.users_id))

        errors = []
        if len(name) < 3:
            errors.append("El campo 'name' debe tener al menos 3 caracteres.")
        if '@' not in email:
            errors.append("El campo 'email' debe contener '@'.")
        if password and len(password) < 6:
            errors.append("La contraseña debe tener al menos 6 caracteres.")
        if not ci.isdigit():
            errors.append("El campo 'ci' debe ser numérico.")
        if not users_id.isdigit():
            errors.append("El campo 'users_id' es obligatorio y numérico.")
        if not nombre_prof:
            errors.append("El campo 'nombre_prof' es obligatorio.")
        if not apellido_prof:
            errors.append("El campo 'apellido_prof' es obligatorio.")
        if not direccion:
            errors.append("El campo 'direccion' es obligatorio.")
        if errors:
            return jsonify({"errors": errors}), 400

        if User.query.filter(User.name == name, User.id != user.id).first():
            return jsonify({"error": "El nombre de usuario ya existe"}), 409
        if User.query.filter(User.email == email, User.id != user.id).first():
            return jsonify({"error": "El email ya está registrado"}), 409

        rol_profesor = Rol.query.filter_by(nombre="Profesor").first()
        if not rol_profesor:
            return jsonify({"error": "Rol 'Profesor' no encontrado"}), 500

        file = request.files.get('photo')
        if file and allowed_file(file.filename):
            if user.photo_storage and os.path.exists(user.photo_storage):
                os.remove(user.photo_storage)
            photo_storage, photo_url = save_user_photo_by_role(file, name, rol_profesor.nombre)
            user.photo_storage = photo_storage
            user.photo_url = photo_url

        user.name = name
        user.email = email
        if password:
            user.password = generate_password_hash(password)

        profesor.ci = int(ci)
        profesor.nombre = nombre_prof
        profesor.apellido = apellido_prof
        profesor.telefono = int(telefono) if telefono.isdigit() else None
        profesor.direccion = direccion
        profesor.users_id = int(users_id)

        if materias_raw is not None:
            materias_info = json.loads(materias_raw)
            for mp in profesor.materias_profesor:
                for mph in mp.materia_profesor_dia_horario:
                    db.session.delete(mph)
                db.session.delete(mp)

            for materia_data in materias_info:
                materia_id = materia_data.get("materia_id")
                horario_id = materia_data.get("horario_id")
                dias = materia_data.get("dias", [])

                if not materia_id or not horario_id or not dias:
                    continue

                materia_profesor = MateriaProfesor(
                    materia_id=materia_id,
                    profesor_id=profesor.id
                )
                db.session.add(materia_profesor)
                db.session.flush()

                for dia_nombre in dias:
                    dia = Dia.query.filter_by(nombre=dia_nombre).first()
                    if not dia:
                        continue
                    dia_horario = DiaHorario.query.filter_by(horario_id=horario_id, dia_id=dia.id).first()
                    if not dia_horario:
                        continue

                    db.session.add(MateriaProfesorDiaHorario(
                        materia_profesor_id=materia_profesor.id,
                        dia_horario_id=dia_horario.id
                    ))

        db.session.commit()

        materias_resultado = []
        for mp in profesor.materias_profesor:
            materia = mp.materia
            dias_horarios = []
            for mph in mp.materia_profesor_dia_horario:
                dh = mph.dia_horario
                dias_horarios.append({
                    "dias_horarios_id": dh.id,
                    "dia_id": dh.dia.id,
                    "dias": dh.dia.nombre,
                    "horario_id": dh.horario.id,
                    "hora_inicio": dh.horario.hora_inicio.strftime("%H:%M:%S"),
                    "hora_final": dh.horario.hora_final.strftime("%H:%M:%S")
                })

            materias_resultado.append({
                "materia_id": materia.id,
                "materia_nombre": materia.nombre,
                "dias_horarios": dias_horarios
            })

        return jsonify({
            "message": "Profesor, usuario y materias actualizadas correctamente",
            "profesor": {
                "id": profesor.id,
                "ci": profesor.ci,
                "nombre_profesor": profesor.nombre,
                "apellido_profesor": profesor.apellido,
                "telefono": profesor.telefono,
                "direccion": profesor.direccion,
                "users_id": profesor.users_id,
                "users_profesor_id": profesor.users_profesor_id
            },
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "photo_url": user.photo_url,
                "status": user.status
            },
            "materias": materias_resultado
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al actualizar profesor: {str(e)}")
        return jsonify({"error": f"Error al actualizar: {str(e)}"}), 500


@profesor_bp.route('/listar', methods=['GET'])
def listar_profesores():
    profesores = Profesor.query.all()
    resultado = []

    for profesor in profesores:
        user = User.query.get(profesor.users_profesor_id)

        materias_resultado = []
        for mp in profesor.materias_profesor:
            materia = mp.materia

            # Agrupar días por materia_id y horario_id
            grupo_clave = (materia.id,)
            horarios_por_materia = {}

            for mph in mp.materia_profesor_dia_horario:
                dh = mph.dia_horario
                key = (materia.id, dh.horario.id)

                if key not in horarios_por_materia:
                    horarios_por_materia[key] = {
                        "materia_id": materia.id,
                        "horario_id": dh.horario.id,
                        "dias": []
                    }

                horarios_por_materia[key]["dias"].append(dh.dia.nombre)

            materias_resultado.extend(horarios_por_materia.values())

        resultado.append({
            "profesor": {
                "id": profesor.id,
                "ci": profesor.ci,
                "nombre_profesor": profesor.nombre,
                "apellido_profesor": profesor.apellido,
                "telefono": profesor.telefono,
                "direccion": profesor.direccion,
                "users_id": profesor.users_id,
                "users_profesor_id": profesor.users_profesor_id
            },
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "photo_url": user.photo_url,
                "status": user.status
            },
            "materias": materias_resultado
        })

    return jsonify(resultado)


@profesor_bp.route('/buscar', methods=['GET'])
def buscar_profesores():
    query_params = request.args
    query = Profesor.query


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


@profesor_bp.route('/uploads/<rol>/<filename>', methods=['GET'])
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


