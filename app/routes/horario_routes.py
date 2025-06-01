from flask import Blueprint, request, jsonify
from app.models.horario import Horario
from app.models.dia_horario import DiaHorario
from app.models.dia import Dia
from app.extensions import db

horario_bp = Blueprint('horario_bp', __name__)


@horario_bp.route('/listar', methods=['GET'])
def listar_horarios():
    horarios = Horario.query.order_by(Horario.id).all()  # Ordenar por id
    result = []
    for horario in horarios:

        dia_horarios = DiaHorario.query.filter_by(horario_id=horario.id).all()
        dias = [Dia.query.get(dh.dia_id).nombre for dh in dia_horarios]

        result.append({
            "id": horario.id,
            "hora_inicio": str(horario.hora_inicio),
            "hora_final": str(horario.hora_final),
            "dias": dias
        }
        )
    return jsonify(result)


@horario_bp.route('/buscar', methods=['GET'])
def buscar_horarios():
    query_params = request.args
    query = Horario.query

    if 'hora_inicio' in query_params:
        query = query.filter(Horario.hora_inicio == query_params.get('hora_inicio'))
    if 'hora_final' in query_params:
        query = query.filter(Horario.hora_final == query_params.get('hora_final'))

    horarios = query.all()
    result = []
    for horario in horarios:

        dia_horarios = DiaHorario.query.filter_by(horario_id=horario.id).all()
        dias = [Dia.query.get(dh.dia_id).nombre for dh in dia_horarios]  # Lista de nombres de los días

        result.append({
            "id": horario.id,
            "hora_inicio": str(horario.hora_inicio),
            "hora_final": str(horario.hora_final),
            "dias": dias
        }
        )

    return jsonify(result)


@horario_bp.route('/guardar', methods=['POST'])
def guardar_horario():
    try:
        data = request.get_json()
        hora_inicio = data.get('hora_inicio')
        hora_final = data.get('hora_final')
        dias_ids = data.get('dias')

        if not hora_inicio or not hora_final or not dias_ids:
            return jsonify({"error": "Los campos 'hora_inicio', 'hora_final' y 'dias' son obligatorios."}), 400

        if Horario.query.filter_by(hora_inicio=hora_inicio, hora_final=hora_final).first():
            return jsonify({"error": "El horario ya existe."}), 409

        horario = Horario(hora_inicio=hora_inicio, hora_final=hora_final)
        db.session.add(horario)
        db.session.commit()

        for dia_id in dias_ids:
            dia = Dia.query.get(dia_id)
            if dia:
                dia_horario = DiaHorario(dia_id=dia.id, horario_id=horario.id)
                db.session.add(dia_horario)

        db.session.commit()

        result = {
            "id": horario.id,
            "hora_inicio": str(horario.hora_inicio),
            "hora_final": str(horario.hora_final),
            "dias": [Dia.query.get(dia_id).nombre for dia_id in dias_ids]
        }

        return jsonify({"message": "Horario creado y asignado a los días exitosamente", "horario": result}), 201
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
        dias_ids = data.get('dias')  # Expecting a list of day ids

        if not hora_inicio or not hora_final or not dias_ids:
            return jsonify({"error": "Los campos 'hora_inicio', 'hora_final' y 'dias' son obligatorios."}), 400

        if Horario.query.filter(Horario.hora_inicio == hora_inicio, Horario.hora_final == hora_final,
                                Horario.id != horario_id
                                ).first():
            return jsonify({"error": "El horario ya está en uso."}), 409

        horario.hora_inicio = hora_inicio
        horario.hora_final = hora_final
        db.session.commit()

        DiaHorario.query.filter(DiaHorario.horario_id == horario_id).delete()

        for dia_id in dias_ids:
            dia = Dia.query.get(dia_id)
            if dia:
                dia_horario = DiaHorario(dia_id=dia.id, horario_id=horario.id)
                db.session.add(dia_horario)

        db.session.commit()

        return jsonify({"message": "Horario actualizado y asignado a los días correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar el horario: {str(e)}"}), 500


@horario_bp.route('/eliminar/<int:horario_id>', methods=['DELETE'])
def eliminar_horario(horario_id):
    horario = Horario.query.get_or_404(horario_id)
    try:
        DiaHorario.query.filter(DiaHorario.horario_id == horario_id).delete()

        db.session.delete(horario)
        db.session.commit()

        return jsonify({"message": "Horario eliminado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo eliminar el horario: {str(e)}"}), 500
