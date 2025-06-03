from flask import Blueprint, jsonify
from sqlalchemy.orm import joinedload
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models.user import User
from ..models.rol import Rol
from ..models.gestion import Gestion
from ..models.gestion_curso_paralelo import GestionCursoParalelo
from ..models.profesor import Profesor
from ..models.dia_horario import DiaHorario
from ..models.materia_horario_curso_paralelo import MateriaHorarioCursoParalelo
from ..models.boleta_inscripcion import BoletaInscripcion
from ..models.estudiante import Estudiante
from ..models.asistencia import Asistencia
from ..models.estudiante_asistencia import EstudianteAsistencia
from ..models.participacion import Participacion
from ..models.estudiante_participa import EstudianteParticipa
from ..models.nota import Nota

apimovil_pb = Blueprint("apimovil_pb", __name__)

@apimovil_pb.route("/listar_administrador_estructura", methods=["GET"])
def listar_administrador_estructura():
    try:
        admin_users = User.query.join(Rol).filter(Rol.nombre == "Administrador").all()
        if not admin_users:
            return jsonify({"error": "No se encontraron usuarios con rol Administrador"}), 404

        gestiones = Gestion.query.options(joinedload(Gestion.gestion_curso_paralelos)).all()
        admins_json = []

        for admin_user in admin_users:
            rol_admin = Rol.query.get(admin_user.rol_id)

            gestiones_json = []
            for gestion in gestiones:
                gcp_list = GestionCursoParalelo.query.filter_by(gestion_id=gestion.id).all()
                gcp_json = []

                for gcp in gcp_list:
                    cp = gcp.curso_paralelo
                    curso = cp.curso
                    paralelo = cp.paralelo

                    materias_json = []
                    mhcps = MateriaHorarioCursoParalelo.query.filter_by(gestion_curso_paralelo_id=gcp.id).all()

                    for mhcp in mhcps:
                        mpdh = mhcp.materia_profesor_dia_horario
                        mp = mpdh.materia_profesor
                        profesor = mp.profesor
                        materia = mp.materia
                        dh = mpdh.dia_horario
                        horario = dh.horario
                        dias = DiaHorario.query.filter_by(horario_id=horario.id).all()
                        dias_nombres = list(set([d.dia.nombre for d in dias]))

                        estudiantes_inscritos = BoletaInscripcion.query.filter_by(gestion_curso_paralelo_id=gcp.id).all()
                        estudiantes_json = [
                            {
                                "estudiante_id": bi.estudiante.id,
                                "estudiante_ci": bi.estudiante.ci,
                                "estudiante_nombre": bi.estudiante.nombre,
                                "estudiante_apellido": bi.estudiante.apellido,
                                "estudiante_sexo": bi.estudiante.sexo,
                                "estudiante_telefono": bi.estudiante.telefono
                            } for bi in estudiantes_inscritos
                        ]

                        materias_json.append({
                            "materia_id": materia.id,
                            "materia_nombre": materia.nombre,
                            "profesor": {
                                "profesor_id": profesor.id,
                                "profesor_ci": profesor.ci,
                                "profesor_nombre": profesor.nombre,
                                "profesor_apellido": profesor.apellido,
                                "profesor_telefono": profesor.telefono
                            },
                            "horario": {
                                "horario_id": horario.id,
                                "horario_inicio": horario.hora_inicio.strftime('%H:%M'),
                                "horario_final": horario.hora_final.strftime('%H:%M'),
                                "dias": dias_nombres
                            },
                            "estudiante": estudiantes_json
                        })

                    gcp_json.append({
                        "gestion_curso_paralelo_id": gcp.id,
                        "curso_paralelo": {
                            "curso_id": curso.id,
                            "curso_nombre": curso.nombre,
                            "paralelo_id": paralelo.id,
                            "paralelo_nombre": paralelo.nombre,
                            "materia": materias_json
                        }
                    })

                gestiones_json.append({
                    "gestion_id": gestion.id,
                    "gestion_nombre": gestion.nombre,
                    "gestion_curso_paralelo": gcp_json
                })

            admins_json.append({
                "rol_id": rol_admin.id,
                "rol_nombre": rol_admin.nombre,
                "users_id": admin_user.id,
                "users_name": admin_user.name,
                "users_email": admin_user.email,
                "password": "Encriptado",
                "photo_url": admin_user.photo_url,
                "photo_storage": admin_user.photo_storage,
                "status": str(admin_user.status),
                "gestion": gestiones_json
            })

        return jsonify(admins_json), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@apimovil_pb.route('/listar_profesor_estructura', methods=['GET'])
