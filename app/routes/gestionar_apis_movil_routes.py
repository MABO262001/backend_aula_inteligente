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
from ..models.apoderado import Apoderado
from ..models.parentesco import Parentesco
from ..models.materia_profesor import MateriaProfesor
from ..models.materia_profesor_dia_horario import MateriaProfesorDiaHorario
from ..models.curso_paralelo import CursoParalelo


apimovil_pb = Blueprint("apimovil_pb", __name__)

@apimovil_pb.route('/listar_administrador_estructura', methods=['GET'])
def listar_administrador_estructura():
    try:
        admin_users = User.query.options(joinedload(User.rol)).join(Rol).filter(Rol.nombre == "Administrador").all()
        if not admin_users:
            return jsonify({"error": "No se encontraron usuarios con rol Administrador"}), 404

        gestiones = Gestion.query.options(
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.curso_paralelo)
            .joinedload(CursoParalelo.curso),
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.curso_paralelo)
            .joinedload(CursoParalelo.paralelo),
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.materias_horario)
            .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
            .joinedload(MateriaProfesorDiaHorario.materia_profesor)
            .joinedload(MateriaProfesor.profesor),
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.materias_horario)
            .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
            .joinedload(MateriaProfesorDiaHorario.materia_profesor)
            .joinedload(MateriaProfesor.materia),
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.materias_horario)
            .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
            .joinedload(MateriaProfesorDiaHorario.dia_horario)
            .joinedload(DiaHorario.horario)
        ).all()

        admins_json = []

        for admin_user in admin_users:
            gestiones_json = []
            for gestion in gestiones:
                gcp_json = []
                for gcp in gestion.gestion_curso_paralelos:
                    cp = gcp.curso_paralelo
                    curso = cp.curso
                    paralelo = cp.paralelo

                    materias_json = []
                    for mhcp in gcp.materias_horario:
                        mpdh = mhcp.materia_profesor_dia_horario
                        mp = mpdh.materia_profesor
                        profesor = mp.profesor
                        materia = mp.materia
                        dh = mpdh.dia_horario
                        horario = dh.horario
                        dias = [d.dia.nombre for d in DiaHorario.query.filter_by(horario_id=horario.id).all()]
                        dias_nombres = list(set(dias))

                        estudiantes_inscritos = BoletaInscripcion.query.options(
                            joinedload(BoletaInscripcion.estudiante)
                        ).filter_by(gestion_curso_paralelo_id=gcp.id).all()

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
                "rol_id": admin_user.rol.id,
                "rol_nombre": admin_user.rol.nombre,
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

