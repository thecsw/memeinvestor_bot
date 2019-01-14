# TODO: add docstrin here
import time
import logging
import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import praw

import config
import utils
import formula
import message
from kill_handler import KillHandler
from models import Investor, Firm
from stopwatch import Stopwatch

logging.basicConfig(level=logging.INFO)

# TODO: add docstring
def main():
    logging.info("Starting payroll...")
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

        top_users = sess.query(Investor).\
            order_by(Investor.balance.desc()).\
            limit(5).\
            all()

        top_firms = sess.query(Firm).\
            order_by(Firm.balance.desc()).\
            limit(5).\
            all()

        # TODO: format as table
        top_users_text = ""
        i = 0
        for user in top_users:
            top_users_text += str(i + 1) + ". " + user.name + " (" + str(user.balance) + " Memecoins)\n"

        # TODO: format as table
        top_firms_text = ""
        i = 0
        for firm in top_firms:
            top_firms_text += str(i + 1) + ". " + firm.name + " (" + str(firm.balance) + " Memecoins)\n"

        sidebar_text = sidebar_text_org.\
            replace("%TOP_USERS%", top_users_text).\
            replace("%TOP_FIRMS%", top_firms_text)

        logging.info(" -- Updating sidebar text to:")
        logging.info(sidebar_text)
        for subreddit in config.SUBREDDITS:
            settings = reddit.update_settings(
                reddit.get_subreddit(subreddit),
                description=sidebar_text)

        sess.commit()

        # Report the Reddit API call stats
        rem = int(reddit.auth.limits['remaining'])
        res = int(reddit.auth.limits['reset_timestamp'] - time.time())
        logging.info(" -- API calls remaining: %s, resetting in %.2fs", rem, res)

        sess.close()

        time.sleep(config.LEADERBOARD_INTERVAL)

if __name__ == "__main__":
    main()
