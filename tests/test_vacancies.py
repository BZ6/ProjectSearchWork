import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.auth.dependencies import require_role
from src.db.models import UserModel, VacancyModel, ApplicationModel, UserRole
from src.main import app

client = TestClient(app)


@pytest.fixture
def test_user_data():
    return {
        "name": "John Doe",
        "email": "john15152@example.com",
        "password": "securepassword",
        "role": "соискатель"
    }


@pytest.fixture
def test_user_data2():
    return {
        "name": "John Doe",
        "email": "john16152@example.com",
        "password": "securepassword",
        "role": "работодатель"
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


@pytest.fixture
def registered_user2(db_session, test_user_data2):
    from src.api.auth.utils import get_password_hash
    user = UserModel(
        name=test_user_data2["name"],
        email=test_user_data2["email"],
        password=get_password_hash(test_user_data2["password"]),
        role=UserRole(test_user_data2["role"])
    )
    try:
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    except Exception as e:
        pass
    return user


@pytest.fixture
def db_session() -> Session:
    from src.db.connection import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_employer(db_session):
    employer = UserModel(name="Test Employer", role="работодатель")
    db_session.add(employer)
    db_session.commit()
    db_session.refresh(employer)
    return employer


@pytest.fixture
def test_applicant(db_session):
    applicant = UserModel(name="Test Applicant", role="соискатель")
    db_session.add(applicant)
    db_session.commit()
    db_session.refresh(applicant)
    return applicant


@pytest.fixture
def test_vacancy(db_session, test_employer):
    vacancy = VacancyModel(title="Python Developer", description="Cool job", employer_id=test_employer.id)
    db_session.add(vacancy)
    db_session.commit()
    db_session.refresh(vacancy)
    return vacancy


def test_search_vacancies(db_session, test_vacancy, registered_user):
    from src.api.auth.utils import create_access_token
    token = create_access_token({"sub": registered_user.email})
    response = client.get("/vacancies/search", params={"keyword": "Python"},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert any("Python" in v["title"] for v in data)


def test_respond_to_vacancy(db_session, test_applicant, test_vacancy, registered_user):
    from src.api.auth.utils import create_access_token
    token = create_access_token({"sub": registered_user.email})

    response = client.post("/vacancies/respond", json={"vacancy_id": test_vacancy.id},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["vacancy_id"] == test_vacancy.id


def test_get_my_vacancy_applications(db_session, test_employer, test_applicant, test_vacancy, registered_user2):
    from src.api.auth.utils import create_access_token
    token = create_access_token({"sub": registered_user2.email})

    application = ApplicationModel(applicant_id=test_applicant.id, vacancy_id=test_vacancy.id)
    db_session.add(application)
    db_session.commit()

    response = client.get("/vacancies/my-vacancy-applications", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_create_vacancy(db_session, test_employer, registered_user2):
    from src.api.auth.utils import create_access_token
    token = create_access_token({"sub": registered_user2.email})

    response = client.post("/vacancies/", json={
        "title": "New Vacancy",
        "description": "Some description"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Vacancy"
