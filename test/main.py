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
        comment = Comment(username, command, submission=Submission(post))
        self.worker(comment)
        return comment.replies

class TestUserInit(Test):
    def test_create(self):
        replies = self.command('!create')
        self.assertEqual(len(replies), 1)
        self.assertEqual(
            replies[0].strip(),
            '*Account created!*\n\nThank you testuser for creating a bank account in r/MemeEconomy!\n\nYour starting balance is **1,000 MemeCoins**.'
        )

    def test_already_created(self):
        replies = self.command('!create')
        replies = self.command('!create')
        self.assertEqual(len(replies), 1)
        self.assertEqual(
            replies[0].strip(),
            'I love the enthusiasm, but you\'ve already got an account!'
        )

    def test_autocreate(self):
        replies = self.command('!balance')
        self.assertEqual(len(replies), 2)
        self.assertEqual(
            replies[0].strip(),
            '*Account created!*\n\nThank you testuser for creating a bank account in r/MemeEconomy!\n\nYour starting balance is **1,000 MemeCoins**.'
        )
        self.assertEqual(
            replies[1].strip(),
            'Currently, your account balance is **1,000 MemeCoins**.'
        )

class TestBasic(Test):
    def test_non_command(self):
        replies = self.command('balance')
        self.assertEqual(len(replies), 0)

    def test_ignore(self):
        replies = self.command('!ignore')
        self.assertEqual(len(replies), 0)

    def test_help(self):
        replies = self.command('!help')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.HELP_ORG)

class TestBalance(Test):
    def test_balance(self):
        self.command('!create')

        replies = self.command('!balance')
        self.assertEqual(replies[0], message.modify_balance(1000))

        sess = self.Session()
        investor = sess.query(Investor)\
            .filter(Investor.name == 'testuser')\
            .first()
        investor.balance = 1234
        sess.commit()

        replies = self.command('!balance')
        self.assertEqual(replies[0], message.modify_balance(1234))

class TestBroke(Test):
    def test_too_much_money(self):
        self.command('!create')

        replies = self.command('!broke')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_broke_money(1000))

    # def test_active(self):
    #     self.command('!create')
    #     self.command('!invest 1000')
    #
    #     replies = self.command('!broke')
    #     self.assertEqual(len(replies), 1)
    #     self.assertEqual(replies[0], message.modify_broke_money(1000))

if __name__ == '__main__':
    unittest.main()
