from sqlalchemy.orm import sessionmaker
from app.core.database import engine

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# FastAPI routes ke liye Generator dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Connection leak roknay ke liye zaroori hai