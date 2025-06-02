import os
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .. import Gestion
from ..extensions import db
from ..models.user import User
from ..models.estudiante import Estudiante
from ..models.parentesco import Parentesco
from ..models.subgestion import Subgestion
from ..models.matricula import Matricula

pagos_matriculas_bp = Blueprint('pagos_matriculas_bp', __name__)

def serializar_matricula(matricula):
    user = User.query.get(matricula.users_id)
    parentesco = Parentesco.query.get(matricula.parentesco_id)
    estudiante = parentesco.estudiante
    apoderado = parentesco.apoderado

    return {
        "id": matricula.id,
        "fecha": matricula.fecha.isoformat(),
        "monto": matricula.monto,
        "user": {
            "id": user.id,
            "name": user.name,
            "status": user.status
        },
        "parentesco": {
            "id": parentesco.id,
            "nombre": parentesco.nombre,
            "apoderado_id": apoderado.id,
            "apoderado_ci": apoderado.ci,
            "apoderado_nombre": apoderado.nombre,
            "apoderado_apellido": apoderado.apellido,
            "apoderado_sexo": apoderado.sexo,
            "apoderado_telefono": apoderado.telefono
        },
        "estudiante": {
            "id": estudiante.id,
            "ci": estudiante.ci,
            "nombre": estudiante.nombre,
            "apellido": estudiante.apellido,
            "sexo": estudiante.sexo,
            "telefono": estudiante.telefono
        }
    }

@pagos_matriculas_bp.route('/listar_todas_subgestiones', methods=['GET'])
def listar_todas_subgestiones():
    subgestiones = Subgestion.query.all()
    resultado = []

    for sub in subgestiones:
        matriculas = Matricula.query.filter_by(subgestion_id=sub.id).all()
        resultado.append({
            "subgestion_id": sub.id,
            "nombre": sub.nombre,
            "fecha_inicio": sub.fecha_inicio.isoformat(),
            "fecha_final": sub.fecha_final.isoformat(),
            "matriculas": [serializar_matricula(m) for m in matriculas]
        })

    return jsonify(resultado)

@pagos_matriculas_bp.route('/guardar', methods=['POST'])
def guardar_matricula():
    try:
        data = request.get_json()
        ci_estudiante = data.get('ci_estudiante')
        subgestion_id = data.get('subgestion_id')
        monto = data.get('monto')
        fecha = data.get('fecha')
        users_id = data.get('users_id')

        if not all([ci_estudiante, subgestion_id, monto, fecha, users_id]):
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        estudiante = Estudiante.query.filter_by(ci=ci_estudiante).first()
        if not estudiante:
            return jsonify({"error": "Estudiante no encontrado"}), 404

        parentesco = Parentesco.query.filter_by(estudiante_id=estudiante.id).first()
        if not parentesco:
            return jsonify({"error": "No se encontró apoderado para este estudiante"}), 404

        subgestion = Subgestion.query.get(subgestion_id)
        if not subgestion:
            return jsonify({"error": "Subgestión no encontrada"}), 404

        # VALIDACIÓN: solo impedir si ya hay matrícula en la misma subgestión
        matricula_existente = Matricula.query \
            .join(Parentesco, Parentesco.id == Matricula.parentesco_id) \
            .filter(
                Parentesco.estudiante_id == estudiante.id,
                Matricula.subgestion_id == subgestion.id
            ).first()

        if matricula_existente:
            return jsonify({"error": "El estudiante ya tiene una matrícula registrada en esta subgestión."}), 409

        matricula = Matricula(
            fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
            monto=float(monto),
            parentesco_id=parentesco.id,
            subgestion_id=int(subgestion_id),
            users_id=int(users_id)
        )

        db.session.add(matricula)
        db.session.commit()

        return jsonify({
            "message": "Matrícula registrada correctamente",
            "matricula": serializar_matricula(matricula)
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad", "detail": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@pagos_matriculas_bp.route('/eliminar/<int:matricula_id>', methods=['DELETE'])
def eliminar_matricula(matricula_id):
    matricula = Matricula.query.get_or_404(matricula_id)
    try:
        db.session.delete(matricula)
        db.session.commit()
        return jsonify({"message": "Matrícula eliminada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar matrícula: {str(e)}"}), 500

def actualizar_matricula(matricula_id):
    matricula = Matricula.query.get_or_404(matricula_id)
    try:
        data = request.get_json()
        if 'monto' in data:
            matricula.monto = float(data['monto'])
        if 'fecha' in data:
            matricula.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        db.session.commit()
        return jsonify({"message": "Matrícula actualizada correctamente", "matricula": serializar_matricula(matricula)})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar matrícula: {str(e)}"}), 500

@pagos_matriculas_bp.route('/buscar', methods=['GET'])
def buscar_matriculas():
    gestion_id = request.args.get('gestion_id')
    subgestion_id = request.args.get('subgestion_id')
    fecha = request.args.get('fecha')

    query = Matricula.query

    if subgestion_id:
        query = query.filter(Matricula.subgestion_id == subgestion_id)
    elif gestion_id:
        subgestiones = Subgestion.query.filter_by(gestion_id=gestion_id).all()
        sub_ids = [s.id for s in subgestiones]
        query = query.filter(Matricula.subgestion_id.in_(sub_ids))

    if fecha:
        try:
            fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
            query = query.filter(Matricula.fecha == fecha_dt)
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Debe ser YYYY-MM-DD."}), 400

    matriculas = query.all()
    return jsonify([serializar_matricula(m) for m in matriculas])


@pagos_matriculas_bp.route('/buscar_estudiante/<int:ci_estudiante>', methods=['GET'])
def buscar_matricula_estudiante(ci_estudiante):
    estudiante = Estudiante.query.filter_by(ci=ci_estudiante).first()
    if not estudiante:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    parentescos = Parentesco.query.filter_by(estudiante_id=estudiante.id).all()
    parentesco_ids = [p.id for p in parentescos]

    matriculas = Matricula.query.filter(Matricula.parentesco_id.in_(parentesco_ids)).all()
    subgestion_map = {}
    for m in matriculas:
        subgestion = Subgestion.query.get(m.subgestion_id)
        if subgestion:
            gestion = Gestion.query.get(subgestion.gestion_id)
            key = (gestion.nombre, subgestion.nombre)
            if key not in subgestion_map:
                subgestion_map[key] = []
            subgestion_map[key].append(serializar_matricula(m))

    resultado = []
    for (gestion_nombre, sub_nombre), mats in sorted(subgestion_map.items()):
        resultado.append({
            "gestion": gestion_nombre,
            "subgestion": sub_nombre,
            "matriculas": mats
        })

    return jsonify(resultado)

@pagos_matriculas_bp.route('/listar-subgestiones', methods=['GET'])
def listar_subgestiones():
    try:
        subgestiones = Subgestion.query.all()
        resultado = []

        for sub in subgestiones:
            gestion = Gestion.query.get(sub.gestion_id)  # Consulta manual
            resultado.append({
                "gestion_nombre": gestion.nombre if gestion else None,
                "gestion_id": sub.gestion_id,
                "fecha_inicio": sub.fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_final": sub.fecha_final.strftime("%Y-%m-%d"),
                "nombre": sub.nombre,
                "subgestion_id": sub.id
            })

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

