from fastapi_crudrouter import SQLAlchemyCRUDRouter

from src.api.users.schema import User, UserCreate
from src.db.connection import get_session
from src.db.models import UserModel


router = SQLAlchemyCRUDRouter(
    schema=User,
    create_schema=UserCreate,
    db_model=UserModel,
    db=get_session,
    prefix='users'
)
