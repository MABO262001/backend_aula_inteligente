from flask import Blueprint, request, jsonify
from app.models.materia import Materia
from app.extensions import db

materia_bp = Blueprint('materia_bp', __name__)

@materia_bp.route('/listar', methods=['GET'])
def listar_materias():
    materias = Materia.query.all()
    result = [{"id": materia.id, "sigla": materia.sigla, "nombre": materia.nombre} for materia in materias]
    return jsonify(result)

@materia_bp.route('/buscar', methods=['GET'])
def buscar_materia():
    try:
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify({"error": "El parámetro 'query' es obligatorio."}), 400

        materias = Materia.query.filter(
            (Materia.sigla.ilike(f"%{query}%")) | (Materia.nombre.ilike(f"%{query}%"))
        ).all()

        if not materias:
            return jsonify({"message": "No se encontraron materias que coincidan con la búsqueda."}), 404

        result = [{"id": materia.id, "sigla": materia.sigla, "nombre": materia.nombre} for materia in materias]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@materia_bp.route('/guardar', methods=['POST'])
def guardar_materia():
    try:
        data = request.get_json()
        sigla = data.get('sigla')
        nombre = data.get('nombre')

        if not sigla or not nombre:
            return jsonify({"error": "Los campos 'sigla' y 'nombre' son obligatorios."}), 400

        if Materia.query.filter_by(sigla=sigla).first():
            return jsonify({"error": "La materia ya existe."}), 409

        materia = Materia(sigla=sigla, nombre=nombre)
        db.session.add(materia)
        db.session.commit()
        return jsonify({"message": "Materia creada exitosamente", "materia_id": materia.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@materia_bp.route('/actualizar/<int:materia_id>', methods=['PUT'])
def actualizar_materia(materia_id):
    materia = Materia.query.get_or_404(materia_id)
    try:
        data = request.get_json()
        sigla = data.get('sigla')
        nombre = data.get('nombre')

        if not sigla or not nombre:
            return jsonify({"error": "Los campos 'sigla' y 'nombre' son obligatorios."}), 400

        if Materia.query.filter(Materia.sigla == sigla, Materia.id != materia_id).first():
            return jsonify({"error": "La sigla ya está en uso."}), 409

        materia.sigla = sigla
        materia.nombre = nombre
        db.session.commit()
        return jsonify({"message": "Materia actualizada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar la materia: {str(e)}"}), 500

@materia_bp.route('/eliminar/<int:materia_id>', methods=['DELETE'])
def eliminar_materia(materia_id):
    materia = Materia.query.get_or_404(materia_id)
    try:
        db.session.delete(materia)
        db.session.commit()
        return jsonify({"message": "Materia eliminada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo eliminar la materia: {str(e)}"}), 500