from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# from TodoApp import models
from TodoApp.database import SessionLocal, engine

router = APIRouter(
    prefix="/todos", tags=["todos"], responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request):
    return templates.TemplateResponse("edit-todo.html", {"request": request})
