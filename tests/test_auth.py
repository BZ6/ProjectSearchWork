import pytest
from fastapi.testclient import TestClient

from src.db.models import UserModel, UserRole
from src.main import app

client = TestClient(app)


@pytest.fixture
def db_session():
    from src.db.connection import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user_data():
    return {
        "name": "John Doe",
        "email": "john1025@example.com",
        "password": "securepassword",
        "role": "соискатель"
    }


@pytest.fixture
def registered_user(db_session, test_user_data):
    from src.api.auth.utils import get_password_hash
    user = UserModel(
        name=test_user_data["name"],
        email=test_user_data["email"],
        password=get_password_hash(test_user_data["password"]),
        role=UserRole(test_user_data["role"])
    )

    try:
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    except Exception as e:
        pass
    return user


def test_register(test_user_data):
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200
    assert response.json()["email"] == test_user_data["email"]


def test_login_success(test_user_data, registered_user):
    response = client.post("/auth/token",
                           data={"username": test_user_data["email"], "password": test_user_data["password"]})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_failure():
    response = client.post("/auth/token", data={"username": "wrong@example.com", "password": "wrongpass"})
    assert response.status_code == 401


def test_refresh_token(test_user_data, registered_user):
    from src.api.auth.utils import create_refresh_token
    refresh_token = create_refresh_token({"sub": test_user_data["email"]})
    response = client.post("/auth/refresh", json=refresh_token)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_me(registered_user):
    from src.api.auth.utils import create_access_token
    token = create_access_token({"sub": registered_user.email})
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == registered_user.email


def test_verify_token(registered_user):
    from src.api.auth.utils import create_access_token
    token = create_access_token({"sub": registered_user.email})
    response = client.get("/auth/verify", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == registered_user.email


def test_applicant_only(registered_user):
    from src.api.auth.utils import create_access_token
    token = create_access_token({"sub": registered_user.email})
    response = client.get("/auth/applicant-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Только для соискателей" in response.json()["message"]


def test_employer_only_reject(registered_user):
    from src.api.auth.utils import create_access_token
    token = create_access_token({"sub": registered_user.email})
    response = client.get("/auth/employer-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_employer_only_accept(db_session):
    from src.api.auth.utils import get_password_hash, create_access_token
    user = UserModel(name="Emp", email="emp@example.com", password=get_password_hash("1234"),
                     role=UserRole("работодатель"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": user.email})
    response = client.get("/auth/employer-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Только для работодателей" in response.json()["message"]
