from sqlalchemy import create_engine

from config import cache
from data import database

engine = create_engine(database.DATABASE_URI)

__all__ = ["enginge", "cache"]
