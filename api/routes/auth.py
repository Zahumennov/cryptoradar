from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.database import get_db
from api.models.user import User
from api.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from api.security import hash_password, verify_password, create_access_token
from api.exceptions import (
    email_taken_exception,
    invalid_credentials_exception,
    inactive_account_exception,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        User.email == user_data.email
    ).first()
    if existing:
        raise email_taken_exception()

    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        telegram_id=user_data.telegram_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise invalid_credentials_exception()

    if not user.is_active:
        raise inactive_account_exception()

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}