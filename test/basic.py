from test import Test
import message
import utils

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

    def test_version(self):
        replies = self.command('!version')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_deploy_version(utils.DEPLOY_DATE))
