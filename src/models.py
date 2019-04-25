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

class Share(Base):
    """
    Here we store our shares bought and sold
    """
    __tablename__ = "Shares"

    # ------
    # Fill below right after buying the stock/share
    # ------
    #
    # Unique share id
    id = Column(Integer, primary_key=True)
    #
    # The post id where the share belongs
    post = Column(String(11), nullable=False)
    #
    # Number of upvotes when the share was bought
    upvotes = Column(Integer, default=0)
    #
    # Name of the user who bought the share
    name = Column(String(32), nullable=False, index=True)
    #
    # Comment that bought the share
    comment = Column(String(11), nullable=False, unique=True)
    #
    # The initial price of the stock
    initial_price = Column(BigInteger, default=-1)
    #
    # Number of shares in the pool when bought
    initial_shares = Column(BigInteger, default=-1)
    #
    # When bought
    initial_time = Column(Integer, server_default=unix_timestamp())

    # ------
    # Fill below after selling the stock, if sold
    # ------
    #
    # If not sold and still owned by the user
    active = Column(Boolean, default=True)
    #
    # The initial price of the stock
    final_price = Column(BigInteger, default=-1)
    #
    # final_price - initial price
    profit = Column(BigInteger, default=0)
    #
    # Number of shares in the pool when sold
    final_shares = Column(BigInteger, default=-1)
    #
    # When the share is sold
    final_time = Column(Integer, server_default=unix_timestamp())

class Investor(Base):
    """
    Our dear investors have these columns
    """
    __tablename__ = "Investors"

    #
    # Unique share id
    id = Column(Integer, primary_key=True)
    #
    # The investor name who bought the share
    name = Column(String(32), nullable=False, unique=True)
    #
    # When the reddit account created
    created_utc = Column(Integer, server_default=unix_timestamp())
    #
    # When MIB account created
    mibcreated_utc = Column(Integer, server_default=unix_timestamp())
    #
    # Karma when registered
    karma = Column(Integer, default=0)
    #
    # The subreddit where user registered
    subreddit = Column(String(32), nullable=False)
    #
    # Current active balance
    balance = Column(BigInteger, default=config.STARTING_BALANCE)
    #
    # Active shares + balance
    networth = Column(BigInteger, default=config.STARTING_BALANCE)
    #
    # Total shares (active and sold)
    total_shares = Column(Integer, default=0)
    #
    # Number of active shares
    active_shares = Column(Integer, default=0)
    #
    # Number of sold shares
    sold_shares = Column(Integer, default=0)
    #
    # Option to automatically start sharing
    # shares when shares are 4 hours old
    option_auto_sell = Column(Boolean, default=True)
    #
    # Option to get recent MIB updates
    option_MIB_updates = Column(Boolean, default=True)
    #
    # Option to receive messages about shares
    option_share_updates = Column(Boolean, default=True)
    #
    # If the user is broke
    broke = Column(Integer, default=0)
    #
    # Badges granted
    badges = Column(String(1024), default="[]")
    #
    # Firm ID
    firm = Column(Integer, default=0)
    #
    # Role in a firm
    firm_role = Column(String(32), default="")
    #
    # Last comment made to MIB
    last_active = Column(Integer, server_default=unix_timestamp())
    #
    # Last share bought
    last_share = Column(Integer, server_default=unix_timestamp())

class Submission(Base):
    """
    Store submission data
    """
    __tablename__ = "Submissions"

    #
    # Unique ID of the submission
    id = Column(Integer, primary_key=True)
    #
    # Name of the submission r'[a-z0-9]{6}'
    name = Column(String(32), nullable=False, unique=True)
    #
    # Name of the author
    author = Column(String(32), nullable=False)
    #
    # Name of the subreddit
    subreddit = Column(String(32), nullable=False)
    #
    # Title of the submission
    title = Column(String(256), nullable=False)
    #
    # When submission created
    created_utc = Column(Integer, server_default=unix_timestamp())
    #
    # Last share made
    last_share = Column(Integer, server_default=unix_timestamp())
    #
    # Link to meme/media attched to the post
    media = Column(String(256), nullable=False)
    #
    # Do not allow buying shares on sticky
    sticky = Column(Boolean, default=False)
    #
    # True if author posted a template
    template_posted = Column(Boolean, default=False)
    #
    # Number of comments calling the bot
    comments = Column(Integer, default=0)
    #
    # Number of shares at this time
    current_shares = Column(Integer, default=0)
    #
    # Current stock price
    current_price = Column(Integer, default=0)
    #
    # Max number of shares reached
    max_shares = Column(Integer, default=0)
    #
    # Max price that shares of this post reached
    max_price = Column(Integer, default=0)
    #
    # Number of unique investors who bought shares
    investors = Column(Integer, default=0)

class Firm(Base):
    """
    Table of our firms
    """
    __tablename__ = "Firms"

    #
    # Unique ID of the submission
    id = Column(Integer, primary_key=True)
    #
    # Name of the firm
    name = Column(String(32), nullable=False, unique=True)
    #
    # Date when firm was created
    created_utc = Column(Integer, server_default=unix_timestamp())
    #
    # The balance of the firm
    balance = Column(BigInteger, default=1000)
    #
    # Size of the firm
    size = Column(Integer, default=0)
    #
    # Number of Chief Operation Officers
    coo = Column(Integer, default=0)
    #
    # Number of Chief Financial Officers
    cfo = Column(Integer, default=0)
    #
    # Number of executives
    execs = Column(Integer, default=0)
    #
    # Number of associates
    assocs = Column(Integer, default=0)
    #
    # Size of tax in percents
    tax = Column(Integer, default=15)
    #
    # Rank of the firm
    rank = Column(Integer, default=0)
    #
    # Whether the firm is private
    private = Column(Boolean, default=False)
    #
    # Last firm payout
    last_payout = Column(Integer, server_default=unix_timestamp())

class Invite(Base):
    __tablename__ = "Invites"

    #
    # Unique ID of the invite
    id = Column(Integer, primary_key=True)
    #
    # The firm that was invited the investor
    firm = Column(Integer)
    #
    # Investor that was invested
    investor = Column(Integer)
    #
    # The time when id was created
    created_utc = Column(Integer, server_default=unix_timestamp())
