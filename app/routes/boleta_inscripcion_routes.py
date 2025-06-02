from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.boleta_inscripcion import BoletaInscripcion

boleta_inscripcion_bp = Blueprint('boleta_inscripcion', __name__)

# Listar todos los registros
@boleta_inscripcion_bp.route('/listar', methods=['GET'])
def listar():
    boletas = BoletaInscripcion.query.all()
    result = [
        {
            "id": b.id,
            "hora": b.hora.strftime('%H:%M:%S'),
            "fecha": b.fecha.strftime('%Y-%m-%d'),
            "estudiante_id": b.estudiante_id,
            "gestion_curso_paralelo_id": b.gestion_curso_paralelo_id,
            "users_id": b.users_id
        } for b in boletas
    ]
    return jsonify(result), 200

# Buscar un registro por ID
@boleta_inscripcion_bp.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    boleta = BoletaInscripcion.query.get_or_404(id)
    result = {
        "id": boleta.id,
        "hora": boleta.hora.strftime('%H:%M:%S'),
        "fecha": boleta.fecha.strftime('%Y-%m-%d'),
        "estudiante_id": boleta.estudiante_id,
        "gestion_curso_paralelo_id": boleta.gestion_curso_paralelo_id,
        "users_id": boleta.users_id
    }
    return jsonify(result), 200

# Crear un nuevo registro
@boleta_inscripcion_bp.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    nueva_boleta = BoletaInscripcion(
        hora=data['hora'],
        fecha=data['fecha'],
        estudiante_id=data['estudiante_id'],
        gestion_curso_paralelo_id=data['gestion_curso_paralelo_id'],
        users_id=data['users_id']
    )
    db.session.add(nueva_boleta)
    db.session.commit()
    return jsonify({"message": "Registro creado exitosamente"}), 201

# Actualizar un registro existente
@boleta_inscripcion_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    boleta = BoletaInscripcion.query.get_or_404(id)
    boleta.hora = data.get('hora', boleta.hora)
    boleta.fecha = data.get('fecha', boleta.fecha)
    boleta.estudiante_id = data.get('estudiante_id', boleta.estudiante_id)
    boleta.gestion_curso_paralelo_id = data.get('gestion_curso_paralelo_id', boleta.gestion_curso_paralelo_id)
    boleta.users_id = data.get('users_id', boleta.users_id)
    db.session.commit()
    return jsonify({"message": "Registro actualizado exitosamente"}), 200

# Eliminar un registro
@boleta_inscripcion_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    boleta = BoletaInscripcion.query.get_or_404(id)
    db.session.delete(boleta)
    db.session.commit()
    return jsonify({"message": "Registro eliminado exitosamente"}), 200


@boleta_inscripcion_bp.route('/listar_boleta_cursos_paralelos', methods=['GET'])
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