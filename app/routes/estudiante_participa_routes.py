
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.estudiante_participa import EstudianteParticipa

estudiante_participa_bp = Blueprint('estudiante_participa', __name__)

# Listar todos los registros
@estudiante_participa_bp.route('/listar', methods=['GET'])
def listar():
    participaciones = EstudianteParticipa.query.all()
    result = [
        {
            "id": p.id,
            "estado": p.estado,
            "participacion_id": p.participacion_id,
            "estudiante_id": p.estudiante_id
        } for p in participaciones
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@estudiante_participa_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    participacion = EstudianteParticipa.query.get_or_404(id)
    result = {
        "id": participacion.id,
        "estado": participacion.estado,
        "participacion_id": participacion.participacion_id,
        "estudiante_id": participacion.estudiante_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@estudiante_participa_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nueva_participacion = EstudianteParticipa(
        estado=data['estado'],
        participacion_id=data['participacion_id'],
        estudiante_id=data['estudiante_id']
    )
    db.session.add(nueva_participacion)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@estudiante_participa_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    participacion = EstudianteParticipa.query.get_or_404(id)
    participacion.estado = data.get('estado', participacion.estado)
    participacion.participacion_id = data.get('participacion_id', participacion.participacion_id)
    participacion.estudiante_id = data.get('estudiante_id', participacion.estudiante_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@estudiante_participa_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    participacion = EstudianteParticipa.query.get_or_404(id)
    db.session.delete(participacion)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200