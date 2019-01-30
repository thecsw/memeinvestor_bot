"""
sqlalchemy is the way we connect to our MySQL database
"""
import os

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles

import config


class unix_timestamp(expression.FunctionElement):
    type = Integer()


@compiles(unix_timestamp)
def compile(element, compiler, **kw):
    if config.DB.startswith("sqlite"):
        return "(strftime('%s', 'now'))"
    # mariadb
    return "unix_timestamp()"


Base = declarative_base()


class Investment(Base):
    """
    Our mighty investments have these columns
    """
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
    """
    Our dear investors have these columns
    """
    __tablename__ = "Investors"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    balance = Column(BigInteger, default=config.STARTING_BALANCE)
    completed = Column(Integer, default=0)
    broke = Column(Integer, default=0)
    badges = Column(String(1024), default="[]")
    firm = Column(Integer, default=0)
    firm_role = Column(String(32), default="")


class Firm(Base):
    __tablename__ = "Firms"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    balance = Column(BigInteger, default=1000)
    size = Column(Integer, default=0)
    execs = Column(Integer, default=0)
    tax = Column(Integer, default=15)
    rank = Column(Integer, default=0)
    private = Column(Boolean, default=False)
    last_payout = Column(Integer, server_default=unix_timestamp())


class Invite(Base):
    __tablename__ = "Invites"

    id = Column(Integer, primary_key=True)
    firm = Column(Integer)
    investor = Column(Integer)
