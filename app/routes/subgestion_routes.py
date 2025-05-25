from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.subgestion import Subgestion

subgestion_bp = Blueprint('subgestion', __name__)

# Listar todos los registros
@subgestion_bp.route('/listar', methods=['GET'])
def listar():
    registros = Subgestion.query.all()
    result = [
        {
            "id": r.id,
            "nombre": r.nombre,
            "fecha_inicio": str(r.fecha_inicio),
            "fecha_final": str(r.fecha_final),
            "gestion_id": r.gestion_id
        } for r in registros
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@subgestion_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    registro = Subgestion.query.get_or_404(id)
    result = {
        "id": registro.id,
        "nombre": registro.nombre,
        "fecha_inicio": str(registro.fecha_inicio),
        "fecha_final": str(registro.fecha_final),
        "gestion_id": registro.gestion_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@subgestion_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_registro = Subgestion(
        nombre=data['nombre'],
        fecha_inicio=data['fecha_inicio'],
        fecha_final=data['fecha_final'],
        gestion_id=data['gestion_id']
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@subgestion_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    registro = Subgestion.query.get_or_404(id)
    registro.nombre = data.get('nombre', registro.nombre)
    registro.fecha_inicio = data.get('fecha_inicio', registro.fecha_inicio)
    registro.fecha_final = data.get('fecha_final', registro.fecha_final)
    registro.gestion_id = data.get('gestion_id', registro.gestion_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@subgestion_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    registro = Subgestion.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200