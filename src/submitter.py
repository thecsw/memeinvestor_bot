import time
import logging
import traceback

import sqlalchemy
from sqlalchemy import create_engine, func, desc, and_
from sqlalchemy.orm import scoped_session, sessionmaker

import praw
import prawcore

import config
import message
from kill_handler import KillHandler
from models import Base, Investment, Investor
from main import reply_wrap
from stopwatch import Stopwatch

praw.models.Submission.reply_wrap = reply_wrap
logging.basicConfig(level=logging.INFO)

def main():
    killhandler = KillHandler()

    engine = create_engine(config.db, pool_recycle=60)
    sm = scoped_session(sessionmaker(bind=engine))

    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)

    logging.info("Starting checking submissions...")

    stopwatch = Stopwatch()

    while not killhandler.killed:

        try:
            sess = sm()
            submission_time = int(time.time())
            for submission in reddit.subreddit('+'.join(config.subreddits)).stream.submissions(skip_existing=True):
                duration = stopwatch.measure()

                logging.info(f"New submission: {submission}")
                logging.info(f" -- retrieved in {duration:5.2f}s")

                # We don't need to post a sticky on stickied posts
                if submission.stickied:
                    logging.info(f" -- skipping (stickied)")
                    continue

                # We are looking if the post is created in the past
                # so we won't double charge it
                if (submission.created_utc < submission_time):
                    logging.info(f" -- skipping (timeout)")
                    continue
                submission_time = int(submission.created_utc)
                logging.info(f" -- Submission timestamp: {time.asctime(time.gmtime(submission_time))}")

                bot_reply = 0
                delete_post = False

                # This is a bit of a controversial update, so im gonna make it
                # agile to switch between different modes
                if config.submission_fee:
                    # If a poster doesn't have an account, delete the post
                    # if he has, take 1000 MemeCoins and invest them
                    investor = sess.query(Investor).\
                        filter(Investor.name == submission.author.name).\
                        first()

                    if not investor:
                        bot_reply = submission.reply_wrap(message.no_account_post_org)
                        delete_post = True
                        logging.info(f" -- Not a registered investor!")
                    elif (investor.balance < 1000):
                        bot_reply = submission.reply_wrap(message.modify_pay_to_post(investor.balance))
                        delete_post = True
                        logging.info(f" -- Not enough funds!")
                    else:
                        # We will make it 6%
                        required_fee = int(investor.balance * 0.06)
                        if (required_fee < 250):
                            required_fee = 250
                        new_balance = investor.balance - required_fee
                        investor.balance = new_balance
                        bot_reply = submission.reply_wrap(message.modify_invest_place_here(required_fee))

                    sess.commit()
                else:
                    # Post a comment to let people know where to invest
                    bot_reply = submission.reply_wrap(message.invest_place_here_no_fee)

                # Sticky the comment
                if config.is_moderator:
                    bot_reply.mod.distinguish(how='yes', sticky=True)
                    if (delete_post):
                        logging.info(f" -- Deleting the post...")
                        #Should we hide or just delete the post?
                        submission.mod.remove()

                # Measure how long processing took
                duration = stopwatch.measure()
                logging.info(f" -- processed in {duration:5.2f}s")

                if killhandler.killed:
                    logging.info("Termination signal received - exiting")
                    break

        except prawcore.exceptions.OAuthException as e_creds:
            traceback.print_exc()
            logging.error(e_creds)
            logging.critical("Invalid login credentials. Check your .env!")
            logging.critical("Fatal error. Cannot continue or fix the problem. Bailing out...")
            exit()

        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            time.sleep(10)

if __name__ == "__main__":
    main()
