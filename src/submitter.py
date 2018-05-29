import time
import logging

import MySQLdb
import MySQLdb.cursors
import _mysql_exceptions
import praw
from bottr.bot import AbstractCommentBot, BotQueueWorker, SubmissionBot

import config
import models
import message
from main import reply_wrap

praw.models.Submission.reply_wrap = reply_wrap
logging.basicConfig(level=logging.INFO)


def submission_bot(submission, db):
    if submission not in db:
        logging.info("New submission: %s" % submission)
        db.append(submission)
        submission.reply_wrap(message.invest_place_here)


def main():
    db = None
    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)

    while not db:
        try:
            db = MySQLdb.connect(cursorclass=MySQLdb.cursors.DictCursor, **config.dbconfig)
        except _mysql_exceptions.OperationalError:
            logging.warning("Waiting 10s for MySQL to go up...")
            time.sleep(10)

    submissions = models.Submissions(db)
    subbot = SubmissionBot(reddit, subreddits=config.subreddits,
                           func_submission=submission_bot,
                           func_submission_args=[submissions], n_jobs=1)
    subbot.start()


if __name__ == "__main__":
    main()
