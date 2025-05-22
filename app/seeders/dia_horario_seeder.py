# app/seeders/dia_horario_seeder.py

from app.models.dia_horario import DiaHorario
from app.models.dia import Dia
from app.models.horario import Horario
from app.extensions import db

def seed_dia_horarios():
    if not DiaHorario.query.first():
        dias = Dia.query.all()
        horarios = Horario.query.all()

        if not dias or not horarios:
            print("ℹ️ Asegúrate de ejecutar los seeders de días y horarios primero.")
            return

        dia_horarios = []

        # horarios cortos
        dias_cortos = ["Lunes", "Miércoles", "Viernes"]
        horarios_cortos = horarios[:len(horarios)//2]

        for dia in dias:
            if dia.nombre in dias_cortos:
                for horario in horarios_cortos:
                    dia_horarios.append(DiaHorario(dia_id=dia.id, horario_id=horario.id))

        dias_largos = ["Martes", "Jueves"]
        horarios_largos = horarios[len(horarios)//2:]

        for dia in dias:
            if dia.nombre in dias_largos:
                for horario in horarios_largos:
                    dia_horarios.append(DiaHorario(dia_id=dia.id, horario_id=horario.id))

        db.session.add_all(dia_horarios)
        db.session.commit()
        print("✅ Día-Horario asignados.")
    else:
        print("ℹ️ Ya existen asignaciones Día-Horario en la tabla.")