from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.nota import Nota

nota_bp = Blueprint('nota', __name__)

# Listar todos los registros
@nota_bp.route('/listar', methods=['GET'])
def listar():
    registros = Nota.query.all()
    result = [
        {
            "id": r.id,
            "promedio_final": r.promedio_final,
            "estudiante_id": r.estudiante_id,
            "materia_horario_curso_paralelo_id": r.materia_horario_curso_paralelo_id
        } for r in registros
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@nota_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    registro = Nota.query.get_or_404(id)
    result = {
        "id": registro.id,
        "promedio_final": registro.promedio_final,
        "estudiante_id": registro.estudiante_id,
        "materia_horario_curso_paralelo_id": registro.materia_horario_curso_paralelo_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@nota_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_registro = Nota(
        promedio_final=data['promedio_final'],
        estudiante_id=data['estudiante_id'],
        materia_horario_curso_paralelo_id=data['materia_horario_curso_paralelo_id']
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@nota_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    registro = Nota.query.get_or_404(id)
    registro.promedio_final = data.get('promedio_final', registro.promedio_final)
    registro.estudiante_id = data.get('estudiante_id', registro.estudiante_id)
    registro.materia_horario_curso_paralelo_id = data.get('materia_horario_curso_paralelo_id', registro.materia_horario_curso_paralelo_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@nota_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    registro = Nota.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200