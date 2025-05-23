from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.asistencia import Asistencia

asistencia_bp = Blueprint('asistencia', __name__)

# Listar todos los registros
@asistencia_bp.route('/listar', methods=['GET'])
def listar():
    asistencias = Asistencia.query.all()
    result = [
        {
            "id": a.id,
            "hora": a.hora.strftime('%H:%M:%S'),
            "fecha": a.fecha.strftime('%Y-%m-%d'),
            "materia_horario_curso_paralelo_id": a.materia_horario_curso_paralelo_id
        } for a in asistencias
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@asistencia_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    asistencia = Asistencia.query.get_or_404(id)
    result = {
        "id": asistencia.id,
        "hora": asistencia.hora.strftime('%H:%M:%S'),
        "fecha": asistencia.fecha.strftime('%Y-%m-%d'),
        "materia_horario_curso_paralelo_id": asistencia.materia_horario_curso_paralelo_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@asistencia_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nueva_asistencia = Asistencia(
        hora=data['hora'],
        fecha=data['fecha'],
        materia_horario_curso_paralelo_id=data['materia_horario_curso_paralelo_id']
    )
    db.session.add(nueva_asistencia)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@asistencia_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    asistencia = Asistencia.query.get_or_404(id)
    asistencia.hora = data.get('hora', asistencia.hora)
    asistencia.fecha = data.get('fecha', asistencia.fecha)
    asistencia.materia_horario_curso_paralelo_id = data.get('materia_horario_curso_paralelo_id', asistencia.materia_horario_curso_paralelo_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@asistencia_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    asistencia = Asistencia.query.get_or_404(id)
    db.session.delete(asistencia)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200