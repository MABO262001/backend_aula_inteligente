from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.gestion_curso_paralelo import GestionCursoParalelo

gestion_curso_paralelo_bp = Blueprint('gestion_curso_paralelo', __name__)

# Listar todos los registros
@gestion_curso_paralelo_bp.route('/listar', methods=['GET'])
def listar():
    registros = GestionCursoParalelo.query.all()
    result = [
        {
            "id": r.id,
            "curso_paralelo_id": r.curso_paralelo_id,
            "gestion_id": r.gestion_id
        } for r in registros
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@gestion_curso_paralelo_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    registro = GestionCursoParalelo.query.get_or_404(id)
    result = {
        "id": registro.id,
        "curso_paralelo_id": registro.curso_paralelo_id,
        "gestion_id": registro.gestion_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@gestion_curso_paralelo_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_registro = GestionCursoParalelo(
        curso_paralelo_id=data['curso_paralelo_id'],
        gestion_id=data['gestion_id']
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@gestion_curso_paralelo_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    registro = GestionCursoParalelo.query.get_or_404(id)
    registro.curso_paralelo_id = data.get('curso_paralelo_id', registro.curso_paralelo_id)
    registro.gestion_id = data.get('gestion_id', registro.gestion_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@gestion_curso_paralelo_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    registro = GestionCursoParalelo.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200