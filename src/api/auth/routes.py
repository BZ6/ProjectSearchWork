from fastapi import APIRouter, Depends, HTTPException, Body, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from src.api.auth.dependencies import oauth2_scheme, get_current_user, require_role
from src.api.auth.utils import SECRET_KEY, ALGORITHM
from src.api.auth.utils import verify_password, get_password_hash, create_access_token, create_refresh_token
from src.api.users.schema import UserCreate, User
from src.db.connection import get_session
from src.db.models import UserModel, UserRole

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_session)):
    if db.query(UserModel).filter(UserModel.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже зарегистрирован")
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=UserRole(user.role)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return User.from_orm(db_user)


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh_token(refresh_token: str = Body(...)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        email = payload.get("sub")
        new_access_token = create_access_token(data={"sub": email})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@router.get("/me", response_model=User)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return User.from_orm(current_user)


@router.get("/verify")
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"status": "ok", "email": email}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.get("/applicant-only")
def applicant_only_route(user: UserModel = Depends(require_role("соискатель"))):
    return {"message": f"Hello, {user.name}! Только для соискателей."}


@router.get("/employer-only")
def employer_only_route(user: UserModel = Depends(require_role("работодатель"))):
    return {"message": f"Hello, {user.name}! Только для работодателей."}
