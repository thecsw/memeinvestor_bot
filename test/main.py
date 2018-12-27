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
    def test_0000_create(self):
        comment = Comment('testuser', '!create')
        self.worker(comment)
        self.assertEqual(len(comment.replies), 1)
        self.assertEqual(
            comment.replies[0].strip(),
            '*Account created!*\n\nThank you testuser for creating a bank account in r/MemeEconomy!\n\nYour starting balance is **1,000 MemeCoins**.'
        )

    def test_0010_already_created(self):
        comment = Comment('testuser', '!create')
        self.worker(comment)
        self.assertEqual(len(comment.replies), 1)
        self.assertEqual(
            comment.replies[0].strip(),
            'I love the enthusiasm, but you\'ve already got an account!'
        )

    def test_0020_autocreate(self):
        comment = Comment('testuser2', '!balance')
        self.worker(comment)
        self.assertEqual(len(comment.replies), 2)
        self.assertEqual(
            comment.replies[0].strip(),
            '*Account created!*\n\nThank you testuser2 for creating a bank account in r/MemeEconomy!\n\nYour starting balance is **1,000 MemeCoins**.'
        )
        self.assertEqual(
            comment.replies[1].strip(),
            'Currently, your account balance is **1,000 MemeCoins**.'
        )

if __name__ == '__main__':
    unittest.main()
