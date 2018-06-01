from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
 
Base = declarative_base()


class Comment(Base):
    __tablename__ = "Comments"

    comment = Column(String(20), nullable=False, primary_key=True, autoincrement=False)