def listar_profesor_estructura():
    try:
        usuarios_profesores = User.query.join(Rol).filter(Rol.nombre == "Profesor").all()
        if not usuarios_profesores:
            return jsonify({"error": "No se encontraron usuarios con rol Profesor"}), 404

        profesores_json = []

        for user in usuarios_profesores:
            rol = Rol.query.get(user.rol_id)
            profesor = Profesor.query.filter_by(users_profesor_id=user.id).first()
            if not profesor:
                continue

            gestiones_json = []
            gestiones = Gestion.query.all()

            for gestion in gestiones:
                gcp_list = GestionCursoParalelo.query.filter_by(gestion_id=gestion.id).all()
                gcp_json = []

                for gcp in gcp_list:
                    mhcps = MateriaHorarioCursoParalelo.query.filter_by(gestion_curso_paralelo_id=gcp.id).all()
                    materias_json = []

                    for mhcp in mhcps:
                        mpdh = mhcp.materia_profesor_dia_horario
                        mp = mpdh.materia_profesor

                        if mp.profesor_id != profesor.id:
                            continue

                        materia = mp.materia
                        cp = gcp.curso_paralelo
                        curso = cp.curso
                        paralelo = cp.paralelo
                        dh = mpdh.dia_horario
                        horario = dh.horario

                        dias = DiaHorario.query.filter_by(horario_id=horario.id).all()
                        dias_nombres = list(set([d.dia.nombre for d in dias]))

                        estudiantes_inscritos = BoletaInscripcion.query.filter_by(gestion_curso_paralelo_id=gcp.id).all()
                        estudiantes_json = [
                            {
                                "estudiante_id": bi.estudiante.id,
                                "estudiante_ci": bi.estudiante.ci,
                                "estudiante_nombre": bi.estudiante.nombre,
                                "estudiante_apellido": bi.estudiante.apellido,
                                "estudiante_sexo": bi.estudiante.sexo,
                                "estudiante_telefono": bi.estudiante.telefono
                            } for bi in estudiantes_inscritos
                        ]

                        materias_json.append({
                            "materia_id": materia.id,
                            "materia_nombre": materia.nombre,
                            "cursos_paralelo": [{
                                "curso_paralelo_id": cp.id,
                                "curso_id": curso.id,
                                "curso_nombre": curso.nombre,
                                "paralelo_id": paralelo.id,
                                "paralelo_nombre": paralelo.nombre,
                                "horario": {
                                    "horario_id": horario.id,
                                    "horario_inicio": horario.hora_inicio.strftime('%H:%M'),
                                    "horario_final": horario.hora_final.strftime('%H:%M'),
                                    "dias": dias_nombres
                                },
                                "estudiante": estudiantes_json
                            }]
                        })

                    if materias_json:
                        gcp_json.append({
                            "gestion_curso_paralelo_id": gcp.id,
                            "materia": materias_json
                        })

                if gcp_json:
                    gestiones_json.append({
                        "gestion_id": gestion.id,
                        "gestion_nombre": gestion.nombre,
                        "gestion_curso_paralelo": gcp_json
                    })

            profesores_json.append({
                "rol_id": rol.id,
                "rol_nombre": rol.nombre,
                "users_id": user.id,
                "users_name": user.name,
                "users_email": user.email,
                "password": "Encriptado",
                "photo_url": user.photo_url,
                "photo_storage": user.photo_storage,
                "status": str(user.status),
                "profesor": {
                    "users_profesor_id": profesor.users_profesor_id,
                    "profesor_id": profesor.id,
                    "profesor_ci": profesor.ci,
                    "profesor_nombre": profesor.nombre,
                    "profesor_apellido": profesor.apellido,
                    "profesor_telefono": profesor.telefono,
                    "profesor_direccion": profesor.direccion,
                    "users_id": profesor.users_id,
                },
                "gestion": gestiones_json
            })

        return jsonify(profesores_json), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@apimovil_pb.route("/listar_estudiante_estructura", methods=["GET"])
