from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.curso import Curso

curso_bp = Blueprint('curso', __name__)

# Listar todos los registros
@curso_bp.route('/listar', methods=['GET'])
def listar():
    cursos = Curso.query.all()
    result = [
        {
            "id": c.id,
            "nombre": c.nombre
        } for c in cursos
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@curso_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    curso = Curso.query.get_or_404(id)
    result = {
        "id": curso.id,
        "nombre": curso.nombre
    }
    return jsonify(result), 200

# Crear un nuevo registro
@curso_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nuevo_curso = Curso(
        nombre=data['nombre']
    )
    db.session.add(nuevo_curso)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@curso_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    curso = Curso.query.get_or_404(id)
    curso.nombre = data.get('nombre', curso.nombre)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@curso_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    curso = Curso.query.get_or_404(id)
    db.session.delete(curso)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200