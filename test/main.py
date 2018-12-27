import sys
sys.path.append('src')

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from comment_worker import CommentWorker
from models import Base
from mock_praw import Comment

class Test(unittest.TestCase):
    def setUp(self):
        # create sqlite db
        engine = create_engine('sqlite:///.testenv/test.db')
        session_maker = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        self.worker = CommentWorker(session_maker)

class TestUserInit(Test):
    def test_create(self):
        comment = Comment('testuser2', '!create')
        self.worker(comment)
        print(comment.replies)

if __name__ == '__main__':
    unittest.main()
