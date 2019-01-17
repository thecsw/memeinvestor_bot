from test import Test

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
