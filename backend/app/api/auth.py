from app.db.dependencies import get_current_user, get_db
from app.core.security import create_access_token
from app.services.auth_service import authenticate_user
from app.schemas.auth import UserLogin
from app.schemas.auth import TokenResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User


from app.schemas.auth import UserRegister, UserResponse
from app.services.auth_service import (create_user,get_user_by_email,)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED,)
def register(user_data: UserRegister,db: Session = Depends(get_db),):

    existing_user = get_user_by_email(db, user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = create_user(db, user_data)

    return user


@router.post("/login",response_model=TokenResponse,)
def login(credentials: UserLogin,db: Session = Depends(get_db),):
    user = authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "type": "access",
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )


@router.get("/me",response_model=UserResponse,)
def get_me(current_user: User = Depends(get_current_user),):
    return current_user