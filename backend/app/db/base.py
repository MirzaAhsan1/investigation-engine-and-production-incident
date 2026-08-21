from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

# Import all models here
import app.models