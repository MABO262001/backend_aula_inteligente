from flask import Blueprint, request, jsonify, current_app, send_from_directory
from sqlalchemy.orm import joinedload
from ..models.gestion_curso_paralelo import GestionCursoParalelo
from ..models.curso_paralelo import CursoParalelo
from ..models.boleta_inscripcion import BoletaInscripcion
from ..models.materia_horario_curso_paralelo import MateriaHorarioCursoParalelo
from ..models.materia_profesor_dia_horario import MateriaProfesorDiaHorario
from ..models.materia_profesor import MateriaProfesor
from ..models.nota import Nota
from ..models.profesor import Profesor
from ..models.dia_horario import DiaHorario
from ..extensions import db


gestion_notas_bp = Blueprint('gestion_notas_bp', __name__)


@gestion_notas_bp.route('/estructura-notas', methods=['GET'])
def obtener_estructura_para_notas():
    try:
        relaciones = GestionCursoParalelo.query.options(
            joinedload(GestionCursoParalelo.gestion),
            joinedload(GestionCursoParalelo.curso_paralelo).joinedload(CursoParalelo.curso),
            joinedload(GestionCursoParalelo.curso_paralelo).joinedload(CursoParalelo.paralelo),
            joinedload(GestionCursoParalelo.boletas).joinedload(BoletaInscripcion.estudiante),
            joinedload(GestionCursoParalelo.materia_horario_curso_paralelo_rel)
                .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
                .joinedload(MateriaProfesorDiaHorario.materia_profesor)
                .joinedload(MateriaProfesor.profesor),
            joinedload(GestionCursoParalelo.materia_horario_curso_paralelo_rel)
                .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
                .joinedload(MateriaProfesorDiaHorario.materia_profesor)
                .joinedload(MateriaProfesor.materia),
            joinedload(GestionCursoParalelo.materia_horario_curso_paralelo_rel)
                .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
                .joinedload(MateriaProfesorDiaHorario.dia_horario)
                .joinedload(DiaHorario.horario)
        ).all()

        data = []

        for gcp in relaciones:
            gestion = gcp.gestion
            cp = gcp.curso_paralelo
            curso = cp.curso
            paralelo = cp.paralelo

            estudiantes = []
            for boleta in gcp.boletas:
                est = boleta.estudiante
                estudiantes.append({
                    "boleta_inscripcion_id": boleta.id,
                    "estudiante_id": est.id,
                    "estudiante_ci": est.ci,
                    "estudiante_nombre": est.nombre,
                    "estudiante_apellido": est.apellido,
                    "estudiante_sexo": est.sexo,
                    "estudiante_telefono": est.telefono
                })

            materias = []
            for mhcp in gcp.materia_horario_curso_paralelo_rel:
                mpdh = mhcp.materia_profesor_dia_horario
                mp = mpdh.materia_profesor
                prof = mp.profesor
                mat = mp.materia
                horario = mpdh.dia_horario.horario

                materias.append({
                    "materia_profesor_dia_horario_id": mpdh.id,
                    "materia_profesor_id": mp.id,  # Añadido materia_profesor_id
                    "materia_id": mat.id,
                    "materia_nombre": mat.nombre,
                    "horario_id": horario.id,
                    "horario_inicio": horario.hora_inicio.strftime('%H:%M'),
                    "horario_final": horario.hora_final.strftime('%H:%M'),
                    "profesor_id": prof.id,
                    "profesor_nombre": prof.nombre
                })

            data.append({
                "gestion_curso_paralelo": {
                    "gestion_curso_paralelo_id": gcp.id,
                    "gestion_id": gestion.id,
                    "gestion_nombre": gestion.nombre,
                    "curso_id": curso.id,
                    "curso_nombre": curso.nombre,
                    "paralelo_id": paralelo.id,
                    "paralelo_nombre": paralelo.nombre,
                    "estudiantes": estudiantes,
                    "materia_profesor_dia_horario": materias
                }
            })

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@gestion_notas_bp.route('/estructura-curso-estudiantes', methods=['GET'])
def obtener_estructura_curso_estudiantes():
    try:
        relaciones = GestionCursoParalelo.query.options(
            joinedload(GestionCursoParalelo.gestion),
            joinedload(GestionCursoParalelo.curso_paralelo).joinedload(CursoParalelo.curso),
            joinedload(GestionCursoParalelo.curso_paralelo).joinedload(CursoParalelo.paralelo),
            joinedload(GestionCursoParalelo.boletas).joinedload(BoletaInscripcion.estudiante),
            joinedload(GestionCursoParalelo.materia_horario_curso_paralelo_rel)
            .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
            .joinedload(MateriaProfesorDiaHorario.materia_profesor)
            .joinedload(MateriaProfesor.profesor),
            joinedload(GestionCursoParalelo.materia_horario_curso_paralelo_rel)
            .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
            .joinedload(MateriaProfesorDiaHorario.materia_profesor)
            .joinedload(MateriaProfesor.materia),
            joinedload(GestionCursoParalelo.materia_horario_curso_paralelo_rel)
            .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
            .joinedload(MateriaProfesorDiaHorario.dia_horario)
            .joinedload(DiaHorario.horario)
        ).all()

        data = []

        for gcp in relaciones:
            gestion = gcp.gestion
            cp = gcp.curso_paralelo
            curso = cp.curso
            paralelo = cp.paralelo

            estudiantes = []
            for boleta in gcp.boletas:
                est = boleta.estudiante
                estudiantes.append({
                    "boleta_inscripcion_id": boleta.id,
                    "estudiante_id": est.id,
                    "estudiante_ci": est.ci,
                    "estudiante_nombre": est.nombre,
                    "estudiante_apellido": est.apellido,
                    "estudiante_sexo": est.sexo,
                    "estudiante_telefono": est.telefono
                }
                )

            materias = []
            for mhcp in gcp.materia_horario_curso_paralelo_rel:
                mpdh = mhcp.materia_profesor_dia_horario
                mp = mpdh.materia_profesor
                prof = mp.profesor
                mat = mp.materia
                horario = mpdh.dia_horario.horario

                estudiantes_asociados = []
                for boleta in gcp.boletas:
                    estudiantes_asociados.append({
                        "estudiante_id": boleta.estudiante.id,
                        "estudiante_ci": boleta.estudiante.ci,
                        "estudiante_nombre": boleta.estudiante.nombre,
                        "estudiante_apellido": boleta.estudiante.apellido,
                        "gestion_id": gcp.gestion.id,
                        "gestion_nombre": gcp.gestion.nombre
                    }
                    )

                materias.append({
                    "materia_profesor_dia_horario_id": mpdh.id,
                    "materia_id": mat.id,
                    "materia_nombre": mat.nombre,
                    "horario_id": horario.id,
                    "horario_inicio": horario.hora_inicio.strftime('%H:%M'),
                    "horario_final": horario.hora_final.strftime('%H:%M'),
                    "profesor_id": prof.id,
                    "profesor_nombre": prof.nombre,
                    "estudiantes_asociados": estudiantes_asociados
                }
                )

            data.append({
                "gestion_curso_paralelo": {
                    "gestion_curso_paralelo_id": gcp.id,
                    "gestion_id": gestion.id,
                    "gestion_nombre": gestion.nombre,
                    "curso_id": curso.id,
                    "curso_nombre": curso.nombre,
                    "paralelo_id": paralelo.id,
                    "paralelo_nombre": paralelo.nombre,
                    "estudiantes": estudiantes,
                    "materia_profesor_dia_horario": materias
                }
            }
            )

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@gestion_notas_bp.route('/guardar', methods=['POST'])
def guardar_nota():
    try:
        data = request.get_json()

        # Validar campos obligatorios
        required_fields = ['promedio_final', 'estudiante_id', 'gestion_curso_paralelo_id', 'materia_profesor_id']
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({"error": f"Faltan campos obligatorios: {', '.join(missing_fields)}"}), 400

        # Validar tipo
        if not isinstance(data['promedio_final'], (int, float)):
            return jsonify({"error": "El promedio_final debe ser un número"}), 400

        # Crear y guardar la nota
        nueva_nota = Nota(
            promedio_final=data['promedio_final'],
            estudiante_id=data['estudiante_id'],
            gestion_curso_paralelo_id=data['gestion_curso_paralelo_id'],
            materia_profesor_id=data['materia_profesor_id']
        )

        db.session.add(nueva_nota)
        db.session.commit()

        return jsonify({
            "mensaje": "Nota registrada exitosamente",
            "nota": {
                "id": nueva_nota.id,
                "promedio_final": nueva_nota.promedio_final,
                "estudiante_id": nueva_nota.estudiante_id,
                "gestion_curso_paralelo_id": nueva_nota.gestion_curso_paralelo_id,
                "materia_profesor_id": nueva_nota.materia_profesor_id
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@gestion_notas_bp.route('/actualizar/<int:nota_id>', methods=['PUT', 'PATCH'])
def actualizar_nota(nota_id):
    try:
        nota = Nota.query.get(nota_id)
        if not nota:
            return jsonify({"error": "Nota no encontrada"}), 404

        data = request.get_json()

        # Validar si al menos viene un campo para actualizar
        if not any(key in data for key in ['promedio_final', 'estudiante_id', 'gestion_curso_paralelo_id', 'materia_profesor_id']):
            return jsonify({"error": "No se envió ningún campo para actualizar"}), 400

        # Validar tipo del promedio si se envía
        if 'promedio_final' in data and not isinstance(data['promedio_final'], (int, float)):
            return jsonify({"error": "El promedio_final debe ser un número"}), 400

        # Actualizar los campos si se proporcionan
        if 'promedio_final' in data:
            nota.promedio_final = data['promedio_final']
        if 'estudiante_id' in data:
            nota.estudiante_id = data['estudiante_id']
        if 'gestion_curso_paralelo_id' in data:
            nota.gestion_curso_paralelo_id = data['gestion_curso_paralelo_id']
        if 'materia_profesor_id' in data:
            nota.materia_profesor_id = data['materia_profesor_id']

        db.session.commit()

        return jsonify({
            "mensaje": "Nota actualizada exitosamente",
            "nota": {
                "id": nota.id,
                "promedio_final": nota.promedio_final,
                "estudiante_id": nota.estudiante_id,
                "gestion_curso_paralelo_id": nota.gestion_curso_paralelo_id,
                "materia_profesor_id": nota.materia_profesor_id
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@gestion_notas_bp.route('/eliminar/<int:nota_id>', methods=['DELETE'])
def eliminar_nota(nota_id):
    try:
        nota = Nota.query.get(nota_id)
        if not nota:
            return jsonify({"error": "Nota no encontrada"}), 404

        db.session.delete(nota)
        db.session.commit()

        return jsonify({"mensaje": "Nota eliminada exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
