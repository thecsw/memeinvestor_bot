import time

from test import Test
import message

class Investment():
    def __init__(self, post, amount, upvotes, time):
        self.post = post
        self.amount = amount
        self.upvotes = upvotes
        self.time = time

class TestActive(Test):
    def test_active_none(self):
        self.command('!create')

        replies = self.command('!active')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_active([]))

    def test_active(self):
        self.command('!create')
        self.command('!invest 100', post='post1')
        self.command('!invest 100', post='post2')

        replies = self.command('!active')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_active([
            Investment('post1', 100, 100, time.time()),
            Investment('post2', 100, 100, time.time())
        ]))
