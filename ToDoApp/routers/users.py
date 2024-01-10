from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from models import ToDos, Users
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(prefix="/user", tags=["user"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChangePasswordRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[Users, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/get_user", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query.filter(Users.id == user.get("id")).first()


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency,
    db: db_dependency,
    change_password_request: ChangePasswordRequest,
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not bcrypt_context.verify(
        change_password_request.password, user_model.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Passwords are not the same")
    new_password_from_request = change_password_request.new_password
    user_model.hashed_password = bcrypt_context.hash(new_password_from_request)
    db.add(user_model)
    db.commit()
