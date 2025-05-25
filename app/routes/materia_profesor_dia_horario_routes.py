from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.materia_profesor_dia_horario import MateriaProfesorDiaHorario

materia_profesor_dia_horario_bp = Blueprint('materia_profesor_dia_horario', __name__)

# Listar todos los registros
@materia_profesor_dia_horario_bp.route('/listar', methods=['GET'])
def listar():
    registros = MateriaProfesorDiaHorario.query.all()
    result = [
        {
            "id": r.id,
            "materia_profesor_id": r.materia_profesor_id,
            "dia_horario_id": r.dia_horario_id
        } for r in registros
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@materia_profesor_dia_horario_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    registro = MateriaProfesorDiaHorario.query.get_or_404(id)
    result = {
        "id": registro.id,
        "materia_profesor_id": registro.materia_profesor_id,
        "dia_horario_id": registro.dia_horario_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@materia_profesor_dia_horario_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_registro = MateriaProfesorDiaHorario(
        materia_profesor_id=data['materia_profesor_id'],
        di