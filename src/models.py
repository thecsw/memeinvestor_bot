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
    if config.TEST:
        # sqlite (used in tests)
        return "(strftime('%s', 'now'))"
    # mariadb
    return "unix_timestamp()"


Base = declarative_base()

class Shares(Base):
    """
    Here we store our shares bought and sold
    """
    __tablename__ = "Shares"

    # Fill when bought
    id = Column(Integer, primary_key=True)
    post = Column(String(11), nullable=False)
    upvotes = Column(Integer, default=0)
    comment = Column(String(11), nullable=False, unique=True) # Comment that bought the share
    name = Column(String(32), nullable=False, index=True)
    initial_price = Column(BigInteger, default=-1) # The initial price of the stock
    initial_shares = Column(BigInteger, default=-1) # Number of shares in the pool when bought
    initial_time = Column(Integer, server_default=unix_timestamp()) # When bought
    # Fill after selling
    active = Column(Boolean, default=False) # If not sold and still owned by the user
    final_price = Column(BigInteger, default=-1) # The initial price of the stock
    profit = Column(BigInteger, default=0) # final_price - initial price
    final_shares = Column(BigInteger, default=-1) # Number of shares in the pool when sold
    final_time = Column(Integer, server_default=unix_timestamp()) # When bought

class Investor(Base):
    """
    Our dear investors have these columns
    """
    __tablename__ = "Investors"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    created_utc = Column(Integer, server_default=unix_timestamp()) # When account created
    mibcreated_utc = Column(Integer, server_default=unix_timestamp()) # When MIB account created
    karma = Column(Integer, default=0) # Karma when registered
    subreddit = Column(String(32), nullable=False) # The subreddit where user registered
    balance = Column(BigInteger, default=config.STARTING_BALANCE)
    networth = Column(BigInteger, default=config.STARTING_BALANCE) # Active shares + balance
    total_shares = Column(Integer, default=0) # Total shares
    active_shares = Column(Integer, default=0) # Active shares
    sold_shares = Column(Integer, default=0)   # Sold shares
    option_auto_sell = Column(Boolean, default=True) # Option to automatically start sharing shares when price goes down
    option_MIB_updates = Column(Boolean, default=True) # Option to get recent MIB updates
    option_share_updates = Column(Boolean, default=True) # Option to receive messages about shares
    broke = Column(Integer, default=0) # If the user is broke
    badges = Column(String(1024), default="[]") # Badges granted
    firm = Column(Integer, default=0) # Firm ID
    firm_role = Column(String(32), default="") # Role in a firm
    last_active = Column(Integer, server_default=unix_timestamp()) # Last comment made to MIB
    last_share = Column(Integer, server_default=unix_timestamp()) # Last share bought

class Submission(Base):
    """
    Store submission data
    """
    __tablename__ = "Investors"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True) # Name of the submission r'[a-z0-9]{6}'
    author = Column(String(32), nullable=False) # Name of the author
    subreddit = Column(String(32), nullable=False) # Name of the subreddit
    title = Column(String(256), nullable=False) # Title of the submission
    created_utc = Column(Integer, server_default=unix_timestamp()) # When submission created
    last_share = Column(Integer, server_default=unix_timestamp()) # Last share made
    media = Column(String(256), nullable=False) # Link to meme/media attched to the post
    sticky = Column(Boolean, default=False) # Do not allow buying shares on sticky
    template_posted = Column(Boolean, default=False) # True if author posted a template
    comments = Column(Integer, default=0) # Number of comments calling the bot
    current_shares = Column(Integer, default=0) # Number of shares at this time
    current_price = Column(Integer, default=0) # Current stock price
    max_shares = Column(Integer, default=0) # Max number of shares reached
    max_price = Column(Integer, default=0)  # Mex price that shares of this post reached
    investors = Column(Integer, default=0)  # Number of unique investors who bought shares

class Firm(Base):
    """
    Table of our firms
    """
    __tablename__ = "Firms"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    balance = Column(BigInteger, default=1000)
    size = Column(Integer, default=0)
    coo = Column(Integer, default=0)
    cfo = Column(Integer, default=0)
    execs = Column(Integer, default=0)
    assocs = Column(Integer, default=0)
    tax = Column(Integer, default=15)
    rank = Column(Integer, default=0)
    private = Column(Boolean, default=False)
    last_payout = Column(Integer, server_default=unix_timestamp())

class Invite(Base):
    __tablename__ = "Invites"

    id = Column(Integer, primary_key=True)
    firm = Column(Integer)
    investor = Column(Integer)