@apimovil_pb.route('/listar_administrador_estructura/administrador/<int:user_id>', methods=['GET'])
def listar_administrador_estructura_por_id(user_id):
    try:
        admin_user = User.query.options(joinedload(User.rol)).get(user_id)
        if not admin_user or admin_user.rol.nombre != "Administrador":
            return jsonify({"error": "Administrador no encontrado"}), 404

        gestiones = Gestion.query.options(
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.curso_paralelo)
            .joinedload(CursoParalelo.curso),
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.curso_paralelo)
            .joinedload(CursoParalelo.paralelo),
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.materias_horario)
            .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
            .joinedload(MateriaProfesorDiaHorario.materia_profesor)
            .joinedload(MateriaProfesor.profesor),
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.materias_horario)
            .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
            .joinedload(MateriaProfesorDiaHorario.materia_profesor)
            .joinedload(MateriaProfesor.materia),
            joinedload(Gestion.gestion_curso_paralelos)
            .joinedload(GestionCursoParalelo.materias_horario)
            .joinedload(MateriaHorarioCursoParalelo.materia_profesor_dia_horario)
            .joinedload(MateriaProfesorDiaHorario.dia_horario)
            .joinedload(DiaHorario.horario)
        ).all()

        gestiones_json = [
            {
                "gestion_id": gestion.id,
                "gestion_nombre": gestion.nombre,
                "gestion_curso_paralelo": [
                    {
                        "gestion_curso_paralelo_id": gcp.id,
                        "curso_paralelo": {
                            "curso_id": gcp.curso_paralelo.curso.id,
                            "curso_nombre": gcp.curso_paralelo.curso.nombre,
                            "paralelo_id": gcp.curso_paralelo.paralelo.id,
                            "paralelo_nombre": gcp.curso_paralelo.paralelo.nombre,
                            "materia": [
                                {
                                    "materia_id": mhcp.materia_profesor_dia_horario.materia_profesor.materia.id,
                                    "materia_nombre": mhcp.materia_profesor_dia_horario.materia_profesor.materia.nombre,
                                    "profesor": {
                                        "profesor_id": mhcp.materia_profesor_dia_horario.materia_profesor.profesor.id,
                                        "profesor_ci": mhcp.materia_profesor_dia_horario.materia_profesor.profesor.ci,
                                        "profesor_nombre": mhcp.materia_profesor_dia_horario.materia_profesor.profesor.nombre,
                                        "profesor_apellido": mhcp.materia_profesor_dia_horario.materia_profesor.profesor.apellido,
                                        "profesor_telefono": mhcp.materia_profesor_dia_horario.materia_profesor.profesor.telefono
                                    },
                                    "horario": {
                                        "horario_id": mhcp.materia_profesor_dia_horario.dia_horario.horario.id,
                                        "horario_inicio": mhcp.materia_profesor_dia_horario.dia_horario.horario.hora_inicio.strftime('%H:%M'),
                                        "horario_final": mhcp.materia_profesor_dia_horario.dia_horario.horario.hora_final.strftime('%H:%M'),
                                        "dias": list(set(
                                            d.dia.nombre for d in DiaHorario.query.filter_by(
                                                horario_id=mhcp.materia_profesor_dia_horario.dia_horario.horario.id
                                            ).all()
                                        ))
                                    },
                                    "estudiante": [
                                        {
                                            "estudiante_id": bi.estudiante.id,
                                            "estudiante_ci": bi.estudiante.ci,
                                            "estudiante_nombre": bi.estudiante.nombre,
                                            "estudiante_apellido": bi.estudiante.apellido,
                                            "estudiante_sexo": bi.estudiante.sexo,
                                            "estudiante_telefono": bi.estudiante.telefono
                                        } for bi in BoletaInscripcion.query.options(
                                            joinedload(BoletaInscripcion.estudiante)
                                        ).filter_by(gestion_curso_paralelo_id=gcp.id).all()
                                    ]
                                } for mhcp in gcp.materias_horario
                            ]
                        }
                    } for gcp in gestion.gestion_curso_paralelos
                ]
            } for gestion in gestiones
        ]

        return jsonify({
            "rol_id": admin_user.rol.id,
            "rol_nombre": admin_user.rol.nombre,
            "users_id": admin_user.id,
            "users_name": admin_user.name,
            "users_email": admin_user.email,
            "password": "Encriptado",
            "photo_url": admin_user.photo_url,
            "photo_storage": admin_user.photo_storage,
            "status": str(admin_user.status),
            "gestion": gestiones_json
        }), 200

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

