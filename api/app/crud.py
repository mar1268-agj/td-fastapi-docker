from sqlalchemy import select
from .db import engine
from .models import items

def get_items():
    with engine.connect() as conn:
        rows = conn.execute(select(items)).all()
        return [{"id": r.id, "name": r.name, "description": r.description} for r in rows]
