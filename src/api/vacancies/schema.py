from pydantic import BaseModel


class VacancyCreate(BaseModel):
    title: str
    description: str


class Vacancy(VacancyCreate):
    id: int
    employer_id: int

    class Config:
        orm_mode = True


class ApplicationCreate(BaseModel):
    vacancy_id: int


class Application(BaseModel):
    id: int
    applicant_id: int
    vacancy_id: int

    class Config:
        orm_mode = True


class VacancyParse(BaseModel):
    vacancy_name: str
    employee_id: int
    pages: int
