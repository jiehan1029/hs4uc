"""
db models
"""

from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class CountBySchool(Base):
    __tablename__ = "count_by_schools"
    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(50))
    school: Mapped[str] = mapped_column(String(100))
    race: Mapped[str] = mapped_column(String(50))
    count_type: Mapped[str] = mapped_column(String(30))
    count: Mapped[int] = mapped_column(Integer)
    year: Mapped[str] = mapped_column(String(10))
    campus: Mapped[str] = mapped_column(String(30))
