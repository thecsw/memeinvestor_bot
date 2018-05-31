from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Submission(Base):
    __tablename__ = "Submissions"

    # id = Column(Integer, primary_key=True)
    submission = Column(String(20), nullable=False, primary_key=True, autoincrement=False)
