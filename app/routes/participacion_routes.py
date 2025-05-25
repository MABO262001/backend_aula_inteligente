from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.participacion import Participacion

participacion_bp = Blueprint('participacion', __name__)

# Listar todos los registros
@participacion_bp.route('/listar', methods=['GET'])
def listar():
    registros = Participacion.query.all()
    result = [
        {
            "id": r.id,
            "descripcion": r.descripcion,
            "hora": str(r.hora),
            "fecha": str(r.fecha),
            "materia_horario_curso_paralelo_id": r.materia_horario_curso_paralelo_id
        } for r in registros
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@participacion_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    registro = Participacion.query.get_or_404(id)
    result = {
        "id": registro.id,
        "descripcion": registro.descripcion,
        "hora": str(registro.hora),
        "fecha": str(registro.fecha),
        "materia_horario_curso_paralelo_id": registro.materia_horario_curso_paralelo_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@participacion_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_registro = Participacion(
        descripcion=data['descripcion'],
        hora=data['hora'],
        fecha=data['fecha'],
        materia_horario_curso_paralelo_id=data['materia_horario_curso_paralelo_id']
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@participacion_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    registro = Participacion.query.get_or_404(id)
    registro.descripcion = data.get('descripcion', registro.descripcion)
    registro.hora = data.get('hora', registro.hora)
    registro.fecha = data.get('fecha', registro.fecha)
    registro.materia_horario_curso_paralelo_id = data.get('materia_horario_curso_paralelo_id', registro.materia_horario_curso_paralelo_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@participacion_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    registro = Participacion.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200