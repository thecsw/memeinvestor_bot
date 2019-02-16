# TODO: add docstrin here
import time
import logging
import traceback

from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker
import praw

import config
import utils
import formula
import message
from kill_handler import KillHandler
from models import Investment, Investor, Firm
from stopwatch import Stopwatch

logging.basicConfig(level=logging.INFO)

def main():
    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = sessionmaker(bind=engine)

    sess = session_maker()

    logging.info("Fetching investors...")
    investors = sess.query(Investor).\
        filter(Investor.completed > 0).\
        all()

    logging.info("Adjusting investors...")
    for investor in investors:
        investor.balance = adjust_amount(investor.balance)

    logging.info("Fetching active investments...")
    investments = sess.query(Investment).\
        filter(Investment.done == 0).\
        all()

    logging.info("Adjusting active investments...")
    for investment in investments:
        investment.amount = adjust_amount(investment.amount)

    logging.info("Fetching firms...")
    firms = sess.query(Firm).all()

    logging.info("Adjusting firms...")
    for firm in firms:
        firm.balance = adjust_amount(firm.balance)

    sess.commit()
    sess.close()

def adjust_amount(n):
    return n ** 0.61

def adjust_balance(n):
    adjusted = adjust_amount(n)
    if adjusted < 1000000:
        adjusted = min(n, 1000000)
    return adjusted

if __name__ == "__main__":
    main()
