from flask import Blueprint, request, jsonify
from app.models.dia import Dia
from app.extensions import db

dia_bp = Blueprint('dia_bp', __name__)

@dia_bp.route('/listar', methods=['GET'])
def listar_dias():
    dias = Dia.query.all()
    result = [{"id": dia.id, "nombre": dia.nombre} for dia in dias]
    return jsonify(result)

@dia_bp.route('/guardar', methods=['POST'])
def guardar_dia():
    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip()

        if not nombre:
            return jsonify({"error": "El campo 'nombre' es obligatorio."}), 400

        if Dia.query.filter_by(nombre=nombre).first():
            return jsonify({"error": "El día ya existe."}), 409

        dia = Dia(nombre=nombre)
        db.session.add(dia)
        db.session.commit()
        return jsonify({"message": "Día creado exitosamente", "dia_id": dia.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@dia_bp.route('/actualizar/<int:dia_id>', methods=['PUT'])
def actualizar_dia(dia_id):
    dia = Dia.query.get_or_404(dia_id)
    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip()

        if not nombre:
            return jsonify({"error": "El campo 'nombre' es obligatorio."}), 400

        if Dia.query.filter(Dia.nombre == nombre, Dia.id != dia_id).first():
            return jsonify({"error": "El nombre del día ya está en uso."}), 409

        dia.nombre = nombre
        db.session.commit()
        return jsonify({"message": "Día actualizado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar el día: {str(e)}"}), 500

@dia_bp.route('/eliminar/<int:dia_id>', methods=['DELETE'])
def eliminar_dia(dia_id):
    dia = Dia.query.get_or_404(dia_id)
    try:
        db.session.delete(dia)
        db.session.commit()
        return jsonify({"message": "Día eliminado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo eliminar el día: {str(e)}"}), 500