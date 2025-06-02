from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.matricula import Matricula

matricula_bp = Blueprint('matricula', __name__)

# Listar todos los registros
@matricula_bp.route('/listar', methods=['GET'])
def listar():
    registros = Matricula.query.all()
    result = [
        {
            "id": r.id,
            "fecha": r.fecha,
            "monto": r.monto,
            "parentesco_id": r.parentesco_id,
            "subgestion_id": r.subgestion_id,
            "users_id": r.users_id
        } for r in registros
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@matricula_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    registro = Matricula.query.get_or_404(id)
    result = {
        "id": registro.id,
        "fecha": registro.fecha,
        "monto": registro.monto,
        "parentesco_id": registro.parentesco_id,
        "subgestion_id": registro.subgestion_id,
        "users_id": registro.users_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@matricula_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_registro = Matricula(
        fecha=data['fecha'],
        monto=data['monto'],
        parentesco_id=data['parentesco_id'],
        subgestion_id=data['subgestion_id'],
        users_id=data['users_id']
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@matricula_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    registro = Matricula.query.get_or_404(id)
    registro.fecha = data.get('fecha', registro.fecha)
    registro.monto = data.get('monto', registro.monto)
    registro.parentesco_id = data.get('parentesco_id', registro.parentesco_id)
    registro.subgestion_id = data.get('subgestion_id', registro.subgestion_id)
    registro.users_id = data.get('users_id', registro.users_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@matricula_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    registro = Matricula.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200


