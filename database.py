"""
func for db connections
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine("postgresql+psycopg2://jie:1234@localhost:5433/admission")
session_factory = sessionmaker(engine)