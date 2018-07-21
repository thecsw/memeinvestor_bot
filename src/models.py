from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles

class unix_timestamp(expression.FunctionElement):
    type = Integer()

@compiles(unix_timestamp)
def compile(element, compiler, **kw):
    return "unix_timestamp()"

Base = declarative_base()

class Investment(Base):
    __tablename__ = "Investments"

    id = Column(Integer, primary_key=True)
    post = Column(String(11), nullable=False)
    upvotes = Column(Integer, default=0)
    comment = Column(String(11), nullable=False, unique=True)
    name = Column(String(20), nullable=False, index=True)
    amount = Column(BigInteger, default=100)
    time = Column(Integer, server_default=unix_timestamp())
    done = Column(Boolean, default=False, nullable=False)
    response = Column(String(11))
    final_upvotes = Column(Integer)
    success = Column(Boolean, default=False)
    profit = Column(BigInteger, default=0)

class Investor(Base):
    __tablename__ = "Investors"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    balance = Column(BigInteger, default=1000)
    completed = Column(Integer, default=0)
    broke = Column(Integer, default=0)
    badges = Column(String(1024), default="[]")
