"""
db models
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class HighSchool(Base):
    __tablename__ = "high_schools"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(
        String(20), default="public", server_default="public"
    )  # "public" or "private"
    gs_score: Mapped[float] = mapped_column(Float, nullable=True)
    gs_url: Mapped[str] = mapped_column(String(250), nullable=True)  # greatschools url
    niche_score: Mapped[float] = mapped_column(Float, nullable=True)
    niche_url: Mapped[str] = mapped_column(String(250), nullable=True)  # niche url
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    populations = relationship("HSPopulation", back_populates="school")
    admission_counts = relationship("CountBySchool", back_populates="school_obj")

    @property
    def population(self):
        # latest population
        if self.populations:
            pop_list = [_.asdict() for _ in self.populations]
            return sorted(pop_list, key=lambda x: int(x["year"]), reverse=True)[0]
        return None


class HSPopulation(Base):
    """
    Denominator of the graduate stats from https://www.cde.ca.gov/ta/ac/cm/graddatafiles.asp
    """

    __tablename__ = "hs_populations"

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[str] = mapped_column(String(10))
    count: Mapped[int] = mapped_column(Integer)
    count_type: Mapped[str] = mapped_column(
        String(30), default="hs_enr"
    )  # can be highschool enrollment (hs_enr) or graduate (hs_grad)
    race: Mapped[str] = mapped_column(String(50))
    sub_race: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # for example, Filipino (also Asian)

    school_id: Mapped[int] = mapped_column(ForeignKey("high_schools.id"), nullable=True)
    school: Mapped["HighSchool"] = relationship(back_populates="populations")


class CountBySchool(Base):
    """
    From https://www.universityofcalifornia.edu/about-us/information-center/admissions-source-school
    """

    __tablename__ = "count_by_schools"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(50))
    school: Mapped[str] = mapped_column(String(100))
    race: Mapped[str] = mapped_column(String(50))
    count_type: Mapped[str] = mapped_column(String(30))
    count: Mapped[int] = mapped_column(Integer)
    year: Mapped[str] = mapped_column(String(10))
    campus: Mapped[str] = mapped_column(String(30))

    school_id: Mapped[int] = mapped_column(ForeignKey("high_schools.id"), nullable=True)
    school_obj: Mapped[HighSchool] = relationship(back_populates="admission_counts")
