from alembic.util import status
from fastapi import FastAPI
from starlette import status
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

import models
from database import engine
from routers import auth, todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(todos.router)
