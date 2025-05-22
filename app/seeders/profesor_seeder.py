import random
from app.models.profesor import Profesor
from app.models.user import User
from app.extensions import db

def generar_ci_unico(existing_cis):
    while True:
        ci = random.randint(10_000_000, 99_999_999)
        if ci not in existing_cis:
            existing_cis.add(ci)
            return ci

def generar_telefono():
    primer_digito = random.choice([6, 7])
    resto = random.randint(0, 9999999)
    telefono_str = f"{primer_digito}{resto:07d}"
    return int(telefono_str)

def seed_profesores():
    if Profesor.query.first():
        print("ℹ️ Ya existen profesores en la tabla.")
        return

    profesores = []
    existing_cis = set()

    admin_usuarios = User.query.filter_by(rol_id=1).all()
    profesor_usuarios = User.query.filter_by(rol_id=2).all()

    if not admin_usuarios:
        print("❌ No hay usuarios con rol Administrador para asignar users_id")
        return

    if not profesor_usuarios:
        print("ℹ️ No hay usuarios con rol Profesor para crear profesores.")
        return

    admin_id = admin_usuarios[0].id

    for user_profesor in profesor_usuarios:
        email_part = user_profesor.email.split('@')[0]
        partes = email_part.split('.')
        nombre = partes[0].capitalize() if len(partes) > 0 else "Nombre"
        apellido = partes[1].capitalize() if len(partes) > 1 else "Apellido"

        ci = generar_ci_unico(existing_cis)
        telefono = generar_telefono()
        direccion = user_profesor.email

        profesor = Profesor(
            ci=ci,
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            direccion=direccion,
            users_id=admin_id,
            users_profesor_id=user_profesor.id
        )
        profesores.append(profesor)

    db.session.add_all(profesores)
    db.session.commit()
    print(f"✅ {len(profesores)} profesores insertados.")
