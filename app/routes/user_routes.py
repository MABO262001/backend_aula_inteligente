from flask import Blueprint, request, current_app, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from ..models.user import User
from ..extensions import db
from datetime import datetime
import os

user_bp = Blueprint('user_bp', __name__)

# 📄 LISTAR con filtros
@user_bp.route('/', methods=['GET'])
def get_users():
    status = request.args.get('status')
    email = request.args.get('email')
    name = request.args.get('name')

    query = User.query

    if status == 'true':
        query = query.filter_by(status=True)
    elif status == 'false':
        query = query.filter_by(status=False)

    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    users = query.all()

    return jsonify([
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "photo_url": u.photo_url,
            "status": u.status
        } for u in users
    ])

# 🔍 BUSCAR
@user_bp.route('/buscar', methods=['GET'])
def search_users():
    q = request.args.get('q', '')
    results = User.query.filter(
        User.name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%")
    ).all()
    return jsonify([
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "photo_url": u.photo_url,
            "status": u.status
        } for u in results
    ])

# ✅ CREAR
@user_bp.route('/guardar', methods=['POST'])
def create_user():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        raw_password = request.form.get('password')
        status = request.form.get('status', 'true').lower() == 'true'

        if not name or not email or not raw_password:
            return jsonify({"error": "Campos 'name', 'email' y 'password' son obligatorios"}), 400

        password = generate_password_hash(raw_password)
        file = request.files.get('photo')
        photo_url = None
        photo_storage = None

        if file:
            model_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'users')
            os.makedirs(model_folder, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = secure_filename(f"{timestamp}_{file.filename}")
            filepath = os.path.join(model_folder, filename)
            file.save(filepath)

            photo_storage = filepath
            photo_url = f"{current_app.config['BASE_URL']}/api/users/uploads/{filename}"

        user = User(
            name=name,
            email=email,
            password=password,
            photo_url=photo_url,
            photo_storage=photo_storage,
            status=status
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "Usuario creado exitosamente",
            "id": user.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "El correo ya está registrado"}), 409

    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

# ✏️ ACTUALIZAR
@user_bp.route('/actualizar/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user = User.query.get_or_404(id)

        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        raw_password = request.form.get('password')
        if raw_password:
            user.password = generate_password_hash(raw_password)

        user.status = request.form.get('status', str(user.status)).lower() == 'true'

        file = request.files.get('photo')
        if file:
            if user.photo_storage and os.path.exists(user.photo_storage):
                os.remove(user.photo_storage)

            model_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'users')
            os.makedirs(model_folder, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = secure_filename(f"{timestamp}_{file.filename}")
            filepath = os.path.join(model_folder, filename)
            file.save(filepath)

            user.photo_storage = filepath
            user.photo_url = f"{current_app.config['BASE_URL']}/api/users/uploads/{filename}"

        db.session.commit()
        return jsonify({"message": "Usuario actualizado correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar: {str(e)}"}), 500

# 🗑️ DESACTIVAR
@user_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def deactivate_user(id):
    try:
        user = User.query.get_or_404(id)
        user.status = False
        db.session.commit()
        return jsonify({"message": "Usuario desactivado correctamente"})
    except Exception as e:
        return jsonify({"error": f"No se pudo desactivar el usuario: {str(e)}"}), 500

# 🌐 ACCEDER A LA FOTO
@user_bp.route('/uploads/<filename>')
def get_user_file(filename):
    model_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'users')
    return send_from_directory(model_folder, filename)
