from test import Test
import message

class TestBalance(Test):
    def test_balance(self):
        self.command('!create')

        replies = self.command('!balance')
        self.assertEqual(replies[0], message.modify_balance(1000))

        self.set_balance(1234)

        replies = self.command('!balance')
        self.assertEqual(replies[0], message.modify_balance(1234))
