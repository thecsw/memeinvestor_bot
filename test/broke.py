from test import Test
import message

class TestBroke(Test):
    def test_too_much_money(self):
        self.command('!create')
        replies = self.command('!broke')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_broke_money(1000))

    def test_active(self):
        self.command('!create')
        self.command('!invest 1000')
        replies = self.command('!broke')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_broke_active(1))

    def test_broke(self):
        self.command('!create')

        self.set_balance(0)
        replies = self.command('!broke')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_broke(1))

        self.set_balance(0)
        replies = self.command('!broke')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_broke(2))
