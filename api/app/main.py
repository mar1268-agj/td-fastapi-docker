from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from . import crud, db, models

app = FastAPI(title="TD API")

@app.on_event("startup")
def startup():
    db.init_db()

@app.get("/status")
async def status():
    return {"status": "OK"}

class ItemOut(BaseModel):
    id: int
    name: str
    description: str | None = None

@app.get("/items", response_model=List[ItemOut])
async def list_items():
    return crud.get_items()
