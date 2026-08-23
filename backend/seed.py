from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models.user import Role, User
from app.models.printer import Printer
from app.services.auth import hash_password
import json

def seed_database():
    create_db_and_tables()

    with Session(engine) as session:
        # Seed users
        # Contas de desenvolvimento: admin, porque sao as unicas do banco
        # semeado e precisam poder criar as demais (POST /api/auth/register
        # e administrativo desde a Fase 1). Contas criadas por elas nascem
        # como "viewer".
        users = [
            User(
                email="mateus.vicentino@example.com",
                password_hash=hash_password("123"),
                name="Mateus Vicentino",
                role=Role.ADMIN.value,
            ),
            User(
                email="pedro.ribeiro@example.com",
                password_hash=hash_password("123"),
                name="Pedro Ribeiro",
                role=Role.ADMIN.value,
            ),
        ]

        for user in users:
            existing = session.exec(select(User).where(User.email == user.email)).first()
            if not existing:
                session.add(user)
                print(f"[+] User created: {user.email}")

        session.commit()

        # Seed 85 printers from JSON
        with open("printers_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        printers_count = 0
        for p_data in data.get("printers", []):
            # Check if printer already exists by IP
            existing = session.exec(
                select(Printer).where(Printer.ip == p_data["ip"])
            ).first()

            if not existing:
                printer = Printer(
                    ip=p_data["ip"],
                    name=p_data["name"],
                    model=p_data["model"],
                    department=p_data["department"],
                )
                session.add(printer)
                printers_count += 1

        session.commit()
        print(f"[+] Printers created: {printers_count}")
        print("[OK] Database seeded")


if __name__ == "__main__":
    seed_database()
