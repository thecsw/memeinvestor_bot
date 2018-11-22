"""
time allows us to record time
logging is the general way we stdout

sqlalchemy is the connection to our MySQL database

praw allows us to connect to reddit

config has all the environmental variables form .env
message has all message constants
utils has some useful functions to make code smaller
kill_handler gracefully handles sigterms
models has database models
main has the reply method
stopwatch is the way we record the time spent on an operation
"""
import time
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import praw

import config
import message
import utils
from kill_handler import KillHandler
from models import Investor
from main import reply_wrap
from stopwatch import Stopwatch

praw.models.Submission.reply_wrap = reply_wrap
logging.basicConfig(level=logging.INFO)


def process_investor(sess, submission):

    """
    This function evaluates investor's post and works with
    their balances. Returns the reddit.comment instance of
    bot's reply and a boolean to delete the submission
    """

    # If a poster doesn't have an account, delete the post
    # if he has, take 1000 MemeCoins and invest them
    investor = sess.query(Investor).\
        filter(Investor.name == submission.author.name).\
        first()

    if not investor:
        bot_reply = submission.reply_wrap(message.NO_ACCOUNT_POST_ORG)
        delete_post = True
        logging.info(" -- Not a registered investor!")
    elif investor.balance < 250:
        bot_reply = submission.reply_wrap(message.modify_pay_to_post(investor.balance))
        delete_post = True
        logging.info(" -- Not enough funds!")
    else:
        # We will make it 6%
        required_fee = int(investor.balance * 0.06)
        if required_fee < 250:
            required_fee = 250
        new_balance = investor.balance - required_fee
        investor.balance = new_balance
        bot_reply = submission.\
        reply_wrap(message.modify_invest_place_here(required_fee))
        sess.commit()

    return (bot_reply, delete_post,)

def main():
    """
    This is the main function that listens to new submissions
    and then posts the ATTENTION sticky comment.
    """

    killhandler = KillHandler()

    engine = create_engine(config.DB, pool_recycle=60)
    sess_maker = scoped_session(sessionmaker(bind=engine))

    reddit = praw.Reddit(client_id=config.CLIENT_ID,
                         client_secret=config.CLIENT_SECRET,
                         username=config.USERNAME,
                         password=config.PASSWORD,
                         user_agent=config.USER_AGENT)

    # We will test our reddit connection here
    if not utils.test_reddit_connection(reddit):
        exit()

    logging.info("Starting checking submissions...")

    stopwatch = Stopwatch()

    sess = sess_maker()
    submission_time = int(time.time())
    for submission in reddit.subreddit('+'.join(config.SUBREDDITS)).\
        stream.submissions(skip_existing=True):

        duration = stopwatch.measure()

        logging.info("New submission: %s", submission)
        logging.info(" -- retrieved in %ss", duration)

        # We don't need to post a sticky on stickied posts
        if submission.stickied:
            logging.info(" -- skipping (stickied)")
            continue

        # We are looking if the post is created in the past
        # so we won't double charge it
        if submission.created_utc < submission_time:
            logging.info(" -- skipping (timeout)")
            continue

        submission_time = int(submission.created_utc)
        logging.info(" -- Submission timestamp: %s", \
                     time.asctime(time.gmtime(submission_time)))

        bot_reply = 0
        delete_post = False

        # This is a bit of a controversial update, so im gonna make it
        # agile to switch between different modes
        if not config.SUBMISSION_FEE:
            # Post a comment to let people know where to invest
            bot_reply = submission.reply_wrap(message.INVEST_PLACE_HERE_NO_FEE)
        else:
            (bot_reply, delete_post) = process_investor(sess, submission)

        # Sticky the comment
        if config.IS_MODERATOR:
            bot_reply.mod.distinguish(how='yes', sticky=True)
            if delete_post:
                logging.info(" -- Deleting the post...")
                #Should we hide or just delete the post?
                submission.mod.remove()

        # Measure how long processing took
        duration = stopwatch.measure()
        logging.info(" -- processed in %s", duration)

        if killhandler.killed:
            logging.info("Termination signal received - exiting")
            break

if __name__ == "__main__":
    main()
