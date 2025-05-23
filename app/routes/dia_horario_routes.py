from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.dia_horario import DiaHorario

dia_horario_bp = Blueprint('dia_horario', __name__)

# Listar todos los registros
@dia_horario_bp.route('/listar', methods=['GET'])
def listar():
    dia_horarios = DiaHorario.query.all()
    result = [
        {
            "id": dh.id,
            "dia_id": dh.dia_id,
            "horario_id": dh.horario_id
        } for dh in dia_horarios
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@dia_horario_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    dia_horario = DiaHorario.query.get_or_404(id)
    result = {
        "id": dia_horario.id,
        "dia_id": dia_horario.dia_id,
        "horario_id": dia_horario.horario_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@dia_horario_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_dia_horario = DiaHorario(
        dia_id=data['dia_id'],
        horario_id=data['horario_id']
    )
    db.session.add(nuevo_dia_horario)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@dia_horario_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    dia_horario = DiaHorario.query.get_or_404(id)
    dia_horario.dia_id = data.get('dia_id', dia_horario.dia_id)
    dia_horario.horario_id = data.get('horario_id', dia_horario.horario_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@dia_horario_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    dia_horario = DiaHorario.query.get_or_404(id)
    db.session.delete(dia_horario)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200