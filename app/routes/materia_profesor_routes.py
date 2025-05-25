from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.materia_horario_curso_paralelo import MateriaHorarioCursoParalelo

materia_horario_curso_paralelo_bp = Blueprint('materia_horario_curso_paralelo', __name__)

# Listar todos los registros
@materia_horario_curso_paralelo_bp.route('/listar', methods=['GET'])
def listar():
    registros = MateriaHorarioCursoParalelo.query.all()
    result = [
        {
            "id": r.id,
            "gestion_curso_paralelo_id": r.gestion_curso_paralelo_id,
            "materia_profesor_dia_horario_id": r.materia_profesor_dia_horario_id
        } for r in registros
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@materia_horario_curso_paralelo_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    registro = MateriaHorarioCursoParalelo.query.get_or_404(id)
    result = {
        "id": registro.id,
        "gestion_curso_paralelo_id": registro.gestion_curso_paralelo_id,
        "materia_profesor_dia_horario_id": registro.materia_profesor_dia_horario_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@materia_horario_curso_paralelo_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_registro = MateriaHorarioCursoParalelo(
        gestion_curso_paralelo_id=data['gestion_curso_paralelo_id'],
        materia_profesor_dia_horario_id=data['materia_profesor_dia_horario_id']
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@materia_horario_curso_paralelo_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    registro = MateriaHorarioCursoParalelo.query.get_or_404(id)
    registro.gestion_curso_paralelo_id = data.get('gestion_curso_paralelo_id', registro.gestion_curso_paralelo_id)
    registro.materia_profesor_dia_horario_id = data.get('materia_profesor_dia_horario_id', registro.materia_profesor_dia_horario_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@materia_horario_curso_paralelo_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    registro = MateriaHorarioCursoParalelo.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200