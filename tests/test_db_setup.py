import pytest
from sqlalchemy import create_engine, inspect
from phishing_detect.app.db.models import Base
from phishing_detect.app.core.settings import settings

def test_database_connection():
    """ Verifica que podemos conectar a la base de datos configurada """
    engine = create_engine(settings.database_url)
    try:
        connection = engine.connect()
        assert connection is not None
        connection.close()
    except Exception as e:
        pytest.fail(f"No se pudo conectar a la base de datos: {e}")

def test_tables_creation():
    """ Verifica que todas las tablas necesarias están presentes """
    engine = create_engine(settings.database_url)
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    expected_tables = ["domains", "alert_rules", "alert_rule_targets", "domain_enrichment"]
    
    for table in expected_tables:
        assert table in existing_tables, f"La tabla {table} no existe en la base de datos"
