"""
json is used to unload user's badges list
logging is the general way we stdout
re is for regexes (commands and commentns parsing)
time makes us sleepy

sqlalchemy works with our MySQL database

praw is the Python Reddit API Wrapper. Must have

config has all of the constants
utils has helper functions
message has message constants
"""
import logging
import time

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import praw

import config
import utils
import message
from kill_handler import KillHandler
from models import Base
from stopwatch import Stopwatch
from comment_worker import CommentWorker

logging.basicConfig(level=logging.INFO)

def main():
    """
    This is where the magic happens. This function listens
    to all new messages in the inbox and passes them to worker
    object that decides on what to do with them.
    """
    logging.info("Starting main")

    if config.POST_TO_REDDIT:
        logging.info("Warning: Bot will actually post to Reddit!")

    logging.info("Setting up database")

    killhandler = KillHandler()
    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = scoped_session(sessionmaker(bind=engine))
    worker = CommentWorker(session_maker)

    while True:
        try:
            Base.metadata.create_all(engine)
            break
        except sqlalchemy.exc.OperationalError:
            logging.info("Database not available yet; retrying in 5s")
            time.sleep(5)

    logging.info("Setting up Reddit connection")

    reddit = praw.Reddit(client_id=config.CLIENT_ID,
                         client_secret=config.CLIENT_SECRET,
                         username=config.USERNAME,
                         password=config.PASSWORD,
                         user_agent=config.USER_AGENT)

    # We will test our reddit connection here
    if not utils.test_reddit_connection(reddit):
        exit()

    stopwatch = Stopwatch()

    logging.info("Listening for inbox replies...")

    while not killhandler.killed:
        # Iterate over the latest comment replies in inbox
        reply_function = reddit.inbox.comment_replies

        if config.MAINTENANCE:
            logging.info("ENTERING MAINTENANCE MODE. NO OPERATIONS WILL BE PROCESSED.")
            for comment in praw.models.util.stream_generator(reply_function):
                logging.info("New comment %s:", comment)
                if comment.new:
                    comment.reply_wrap(message.MAINTENANCE_ORG)
                    comment.mark_read()

        for comment in praw.models.util.stream_generator(reply_function):
            # Measure how long since we finished the last loop iteration
            duration = stopwatch.measure()
            logging.info("New comment %s (%s):", comment, type(comment))
            logging.info(" -- retrieved in %.2fs", duration)

            if comment.new:
                if comment.subreddit.display_name.lower() in config.SUBREDDITS:
                    # Process the comment only in allowed subreddits
                    worker(comment)
                else:
                    logging.info(" -- skipping (wrong subreddit)")

                # Mark the comment as processed
                comment.mark_read()
            else:
                logging.info(" -- skipping (already processed)")

            # Measure how long processing took
            duration = stopwatch.measure()
            logging.info(" -- processed in %.2fs", duration)

            # Report the Reddit API call stats
            rem = int(reddit.auth.limits['remaining'])
            res = int(reddit.auth.limits['reset_timestamp'] - time.time())
            logging.info(" -- API calls remaining: %.2f, resetting in %.2fs", rem, res)

            # Check for termination requests
            if killhandler.killed:
                logging.info("Termination signal received - exiting")
                break

            stopwatch.reset()

if __name__ == "__main__":
    main()
