from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from ..main import app
from ..database import Base
from ..routers.todos import get_current_user, get_db
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..models import ToDos

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

@pytest.fixture
def test_todo():
    todo = ToDos(
        title="Nauka FastAPI",
        description="codziennie",
        priority=5,
        complete=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"complete": False, "title": "Nauka FastAPI", "description": "codziennie", "id": 1, "priority": 5, "owner_id": 1}]