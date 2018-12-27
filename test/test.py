import sys
sys.path.append('src')

import os
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from comment_worker import CommentWorker
from models import Base, Investor
from mock_praw import Comment, Submission
import message

class Test(unittest.TestCase):
    def setUp(self):
        # create sqlite db
        engine = create_engine('sqlite:///.testenv/test.db')
        self.Session = session_maker = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        self.worker = CommentWorker(session_maker)

    def tearDown(self):
        # remove db file
        os.remove('.testenv/test.db')

    def command(self, command, username='testuser', post='testpost'):
        comment = Comment('id', username, command, Submission(post))
        self.worker(comment)
        return comment.replies

    def set_balance(self, balance, user='testuser'):
        sess = self.Session()
        investor = sess.query(Investor)\
            .filter(Investor.name == user)\
            .first()
        investor.balance = balance
        sess.commit()
