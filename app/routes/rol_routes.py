from flask import Blueprint, request, jsonify
from ..models.rol import Rol
from ..extensions import db

rol_bp = Blueprint('rol_bp', __name__)

@rol_bp.route('/listar', methods=['GET'])
def listar_roles():
    roles = Rol.query.all()
    result = [{"id": rol.id, "nombre": rol.nombre} for rol in roles]
    return jsonify(result)

@rol_bp.route('/guardar', methods=['POST'])
def guardar_rol():
    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip()

        if not nombre:
            return jsonify({"error": "El campo 'nombre' es obligatorio."}), 400

        if Rol.query.filter_by(nombre=nombre).first():
            return jsonify({"error": "El rol ya existe."}), 409

        rol = Rol(nombre=nombre)
        db.session.add(rol)
        db.session.commit()
        return jsonify({"message": "Rol creado exitosamente", "rol_id": rol.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@rol_bp.route('/actualizar/<int:rol_id>', methods=['PUT'])
def actualizar_rol(rol_id):
    rol = Rol.query.get_or_404(rol_id)
    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip()

        if not nombre:
            return jsonify({"error": "El campo 'nombre' es obligatorio."}), 400

        if Rol.query.filter(Rol.nombre == nombre, Rol.id != rol_id).first():
            return jsonify({"error": "El nombre del rol ya está en uso."}), 409

        rol.nombre = nombre
        db.session.commit()
        return jsonify({"message": "Rol actualizado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar el rol: {str(e)}"}), 500

@rol_bp.route('/eliminar/<int:rol_id>', methods=['DELETE'])
def eliminar_rol(rol_id):
    rol = Rol.query.get_or_404(rol_id)
    try:
        db.session.delete(rol)
        db.session.commit()
        return jsonify({"message": "Rol eliminado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo eliminar el rol: {str(e)}"}), 500