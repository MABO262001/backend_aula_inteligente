from flask import Blueprint, jsonify
from sqlalchemy.orm import joinedload
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models.user import User
from ..models.rol import Rol
from ..models.gestion import Gestion
from ..models.gestion_curso_paralelo import GestionCursoParalelo
from ..models.curso_paralelo import CursoParalelo
from ..models.curso import Curso
from ..models.paralelo import Paralelo
from ..models.materia_profesor import MateriaProfesor
from ..models.materia_profesor_dia_horario import MateriaProfesorDiaHorario
from ..models.materia import Materia
from ..models.profesor import Profesor
from ..models.dia_horario import DiaHorario
from ..models.dia import Dia
from ..models.horario import Horario
from ..models.materia_horario_curso_paralelo import MateriaHorarioCursoParalelo
from ..models.boleta_inscripcion import BoletaInscripcion
from ..models.estudiante import Estudiante

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


