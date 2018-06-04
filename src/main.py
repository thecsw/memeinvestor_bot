import re
import time
import logging
from queue import Queue

from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker
import praw
from bottr.bot import BotQueueWorker

import config
import message
from models import Investment, Investor

logging.basicConfig(level=logging.INFO)

STARTER = 1000
REDDIT = None


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
    if config.dry_run:
        return "dryrun_True"

    try:
        return self.reply(body)
    except Exception as e:
        logging.error(e)
        return False

praw.models.Comment.reply_wrap = reply_wrap


class CommentWorker(BotQueueWorker):
    db = None
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

    def __init__(self, reddit, sm, *args, **kwargs):
        super().__init__(target=self._process_comment, *args, **kwargs)

        self.regexes = [re.compile(x, re.MULTILINE | re.IGNORECASE)
                        for x in self.commands]
        self.reddit = reddit
        self.Session = sm

    def _process_comment(self, comment: praw.models.Comment):
        if comment.is_root or \
           comment.author.name.lower().endswith("_bot") or \
           comment.parent().author.name != config.username:
            return

        for reg in self.regexes:
            matches = reg.search(comment.body.lower())
            if not matches:
                continue

            cmd = matches.group()
            attrname = cmd.split(" ")[0][1:]

            if not hasattr(self, attrname):
                continue

            logging.info("%s: %s" % (comment.author.name, cmd))

            try:
                sess = self.Session()
                getattr(self, attrname)(sess, comment, *matches.groups())
            except Exception as e:
                logging.error(e)
                sess.rollback()
            else:
                sess.commit()
            finally:
                sess.close()

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
        leaders = sess.query(Investor).order_by(Investor.balance.desc()).limit(5).all()
        comment.reply_wrap(message.modify_top(leaders))

    def create(self, sess, comment):
        author = comment.author.name
        q = sess.query(Investor).filter(Investor.name == author).exists()

        if not sess.query(q).scalar():
            sess.add(Investor(name=author))
            comment.reply_wrap(message.modify_create(comment.author, 1000))

    @req_user
    def invest(self, sess, comment, investor, amount):
        # Post related vars
        if not investor:
            return

        if comment.submission.author.name == comment.author.name:
            comment.reply(message.inside_trading_org)
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

        sess.query(Investor).\
            filter(Investor.name == author).\
            update({
                Investor.balance: new_balance,
            }, synchronize_session=False)

    @req_user
    def balance(self, sess, comment, investor):
        comment.reply_wrap(message.modify_balance(investor.balance))

    @req_user
    def broke(self, sess, comment, investor):
        if investor.balance >= 100:
            return comment.reply_wrap(message.modify_broke_money(investor.balance))

        active = sess.query(
            func.count(Investment.id)
        ).filter(Investment.done).filter(Investment.name == investor.name).scalar()
        if active:
            comment.reply_wrap(message.modify_broke_active(active))

        # Indeed, broke
        sess.query(Investor).filter(Investor.name == investor.name).update({
            Investor.balance: 100,
            Investor.broke: investor.broke + 1,
        }, synchronize_session=False)

        comment.reply_wrap(message.modify_broke(investor.broke + 1))

    @req_user
    def active(self, sess, comment, investor):
        total = sess.query(
            func.count(Investment.id)
        ).filter(Investment.done == 0).\
        filter(Investment.name == investor.name).scalar()
        comment.reply_wrap(message.modify_active(total))

    def no_such_user(self, comment):
        comment.reply_wrap(message.no_account_org)


def main(n_jobs=4):
    comments_queue = Queue(maxsize=n_jobs * 4)
    threads = []
    engine = create_engine(config.db)
    sm = scoped_session(sessionmaker(bind=engine))
    reddit = praw.Reddit(
        client_id=config.client_id,
        client_secret=config.client_secret,
        username=config.username,
        password=config.password,
        user_agent=config.user_agent
    )

    while True:
        try:
            # Create n_jobs CommentsThreads
            for i in range(n_jobs):
                t = CommentWorker(
                    reddit,
                    sm,
                    name='CommentThread-t-{}'.format(i),
                    jobs=comments_queue
                )

                t.start()
                threads.append(t)

            # Iterate over all comments in the comment stream
            for comment in reddit.subreddit('+'.join(config.subreddits)).stream.comments(skip_existing=True):
                comments_queue.put(comment)
        except Exception as e:
            logging.error(e)

            for t in threads:
                t.stop()

            comments_queue.queue.clear()
            time.sleep(10)


if __name__ == "__main__":
    main()
