from flask import Blueprint, request, jsonify
from datetime import datetime
from ..extensions import db
from ..models.participacion import Participacion
from ..models.estudiante_participa import EstudianteParticipa
from ..models.estudiante import Estudiante
from ..models.gestion_curso_paralelo import GestionCursoParalelo

gestionar_participaciones_bp = Blueprint('gestionar_participaciones_bp', __name__)

# GUARDAR
@gestionar_participaciones_bp.route('/guardar', methods=['POST'])
def guardar_participacion():
    try:
        data = request.get_json()

        required = ['descripcion', 'hora', 'fecha', 'gestion_curso_paralelo_id', 'profesor_id', 'materia_profesor_id', 'estudiantes']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

        participacion = Participacion(
            descripcion=data['descripcion'],
            hora=datetime.strptime(data['hora'], '%H:%M').time(),
            fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
            gestion_curso_paralelo_id=data['gestion_curso_paralelo_id'],
            profesor_id=data['profesor_id'],
            materia_profesor_id=data['materia_profesor_id']
        )

        db.session.add(participacion)
        db.session.flush()

        estudiantes_response = []

        for est_data in data['estudiantes']:
            ep = EstudianteParticipa(
                estado=est_data['estado'],
                estudiante_id=est_data['estudiante_id'],
                participacion_id=participacion.id
            )
            db.session.add(ep)

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
            "mensaje": "Participación registrada correctamente",
            "participacion": {
                "participacion_id": participacion.id,
                "descripcion": participacion.descripcion,
                "hora": participacion.hora.strftime('%H:%M'),
                "fecha": participacion.fecha.strftime('%Y-%m-%d'),
                "gestion_curso_paralelo_id": gcp.id,
                "curso_id": curso.id,
                "curso_nombre": curso.nombre,
                "paralelo_id": paralelo.id,
                "paralelo_nombre": paralelo.nombre,
                "profesor_id": participacion.profesor_id,
                "profesor_nombre": participacion.profesor.nombre,
                "materia_profesor_id": participacion.materia_profesor_id,
                "estudiantes": estudiantes_response
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ACTUALIZAR
@gestionar_participaciones_bp.route('/actualizar/<int:participacion_id>', methods=['PUT', 'PATCH'])
def actualizar_participacion(participacion_id):
    try:
        data = request.get_json()

        required = ['descripcion', 'hora', 'fecha', 'gestion_curso_paralelo_id', 'profesor_id', 'materia_profesor_id', 'estudiantes']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

        participacion = Participacion.query.get(participacion_id)
        if not participacion:
            return jsonify({"error": "Participación no encontrada"}), 404

        EstudianteParticipa.query.filter_by(participacion_id=participacion.id).delete()

        participacion.descripcion = data['descripcion']
        participacion.hora = datetime.strptime(data['hora'], '%H:%M').time()
        participacion.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        participacion.gestion_curso_paralelo_id = data['gestion_curso_paralelo_id']
        participacion.profesor_id = data['profesor_id']
        participacion.materia_profesor_id = data['materia_profesor_id']

        db.session.flush()

        estudiantes_response = []

        for est_data in data['estudiantes']:
            ep = EstudianteParticipa(
                estado=est_data['estado'],
                estudiante_id=est_data['estudiante_id'],
                participacion_id=participacion.id
            )
            db.session.add(ep)

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
            "mensaje": "Participación actualizada correctamente",
            "participacion": {
                "participacion_id": participacion.id,
                "descripcion": participacion.descripcion,
                "hora": participacion.hora.strftime('%H:%M'),
                "fecha": participacion.fecha.strftime('%Y-%m-%d'),
                "gestion_curso_paralelo_id": gcp.id,
                "curso_id": curso.id,
                "curso_nombre": curso.nombre,
                "paralelo_id": paralelo.id,
                "paralelo_nombre": paralelo.nombre,
                "profesor_id": participacion.profesor_id,
                "profesor_nombre": participacion.profesor.nombre,
                "materia_profesor_id": participacion.materia_profesor_id,
                "estudiantes": estudiantes_response
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# LISTAR
@gestionar_participaciones_bp.route('/listar', methods=['GET'])
def listar_participaciones():
    try:
        participaciones = Participacion.query.order_by(Participacion.fecha.desc(), Participacion.hora.desc()).all()
        respuesta = []

        for participacion in participaciones:
            gcp = GestionCursoParalelo.query.get(participacion.gestion_curso_paralelo_id)
            curso = gcp.curso_paralelo.curso
            paralelo = gcp.curso_paralelo.paralelo

            estudiantes_participa = EstudianteParticipa.query.filter_by(participacion_id=participacion.id).all()
            estudiantes_response = []

            for ep in estudiantes_participa:
                estudiante = ep.estudiante
                estudiantes_response.append({
                    "estudiante_id": estudiante.id,
                    "estudiante_nombre": estudiante.nombre,
                    "estudiante_apellido": estudiante.apellido,
                    "estudiante_ci": estudiante.ci,
                    "estudiante_telefono": estudiante.telefono,
                    "estado": ep.estado
                })

            respuesta.append({
                "id": participacion.id,
                "descripcion": participacion.descripcion,
                "hora": participacion.hora.strftime('%H:%M'),
                "fecha": participacion.fecha.strftime('%Y-%m-%d'),
                "gestion_curso_paralelo_id": gcp.id,
                "curso_nombre": curso.nombre,
                "paralelo_nombre": paralelo.nombre,
                "profesor_id": participacion.profesor_id,
                "profesor_nombre": participacion.profesor.nombre,
                "materia_profesor_id": participacion.materia_profesor_id,
                "estudiantes": estudiantes_response
            })

        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ELIMINAR
@gestionar_participaciones_bp.route('/eliminar/<int:participacion_id>', methods=['DELETE'])
def eliminar_participacion(participacion_id):
    try:
        participacion = Participacion.query.get(participacion_id)
        if not participacion:
            return jsonify({"error": "Participación no encontrada"}), 404

        EstudianteParticipa.query.filter_by(participacion_id=participacion_id).delete()
        db.session.delete(participacion)
        db.session.commit()

        return jsonify({"mensaje": "Participación eliminada correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
