from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
 
Base = declarative_base()


class Investor(Base):
    __tablename__ = "Investors"

    name = Column(String(20), nullable=False, primary_key=True, autoincrement=False)
    balance = Column(Integer, default=1000)
    completed = Column(Integer, default=0)
    broke = Column(Integer, default=0)
