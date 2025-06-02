from flask import Blueprint, request, jsonify

from flask import Blueprint, jsonify
from sqlalchemy.orm import joinedload

from ..models.materia import Materia
from ..extensions import db
from ..models.gestion import Gestion
from ..models.gestion_curso_paralelo import GestionCursoParalelo
from ..models.curso_paralelo import CursoParalelo
from ..models.materia_horario_curso_paralelo import MateriaHorarioCursoParalelo
from ..models.materia_profesor_dia_horario import MateriaProfesorDiaHorario
from ..models.materia_profesor import MateriaProfesor
from ..models.profesor import Profesor

from ..models.dia_horario import DiaHorario


gestion_bp = Blueprint('gestion_bp', __name__)

@gestion_bp.route('/listar-estructura', methods=['GET'])
def listar_estructura_gestion():
    gestiones = Gestion.query.options(
        joinedload(Gestion.gestion_curso_paralelos)
        .joinedload(GestionCursoParalelo.curso_paralelo)
        .joinedload(CursoParalelo.curso),

        joinedload(Gestion.gestion_curso_paralelos)
        .joinedload(GestionCursoParalelo.curso_paralelo)
        .joinedload(CursoParalelo.paralelo),

        joinedload(Gestion.gestion_curso_paralelos)
        .joinedload(GestionCursoParalelo.materia_horario_curso_paralelo_rel)
        .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
        .joinedload(MateriaProfesorDiaHorario.materia_profesor)
        .joinedload(MateriaProfesor.profesor_rel)
        .joinedload(Profesor.user_profesor),

        joinedload(Gestion.gestion_curso_paralelos)
        .joinedload(GestionCursoParalelo.materia_horario_curso_paralelo_rel)
        .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
        .joinedload(MateriaProfesorDiaHorario.materia_profesor)
        .joinedload(MateriaProfesor.materia),

        joinedload(Gestion.gestion_curso_paralelos)
        .joinedload(GestionCursoParalelo.materia_horario_curso_paralelo_rel)
        .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
        .joinedload(MateriaProfesorDiaHorario.dia_horario)
        .joinedload(DiaHorario.dia),

        joinedload(Gestion.gestion_curso_paralelos)
        .joinedload(GestionCursoParalelo.materia_horario_curso_paralelo_rel)
        .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
        .joinedload(MateriaProfesorDiaHorario.dia_horario)
        .joinedload(DiaHorario.horario)
    ).all()

    resultado = []
    for g in gestiones:
        gestion_dict = {
            "gestion_id": g.id,
            "nombre": g.nombre,
            "cursos_paralelos": []
        }

        for gcp in g.gestion_curso_paralelos:
            cp = gcp.curso_paralelo
            curso_paralelo_dict = {
                "curso_paralelo_id": cp.id,
                "curso": cp.curso.nombre,
                "paralelo": cp.paralelo.nombre,
                "materias_asignadas": []
            }

            for mhcp in gcp.materia_horario_curso_paralelo_rel:
                mpdh = mhcp.materia_profesor_dia_horario
                mp = mpdh.materia_profesor
                materia = mp.materia
                profesor = mp.profesor_rel
                user = profesor.user_profesor
                dia = mpdh.dia_horario.dia
                horario = mpdh.dia_horario.horario

                curso_paralelo_dict["materias_asignadas"].append({
                    "materia_id": materia.id,
                    "materia_nombre": materia.nombre,
                    "profesor": {
                        "id": profesor.id,
                        "ci": profesor.ci,
                        "nombre": profesor.nombre,
                        "apellido": profesor.apellido,
                        "telefono": profesor.telefono,
                        "direccion": profesor.direccion,
                        "user": {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email,
                            "photo_url": user.photo_url,
                            "status": user.status
                        }
                    },
                    "dia": dia.nombre,
                    "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
                    "hora_final": horario.hora_final.strftime("%H:%M")
                })

            gestion_dict["cursos_paralelos"].append(curso_paralelo_dict)

        resultado.append(gestion_dict)

    return jsonify(resultado)

