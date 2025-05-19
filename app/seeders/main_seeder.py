from app.seeders.user_seeder import seed_users
from app.seeders.rol_seeder import seed_roles

def run_all_seeders():
    seed_roles()
    seed_users()

