from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api.vacancies.schema import Application, ApplicationCreate, Vacancy, VacancyCreate
from src.db.connection import get_session
from src.db.models import ApplicationModel, VacancyModel, UserModel
from src.api.auth.dependencies import require_role


router = APIRouter(prefix="/vacancies", tags=["Vacancies"])

# Поиск и фильтрация
@router.get("/search", response_model=List[Vacancy])
def search_vacancies(
    keyword: Optional[str] = Query(None, description="Ключевое слово для поиска"),
    employer_id: Optional[int] = Query(None, description="ID работодателя"),
    db: Session = Depends(get_session)
):
    query = db.query(VacancyModel)
    if keyword:
        query = query.filter(
            (VacancyModel.title.ilike(f"%{keyword}%")) |
            (VacancyModel.description.ilike(f"%{keyword}%"))
        )
    if employer_id:
        query = query.filter(VacancyModel.employer_id == employer_id)
    return query.all()

# Отклики на вакансии
@router.post("/respond", response_model=Application, status_code=status.HTTP_201_CREATED)
def respond_to_vacancy(
    application: ApplicationCreate,
    db: Session = Depends(get_session),
    applicant: UserModel = Depends(require_role("соискатель"))
):
    exists = db.query(ApplicationModel).filter_by(
        applicant_id=applicant.id,
        vacancy_id=application.vacancy_id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Вы уже откликались на эту вакансию")
    db_application = ApplicationModel(
        applicant_id=applicant.id,
        vacancy_id=application.vacancy_id
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

# Отклики на вакансии работодателя
@router.get("/my-vacancy-applications", response_model=List[Application])
def get_my_vacancy_applications(
    db: Session = Depends(get_session),
    employer = Depends(require_role("работодатель"))
):
    vacancy_ids = db.query(VacancyModel.id).filter(VacancyModel.employer_id == employer.id).subquery()
    applications = db.query(ApplicationModel).filter(ApplicationModel.vacancy_id.in_(vacancy_ids)).all()
    return applications

# Создание вакансии
@router.post("/", response_model=Vacancy, status_code=status.HTTP_201_CREATED)
def create_vacancy(
    vacancy: VacancyCreate,
    db: Session = Depends(get_session),
    employer: UserModel = Depends(require_role("работодатель"))
):
    db_vacancy = VacancyModel(
        title=vacancy.title,
        description=vacancy.description,
        employer_id=employer.id
    )
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy

# CRUD-роутер
crud_router = SQLAlchemyCRUDRouter(
    schema=Vacancy,
    create_schema=VacancyCreate,
    db_model=VacancyModel,
    db=get_session,
    create_route=False,
)

