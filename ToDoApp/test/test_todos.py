from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from ..main import app
from ..database import Base
from ..routers.todos import get_current_user, get_db
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import status

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username": "szyms0n", "id": 1, "user_role": "admin"}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def test_read_all_authenticated():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK