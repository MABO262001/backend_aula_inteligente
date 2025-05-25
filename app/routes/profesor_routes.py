from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.profesor import Profesor

profesor_bp = Blueprint('profesor', __name__)

# Listar todos los registros
@profesor_bp.route('/listar', methods=['GET'])
def listar():
    registros = Profesor.query.all()
    result = [
        {
            "id": r.id,
            "ci": r.ci,
            "nombre": r.nombre,
            "apellido": r.apellido,
            "telefono": r.telefono,
            "direccion": r.direccion,
            "users_id": r.users_id,
            "users_profesor_id": r.users_profesor_id
        } for r in registros
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@profesor_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    registro = Profesor.query.get_or_404(id)
    result = {
        "id": registro.id,
        "ci": registro.ci,
        "nombre": registro.nombre,
        "apellido": registro.apellido,
        "telefono": registro.telefono,
        "direccion": registro.direccion,
        "users_id": registro.users_id,
        "users_profesor_id": registro.users_profesor_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@profesor_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_registro = Profesor(
        ci=data['ci'],
        nombre=data['nombre'],
        apellido=data['apellido'],
        telefono=data.get('telefono'),
        direccion=data['direccion'],
        users_id=data['users_id'],
        users_profesor_id=data.get('users_profesor_id')
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@profesor_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    registro = Profesor.query.get_or_404(id)
    registro.ci = data.get('ci', registro.ci)
    registro.nombre = data.get('nombre', registro.nombre)
    registro.apellido = data.get('apellido', registro.apellido)
    registro.telefono = data.get('telefono', registro.telefono)
    registro.direccion = data.get('direccion', registro.direccion)
    registro.users_id = data.get('users_id', registro.users_id)
    registro.users_profesor_id = data.get('users_profesor_id', registro.users_profesor_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@profesor_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    registro = Profesor.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200