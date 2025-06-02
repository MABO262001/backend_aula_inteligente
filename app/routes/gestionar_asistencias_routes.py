from flask import Blueprint, request, jsonify
from datetime import datetime
from ..extensions import db
from ..models.asistencia import Asistencia
from ..models.estudiante_asistencia import EstudianteAsistencia
from ..models.estudiante import  Estudiante
from ..models.gestion_curso_paralelo import GestionCursoParalelo

gestionar_asistencias_bp = Blueprint('gestionar_asistencias_bp', __name__)

@gestionar_asistencias_bp.route('/guardar', methods=['POST'])
def guardar_asistencia():
    try:
        data = request.get_json()

        required_fields = ['hora', 'fecha', 'gestion_curso_paralelo_id', 'profesor_id', 'estudiantes']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

        # Crear asistencia
        asistencia = Asistencia(
            hora=datetime.strptime(data['hora'], '%H:%M').time(),
            fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
            gestion_curso_paralelo_id=data['gestion_curso_paralelo_id'],
            profesor_id=data['profesor_id']
        )

        db.session.add(asistencia)
        db.session.flush()

        estudiantes_response = []

        for est_data in data['estudiantes']:
            ea = EstudianteAsistencia(
                estado=est_data['estado'],
                estudiante_id=est_data['estudiante_id'],
                asistencia_id=asistencia.id
            )
            db.session.add(ea)

            estudiante = Estudiante.query.get(est_data['estudiante_id'])
            estudiantes_response.append({
                "estudiante_id": estudiante.id,
                "estudiante_nombre": estudiante.nombre,
                "estudiante_apellido": estudiante.apellido,
                "estudiante_ci": estudiante.ci,
                "estudiante_telefono": estudiante.telefono,
                "estado": est_data['estado']
            })

        gcp = GestionCursoParalelo.query.get(data['gestion_curso_paralelo_id'])
        curso = gcp.curso_paralelo.curso
        paralelo = gcp.curso_paralelo.paralelo

        db.session.commit()

        return jsonify({
            "mensaje": "Asistencia registrada correctamente",
            "asistencia": {
                "hora": asistencia.hora.strftime('%H:%M'),
                "fecha": asistencia.fecha.strftime('%Y-%m-%d'),
                "gestion_curso_paralelo_id": gcp.id,
                "curso_nombre": curso.nombre,
                "paralelo_nombre": paralelo.nombre,
                "profesor_id": asistencia.profesor_id,
                "profesor_nombre": asistencia.profesor.nombre,
                "estudiantes": estudiantes_response
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@gestionar_asistencias_bp.route('/actualizar/<int:asistencia_id>', methods=['PUT', 'PATCH'])
def actualizar_asistencia(asistencia_id):
    try:
        data = request.get_json()

        required_fields = ['hora', 'fecha', 'gestion_curso_paralelo_id', 'profesor_id', 'estudiantes']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

        asistencia = Asistencia.query.get(asistencia_id)
        if not asistencia:
            return jsonify({"error": "Asistencia no encontrada"}), 404

        # Eliminar registros de estudiante_asistencia anteriores
        EstudianteAsistencia.query.filter_by(asistencia_id=asistencia.id).delete()

        # Actualizar datos de asistencia
        asistencia.hora = datetime.strptime(data['hora'], '%H:%M').time()
        asistencia.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        asistencia.gestion_curso_paralelo_id = data['gestion_curso_paralelo_id']
        asistencia.profesor_id = data['profesor_id']

        db.session.flush()  # para mantener el id de la asistencia

        estudiantes_response = []

        for est_data in data['estudiantes']:
            ea = EstudianteAsistencia(
                estado=est_data['estado'],
                estudiante_id=est_data['estudiante_id'],
                asistencia_id=asistencia.id
            )
            db.session.add(ea)

            estudiante = Estudiante.query.get(est_data['estudiante_id'])
            estudiantes_response.append({
                "estudiante_id": estudiante.id,
                "estudiante_nombre": estudiante.nombre,
                "estudiante_apellido": estudiante.apellido,
                "estudiante_ci": estudiante.ci,
                "estudiante_telefono": estudiante.telefono,
                "estado": est_data['estado']
            })

        gcp = GestionCursoParalelo.query.get(data['gestion_curso_paralelo_id'])
        curso = gcp.curso_paralelo.curso
        paralelo = gcp.curso_paralelo.paralelo

        db.session.commit()

        return jsonify({
            "mensaje": "Asistencia actualizada correctamente",
            "asistencia": {
                "hora": asistencia.hora.strftime('%H:%M'),
                "fecha": asistencia.fecha.strftime('%Y-%m-%d'),
                "gestion_curso_paralelo_id": gcp.id,
                "curso_nombre": curso.nombre,
                "paralelo_nombre": paralelo.nombre,
                "profesor_id": asistencia.profesor_id,
                "profesor_nombre": asistencia.profesor.nombre,
                "estudiantes": estudiantes_response
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@gestionar_asistencias_bp.route('/listar', methods=['GET'])
def listar_asistencias():
    try:
        asistencias = Asistencia.query.order_by(Asistencia.fecha.desc(), Asistencia.hora.desc()).all()
        respuesta = []

        for asistencia in asistencias:
            gcp = GestionCursoParalelo.query.get(asistencia.gestion_curso_paralelo_id)
            curso = gcp.curso_paralelo.curso
            paralelo = gcp.curso_paralelo.paralelo

            estudiantes_asistencia = EstudianteAsistencia.query.filter_by(asistencia_id=asistencia.id).all()
            estudiantes_response = []

            for ea in estudiantes_asistencia:
                estudiante = ea.estudiante
                estudiantes_response.append({
                    "estudiante_id": estudiante.id,
                    "estudiante_nombre": estudiante.nombre,
                    "estudiante_apellido": estudiante.apellido,
                    "estudiante_ci": estudiante.ci,
                    "estudiante_telefono": estudiante.telefono,
                    "estado": ea.estado
                })

            respuesta.append({
                "id": asistencia.id,
                "hora": asistencia.hora.strftime('%H:%M'),
                "fecha": asistencia.fecha.strftime('%Y-%m-%d'),
                "gestion_curso_paralelo_id": gcp.id,
                "curso_nombre": curso.nombre,
                "paralelo_nombre": paralelo.nombre,
                "profesor_id": asistencia.profesor_id,
                "profesor_nombre": asistencia.profesor.nombre,
                "estudiantes": estudiantes_response
            })

        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@gestionar_asistencias_bp.route('/eliminar/<int:asistencia_id>', methods=['DELETE'])
def eliminar_asistencia(asistencia_id):
    try:
        asistencia = Asistencia.query.get(asistencia_id)
        if not asistencia:
            return jsonify({"error": "Asistencia no encontrada"}), 404

        # Eliminar relaciones de estudiantes
        EstudianteAsistencia.query.filter_by(asistencia_id=asistencia_id).delete()

        # Eliminar la asistencia principal
        db.session.delete(asistencia)
        db.session.commit()

        return jsonify({"mensaje": "Asistencia eliminada correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
