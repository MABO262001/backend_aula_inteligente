from flask import Blueprint, request, jsonify
from app.models.horario import Horario
from app.extensions import db

horario_bp = Blueprint('horario_bp', __name__)

@horario_bp.route('/listar', methods=['GET'])
def listar_horarios():
    horarios = Horario.query.all()
    result = [{"id": horario.id, "hora_inicio": str(horario.hora_inicio), "hora_final": str(horario.hora_final)} for horario in horarios]
    return jsonify(result)

@horario_bp.route('/guardar', methods=['POST'])
def guardar_horario():
    try:
        data = request.get_json()
        hora_inicio = data.get('hora_inicio')
        hora_final = data.get('hora_final')

        if not hora_inicio or not hora_final:
            return jsonify({"error": "Los campos 'hora_inicio' y 'hora_final' son obligatorios."}), 400

        if Horario.query.filter_by(hora_inicio=hora_inicio, hora_final=hora_final).first():
            return jsonify({"error": "El horario ya existe."}), 409

        horario = Horario(hora_inicio=hora_inicio, hora_final=hora_final)
        db.session.add(horario)
        db.session.commit()
        return jsonify({"message": "Horario creado exitosamente", "horario_id": horario.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@horario_bp.route('/actualizar/<int:horario_id>', methods=['PUT'])
def actualizar_horario(horario_id):
    horario = Horario.query.get_or_404(horario_id)
    try:
        data = request.get_json()
        hora_inicio = data.get('hora_inicio')
        hora_final = data.get('hora_final')

        if not hora_inicio or not hora_final:
            return jsonify({"error": "Los campos 'hora_inicio' y 'hora_final' son obligatorios."}), 400

        if Horario.query.filter(Horario.hora_inicio == hora_inicio, Horario.hora_final == hora_final, Horario.id != horario_id).first():
            return jsonify({"error": "El horario ya está en uso."}), 409

        horario.hora_inicio = hora_inicio
        horario.hora_final = hora_final
        db.session.commit()
        return jsonify({"message": "Horario actualizado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar el horario: {str(e)}"}), 500

@horario_bp.route('/eliminar/<int:horario_id>', methods=['DELETE'])
def eliminar_horario(horario_id):
    horario = Horario.query.get_or_404(horario_id)
    try:
        db.session.delete(horario)
        db.session.commit()
        return jsonify({"message": "Horario eliminado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo eliminar el horario: {str(e)}"}), 500