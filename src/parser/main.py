import requests
from sqlalchemy.orm import Session

from src.db.connection import SessionLocal
from src.db.models import VacancyModel

HH_API_URL = "https://api.hh.ru/vacancies"


def fetch_vacancies(text="Python разработчик", pages=1):
    results = []
    for page in range(pages):
        params = {
            "text": text,
            "page": page,
            "per_page": 20
        }
        response = requests.get(HH_API_URL, params=params)
        data = response.json()
        results.extend(data.get("items", []))
    return results


def save_vacancies(vacancies: list[dict], db: Session, employer_id: int):
    for item in vacancies:
        vacancy = VacancyModel(
            title=item["name"],
            description=item.get("snippet", {}).get("responsibility", "Описание отсутствует"),
            employer_id=employer_id
        )
        db.add(vacancy)
    db.commit()
    db.close()


def fetch_and_save(vacancy_name: str, employer_id: int, pages: int):
    db = SessionLocal()
    vacancies = fetch_vacancies(vacancy_name, pages)
    save_vacancies(vacancies, db, employer_id)
