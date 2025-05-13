from fastapi import APIRouter

from src.api.users import routes as users


router = APIRouter()

router.include_router(users.router)
