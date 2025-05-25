from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.paralelo import Paralelo

paralelo_bp = Blueprint('paralelo', __name__)

# Listar todos los registros
@paralelo_bp.route('/listar', methods=['GET'])
def listar():
    registros = Paralelo.query.all()
    result = [
        {
            "id": r.id,
            "nombre": r.nombre
        } for r in registros
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@paralelo_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    registro = Paralelo.query.get_or_404(id)
    result = {
        "id": registro.id,
        "nombre": registro.nombre
    }
    return jsonify(result), 200

# Crear un nuevo registro
@paralelo_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_registro = Paralelo(
        nombre=data['nombre']
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@paralelo_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    registro = Paralelo.query.get_or_404(id)
    registro.nombre = data.get('nombre', registro.nombre)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@paralelo_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    registro = Paralelo.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200