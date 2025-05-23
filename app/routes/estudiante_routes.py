from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.estudiante import Estudiante

estudiante_bp = Blueprint('estudiante', __name__)

# Listar todos los registros
@estudiante_bp.route('/listar', methods=['GET'])
def listar():
    estudiantes = Estudiante.query.all()
    result = [
        {
            "id": e.id,
            "ci": e.ci,
            "nombre": e.nombre,
            "apellido": e.apellido,
            "sexo": e.sexo,
            "telefono": e.telefono,
            "users_id": e.users_id,
            "users_estudiante_id": e.users_estudiante_id
        } for e in estudiantes
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@estudiante_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    estudiante = Estudiante.query.get_or_404(id)
    result = {
        "id": estudiante.id,
        "ci": estudiante.ci,
        "nombre": estudiante.nombre,
        "apellido": estudiante.apellido,
        "sexo": estudiante.sexo,
        "telefono": estudiante.telefono,
        "users_id": estudiante.users_id,
        "users_estudiante_id": estudiante.users_estudiante_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@estudiante_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_estudiante = Estudiante(
        ci=data['ci'],
        nombre=data['nombre'],
        apellido=data['apellido'],
        sexo=data['sexo'],
        telefono=data.get('telefono'),
        users_id=data['users_id'],
        users_estudiante_id=data.get('users_estudiante_id')
    )
    db.session.add(nuevo_estudiante)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@estudiante_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    estudiante = Estudiante.query.get_or_404(id)
    estudiante.ci = data.get('ci', estudiante.ci)
    estudiante.nombre = data.get('nombre', estudiante.nombre)
    estudiante.apellido = data.get('apellido', estudiante.apellido)
    estudiante.sexo = data.get('sexo', estudiante.sexo)
    estudiante.telefono = data.get('telefono', estudiante.telefono)
    estudiante.users_id = data.get('users_id', estudiante.users_id)
    estudiante.users_estudiante_id = data.get('users_estudiante_id', estudiante.users_estudiante_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@estudiante_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    estudiante = Estudiante.query.get_or_404(id)
    db.session.delete(estudiante)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200