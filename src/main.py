import re
import time
import logging
import traceback

import sqlalchemy
from sqlalchemy import create_engine, func, desc, and_
from sqlalchemy.orm import scoped_session, sessionmaker

import praw

import config
import message
from kill_handler import KillHandler
from models import Base, Investment, Investor
from stopwatch import Stopwatch

logging.basicConfig(level=logging.INFO)

# Decorator to mark a commands that require a user
# Adds the investor after the comment when it calls the method (see broke)
def req_user(fn):
    def wrapper(self, sess, comment, *args):
        investor = sess.query(Investor).\
            filter(Investor.name == comment.author.name).\
            first()

        if not investor:
            return self.no_such_user(comment)

        return fn(self, sess, comment, investor, *args)
    return wrapper


# Monkey patch exception handling
def reply_wrap(self, body):
    logging.info(" -- replying")

    if config.post_to_reddit:
        try:
            return self.reply(body)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            return False
    else:
        logging.info(body)
        return "0"

praw.models.Comment.reply_wrap = reply_wrap


class CommentWorker():
    commands = [
        r"!active",
        r"!balance",
        r"!broke",
        r"!create",
        r"!help",
        r"!ignore",
        r"!invest (\d+)",
        r"!market",
        r"!top",
    ]

    def __init__(self, sm):
        self.regexes = [re.compile(x, re.MULTILINE | re.IGNORECASE)
                        for x in self.commands]
        self.Session = sm

    def __call__(self, comment):
        # Ignore items that aren't Comments (i.e. Submissions)
        if not isinstance(comment, praw.models.Comment):
            return
        
        # Ignore comments at the root of a Submission
        if comment.is_root:
            return

        # Ignore comments without an author (deleted)
        if not comment.author:
            return

        # Ignore comments by other bots
        if comment.author.name.lower().endswith("_bot"):
            return

        # Ignore comments older than a threshold
        max_age = 60*15 # fifteen minutes
        comment_age = time.time() - int(comment.created_utc)
        if comment_age > max_age:
            return

        # Parse the comment body for a command
        for reg in self.regexes:
            matches = reg.search(comment.body.lower())
            if not matches:
                continue

            cmd = matches.group()
            attrname = cmd.split(" ")[0][1:]

            if not hasattr(self, attrname):
                continue

            logging.info(f" -- {comment.author.name}: {cmd}")

            try:
                sess = self.Session()
                getattr(self, attrname)(sess, comment, *matches.groups())
            except Exception as e:
                logging.error(e)
                traceback.print_exc()
                sess.rollback()
            else:
                sess.commit()

            sess.close()
            break

    def ignore(self, sess, comment):
        pass

    def help(self, sess, comment):
        comment.reply_wrap(message.help_org)

    def market(self, sess, comment):
        total = sess.query(
            func.coalesce(func.sum(Investor.balance), 0)
        ).scalar()

        invested, active = sess.query(
            func.coalesce(func.sum(Investment.amount), 0),
            func.count(Investment.id)
        ).filter(Investment.done == 0).first()

        comment.reply_wrap(message.modify_market(active, total, invested))

    def top(self, sess, comment):
        leaders = sess.query(
            Investor.name,
            func.coalesce(Investor.balance+func.sum(Investment.amount), Investor.balance).label('networth')).\
        outerjoin(Investment, and_(Investor.name == Investment.name, Investment.done == 0)).\
        group_by(Investor.name).\
        order_by(desc('networth')).\
        limit(5).\
        all()

        comment.reply_wrap(message.modify_top(leaders))

    def create(self, sess, comment):
        author = comment.author.name
        q = sess.query(Investor).filter(Investor.name == author).exists()

        # Let user know they already have an account
        if sess.query(q).scalar():
            comment.reply_wrap(message.create_exists_org)
            return

        # Create new investor account
        sess.add(Investor(name=author))
        comment.reply_wrap(message.modify_create(comment.author, 1000))

    @req_user
    def invest(self, sess, comment, investor, amount):
        if not isinstance(comment, praw.models.Comment):
            return

        if config.prevent_insiders:
            if comment.submission.author.name == comment.author.name:
                comment.reply_wrap(message.inside_trading_org)
                return

        try:
            amount = int(amount)
        except ValueError:
            return

        if amount < 100:
            comment.reply_wrap(message.min_invest_org)
            return

        author = comment.author.name
        new_balance = investor.balance - amount

        if new_balance < 0:
            comment.reply_wrap(message.insuff_org)
            return

        # Sending a confirmation
        response = comment.reply_wrap(message.modify_invest(
            amount,
            comment.submission.ups,
            new_balance
        ))

        sess.add(Investment(
            post=comment.submission,
            upvotes=comment.submission.ups,
            comment=comment,
            name=author,
            amount=amount,
            response=response,
            done=False,
        ))

        investor.balance = new_balance

    @req_user
    def balance(self, sess, comment, investor):
        comment.reply_wrap(message.modify_balance(investor.balance))

    @req_user
    def broke(self, sess, comment, investor):
        if investor.balance >= 100:
            return comment.reply_wrap(message.modify_broke_money(investor.balance))

        active = sess.query(func.count(Investment.id)).\
            filter(Investment.done == 0).\
            filter(Investment.name == investor.name).\
            scalar()

        if active > 0:
            return comment.reply_wrap(message.modify_broke_active(active))

        # Indeed, broke
        investor.balance = 100
        investor.broke += 1

        comment.reply_wrap(message.modify_broke(investor.broke))

    @req_user
    def active(self, sess, comment, investor):
        total = sess.query(
            func.count(Investment.id)
        ).filter(Investment.done == 0).\
        filter(Investment.name == investor.name).scalar()
        comment.reply_wrap(message.modify_active(total))

    def no_such_user(self, comment):
        comment.reply_wrap(message.no_account_org)


def main():
    logging.info("Starting main")

    if config.post_to_reddit:
        logging.info("Warning: Bot will actually post to Reddit!")

    logging.info("Setting up database")

    killhandler = KillHandler()
    engine = create_engine(config.db, pool_recycle=60)
    sm = scoped_session(sessionmaker(bind=engine))
    worker = CommentWorker(sm)

    while True:
        try:
            Base.metadata.create_all(engine)
            break
        except sqlalchemy.exc.OperationalError:
            logging.info("Database not available yet; retrying in 5s")
            time.sleep(5)

    logging.info("Setting up Reddit connection")

    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)

    stopwatch = Stopwatch()

    logging.info("Listening for inbox replies...")

    while not killhandler.killed:
        try:
            # Iterate over the latest comment replies in inbox
            reply_function = reddit.inbox.comment_replies
            for comment in praw.models.util.stream_generator(reply_function):
                # Measure how long since we finished the last loop iteration
                duration = stopwatch.measure()
                logging.info(f"New comment {comment}:")
                logging.info(f" -- retrieved in {duration:5.2f}s")

                if comment.new:
                    # Process the comment
                    worker(comment)

                    # Mark the comment as processed
                    comment.mark_read()
                else:
                    logging.info(" -- skipping (already processed)")

                # Measure how long processing took
                duration = stopwatch.measure()
                logging.info(f" -- processed in {duration:5.2f}s")

                # Report the Reddit API call stats
                rem = int(reddit.auth.limits['remaining'])
                res = int(reddit.auth.limits['reset_timestamp'] - time.time())
                logging.info(f" -- API calls remaining: {rem:3d}, resetting in {res:3d}s")

                # Check for termination requests
                if killhandler.killed:
                    logging.info("Termination signal received - exiting")
                    break

                stopwatch.reset()
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            time.sleep(10)

if __name__ == "__main__":
    main()
