from fastapi import APIRouter

from src.api.users import routes as users
from src.api.auth import routes as auth


router = APIRouter()

router.include_router(users.router)
router.include_router(auth.router)
