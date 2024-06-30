import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import User

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(
        User(email="test@test.com", sources="http://test.com", drafter_prompt="prompt")
    )
    db.add(User(email="a@a.com", sources="http://test.com", drafter_prompt="prompt a"))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def get_test_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db
client = TestClient(app)


def test_get_all_users(setup_db):
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2