def listar_estudiante_estructura():
    try:
        estudiantes_data = []

        estudiantes_users = User.query.join(Rol).filter(Rol.nombre == "Estudiante").all()

        for user in estudiantes_users:
            estudiante = Estudiante.query.filter_by(users_estudiante_id=user.id).first()
            if not estudiante:
                continue

            gestiones_json = []
            boletas = BoletaInscripcion.query.filter_by(estudiante_id=estudiante.id).all()

            for boleta in boletas:
                gcp = boleta.gestion_curso_paralelo
                gestion = gcp.gestion
                cp = gcp.curso_paralelo
                curso = cp.curso
                paralelo = cp.paralelo

                # Asistencias del estudiante
                asistencias = Asistencia.query.filter_by(gestion_curso_paralelo_id=gcp.id).all()
                asistencia_json = []
                for a in asistencias:
                    ea = EstudianteAsistencia.query.filter_by(estudiante_id=estudiante.id, asistencia_id=a.id).first()
                    if ea:
                        asistencia_json.append({
                            "asistencia_id": a.id,
                            "asistencia_hora": a.hora.strftime('%H:%M'),
                            "asistencia_fecha": a.fecha.strftime('%Y-%m-%d'),
                            "estudiante_asistencia": {
                                "estudiante_asistencia_id": ea.id,
                                "estudiante_asistencia_estado": ea.estado
                            }
                        })

                # Materias
                materias_json = []
                mhcps = MateriaHorarioCursoParalelo.query.filter_by(gestion_curso_paralelo_id=gcp.id).all()
                for mhcp in mhcps:
                    mpdh = mhcp.materia_profesor_dia_horario
                    mp = mpdh.materia_profesor
                    materia = mp.materia
                    profesor = mp.profesor
                    dh = mpdh.dia_horario
                    horario = dh.horario

                    dias = DiaHorario.query.filter_by(horario_id=horario.id).all()
                    dias_nombres = list(set([d.dia.nombre for d in dias]))

                    # Participaciones
                    participaciones = Participacion.query.filter_by(gestion_curso_paralelo_id=gcp.id, materia_profesor_id=mp.id).all()
                    participacion_json = []
                    for p in participaciones:
                        ep = EstudianteParticipa.query.filter_by(estudiante_id=estudiante.id, participacion_id=p.id).first()
                        if ep:
                            participacion_json.append({
                                "participacion_id": p.id,
                                "participacion_descripcion": p.descripcion,
                                "participacion_hora": p.hora.strftime('%H:%M'),
                                "participacion_fecha": p.fecha.strftime('%Y-%m-%d'),
                                "estudiante_participa": {
                                    "estudiante_participa_id": ep.id,
                                    "estudiante_participa_estado": ep.estado
                                }
                            })

                    # Nota
                    nota = Nota.query.filter_by(estudiante_id=estudiante.id, gestion_curso_paralelo_id=gcp.id, materia_profesor_id=mp.id).first()

                    materias_json.append({
                        "materia_id": materia.id,
                        "materia_nombre": materia.nombre,
                        "participacion": participacion_json,
                        "nota": {
                            "nota_id": nota.id if nota else None,
                            "nota_promedio_final": nota.promedio_final if nota else None
                        },
                        "horario": {
                            "horario_id": horario.id,
                            "horario_inicio": horario.hora_inicio.strftime('%H:%M'),
                            "horario_final": horario.hora_final.strftime('%H:%M'),
                            "dias": dias_nombres
                        },
                        "profesor": {
                            "profesor_id": profesor.id,
                            "profesor_ci": profesor.ci,
                            "profesor_nombre": profesor.nombre,
                            "profesor_apellido": profesor.apellido,
                            "profesor_telefono": profesor.telefono,
                            "profesor_direccion": profesor.direccion
                        }
                    })

                gestiones_json.append({
                    "gestion_id": gestion.id,
                    "gestion_nombre": gestion.nombre,
                    "gestion_curso_paralelo": {
                        "gestion_curso_paralelo_id": gcp.id,
                        "cursos_paralelo": {
                            "curso_paralelo_id": cp.id,
                            "curso_id": curso.id,
                            "curso_nombre": curso.nombre,
                            "paralelo_id": paralelo.id,
                            "paralelo_nombre": paralelo.nombre,
                            "asistencia": asistencia_json,
                            "materia": materias_json
                        }
                    }
                })

            estudiantes_data.append({
                "rol_id": user.rol.id,
                "rol_nombre": user.rol.nombre,
                "users_id": user.id,
                "users_name": user.name,
                "users_email": user.email,
                "password": "Encriptado",
                "photo_url": user.photo_url,
                "photo_storage": user.photo_storage,
                "status": str(user.status),
                "estudiante": {
                    "users_estudiante_id": estudiante.users_estudiante_id,
                    "estudiante_id": estudiante.id,
                    "estudiante_ci": estudiante.ci,
                    "estudiante_nombre": estudiante.nombre,
                    "estudiante_apellido": estudiante.apellido,
                    "estudiante_telefono": estudiante.telefono,
                    "users_id": estudiante.users_id
                },
                "gestion": gestiones_json
            })

        return jsonify(estudiantes_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
