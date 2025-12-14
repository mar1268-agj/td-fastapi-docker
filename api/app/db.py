import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from .models import metadata

# même URL que dans docker-compose.yml
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@db:5432/app_db",
)

def create_engine_with_retry(retries: int = 5, delay: float = 1.0):
    last_exc = None
    for _ in range(retries):
        try:
            engine = create_engine(DATABASE_URL, future=True)
            # test de connexion compatible SQLAlchemy 2.x
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as exc:
            last_exc = exc
            time.sleep(delay)
    raise last_exc

engine = create_engine_with_retry()

def init_db():
    metadata.create_all(engine)
