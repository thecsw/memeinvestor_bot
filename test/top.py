from test import Test
import message

class Leader():
    def __init__(self, name, networth):
        self.name = name
        self.networth = networth

class TestTop(Test):
    def test_top_none(self):
        replies = self.command('!top')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_top([]))

    def test_top(self):
        self.command('!create')
        replies = self.command('!top')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_top([
            Leader('testuser', 1000)
        ]))

        self.command('!create', username='testuser2')
        self.command('!create', username='testuser3')
        self.command('!create', username='testuser4')
        self.command('!create', username='testuser5')
        self.command('!create', username='testuser6')

        replies = self.command('!top')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_top([
            Leader('testuser', 1000),
            Leader('testuser2', 1000),
            Leader('testuser3', 1000),
            Leader('testuser4', 1000),
            Leader('testuser5', 1000)
        ]))

        self.set_balance(1234, username='testuser6')
        replies = self.command('!top')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_top([
            Leader('testuser6', 1234),
            Leader('testuser', 1000),
            Leader('testuser2', 1000),
            Leader('testuser3', 1000),
            Leader('testuser4', 1000)
        ]))

    def test_networth(self):
        self.command('!create')
        self.command('!invest 100')

        replies = self.command('!top')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_top([
            Leader('testuser', 1000)
        ]))
