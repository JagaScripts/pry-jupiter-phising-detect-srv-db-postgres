import uuid
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared_kernel.models import Base, Domain, AlertRule, AlertRuleTarget, DomainEnrichment
from shared_kernel.logging import get_logger

logger = get_logger("db.seed")

# URL de la base de datos desde entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/phishing_detect")

def seed_data():
    logger.info("Iniciando siembra de datos de prueba...")
    engine = create_engine(DATABASE_URL)
    
    # Asegurar que las tablas existen (Resetear esquema en desarrollo)
    logger.info("Limpiando esquema antiguo y asegurando que las tablas existen...")
    # Base.metadata.drop_all(engine) # Comentado: Ya no queremos borrar los datos en cada reinicio
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Crear dominios de ejemplo
        domains_data = [
            {"id": "dom_google", "name": "google.com", "user": "user_demo", "tags": ["legitimo", "whitelist"]},
            {"id": "dom_phish", "name": "paypal-secure-login.com", "user": "user_demo", "tags": ["sospechoso", "phishing"]},
        ]

        for d in domains_data:
            existing = session.query(Domain).filter_by(domain_name=d["name"]).first()
            if not existing:
                new_domain = Domain(
                    id=d["id"],
                    domain_name=d["name"],
                    user_id=d["user"],
                    tags=d["tags"],
                    status="activo"
                )
                session.add(new_domain)
                
                # Añadir un enriquecimiento inicial
                enrichment = DomainEnrichment(
                    id=f"en_{d['id']}",
                    domain_id=d["id"],
                    enrichment_status="completed" if "google.com" in d["name"] else "pending",
                    reputation_score=0.0 if "google.com" in d["name"] else 85.0,
                    last_enriched_at=datetime.now(timezone.utc)
                )
                session.add(enrichment)
                logger.info(f"Dominio y enriquecimiento creado: {d['name']}")

        # 2. Crear Reglas de Alerta (usando el formato de Julián)
        rules_data = [
            {
                "id": "rule_01",
                "name": "Detección de Typosquatting Crítico",
                "type": "risk",
                "severity": "high",
                "logic": {"condition": {"min_score": 85}},
                "schedule": {"frequency": "hourly"}
            }
        ]

        for r in rules_data:
            existing = session.query(AlertRule).filter_by(name=r["name"]).first()
            if not existing:
                new_rule = AlertRule(
                    id=r["id"],
                    user_id="user_demo",
                    name=r["name"],
                    rule_type=r["type"],
                    severity=r["severity"],
                    logic_json=r["logic"],
                    schedule_json=r["schedule"],
                    is_enabled=True
                )
                session.add(new_rule)
                logger.info(f"Regla de alerta creada: {r['name']}")

        session.commit()
        logger.info("¡Siembra de datos completada con éxito!")
        
    except Exception as e:
        logger.error(f"Error durante la siembra de datos: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()