@apimovil_pb.route('/listar_profesor_estructura/profesor/<int:profesor_id>', methods=['GET'])
def listar_profesor_estructura_por_id(profesor_id):
    try:
        profesor = Profesor.query.get(profesor_id)
        if not profesor:
            return jsonify({"error": "Profesor no encontrado"}), 404

        user = User.query.get(profesor.users_profesor_id)
        rol = Rol.query.get(user.rol_id)

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

        return jsonify({
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
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@apimovil_pb.route("/listar_estudiante_estructura", methods=["GET"])
def listar_estudiante_estructura():
    try:
        estudiantes_users = User.query.options(
            joinedload(User.rol),
            joinedload(User.estudiante),
            joinedload(User.estudiante).joinedload(Estudiante.boletas)
                .joinedload(BoletaInscripcion.gestion_curso_paralelo)
                .joinedload(GestionCursoParalelo.curso_paralelo)
                .joinedload(CursoParalelo.curso),
            joinedload(User.estudiante).joinedload(Estudiante.boletas)
                .joinedload(BoletaInscripcion.gestion_curso_paralelo)
                .joinedload(GestionCursoParalelo.curso_paralelo)
                .joinedload(CursoParalelo.paralelo),
            joinedload(User.estudiante).joinedload(Estudiante.boletas)
                .joinedload(BoletaInscripcion.gestion_curso_paralelo)
                .joinedload(GestionCursoParalelo.gestion),
        ).join(Rol).filter(Rol.nombre == "Estudiante").all()

        estudiantes_data = []

        for user in estudiantes_users:
            estudiante = user.estudiante
            if not estudiante:
                continue

            gestiones_json = []

            for boleta in estudiante.boletas:
                gcp = boleta.gestion_curso_paralelo
                gestion = gcp.gestion
                cp = gcp.curso_paralelo
                curso = cp.curso
                paralelo = cp.paralelo

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

                materias_json = []
                mhcps = MateriaHorarioCursoParalelo.query.filter_by(gestion_curso_paralelo_id=gcp.id).all()
                for mhcp in mhcps:
                    mpdh = mhcp.materia_profesor_dia_horario
                    mp = mpdh.materia_profesor
                    materia = mp.materia
                    profesor = mp.profesor
                    horario = mpdh.dia_horario.horario

                    dias = DiaHorario.query.filter_by(horario_id=horario.id).all()
                    dias_nombres = list(set([d.dia.nombre for d in dias]))

                    participaciones = Participacion.query.filter_by(
                        gestion_curso_paralelo_id=gcp.id,
                        materia_profesor_id=mp.id
                    ).all()

                    participacion_json = []
                    for p in participaciones:
                        ep = EstudianteParticipa.query.filter_by(
                            estudiante_id=estudiante.id,
                            participacion_id=p.id
                        ).first()
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

                    nota = Nota.query.filter_by(
                        estudiante_id=estudiante.id,
                        gestion_curso_paralelo_id=gcp.id,
                        materia_profesor_id=mp.id
                    ).first()

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

@apimovil_pb.route('/listar_estudiante_estructura/estudiante/<int:estudiante_id>', methods=['GET'])
def listar_estudiante_estructura_por_id(estudiante_id):
    try:
        estudiante = Estudiante.query.get(estudiante_id)
        if not estudiante:
            return jsonify({"error": "Estudiante no encontrado"}), 404

        user = User.query.options(joinedload(User.rol)).get(estudiante.users_estudiante_id)
        if not user or user.rol.nombre != "Estudiante":
            return jsonify({"error": "Usuario estudiante no encontrado"}), 404

        gestiones_json = []
        boletas = BoletaInscripcion.query.options(
            joinedload(BoletaInscripcion.gestion_curso_paralelo)
                .joinedload(GestionCursoParalelo.curso_paralelo)
                .joinedload(CursoParalelo.curso),
            joinedload(BoletaInscripcion.gestion_curso_paralelo)
                .joinedload(GestionCursoParalelo.curso_paralelo)
                .joinedload(CursoParalelo.paralelo),
            joinedload(BoletaInscripcion.gestion_curso_paralelo)
                .joinedload(GestionCursoParalelo.gestion)
        ).filter_by(estudiante_id=estudiante.id).all()

        for boleta in boletas:
            gcp = boleta.gestion_curso_paralelo
            gestion = gcp.gestion
            cp = gcp.curso_paralelo
            curso = cp.curso
            paralelo = cp.paralelo

            # Asistencias
            asistencia_json = []
            asistencias = Asistencia.query.filter_by(gestion_curso_paralelo_id=gcp.id).all()
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

                participacion_json = []
                participaciones = Participacion.query.filter_by(
                    gestion_curso_paralelo_id=gcp.id, materia_profesor_id=mp.id
                ).all()
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

                nota = Nota.query.filter_by(
                    estudiante_id=estudiante.id,
                    gestion_curso_paralelo_id=gcp.id,
                    materia_profesor_id=mp.id
                ).first()

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

        return jsonify({
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
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@apimovil_pb.route("/listar_apoderado_estructura", methods=["GET"])
def listar_apoderado_estructura():
    try:
        apoderados = User.query.join(Rol).filter(Rol.nombre == "Apoderado").all()
        data = []

        for user in apoderados:
            rol = user.rol
            apoderado = Apoderado.query.filter_by(users_apoderado_id=user.id).first()
            if not apoderado:
                continue

            parentescos = Parentesco.query.filter_by(apoderado_id=apoderado.id).all()
            gestiones_json = {}

            for parentesco in parentescos:
                est = parentesco.estudiante
                boletas = BoletaInscripcion.query.filter_by(estudiante_id=est.id).all()

                for boleta in boletas:
                    gcp = boleta.gestion_curso_paralelo
                    gestion = gcp.gestion
                    cp = gcp.curso_paralelo
                    curso = cp.curso
                    paralelo = cp.paralelo

                    asistencias_json = []
                    asistencias = Asistencia.query.filter_by(gestion_curso_paralelo_id=gcp.id).all()
                    for asistencia in asistencias:
                        ea = EstudianteAsistencia.query.filter_by(
                            estudiante_id=est.id, asistencia_id=asistencia.id
                        ).first()
                        if ea:
                            asistencias_json.append({
                                "asistencia_id": asistencia.id,
                                "asistencia_hora": asistencia.hora.strftime('%H:%M'),
                                "asistencia_fecha": asistencia.fecha.strftime('%Y-%m-%d'),
                                "estudiante_asistencia": {
                                    "estudiante_asistencia_id": ea.id,
                                    "estudiante_asistencia_estado": ea.estado
                                }
                            })

                    materias_json = []
                    mhcps = MateriaHorarioCursoParalelo.query.filter_by(gestion_curso_paralelo_id=gcp.id).all()
                    for mhcp in mhcps:
                        mpdh = mhcp.materia_profesor_dia_horario
                        mp = mpdh.materia_profesor
                        materia = mp.materia
                        profesor = mp.profesor
                        horario = mpdh.dia_horario.horario
                        dias_nombres = list(set(
                            d.dia.nombre for d in DiaHorario.query.filter_by(horario_id=horario.id).all()
                        ))

                        participaciones_json = []
                        participaciones = Participacion.query.filter_by(
                            gestion_curso_paralelo_id=gcp.id,
                            materia_profesor_id=mp.id
                        ).all()
                        for p in participaciones:
                            ep = EstudianteParticipa.query.filter_by(
                                estudiante_id=est.id, participacion_id=p.id
                            ).first()
                            if ep:
                                participaciones_json.append({
                                    "participacion_id": p.id,
                                    "participacion_descripcion": p.descripcion,
                                    "participacion_hora": p.hora.strftime('%H:%M'),
                                    "participacion_fecha": p.fecha.strftime('%Y-%m-%d'),
                                    "estudiante_participa": {
                                        "estudiante_participa_id": ep.id,
                                        "estudiante_participa_estado": ep.estado
                                    }
                                })

                        nota = Nota.query.filter_by(
                            estudiante_id=est.id,
                            gestion_curso_paralelo_id=gcp.id,
                            materia_profesor_id=mp.id
                        ).first()

                        materias_json.append({
                            "materia_id": materia.id,
                            "materia_nombre": materia.nombre,
                            "participacion": participaciones_json,
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

                    est_json = {
                        "estudiante_id": est.id,
                        "estudiante_ci": est.ci,
                        "estudiante_nombre": est.nombre,
                        "estudiante_apellido": est.apellido,
                        "estudiante_sexo": est.sexo,
                        "estudiante_telefono": est.telefono,
                        "parentesco": {
                            "parentesco_id": parentesco.id,
                            "parentesco_nombre": parentesco.nombre,
                        },
                        "curso_paralelo": {
                            "curso_paralelo_id": cp.id,
                            "curso_id": curso.id,
                            "curso_nombre": curso.nombre,
                            "paralelo_id": paralelo.id,
                            "paralelo_nombre": paralelo.nombre,
                            "asistencia": asistencias_json,
                            "materia": materias_json
                        }
                    }

                    if gestion.id not in gestiones_json:
                        gestiones_json[gestion.id] = {
                            "gestion_id": gestion.id,
                            "gestion_nombre": gestion.nombre,
                            "estudiantes": []
                        }

                    gestiones_json[gestion.id]["estudiantes"].append(est_json)

            data.append({
                "rol_id": rol.id,
                "rol_nombre": rol.nombre,
                "users_id": user.id,
                "users_name": user.name,
                "users_email": user.email,
                "password": "Encriptado",
                "photo_url": user.photo_url,
                "photo_storage": user.photo_storage,
                "status": str(user.status),
                "apoderado": {
                    "users_apoderado_id": apoderado.users_apoderado_id,
                    "apoderado_id": apoderado.id,
                    "apoderado_ci": apoderado.ci,
                    "apoderado_nombre": apoderado.nombre,
                    "apoderado_apellido": apoderado.apellido,
                    "apoderado_telefono": apoderado.telefono,
                    "users_id": apoderado.users_id
                },
                "gestion": list(gestiones_json.values())
            })

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@apimovil_pb.route("/listar_apoderado_estructura/apoderado/<int:apoderado_id>", methods=["GET"])
def listar_apoderado_estructura_por_id(apoderado_id):
    try:
        apoderado = Apoderado.query.options(
            joinedload(Apoderado.user_apoderado).joinedload(User.rol)
        ).get(apoderado_id)

        if not apoderado or apoderado.user_apoderado.rol.nombre != "Apoderado":
            return jsonify({"error": "Apoderado no encontrado o sin rol válido"}), 404

        user = apoderado.user_apoderado
        rol = user.rol
        gestiones_json = {}

        parentescos = Parentesco.query.filter_by(apoderado_id=apoderado.id).all()

        for parentesco in parentescos:
            est = parentesco.estudiante

            for boleta in est.boletas:
                gcp = boleta.gestion_curso_paralelo
                gestion = gcp.gestion
                cp = gcp.curso_paralelo
                curso = cp.curso
                paralelo = cp.paralelo

                asistencias_json = []
                for asistencia in Asistencia.query.filter_by(gestion_curso_paralelo_id=gcp.id):
                    ea = EstudianteAsistencia.query.filter_by(estudiante_id=est.id, asistencia_id=asistencia.id).first()
                    if ea:
                        asistencias_json.append({
                            "asistencia_id": asistencia.id,
                            "asistencia_hora": asistencia.hora.strftime('%H:%M'),
                            "asistencia_fecha": asistencia.fecha.strftime('%Y-%m-%d'),
                            "estudiante_asistencia": {
                                "estudiante_asistencia_id": ea.id,
                                "estudiante_asistencia_estado": ea.estado
                            }
                        })

                materias_json = []
                for mhcp in MateriaHorarioCursoParalelo.query.filter_by(gestion_curso_paralelo_id=gcp.id).all():
                    mpdh = mhcp.materia_profesor_dia_horario
                    mp = mpdh.materia_profesor
                    materia = mp.materia
                    profesor = mp.profesor
                    horario = mpdh.dia_horario.horario
                    dias = DiaHorario.query.filter_by(horario_id=horario.id).all()
                    dias_nombres = list(set([d.dia.nombre for d in dias]))

                    participacion_json = []
                    for p in Participacion.query.filter_by(gestion_curso_paralelo_id=gcp.id, materia_profesor_id=mp.id):
                        ep = EstudianteParticipa.query.filter_by(estudiante_id=est.id, participacion_id=p.id).first()
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

                    nota = Nota.query.filter_by(estudiante_id=est.id, gestion_curso_paralelo_id=gcp.id, materia_profesor_id=mp.id).first()

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

                est_json = {
                    "estudiante_id": est.id,
                    "estudiante_ci": est.ci,
                    "estudiante_nombre": est.nombre,
                    "estudiante_apellido": est.apellido,
                    "estudiante_sexo": est.sexo,
                    "estudiante_telefono": est.telefono,
                    "parentesco": {
                        "parentesco_id": parentesco.id,
                        "parentesco_nombre": parentesco.nombre,
                    },
                    "curso_paralelo": {
                        "curso_paralelo_id": cp.id,
                        "curso_id": curso.id,
                        "curso_nombre": curso.nombre,
                        "paralelo_id": paralelo.id,
                        "paralelo_nombre": paralelo.nombre,
                        "asistencia": asistencias_json,
                        "materia": materias_json
                    }
                }

                if gestion.id not in gestiones_json:
                    gestiones_json[gestion.id] = {
                        "gestion_id": gestion.id,
                        "gestion_nombre": gestion.nombre,
                        "estudiantes": []
                    }
                gestiones_json[gestion.id]["estudiantes"].append(est_json)

        return jsonify({
            "rol_id": rol.id,
            "rol_nombre": rol.nombre,
            "users_id": user.id,
            "users_name": user.name,
            "users_email": user.email,
            "password": "Encriptado",
            "photo_url": user.photo_url,
            "photo_storage": user.photo_storage,
            "status": str(user.status),
            "apoderado": {
                "users_apoderado_id": apoderado.users_apoderado_id,
                "apoderado_id": apoderado.id,
                "apoderado_ci": apoderado.ci,
                "apoderado_nombre": apoderado.nombre,
                "apoderado_apellido": apoderado.apellido,
                "apoderado_telefono": apoderado.telefono,
                "users_id": apoderado.users_id
            },
            "gestion": list(gestiones_json.values())
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500