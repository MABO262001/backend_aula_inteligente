import random
from app.models.estudiante import Estudiante
from app.models.user import User
from app.extensions import db

def generar_ci_unico(existing_cis):
    while True:
        ci = random.randint(10_000_000, 99_999_999)  # 8 dígitos
        if ci not in existing_cis:
            existing_cis.add(ci)
            return ci

def generar_telefono():
    primer_digito = random.choice([6, 7])
    resto = random.randint(0, 9999999)
    telefono_str = f"{primer_digito}{resto:07d}"
    return int(telefono_str)

def generar_sexo():
    return random.choice(['Masculino', 'Femenino'])

def seed_estudiantes():
    if Estudiante.query.first():
        print("ℹ️ Ya existen estudiantes en la tabla.")
        return

    estudiantes = []
    existing_cis = set()

    admin_usuarios = User.query.filter_by(rol_id=1).all()
    estudiante_usuarios = User.query.filter_by(rol_id=3).all()

    if not admin_usuarios:
        print("❌ No hay usuarios con rol Administrador para asignar users_id")
        return

    if not estudiante_usuarios:
        print("ℹ️ No hay usuarios con rol Estudiante para crear estudiantes.")
        return

    admin_id = admin_usuarios[0].id

    for user_est in estudiante_usuarios:
        email_part = user_est.email.split('@')[0]
        partes = email_part.split('.')
        nombre = partes[0].capitalize() if len(partes) > 0 else "Nombre"
        apellido = partes[1].capitalize() if len(partes) > 1 else "Apellido"

        ci = generar_ci_unico(existing_cis)
        telefono = generar_telefono()
        sexo = generar_sexo()

        estudiante = Estudiante(
            ci=ci,
            nombre=nombre,
            apellido=apellido,
            sexo=sexo,
            telefono=telefono,
            users_id=admin_id,
            users_estudiante_id=user_est.id
        )
        estudiantes.append(estudiante)

    db.session.add_all(estudiantes)
    db.session.commit()
    print(f"✅ {len(estudiantes)} estudiantes insertados.")
