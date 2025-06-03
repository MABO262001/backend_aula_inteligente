from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.boleta_inscripcion import BoletaInscripcion
from ..models.estudiante import Estudiante
from ..models.gestion_curso_paralelo import GestionCursoParalelo
from ..models.user import User
from ..models.curso import Curso
from ..models.paralelo import Paralelo
from ..models.gestion import Gestion
from ..models.curso_paralelo import CursoParalelo
from ..models.subgestion import Subgestion
from datetime import datetime
from app.models.materia_horario_curso_paralelo import MateriaHorarioCursoParalelo

boleta_bp = Blueprint('boleta_bp', __name__)

@boleta_bp.route('/listar-boletas-por-gestion', methods=['GET'])
def listar_boletas_por_gestion():
    try:
        boletas = db.session.query(BoletaInscripcion) \
            .join(BoletaInscripcion.estudiante) \
            .join(BoletaInscripcion.gestion_curso_paralelo) \
            .join(GestionCursoParalelo.curso_paralelo) \
            .join(CursoParalelo.curso) \
            .join(CursoParalelo.paralelo) \
            .join(GestionCursoParalelo.gestion) \
            .join(BoletaInscripcion.user) \
            .all()

        gestiones_dict = {}

        for boleta in boletas:
            gestion = boleta.gestion_curso_paralelo.gestion
            curso_paralelo = boleta.gestion_curso_paralelo.curso_paralelo
            curso = curso_paralelo.curso
            paralelo = curso_paralelo.paralelo
            estudiante = boleta.estudiante
            user_registrador = boleta.user

            if gestion.id not in gestiones_dict:
                gestiones_dict[gestion.id] = {
                    "gestion_id": gestion.id,
                    "gestion_nombre": gestion.nombre,
                    "boletas": []
                }

            gestiones_dict[gestion.id]["boletas"].append({
                "gestion_curso_paralelo_id": boleta.gestion_curso_paralelo_id,
                "curso_paralelo": {
                    "curso": curso.nombre,
                    "paralelo": paralelo.nombre
                },
                "boleta_id": boleta.id,
                "fecha": boleta.fecha.strftime('%Y-%m-%d'),
                "hora": boleta.hora.strftime('%H:%M'),
                "estudiante": {
                    "id": estudiante.id,
                    "ci": estudiante.ci,
                    "nombre": estudiante.nombre,
                    "apellido": estudiante.apellido
                },
                "registrado_por": {
                    "id": user_registrador.id,
                    "name": user_registrador.name,
                    "email": user_registrador.email
                }
            })

        return jsonify(list(gestiones_dict.values())), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@boleta_bp.route('/registrar-boleta', methods=['POST'])