@gestion_bp.route('/listar', methods=['GET'])
def listar():
    gestiones = Gestion.query.all()
    result = [
        {
            "id": g.id,
            "nombre": g.nombre
        } for g in gestiones
    ]
    return jsonify(result), 200

@gestion_bp.route('/listar_cursos_paralelos', methods=['GET'])
def listar_cursos_paralelos():
    try:
        cursos_paralelos = CursoParalelo.query.all()
        resultado = []

        for cp in cursos_paralelos:
            resultado.append({
                "id": cp.id,
                "curso": cp.curso.nombre,
                "paralelo": cp.paralelo.nombre
            })

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": f"Error al listar cursos paralelos: {str(e)}"}), 500

@gestion_bp.route('/guardar_curso_parelo', methods=['POST'])
def guardar_gestion_curso_paralelo():
    try:
        data = request.get_json()
        nombre = data.get("nombre", "").strip()
        cursos_ids = data.get("cursos_paralelos_ids", [])

        errors = []
        if not nombre:
            errors.append("El campo 'nombre' es obligatorio.")
        if not isinstance(cursos_ids, list) or not all(isinstance(i, int) for i in cursos_ids):
            errors.append("El campo 'cursos_paralelos_ids' debe ser una lista de enteros.")
        if errors:
            return jsonify({"errors": errors}), 400

        nueva_gestion = Gestion(nombre=nombre)
        db.session.add(nueva_gestion)
        db.session.flush()  # Obtener ID antes del commit

        detalle_cursos = []

        for cp_id in cursos_ids:
            curso_paralelo = CursoParalelo.query.get(cp_id)
            if not curso_paralelo:
                db.session.rollback()
                return jsonify({"error": f"CursoParalelo con id {cp_id} no encontrado"}), 404

            relacion = GestionCursoParalelo(
                gestion_id=nueva_gestion.id,
                curso_paralelo_id=cp_id
            )
            db.session.add(relacion)

            detalle_cursos.append({
                "curso_paralelo_id": curso_paralelo.id,
                "curso": curso_paralelo.curso.nombre,
                "paralelo": curso_paralelo.paralelo.nombre
            })

        db.session.commit()

        return jsonify({
            "message": "Gestión creada y cursos paralelos asociados correctamente.",
            "gestion": {
                "id": nueva_gestion.id,
                "nombre": nueva_gestion.nombre,
                "cursos_paralelos": detalle_cursos
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al guardar gestión: {str(e)}"}), 500

@gestion_bp.route('/actualizar/<int:gestion_id>', methods=['PATCH'])
def actualizar_gestion(gestion_id):
    gestion = Gestion.query.get_or_404(gestion_id)

    try:
        data = request.get_json()

        # 1. Actualizar nombre si se envía
        if 'nombre' in data:
            nuevo_nombre = data['nombre'].strip()
            if nuevo_nombre:
                gestion.nombre = nuevo_nombre

        if 'cursos_paralelos_ids' in data:
            nuevos_ids = data['cursos_paralelos_ids']
            if not isinstance(nuevos_ids, list) or not all(isinstance(i, int) for i in nuevos_ids):
                return jsonify({"error": "El campo 'cursos_paralelos_ids' debe ser una lista de enteros."}), 400

            GestionCursoParalelo.query.filter_by(gestion_id=gestion.id).delete(synchronize_session=False)

            for cp_id in nuevos_ids:
                curso_paralelo = CursoParalelo.query.get(cp_id)
                if not curso_paralelo:
                    db.session.rollback()
                    return jsonify({"error": f"CursoParalelo con id {cp_id} no encontrado"}), 404

                nueva_rel = GestionCursoParalelo(
                    gestion_id=gestion.id,
                    curso_paralelo_id=cp_id
                )
                db.session.add(nueva_rel)

        db.session.commit()

        relaciones_actuales = GestionCursoParalelo.query.filter_by(gestion_id=gestion.id).all()
        cursos = [{
            "curso_paralelo_id": r.curso_paralelo.id,
            "curso": r.curso_paralelo.curso.nombre,
            "paralelo": r.curso_paralelo.paralelo.nombre
        } for r in relaciones_actuales]

        return jsonify({
            "message": "Gestión actualizada correctamente.",
            "gestion": {
                "id": gestion.id,
                "nombre": gestion.nombre,
                "cursos_paralelos": cursos
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar gestión: {str(e)}"}), 500

@gestion_bp.route('/eliminar/<int:gestion_id>', methods=['DELETE'])
def eliminar_gestion(gestion_id):
    gestion = Gestion.query.get_or_404(gestion_id)

    try:
        GestionCursoParalelo.query.filter_by(gestion_id=gestion.id).delete()

        db.session.delete(gestion)
        db.session.commit()

        return jsonify({"message": "Gestión y relaciones eliminadas correctamente."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo eliminar la gestión: {str(e)}"}), 500

# Designar Materia del Profesor a un Curso Paralelo
@gestion_bp.route('/buscar_materia/<int:materia_id>', methods=['GET'])
def buscar_materia(materia_id):
    try:
        materia = Materia.query.get_or_404(materia_id)

        profesores_data = []

        for mp in materia.materia_profesor:
            profesor = mp.profesor
            user = profesor.user_profesor

            dias_horarios = []
            for mpdh in mp.materia_profesor_dia_horario:
                dia = mpdh.dia_horario.dia
                horario = mpdh.dia_horario.horario

                dias_horarios.append({
                    "dia_id": dia.id,
                    "dia_nombre": dia.nombre,
                    "horario": {
                        "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
                        "hora_final": horario.hora_final.strftime("%H:%M")
                    }
                })

            profesores_data.append({
                "profesor_id": profesor.id,
                "nombre": profesor.nombre,
                "apellido": profesor.apellido,
                "ci": profesor.ci,
                "telefono": profesor.telefono,
                "direccion": profesor.direccion,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "photo_url": user.photo_url
                },
                "dias_horarios": dias_horarios
            })

        return jsonify({
            "materia_id": materia.id,
            "materia_nombre": materia.nombre,
            "profesores": profesores_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gestion_bp.route('/asignar_materias_gestion_cp', methods=['POST'])
def asignar_materias_gestion_cp():
    try:
        data = request.get_json()
        gestion_id = data.get("gestion_id")
        curso_paralelo_id = data.get("curso_paralelo_id")
        materias_profesores = data.get("materias_profesores", [])

        errors = []
        if not gestion_id or not curso_paralelo_id:
            errors.append("Faltan 'gestion_id' o 'curso_paralelo_id'")
        if not isinstance(materias_profesores, list):
            errors.append("materias_profesores debe ser una lista")
        if errors:
            return jsonify({"errors": errors}), 400

        gcp = GestionCursoParalelo.query.filter_by(
            gestion_id=gestion_id,
            curso_paralelo_id=curso_paralelo_id
        ).first()
        if not gcp:
            return jsonify({"error": "No existe la relación gestión-curso paralelo"}), 404

        asignaciones_existentes = MateriaHorarioCursoParalelo.query.filter_by(
            gestion_curso_paralelo_id=gcp.id
        ).join(MateriaProfesorDiaHorario).all()

        horarios_ocupados = set(
            m.materia_profesor_dia_horario.dia_horario_id for m in asignaciones_existentes
        )
        materias_asignadas = set(
            (m.materia_profesor_dia_horario.materia_profesor.materia_id, m.materia_profesor_dia_horario.materia_profesor.profesor_id) for m in asignaciones_existentes
        )

        nuevos_registros = []

        for mp_data in materias_profesores:
            materia_id = mp_data.get("materia_id")
            profesor_id = mp_data.get("profesor_id")

            materia_profesor = MateriaProfesor.query.filter_by(
                materia_id=materia_id,
                profesor_id=profesor_id
            ).first()
            if not materia_profesor:
                return jsonify({"error": f"No se encontró relación materia-profesor con materia_id {materia_id} y profesor_id {profesor_id}"}), 404

            if (materia_id, profesor_id) in materias_asignadas:
                continue

            for mpdh in materia_profesor.materia_profesor_dia_horario:
                dia_horario_id = mpdh.dia_horario_id

                if dia_horario_id in horarios_ocupados:
                    continue

                mhcp = MateriaHorarioCursoParalelo(
                    gestion_curso_paralelo_id=gcp.id,
                    materia_profesor_dia_horario_id=mpdh.id
                )
                db.session.add(mhcp)

                horarios_ocupados.add(dia_horario_id)
                nuevos_registros.append(mhcp)

            materias_asignadas.add((materia_id, profesor_id))

        db.session.commit()

        # Construir respuesta detallada agrupando por materia y profesor
        cp = gcp.curso_paralelo
        materias_asignadas_info = []
        grouped = {}
        for mhcp in nuevos_registros:
            mpdh = mhcp.materia_profesor_dia_horario
            mp = mpdh.materia_profesor
            materia = mp.materia
            profesor = mp.profesor
            user = profesor.user_profesor
            dia = mpdh.dia_horario.dia
            horario = mpdh.dia_horario.horario

            key = (materia.id, profesor.id)
            if key not in grouped:
                grouped[key] = {
                    "materia_id": materia.id,
                    "materia_nombre": materia.nombre,
                    "profesor": {
                        "id": profesor.id,
                        "nombre": profesor.nombre,
                        "apellido": profesor.apellido,
                        "ci": profesor.ci,
                        "telefono": profesor.telefono,
                        "direccion": profesor.direccion,
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "name": user.name,
                            "photo_url": user.photo_url
                        }
                    },
                    "horarios": []
                }
            grouped[key]["horarios"].append({
                "dia": dia.nombre,
                "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
                "hora_final": horario.hora_final.strftime("%H:%M")
            })

        materias_asignadas_info = list(grouped.values())

        return jsonify({
            "message": "Materias asignadas correctamente.",
            "gestion": {
                "id": gcp.gestion.id,
                "nombre": gcp.gestion.nombre
            },
            "curso_paralelo": {
                "id": cp.id,
                "curso": cp.curso.nombre,
                "paralelo": cp.paralelo.nombre
            },
            "materias_asignadas": materias_asignadas_info
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@gestion_bp.route('/actualizar_materias_gestion_cp', methods=['PUT'])
def actualizar_materias_gestion_cp():
    try:
        data = request.get_json()
        gestion_id = data.get("gestion_id")
        curso_paralelo_id = data.get("curso_paralelo_id")
        materias_profesores = data.get("materias_profesores", [])

        if not gestion_id or not curso_paralelo_id:
            return jsonify({"error": "Faltan 'gestion_id' o 'curso_paralelo_id'"}), 400

        gcp = GestionCursoParalelo.query.filter_by(
            gestion_id=gestion_id,
            curso_paralelo_id=curso_paralelo_id
        ).first()
        if not gcp:
            return jsonify({"error": "No existe la relación gestión-curso paralelo"}), 404

        # Eliminar todas las asignaciones anteriores
        MateriaHorarioCursoParalelo.query.filter_by(
            gestion_curso_paralelo_id=gcp.id
        ).delete()

        nuevos_registros = []

        for item in materias_profesores:
            materia_id = item.get("materia_id")
            profesor_id = item.get("profesor_id")

            materia_profesor = MateriaProfesor.query.filter_by(
                materia_id=materia_id,
                profesor_id=profesor_id
            ).first()
            if not materia_profesor:
                continue

            for mpdh in materia_profesor.materia_profesor_dia_horario:
                mhcp = MateriaHorarioCursoParalelo(
                    gestion_curso_paralelo_id=gcp.id,
                    materia_profesor_dia_horario_id=mpdh.id
                )
                db.session.add(mhcp)
                nuevos_registros.append(mhcp)

        db.session.commit()

        cp = gcp.curso_paralelo
        grouped = {}
        for mhcp in MateriaHorarioCursoParalelo.query.filter_by(gestion_curso_paralelo_id=gcp.id).all():
            mpdh = mhcp.materia_profesor_dia_horario
            mp = mpdh.materia_profesor
            materia = mp.materia
            profesor = mp.profesor
            user = profesor.user_profesor
            dia = mpdh.dia_horario.dia
            horario = mpdh.dia_horario.horario

            key = (materia.id, profesor.id)
            if key not in grouped:
                grouped[key] = {
                    "materia_id": materia.id,
                    "materia_nombre": materia.nombre,
                    "profesor": {
                        "id": profesor.id,
                        "nombre": profesor.nombre,
                        "apellido": profesor.apellido,
                        "ci": profesor.ci,
                        "telefono": profesor.telefono,
                        "direccion": profesor.direccion,
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "name": user.name,
                            "photo_url": user.photo_url
                        }
                    },
                    "horarios": []
                }

            grouped[key]["horarios"].append({
                "dia": dia.nombre,
                "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
                "hora_final": horario.hora_final.strftime("%H:%M")
            })

        materias_asignadas_info = list(grouped.values())

        return jsonify({
            "message": "Materias actualizadas correctamente.",
            "gestion": {
                "id": gcp.gestion.id,
                "nombre": gcp.gestion.nombre
            },
            "curso_paralelo": {
                "id": cp.id,
                "curso": cp.curso.nombre,
                "paralelo": cp.paralelo.nombre
            },
            "materias_asignadas": materias_asignadas_info
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@gestion_bp.route('/detalle_gestion_completo', methods=['GET'])
def detalle_gestion_completo():
    try:
        gestiones = Gestion.query.all()
        resultado = []

        for g in gestiones:
            gestion_dict = {
                "gestion_id": g.id,
                "nombre": g.nombre,
                "cursos_paralelos": []
            }

            for gcp in g.gestion_curso_paralelos:
                cp = gcp.curso_paralelo
                cp_dict = {
                    "curso_paralelo_id": cp.id,
                    "curso": cp.curso.nombre,
                    "paralelo": cp.paralelo.nombre,
                    "materias": []
                }

                for mhcp in gcp.materia_horario_curso_paralelo_rel:
                    mpdh = mhcp.materia_profesor_dia_horario
                    mp = mpdh.materia_profesor
                    materia = mp.materia
                    profesor = mp.profesor
                    user = profesor.user_profesor
                    dia = mpdh.dia_horario.dia
                    horario = mpdh.dia_horario.horario

                    cp_dict["materias"].append({
                        "materia_id": materia.id,
                        "materia_nombre": materia.nombre,
                        "dia": dia.nombre,
                        "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
                        "hora_final": horario.hora_final.strftime("%H:%M"),
                        "profesor": {
                            "id": profesor.id,
                            "nombre": profesor.nombre,
                            "apellido": profesor.apellido,
                            "ci": profesor.ci,
                            "telefono": profesor.telefono,
                            "direccion": profesor.direccion,
                            "user": {
                                "id": user.id,
                                "email": user.email,
                                "name": user.name,
                                "photo_url": user.photo_url
                            }
                        }
                    })

                gestion_dict["cursos_paralelos"].append(cp_dict)

            resultado.append(gestion_dict)

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gestion_bp.route('/listar_cursos_por_gestion', methods=['GET'])
def listar_cursos_por_gestion():
    try:
        gestiones = Gestion.query.options(
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.curso_paralelo)
            .joinedload(CursoParalelo.curso),
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.curso_paralelo)
            .joinedload(CursoParalelo.paralelo)
        ).all()

        resultado = []
        for g in gestiones:
            gestion_dict = {
                "id": g.id,
                "nombre": g.nombre,
                "cursos_paralelos": []
            }

            for gcp in g.gestion_curso_paralelos:
                cp = gcp.curso_paralelo
                gestion_dict["cursos_paralelos"].append({
                    "curso_paralelo_id": cp.id,
                    "curso": cp.curso.nombre,
                    "paralelo": cp.paralelo.nombre
                })

            resultado.append(gestion_dict)

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
