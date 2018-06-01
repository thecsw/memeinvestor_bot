import time
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import praw

import config
import message
from main import reply_wrap
from models import Submission

praw.models.Submission.reply_wrap = reply_wrap
logging.basicConfig(level=logging.INFO)


def main():
    engine = create_engine(config.db)
    sm = sessionmaker(bind=engine)
    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)

    logging.info("Starting checking submissions...")
    while True:
        try:
            for submission in reddit.subreddit('+'.join(config.subreddits)).stream.submissions():
                sess = sm()
                q = sess.query(Submission).filter(Submission.submission == submission).exists()

                if not sess.query(q).scalar():
                    logging.info("New submission: %s" % submission)
                    sess.add(Submission(submission=submission))
                    sess.commit()
                    submission.reply_wrap(message.invest_place_here)

                sess.close()
        except Exception as e:
            logging.error(e)
            time.sleep(10)


if __name__ == "__main__":
    main()
