from fastapi import APIRouter

from src.api.users import routes as users
from src.api.auth import routes as auth
from src.api.vacancies import routes as vacancies


router = APIRouter()

router.include_router(users.crud_router)
router.include_router(auth.router)
router.include_router(vacancies.router)
router.include_router(vacancies.crud_router)
