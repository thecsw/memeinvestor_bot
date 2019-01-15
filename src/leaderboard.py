# TODO: add docstrin here
import time
import logging
import traceback

from sqlalchemy import create_engine, func, desc, and_
from sqlalchemy.orm import sessionmaker
import praw

import config
import utils
import formula
import message
from kill_handler import KillHandler
from models import Investor, Investment, Firm
from stopwatch import Stopwatch

logging.basicConfig(level=logging.INFO)

sidebar_text_org = """
test
123

noerdy should put stuff here

TODO

*****

**Top Users:**

%TOP_USERS%

**Top Firms:**

%TOP_FIRMS%
"""

# TODO: add docstring
def main():
    logging.info("Starting leaderboard...")
    logging.info("Sleeping for 8 seconds. Waiting for the database to turn on...")
    time.sleep(8)

    killhandler = KillHandler()

    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = sessionmaker(bind=engine)

    reddit = praw.Reddit(client_id=config.CLIENT_ID,
                         client_secret=config.CLIENT_SECRET,
                         username=config.USERNAME,
                         password=config.PASSWORD,
                         user_agent=config.USER_AGENT)

    # We will test our reddit connection here
    if not utils.test_reddit_connection(reddit):
        exit()

    while not killhandler.killed:
        sess = session_maker()

        top_users = sess.query(
                Investor.name,
                func.coalesce(Investor.balance+func.sum(Investment.amount), Investor.balance).label('networth')).\
                outerjoin(Investment, and_(Investor.name == Investment.name, Investment.done == 0)).\
            group_by(Investor.name).\
            order_by(desc('networth')).\
            all()

        top_firms = sess.query(Firm).\
            order_by(Firm.balance.desc()).\
            limit(5).\
            all()

        top_users_text = "Rank|User|Net Worth\n"
        top_users_text += ":-:|:-:|:-:\n"
        for i, user in enumerate(top_users):
            top_users_text += str(i + 1) + "|/u/" + user.name + "|" + str(user.networth) + " MC\n"

        top_firms_text = "Rank|Firm|Total Assets|Level\n"
        top_firms_text += ":-:|:-:|:-:|:-:\n"
        for i, firm in enumerate(top_firms):
            top_firms_text += str(i + 1) + "|" + firm.name + "|" + str(firm.balance) + " MC|" + str(firm.rank + 1) + "\n"

        sidebar_text = sidebar_text_org.\
            replace("%TOP_USERS%", top_users_text).\
            replace("%TOP_FIRMS%", top_firms_text)

        logging.info(" -- Updating sidebar text to:")
        logging.info(sidebar_text)
        for subreddit in config.SUBREDDITS:
            reddit.subreddit(subreddit).mod.update(description=sidebar_text)

        sess.commit()

        # Report the Reddit API call stats
        rem = int(reddit.auth.limits['remaining'])
        res = int(reddit.auth.limits['reset_timestamp'] - time.time())
        logging.info(" -- API calls remaining: %s, resetting in %.2fs", rem, res)

        sess.close()

        time.sleep(config.LEADERBOARD_INTERVAL)

if __name__ == "__main__":
    main()
