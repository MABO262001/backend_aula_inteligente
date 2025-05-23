from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.apoderado import Apoderado

apoderado_bp = Blueprint('apoderado', __name__)

# Listar todos los registros
@apoderado_bp.route('/listar', methods=['GET'])
def listar():
    apoderados = Apoderado.query.all()
    result = [
        {
            "id": ap.id,
            "ci": ap.ci,
            "nombre": ap.nombre,
            "apellido": ap.apellido,
            "sexo": ap.sexo,
            "telefono": ap.telefono,
            "users_id": ap.users_id,
            "users_apoderado_id": ap.users_apoderado_id
        } for ap in apoderados
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@apoderado_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    apoderado = Apoderado.query.get_or_404(id)
    result = {
        "id": apoderado.id,
        "ci": apoderado.ci,
        "nombre": apoderado.nombre,
        "apellido": apoderado.apellido,
        "sexo": apoderado.sexo,
        "telefono": apoderado.telefono,
        "users_id": apoderado.users_id,
        "users_apoderado_id": apoderado.users_apoderado_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@apoderado_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_apoderado = Apoderado(
        ci=data['ci'],
        nombre=data['nombre'],
        apellido=data['apellido'],
        sexo=data['sexo'],
        telefono=data.get('telefono'),
        users_id=data['users_id'],
        users_apoderado_id=data.get('users_apoderado_id')
    )
    db.session.add(nuevo_apoderado)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@apoderado_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    apoderado = Apoderado.query.get_or_404(id)
    apoderado.ci = data.get('ci', apoderado.ci)
    apoderado.nombre = data.get('nombre', apoderado.nombre)
    apoderado.apellido = data.get('apellido', apoderado.apellido)
    apoderado.sexo = data.get('sexo', apoderado.sexo)
    apoderado.telefono = data.get('telefono', apoderado.telefono)
    apoderado.users_id = data.get('users_id', apoderado.users_id)
    apoderado.users_apoderado_id = data.get('users_apoderado_id', apoderado.users_apoderado_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@apoderado_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    apoderado = Apoderado.query.get_or_404(id)
    db.session.delete(apoderado)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200