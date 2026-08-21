from app.db.session import SessionLocal
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

# from app.db.dependencies import get_db
from app.core.security import decode_access_token
from app.models.user import User


def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# Automatically extracts the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login",)

# Decodes the token and returns the user
def get_current_user(
    token: str = Depends(oauth2_scheme), # Depends on the OAuth2 scheme to extract the token 
    db: Session = Depends(get_db),  # Depends on the get_db function to get the database session
) -> User:

    
    print("Received Token:", token)

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")


    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    token_type = payload.get("type")

    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user = db.get(
        User,
        UUID(user_id),
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user