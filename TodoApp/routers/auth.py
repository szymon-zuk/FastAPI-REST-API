from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import models
from database import SessionLocal, engine

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

templates = Jinja2Templates(directory="templates")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}},
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(
    username: str, password: str, db: Session
) -> Optional[models.Users]:
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    username: str, user_id: int, expires_delta: Optional[timedelta] = None
) -> str:
    encode = {"sub": username, "id": user_id}
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            await logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not found")


@router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: LoginForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(
            response=response, form_data=form, db=db
        )
        if not validate_user_cookie:
            msg = "Incorrect username or password"
            return templates.TemplateResponse(
                "login.html", {"request": request, "msg": msg}
            )
        return response
    except HTTPException:
        msg = "Unknown error"
        return templates.TemplateResponse(
            "login.html", {"request": request, "msg": msg}
        )


@router.get("/logout")
async def logout(request: Request):
    msg = "Logout successful"
    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg}
    )
    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: Session = Depends(get_db),
):
    validation1 = (
        db.query(models.Users).filter(models.Users.username == username).first()
    )
    validation2 = db.query(models.Users).filter(models.Users.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )
    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = first_name
    user_model.last_name = last_name

    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get("/change-password", response_class=HTMLResponse)
async def change_password(request: Request):
    return templates.TemplateResponse("change-password.html", {"request": request})


@router.post("/change-password", response_class=HTMLResponse)
async def change_password_commit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if user is None:
        msg = "There is no user with such username"
        return templates.TemplateResponse(
            "change-password.html",
            {"request": request, "msg": msg},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not verify_password(password, user.hashed_password):
        msg = "Invalid current password"
        return templates.TemplateResponse(
            "change-password.html",
            {"request": request, "msg": msg},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user.hashed_password = get_password_hash(new_password)
    db.commit()

    msg = "Password successfully changed"
    return templates.TemplateResponse(
        "change-password.html",
        {"request": request, "msg": msg},
        status_code=status.HTTP_200_OK,
    )
