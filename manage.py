from app import create_app
from app.extensions import db
from flask.cli import with_appcontext
import click
import sqlalchemy
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import inspect

app = create_app()

# 🔧 Comando para inicializar la BD y mostrar qué tablas se crearon
@app.cli.command("init-db")
@with_appcontext
def init_db():
    """Crea la base de datos si no existe y muestra tablas creadas."""
    engine = sqlalchemy.create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    connection = engine.connect()
    inspector = inspect(engine)

    if not database_exists(engine.url):
        print("🔧 Creando base de datos...")
        create_database(engine.url)
    else:
        print("✅ La base de datos ya existe.")

    existing_tables = inspector.get_table_names()
    print(f"📋 Tablas antes de crear: {existing_tables}")

    db.create_all()

    # Verificamos después de crear
    inspector = inspect(engine)
    new_tables = inspector.get_table_names()
    created = list(set(new_tables) - set(existing_tables))

    if created:
        print("🆕 Tablas creadas:")
        for table in created:
            print(f"  ➕ {table}")
    else:
        print("✅ No se crearon nuevas tablas.")

    print(f"📦 Tablas actuales: {new_tables}")




# 🌱 Comando para poblar la base con datos de prueba
@app.cli.command("seed-db")
@with_appcontext
def seed_db():
    """Inserta todos los datos de prueba."""
    from app.seeders.main_seeder import run_all_seeders
    run_all_seeders()