def registrar_boleta():
    try:
        data = request.get_json()
        ci = data.get('ci')
        gestion_cp_id = data.get('gestion_curso_paralelo_id')
        user_id = data.get('users_id')
        fecha_str = data.get('fecha')
        hora_str = data.get('hora')

        if not all([ci, gestion_cp_id, user_id]):
            return jsonify({"error": "Faltan datos requeridos"}), 400

        estudiante = Estudiante.query.filter_by(ci=ci).first()
        if not estudiante:
            return jsonify({"error": f"No se encontró estudiante con CI {ci}"}), 404

        gestion_cp = GestionCursoParalelo.query.get(gestion_cp_id)
        if not gestion_cp:
            return jsonify({"error": f"No existe GestionCursoParalelo con id {gestion_cp_id}"}), 404

        user_registrador = User.query.get(user_id)
        if not user_registrador:
            return jsonify({"error": f"No existe usuario con id {user_id}"}), 404

        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else datetime.now().date()
        hora = datetime.strptime(hora_str, "%H:%M").time() if hora_str else datetime.now().time()

        ya_inscrito = db.session.query(BoletaInscripcion).filter(
            BoletaInscripcion.estudiante_id == estudiante.id,
            BoletaInscripcion.gestion_curso_paralelo_id == gestion_cp.id,
            BoletaInscripcion.id != BoletaInscripcion.id
        ).first()

        if ya_inscrito:
            return jsonify({"error": "El estudiante ya está inscrito en esa gestión"}), 409

        boleta = BoletaInscripcion(
            hora=hora,
            fecha=fecha,
            estudiante_id=estudiante.id,
            gestion_curso_paralelo_id=gestion_cp.id,
            users_id=user_registrador.id
        )

        db.session.add(boleta)
        db.session.commit()

        curso = gestion_cp.curso_paralelo.curso.nombre
        paralelo = gestion_cp.curso_paralelo.paralelo.nombre

        materias_resultado = []

        materias_horarios = MateriaHorarioCursoParalelo.query.filter_by(
            gestion_curso_paralelo_id=gestion_cp.id
        ).all()

        for mhcp in materias_horarios:
            mpdh = mhcp.materia_profesor_dia_horario
            mp = mpdh.materia_profesor
            materia = mp.materia
            profesor = mp.profesor
            dia = mpdh.dia_horario.dia
            horario = mpdh.dia_horario.horario

            clave = f"{materia.id}-{profesor.id}"
            materia_info = next((m for m in materias_resultado if m['clave'] == clave), None)

            if not materia_info:
                materia_info = {
                    "clave": clave,
                    "materia_id": materia.id,
                    "materia_nombre": materia.nombre,
                    "profesor_datos": {
                        "id": profesor.id,
                        "nombre": profesor.nombre,
                        "ci": profesor.ci,
                        "email": profesor.user_profesor.email
                    },
                    "dias_horarios": []
                }
                materias_resultado.append(materia_info)

            materia_info["dias_horarios"].append({
                "dia_nombre": dia.nombre,
                "horario_inicio": horario.hora_inicio.strftime('%H:%M'),
                "horario_final": horario.hora_final.strftime('%H:%M')
            })

        for m in materias_resultado:
            m.pop("clave", None)

        return jsonify({
            "mensaje": "Boleta de inscripción registrada exitosamente",
            "boleta_id": boleta.id,
            "curso_paralelo": f"{curso} {paralelo}",
            "materias": materias_resultado
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@boleta_bp.route('/actualizar-boleta/<int:id>', methods=['PUT'])
def actualizar_boleta(id):
    try:
        data = request.get_json()
        ci = data.get('ci')
        gestion_cp_id = data.get('gestion_curso_paralelo_id')
        user_id = data.get('users_id')
        fecha_str = data.get('fecha')
        hora_str = data.get('hora')

        if not all([ci, gestion_cp_id, user_id]):
            return jsonify({"error": "Faltan datos requeridos"}), 400

        boleta = BoletaInscripcion.query.get(id)
        if not boleta:
            return jsonify({"error": f"No se encontró boleta con id {id}"}), 404

        estudiante = Estudiante.query.filter_by(ci=ci).first()
        if not estudiante:
            return jsonify({"error": f"No se encontró estudiante con CI {ci}"}), 404

        gestion_cp = GestionCursoParalelo.query.get(gestion_cp_id)
        if not gestion_cp:
            return jsonify({"error": f"No existe GestionCursoParalelo con id {gestion_cp_id}"}), 404

        user_registrador = User.query.get(user_id)
        if not user_registrador:
            return jsonify({"error": f"No existe usuario con id {user_id}"}), 404

        # Excluir la boleta actual al validar duplicado
        ya_inscrito = db.session.query(BoletaInscripcion).join(GestionCursoParalelo).filter(
            BoletaInscripcion.estudiante_id == estudiante.id,
            GestionCursoParalelo.gestion_id == gestion_cp.gestion_id,
            BoletaInscripcion.id != boleta.id
        ).first()

        if ya_inscrito:
            return jsonify({"error": "El estudiante ya está inscrito en esa gestión"}), 409

        # Actualizar valores
        boleta.estudiante_id = estudiante.id
        boleta.gestion_curso_paralelo_id = gestion_cp.id
        boleta.users_id = user_registrador.id
        boleta.fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else boleta.fecha
        boleta.hora = datetime.strptime(hora_str, "%H:%M").time() if hora_str else boleta.hora

        db.session.commit()

        return jsonify({"mensaje": "Boleta actualizada correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@boleta_bp.route('/eliminar-boleta/<int:id>', methods=['DELETE'])
def eliminar_boleta(id):
    try:
        boleta = BoletaInscripcion.query.get(id)
        if not boleta:
            return jsonify({"error": f"No existe boleta con id {id}"}), 404

        db.session.delete(boleta)
        db.session.commit()

        return jsonify({"mensaje": "Boleta eliminada correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@boleta_bp.route('/buscar-boleta/<int:ci>', methods=['GET'])
def buscar_boleta(ci):
    try:
        estudiante = Estudiante.query.filter_by(ci=ci).first()
        if not estudiante:
            return jsonify({"error": f"No se encontró estudiante con CI {ci}"}), 404

        boletas = BoletaInscripcion.query.filter_by(estudiante_id=estudiante.id).all()
        resultado = []

        for boleta in boletas:
            gestion_cp = boleta.gestion_curso_paralelo
            curso_paralelo = gestion_cp.curso_paralelo
            curso = curso_paralelo.curso.nombre
            paralelo = curso_paralelo.paralelo.nombre

            materias_resultado = []
            materias_horarios = MateriaHorarioCursoParalelo.query.filter_by(
                gestion_curso_paralelo_id=gestion_cp.id
            ).all()

            for mhcp in materias_horarios:
                mpdh = mhcp.materia_profesor_dia_horario
                mp = mpdh.materia_profesor
                materia = mp.materia
                profesor = mp.profesor
                dia = mpdh.dia_horario.dia
                horario = mpdh.dia_horario.horario

                clave = f"{materia.id}-{profesor.id}"
                materia_info = next((m for m in materias_resultado if m['clave'] == clave), None)

                if not materia_info:
                    materia_info = {
                        "clave": clave,
                        "materia_id": materia.id,
                        "materia_nombre": materia.nombre,
                        "profesor_datos": {
                            "id": profesor.id,
                            "nombre": profesor.nombre,
                            "ci": profesor.ci,
                            "email": profesor.user_profesor.email
                        },
                        "dias_horarios": []
                    }
                    materias_resultado.append(materia_info)

                materia_info["dias_horarios"].append({
                    "dia_nombre": dia.nombre,
                    "horario_inicio": horario.hora_inicio.strftime('%H:%M'),
                    "horario_final": horario.hora_final.strftime('%H:%M')
                })

            for m in materias_resultado:
                m.pop("clave", None)

            resultado.append({
                "boleta_id": boleta.id,
                "fecha": boleta.fecha.strftime('%Y-%m-%d'),
                "hora": boleta.hora.strftime('%H:%M'),
                "curso_paralelo": f"{curso} {paralelo}",
                "estudiante": {
                    "id": estudiante.id,
                    "ci": estudiante.ci,
                    "nombre": estudiante.nombre,
                    "apellido": estudiante.apellido
                },
                "materias": materias_resultado
            })

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@boleta_bp.route('/listar_boleta_cursos_paralelos', methods=['GET'])
def listar_boleta_cursos_paralelos():
    boletas = BoletaInscripcion.query.all()
    resultado = []

    for b in boletas:
        gcp = b.gestion_curso_paralelo
        cp = gcp.curso_paralelo
        paralelo = cp.paralelo
        curso = cp.curso
        gestion = gcp.gestion

        resultado.append({
            "boleta_id": b.id,
            "hora": b.hora.strftime('%H:%M'),
            "fecha": b.fecha.strftime('%Y-%m-%d'),
            "gestion_curso_paralelo": {
                "gestion_curso_paralelo_id": gcp.id,
                "gestion": {
                    "gestion_id": gestion.id,
                    "gestion_nombre": gestion.nombre
                },
                "curso_paralelo": {
                    "curso_paralelo_id": cp.id,
                    "paralelo": {
                        "paralelo_id": paralelo.id,
                        "paralelo_nombre": paralelo.nombre
                    },
                    "curso": {
                        "curso_id": curso.id,
                        "curso_nombre": curso.nombre
                    }
                }
            }
        })

    return jsonify(resultado), 200

@boleta_bp.route('/listar_gestion_paralelo', methods=['GET'])
def listar_gestion_paralelo():
    # Obtenemos todos los registros de GestionCursoParalelo
    registros = GestionCursoParalelo.query.all()
    resultado = []

    for gcp in registros:
        curso_paralelo = gcp.curso_paralelo
        curso = curso_paralelo.curso
        paralelo = curso_paralelo.paralelo
        gestion = gcp.gestion

        resultado.append({
            "gestion_curso_paralelo_id": gcp.id,
            "curso_paralelo": {
                "curso_paralelo_id": curso_paralelo.id,
                "curso": {
                    "curso_id": curso.id,
                    "curso_nombre": curso.nombre
                },
                "paralelo": {
                    "paralelo_id": paralelo.id,
                    "paralelo_nombre": paralelo.nombre
                }
            },
            "gestion": {
                "gestion_id": gestion.id,
                "gestion_nombre": gestion.nombre
            }
        })

    return jsonify(resultado), 200


