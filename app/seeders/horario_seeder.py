# app/seeders/horario_seeder.py

from app.models.horario import Horario
from app.extensions import db
from datetime import time, datetime, timedelta

def seed_horarios():
    if not Horario.query.first():
        horarios = []

        # horarios de lapso corto
        hora_actual_corto = time(7, 0)
        lapso_corto = timedelta(hours=1, minutes=30)
        while hora_actual_corto < time(22, 30):
            hora_final_corto = (datetime.combine(datetime.min, hora_actual_corto) + lapso_corto).time()
            if hora_final_corto > time(22, 30):
                break
            horarios.append(Horario(hora_inicio=hora_actual_corto, hora_final=hora_final_corto))
            hora_actual_corto = hora_final_corto

        # horarios de lapso largo
        hora_actual_largo = time(7, 0)
        lapso_largo = timedelta(hours=2, minutes=15)
        while hora_actual_largo < time(22, 30):
            hora_final_largo = (datetime.combine(datetime.min, hora_actual_largo) + lapso_largo).time()
            if hora_final_largo > time(23, 00):
                break
            horarios.append(Horario(hora_inicio=hora_actual_largo, hora_final=hora_final_largo))
            hora_actual_largo = hora_final_largo

        db.session.add_all(horarios)
        db.session.commit()
        print("✅ Horarios insertados.")
    else:
        print("ℹ️ Ya existen horarios en la tabla.")