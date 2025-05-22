import random
from datetime import timedelta
from app.models.matricula import Matricula
from app.models.parentesco import Parentesco
from app.models.subgestion import Subgestion
from app.models.gestion import Gestion
from app.extensions import db

def random_date_in_range(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def seed_matriculas():
    if Matricula.query.first():
        print("ℹ️ Ya existen matrículas en la tabla.")
        return

    parentescos = Parentesco.query.all()
    subgestiones = Subgestion.query.all()
    gestiones = Gestion.query.all()

    if not parentescos or not subgestiones or not gestiones:
        print("❌ No hay parentescos, subgestiones o gestiones para generar matrículas.")
        return

    subgestiones_por_gestion = {}
    for sg in subgestiones:
        subgestiones_por_gestion.setdefault(sg.gestion_id, []).append(sg)

    matrículas = []

    for parentesco in parentescos:

        cantidad_gestiones = random.randint(1, min(3, len(gestiones)))
        gestiones_elegidas = random.sample(gestiones, cantidad_gestiones)

        for gestion in gestiones_elegidas:

            subgestiones_de_gestion = subgestiones_por_gestion.get(gestion.id, [])

            for subgestion in subgestiones_de_gestion:
                fecha_random = random_date_in_range(subgestion.fecha_inicio, subgestion.fecha_final)
                matricula = Matricula(
                    fecha=fecha_random,
                    monto=50.0,
                    parentesco_id=parentesco.id,
                    subgestion_id=subgestion.id,
                    users_id=parentesco.apoderado_id
                )
                matrículas.append(matricula)

    db.session.add_all(matrículas)
    db.session.commit()

    print(f"✅ Insertadas {len(matrículas)} matrículas.")
