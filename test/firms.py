from test import Test
from models import Investor, Firm
import message

class MockFirm():
    def __init__(self, name, size=1, execs=0, rank=0):
        self.name = name
        self.size = size
        self.rank = rank
        self.execs = execs

class MockInvestor():
    def __init__(self, name, firm_role):
        self.name = name
        self.firm_role = firm_role

class TestCreateFirm(Test):
    def test_already_in_firm(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm foobar')
        replies = self.command('!createfirm foobar2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_createfirm_exists_failure('foobar'))

    def test_insufficient_funds(self):
        self.command('!create')
        replies = self.command('!createfirm foobar')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.createfirm_cost_failure_org)

    def test_deducts_balance(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm foobar')

        sess = self.Session()
        investor = sess.query(Investor).filter(Investor.name == 'testuser').first()
        self.assertEqual(investor.balance, 4000000)

    def test_short_name(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!createfirm foo')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.createfirm_format_failure_org)

    def test_long_name(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!createfirm foobar1234567890123456789012345678901234567890')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.createfirm_format_failure_org)

    def test_invalid_name(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!createfirm foo!bar')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.createfirm_format_failure_org)

    def test_existing_name(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm foobar')

        self.command('!create', username='testuser2')
        self.set_balance(5000000, username='testuser2')
        replies = self.command('!createfirm foobar', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.createfirm_nametaken_failure_org)

    def test_createfirm(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!createfirm Foo Bar Inc')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.createfirm_org)

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'ceo')

        firm = sess.query(Firm).filter(Firm.name == 'Foo Bar Inc').first()
        self.assertEqual(firm.id, 1)

class TestFirm(Test):
    def test_none(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!firm')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.firm_none_org)

    def test_ceo(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')
        replies = self.command('!firm')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_firm(
            'ceo',
            MockFirm('Foobar'),
            '/u/testuser',
            '',
            ''))

    def test_full(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!create', username='testuser3')
        self.command('!create', username='testuser4')

        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser4')

        self.command('!promote testuser2')

        replies = self.command('!firm', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_firm(
            'exec',
            MockFirm('Foobar'),
            '/u/testuser',
            '/u/testuser2',
            '/u/testuser3, /u/testuser4'))

class TestLeaveFirm(Test):
    def test_none(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!leavefirm')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.leavefirm_none_failure_org)

    def test_ceo_empty(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')
        replies = self.command('!leavefirm')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.leavefirm_org)

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser').first()
        self.assertEqual(user.firm, 0)

    def test_ceo_full(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        replies = self.command('!leavefirm')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.leavefirm_ceo_failure_org)

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser').first()
        self.assertEqual(user.firm, 1)

    def test_trader(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        replies = self.command('!leavefirm', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.leavefirm_org)

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 0)

class TestPromote(Test):
    def test_none(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!promote foo')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.firm_none_org)

    def test_not_ceo(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        replies = self.command('!promote foo', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_org)

    def test_non_existent(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        replies = self.command('!promote foo')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.promote_failure_org)

    def test_wrong_firm(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!createfirm Foobar2', username='testuser2')

        replies = self.command('!promote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.promote_failure_org)

    def test_promote_trader(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        replies = self.command('!promote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_promote(MockInvestor('testuser2', 'exec')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'exec')

    def test_promote_full(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')

        self.command('!create', username='testuser4')
        self.command('!joinfirm Foobar', username='testuser4')

        replies = self.command('!promote testuser4')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_promote_full(MockFirm('Foobar', size=2, execs=2)))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'exec')

    def test_promote_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        self.command('!promote testuser2')
        replies = self.command('!promote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_promote(MockInvestor('testuser2', 'ceo')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'ceo')

        me = sess.query(Investor).filter(Investor.name == 'testuser').first()
        self.assertEqual(me.firm, 1)
        self.assertEqual(me.firm_role, 'exec')

class TestFire(Test):
    def test_none(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!fire foo')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.firm_none_org)

    def test_not_ceo_or_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        replies = self.command('!fire foo', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_or_exec_org)

    def test_non_existent(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        replies = self.command('!fire foo')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.fire_failure_org)

    def test_self(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        replies = self.command('!fire testuser')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.fire_failure_org)

    def test_wrong_firm(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!createfirm Foobar2', username='testuser2')

        replies = self.command('!fire testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.fire_failure_org)

    def test_fire_exec_as_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')

        replies = self.command('!fire testuser3', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_org)

    def test_fire_trader(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        replies = self.command('!fire testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_fire(MockInvestor('testuser2', '')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 0)
        self.assertEqual(user.firm_role, '')

    def test_fire_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')

        replies = self.command('!fire testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_fire(MockInvestor('testuser2', '')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 0)
        self.assertEqual(user.firm_role, '')

    def test_fire_trader_as_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')

        replies = self.command('!fire testuser3', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_fire(MockInvestor('testuser3', '')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser3').first()
        self.assertEqual(user.firm, 0)
        self.assertEqual(user.firm_role, '')

class TestJoinFirm(Test):
    def test_already_in_firm(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.set_balance(5000000, username='testuser2')
        self.command('!createfirm Foobar2', username='testuser2')
        replies = self.command('!joinfirm Foobar', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.joinfirm_exists_failure_org)

    def test_non_existent(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!joinfirm Foobar')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.joinfirm_failure_org)

    def test_full(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        replies = self.command('!joinfirm Foobar', username='testuser2')

        self.command('!create', username='testuser3')
        replies = self.command('!joinfirm Foobar', username='testuser3')

        self.command('!create', username='testuser4')
        replies = self.command('!joinfirm Foobar', username='testuser4')

        self.command('!create', username='testuser5')
        replies = self.command('!joinfirm Foobar', username='testuser5')

        self.command('!create', username='testuser6')
        replies = self.command('!joinfirm Foobar', username='testuser6')

        self.command('!create', username='testuser7')
        replies = self.command('!joinfirm Foobar', username='testuser7')

        self.command('!create', username='testuser8')
        replies = self.command('!joinfirm Foobar', username='testuser8')

        self.command('!create', username='testuser9')
        replies = self.command('!joinfirm Foobar', username='testuser9')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_joinfirm_full(MockFirm('Foobar', size=8)))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, '')

    def test_joinfirm(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        replies = self.command('!joinfirm Foobar', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_joinfirm(MockFirm('Foobar')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, '')
