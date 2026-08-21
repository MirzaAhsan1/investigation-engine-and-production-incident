from sqlalchemy import create_engine
from app.core.config import settings  # ya jahan se aap DATABASE_URL le rahe hain

engine = create_engine(
    settings.DATABASE_URL, # ya aapka DATABASE_URL variable
    pool_size=15,          # Connections limit ko 5 se barha kar 15 karein
    max_overflow=20,       # High load par 20 extra temporary connections
    pool_timeout=30,       # Wait limit
    pool_pre_ping=True,    # Dead/Stale connections ko automatically clear karega
    pool_recycle=1800,     # Connections ko recycle karta rahega
)