from fastapi import FastAPI, Depends, Path
from starlette import status
from starlette.exceptions import HTTPException
import models
from models import ToDos
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def read_all(db: db_dependency):
    return db.query(ToDos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(ToDos).filter(ToDos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")
