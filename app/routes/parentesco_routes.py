from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.parentesco import Parentesco

parentesco_bp = Blueprint('parentesco', __name__)

# Listar todos los registros
@parentesco_bp.route('/listar', methods=['GET'])
def listar():
    registros = Parentesco.query.all()
    result = [
        {
            "id": r.id,
            "nombre": r.nombre,
            "apoderado_id": r.apoderado_id,
            "estudiante_id": r.estudiante_id
        } for r in registros
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@parentesco_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    registro = Parentesco.query.get_or_404(id)
    result = {
        "id": registro.id,
        "nombre": registro.nombre,
        "apoderado_id": registro.apoderado_id,
        "estudiante_id": registro.estudiante_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@parentesco_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_registro = Parentesco(
        nombre=data['nombre'],
        apoderado_id=data['apoderado_id'],
        estudiante_id=data['estudiante_id']
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@parentesco_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    registro = Parentesco.query.get_or_404(id)
    registro.nombre = data.get('nombre', registro.nombre)
    registro.apoderado_id = data.get('apoderado_id', registro.apoderado_id)
    registro.estudiante_id = data.get('estudiante_id', registro.estudiante_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@parentesco_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    registro = Parentesco.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200