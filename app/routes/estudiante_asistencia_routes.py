from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.estudiante_asistencia import EstudianteAsistencia

estudiante_asistencia_bp = Blueprint('estudiante_asistencia', __name__)

# Listar todos los registros
@estudiante_asistencia_bp.route('/listar', methods=['GET'])
def listar():
    asistencias = EstudianteAsistencia.query.all()
    result = [
        {
            "id": a.id,
            "estado": a.estado,
            "estudiante_id": a.estudiante_id,
            "asistencia_id": a.asistencia_id
        } for a in asistencias
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@estudiante_asistencia_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    asistencia = EstudianteAsistencia.query.get_or_404(id)
    result = {
        "id": asistencia.id,
        "estado": asistencia.estado,
        "estudiante_id": asistencia.estudiante_id,
        "asistencia_id": asistencia.asistencia_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@estudiante_asistencia_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nueva_asistencia = EstudianteAsistencia(
        estado=data['estado'],
        estudiante_id=data['estudiante_id'],
        asistencia_id=data['asistencia_id']
    )
    db.session.add(nueva_asistencia)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@estudiante_asistencia_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    asistencia = EstudianteAsistencia.query.get_or_404(id)
    asistencia.estado = data.get('estado', asistencia.estado)
    asistencia.estudiante_id = data.get('estudiante_id', asistencia.estudiante_id)
    asistencia.asistencia_id = data.get('asistencia_id', asistencia.asistencia_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@estudiante_asistencia_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    asistencia = EstudianteAsistencia.query.get_or_404(id)
    db.session.delete(asistencia)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200