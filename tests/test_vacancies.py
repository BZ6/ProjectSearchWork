import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.auth.dependencies import require_role
from src.db.models import UserModel, VacancyModel, ApplicationModel
from src.main import app

client = TestClient(app)


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


def test_search_vacancies(db_session, test_vacancy):
    response = client.get("/vacancies/search", params={"keyword": "Python"})
    assert response.status_code == 200
    data = response.json()
    assert any("Python" in v["title"] for v in data)


def test_respond_to_vacancy(db_session, test_applicant, test_vacancy):
    def override_role():
        return test_applicant

    app.dependency_overrides[require_role("соискатель")] = override_role

    response = client.post("/vacancies/respond", json={"vacancy_id": test_vacancy.id})
    assert response.status_code == 201
    data = response.json()
    assert data["vacancy_id"] == test_vacancy.id


def test_get_my_vacancy_applications(db_session, test_employer, test_applicant, test_vacancy):
    application = ApplicationModel(applicant_id=test_applicant.id, vacancy_id=test_vacancy.id)
    db_session.add(application)
    db_session.commit()

    def override_role():
        return test_employer

    app.dependency_overrides[require_role("работодатель")] = override_role

    response = client.get("/vacancies/my-vacancy-applications")
    assert response.status_code == 200
    data = response.json()
    assert any(a["vacancy_id"] == test_vacancy.id for a in data)


def test_create_vacancy(db_session, test_employer):
    def override_role():
        return test_employer

    app.dependency_overrides[require_role("работодатель")] = override_role

    response = client.post("/vacancies/", json={
        "title": "New Vacancy",
        "description": "Some description"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Vacancy"
