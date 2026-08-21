import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base


# ============================================================
# Test Database
# ============================================================

TEST_DATABASE_URL = (
    "sqlite:///:memory:"
)


# ============================================================
# Engine
# ============================================================

engine = create_engine(

    TEST_DATABASE_URL,

    connect_args={
        "check_same_thread": False,
    },

)


# ============================================================
# Session
# ============================================================

TestingSessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine,

)


# ============================================================
# Database Fixture
# ============================================================

@pytest.fixture
def db_session():

    # --------------------------------------------------------
    # Create tables
    # --------------------------------------------------------

    Base.metadata.create_all(
        bind=engine,
    )

    # --------------------------------------------------------
    # Create session
    # --------------------------------------------------------

    db = TestingSessionLocal()

    try:

        yield db

    finally:

        db.close()

        # ----------------------------------------------------
        # Clean database after each test
        # ----------------------------------------------------

        Base.metadata.drop_all(
            bind=engine,
        )