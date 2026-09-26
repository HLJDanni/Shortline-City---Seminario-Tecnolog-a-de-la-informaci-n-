"""Datos de demostración para probar el sistema rápidamente.

Ejecutar dentro del contenedor web:
    docker compose exec web python -m scripts.seed_demo
o localmente con la base configurada:
    python -m scripts.seed_demo
"""
from datetime import date, timedelta

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import (
    Cohorte, InscripcionUnete, Persona, Rol, Servicio, Usuario,
)
from app.seed import sembrar
from app.services import checkin_service as ci

NOMBRES = [
    ("Ana", "López"), ("Carlos", "Méndez"), ("Sofía", "Ramírez"),
    ("Luis", "García"), ("María", "Hernández"), ("Jorge", "Castillo"),
    ("Elena", "Morales"), ("Pedro", "Ruiz"), ("Lucía", "Flores"),
    ("Diego", "Ortiz"), ("Valeria", "Recinos"), ("Daniel", "González"),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        sembrar(db)

        # Usuarios de ejemplo por rol
        roles = {r.nombre: r for r in db.scalars(select(Rol)).all()}
        for nombre, email, rol in [
            ("Coordinador Demo", "coordinador@shorelinecity.org", "Coordinador"),
            ("Usher Demo", "usher@shorelinecity.org", "Usher"),
        ]:
            if not db.scalar(select(Usuario).where(Usuario.email == email)):
                db.add(Usuario(nombre=nombre, email=email,
                               hashed_password=hash_password("Demo1234"),
                               rol_id=roles[rol].id))
        db.commit()

        if db.scalar(select(Persona)):
            print("Ya existen datos de demostración.")
            return

        personas = []
        for n, a in NOMBRES:
            p = Persona(nombres=n, apellidos=a, estado="activo",
                        telefono=f"5000-{1000+len(personas)}",
                        correo=f"{n.lower()}.{a.lower()}@example.com")
            db.add(p)
            personas.append(p)
        db.commit()

        # Servicios recientes + check-ins
        for i in range(3):
            s = Servicio(nombre=f"Servicio Dominical {i+1}",
                         fecha=date.today() - timedelta(days=7 * i),
                         ubicacion="Auditorio central", tipo="regular")
            db.add(s)
            db.flush()
            for p in personas[: 8 - i]:
                ci.registrar_checkin(db, p.id, s.id)

        # Cohorte de Únete
        coh = Cohorte(nombre="Únete - Grupo A", fecha_inicio=date.today(),
                      horario="Sábados 4pm", estado="en_curso")
        db.add(coh)
        db.flush()
        for p, estado in zip(personas[:5], ["inscrito", "en_proceso", "completado",
                                            "integrado", "inscrito"]):
            db.add(InscripcionUnete(persona_id=p.id, cohorte_id=coh.id, estado=estado))
        db.commit()
        print(f"Demo lista: {len(personas)} personas, 3 servicios, 1 cohorte.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
