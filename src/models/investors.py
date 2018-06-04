from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
 
Base = declarative_base()


class Investor(Base):
    __tablename__ = "Investors"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    balance = Column(Integer, default=1000)
    completed = Column(Integer, default=0)
    broke = Column(Integer, default=0)
