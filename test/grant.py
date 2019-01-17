from test import Test
import message

class TestGrant(Test):
    def test_non_admin(self):
        replies = self.command('!grant testuser foo')
        self.assertEqual(len(replies), 0)

    def test_no_account(self):
        replies = self.command('!grant testuser foo', username='admin')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_grant_failure('no such investor'))

    def test_grant(self):
        self.command('!create')
        replies = self.command('!grant testuser foo', username='admin')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_grant_success('testuser', 'foo'))

    def test_grant_duplicate(self):
        self.command('!create')
        self.command('!grant testuser foo', username='admin')

        replies = self.command('!grant testuser foo', username='admin')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_grant_failure('already owned'))
