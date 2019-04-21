from test import Test
from models import Investor, Firm
import message

class MockFirm():
    def __init__(self, name, id=1, size=1, assocs=0, execs=0, cfo=0, coo=0, rank=0, balance=1234):
        self.id = id
        self.name = name
        self.size = size
        self.rank = rank
        self.assocs = assocs
        self.execs = execs
        self.cfo = cfo
        self.coo = coo
        self.balance = balance

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
        self.assertEqual(investor.balance, 4900000)

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
        self.assertEqual(replies[0], message.modify_firm_self(
            'ceo',
            MockFirm('Foobar', balance=1000)))

    def test_firm_assoc(self):
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
        self.assertEqual(replies[0], message.modify_firm_self(
            'assoc',
            MockFirm('Foobar', balance=1000)))

    def test_firm_cfo(self):
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
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        replies = self.command('!firm', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_firm_self(
            'cfo',
            MockFirm('Foobar', balance=1000)))

    def test_lookup(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        replies = self.command('!firm Foobar', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_firm_other(
            MockFirm('Foobar', balance=1000)))

    def test_lookup_different_case(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        replies = self.command('!firm foobar', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_firm_other(
            MockFirm('Foobar', balance=1000)))

    def test_lookup_invalid(self):
        self.command('!create')
        replies = self.command('!firm Foobar')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.firm_notfound_org)

class TestLeaveFirm(Test):
    def test_leave_none(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!leavefirm')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.leavefirm_none_failure_org)

    def test_leave_ceo_empty(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')
        replies = self.command('!leavefirm')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.leavefirm_org)

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser').first()
        self.assertEqual(user.firm, 0)

    def test_leave_ceo_full(self):
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

    def test_leave_trader(self):
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

    def test_leave_assoc(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')

        replies = self.command('!leavefirm', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.leavefirm_org)

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 0)
        self.assertEqual(user.firm_role, '')

        firm = sess.query(Firm).filter(Firm.name == 'Foobar').first()
        self.assertEqual(firm.size, 1)
        self.assertEqual(firm.assocs, 0)

    def test_leave_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        replies = self.command('!leavefirm', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.leavefirm_org)

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 0)
        self.assertEqual(user.firm_role, '')

        firm = sess.query(Firm).filter(Firm.name == 'Foobar').first()
        self.assertEqual(firm.size, 1)
        self.assertEqual(firm.execs, 0)

class TestPromote(Test):
    def test_none(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!promote foo')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.firm_none_org)

    def test_not_ceo_or_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')

        replies = self.command('!promote testuser3', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_or_exec_org)

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

    def test_promote_self(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        replies = self.command('!promote testuser')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.promote_failure_org)


    def test_promote_to_assoc(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        replies = self.command('!promote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_promote(MockInvestor('testuser2', 'assoc'), ''))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'assoc')

    def test_promote_execs_full(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')
        self.command('!promote testuser3')

        self.command('!create', username='testuser4')
        self.command('!joinfirm Foobar', username='testuser4')
        self.command('!promote testuser4')

        replies = self.command('!promote testuser4')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_promote_execs_full(MockFirm('Foobar', execs=2)))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'exec')

    def test_promote_to_assoc_and_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')
        self.command('!promote testuser3')

        self.command('!create', username='testuser4')
        self.command('!joinfirm Foobar', username='testuser4')

        replies = self.command('!promote testuser4')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_promote(MockInvestor('testuser4', 'assoc'), ''))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser3').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'exec')

        user = sess.query(Investor).filter(Investor.name == 'testuser4').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'assoc')

    def test_promote_to_cfo(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')
        replies = self.command('!promote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_promote(MockInvestor('testuser2', 'cfo'), 'exec'))

    def test_promote_to_cfo_full(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')
        self.command('!promote testuser3')

        replies = self.command('!promote testuser3')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_promote(MockInvestor('testuser3', 'coo'), 'exec'))

        sess = self.Session()
        firm = sess.query(Firm).filter(Firm.name == 'Foobar').first()
        self.assertEqual(firm.size, 3)
        self.assertEqual(firm.execs, 0)
        self.assertEqual(firm.cfo, 1)
        self.assertEqual(firm.coo, 1)

class TestDemote(Test):
    def test_none(self):
        self.command('!create')
        self.set_balance(5000000)
        replies = self.command('!demote foo')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.firm_none_org)

    def test_demote_trader(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        replies = self.command('!demote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.demote_failure_trader_org)

    def test_not_ceo_or_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')

        replies = self.command('!demote testuser3', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_or_exec_org)

    def test_non_existent(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        replies = self.command('!demote foo')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.demote_failure_org)

    def test_wrong_firm(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!createfirm Foobar2', username='testuser2')

        replies = self.command('!demote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.demote_failure_org)

    def test_demote_self(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        replies = self.command('!demote testuser')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.demote_failure_org)

    def test_demote_to_trader(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')

        replies = self.command('!demote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_demote(MockInvestor('testuser2', ''), 'assoc'))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, '')

    def test_demote_to_assoc(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        replies = self.command('!demote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_demote(MockInvestor('testuser2', 'assoc'), 'exec'))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'assoc')

    def test_demote_execs_full(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')
        self.command('!promote testuser3')

        self.command('!create', username='testuser4')
        self.command('!joinfirm Foobar', username='testuser4')
        self.command('!promote testuser4')
        self.command('!promote testuser4')

        replies = self.command('!demote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_demote_execs_full(MockFirm('Foobar', execs=2)))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'cfo')

    def test_demote_to_cfo(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        replies = self.command('!demote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_demote(MockInvestor('testuser2', 'cfo'), 'coo'))

    def test_demote_to_cfo_full(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')
        self.command('!promote testuser3')
        self.command('!promote testuser3')

        replies = self.command('!demote testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_demote(MockInvestor('testuser2', 'exec'), 'coo'))

        sess = self.Session()
        firm = sess.query(Firm).filter(Firm.name == 'Foobar').first()
        self.assertEqual(firm.size, 3)
        self.assertEqual(firm.execs, 1)
        self.assertEqual(firm.cfo, 1)
        self.assertEqual(firm.coo, 0)

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

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')

        replies = self.command('!fire testuser2', username='testuser3')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_or_exec_org)

    def test_not_ceo_or_coo(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')
        self.command('!promote testuser3')

        replies = self.command('!fire testuser3', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_or_coo_org)

    def test_not_ceo(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')
        self.command('!promote testuser3')
        self.command('!promote testuser3')

        replies = self.command('!fire testuser3', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_org)

    def test_non_existent(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        replies = self.command('!fire foo')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.fire_failure_org)

    def test_fire_self(self):
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

    def test_fire_trader_as_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
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

    def test_fire_assoc_as_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')

        replies = self.command('!fire testuser3', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_fire(MockInvestor('testuser3', '')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser3').first()
        self.assertEqual(user.firm, 0)
        self.assertEqual(user.firm_role, '')

        firm = sess.query(Firm).filter(Firm.name == 'Foobar').first()
        self.assertEqual(firm.size, 2)
        self.assertEqual(firm.assocs, 0)

    def test_fire_exec_as_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm Foobar', username='testuser3')
        self.command('!promote testuser3')
        self.command('!promote testuser3')

        replies = self.command('!fire testuser3', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_or_coo_org)

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

    def test_fire_assoc(self):
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

        firm = sess.query(Firm).filter(Firm.name == 'Foobar').first()
        self.assertEqual(firm.size, 1)
        self.assertEqual(firm.assocs, 0)

    def test_fire_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        replies = self.command('!fire testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_fire(MockInvestor('testuser2', '')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 0)
        self.assertEqual(user.firm_role, '')

        firm = sess.query(Firm).filter(Firm.name == 'Foobar').first()
        self.assertEqual(firm.size, 1)
        self.assertEqual(firm.execs, 0)

    def test_fire_trader_as_assoc(self):
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
        self.assertEqual(replies[0], message.not_ceo_or_exec_org)

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser3').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, '')

    def test_fire_trader_as_exec(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, '')
        self.command('!promote testuser2')
        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'assoc')
        self.command('!promote testuser2')
        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, 'exec')

        replies = self.command('!fire testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_fire(MockInvestor('testuser2', '')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 0)
        self.assertEqual(user.firm_role, '')

        firm = sess.query(Firm).filter(Firm.name == 'Foobar').first()
        self.assertEqual(firm.size, 1)
        self.assertEqual(firm.cfo, 0)

    def test_fire_coo(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        replies = self.command('!fire testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_fire(MockInvestor('testuser2', '')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 0)
        self.assertEqual(user.firm_role, '')

        firm = sess.query(Firm).filter(Firm.name == 'Foobar').first()
        self.assertEqual(firm.size, 1)
        self.assertEqual(firm.coo, 0)

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

    def test_join_private_fail(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')
        self.command('!setprivate')

        self.command('!create', username='testuser2')
        replies = self.command('!joinfirm Foobar', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.joinfirm_private_failure_org)

    def test_join_private(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')
        self.command('!setprivate')

        self.command('!create', username='testuser2')
        self.command('!invite testuser2')

        replies = self.command('!joinfirm Foobar', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_joinfirm(MockFirm('Foobar')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, '')

    def test_joinfirm_quotes(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command("!createfirm 'Name with many words'")

        self.command('!create', username='testuser2')
        replies = self.command("!joinfirm 'Name with many words'", username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_joinfirm(MockFirm('Name with many words')))

        sess = self.Session()
        user = sess.query(Investor).filter(Investor.name == 'testuser2').first()
        self.assertEqual(user.firm, 1)
        self.assertEqual(user.firm_role, '')

class TestInvite(Test):
    def test_not_in_firm(self):
        self.command('!create')
        replies = self.command('!invite noerdy')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.no_firm_failure_org)

    def test_not_assoc(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm foobar', username='testuser2')
        replies = self.command('!invite thecsw', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_assoc_org)

    def test_not_private(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm foobar')

        self.command('!create', username='testuser2')
        replies = self.command('!invite testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.invite_not_private_failure_org)

    def test_no_user(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm foobar')
        self.command('!setprivate')

        replies = self.command('!invite testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.invite_no_user_failure_org)

    def test_user_in_firm(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm foobar')
        self.command('!setprivate')

        self.command('!create', username='testuser2')
        self.set_balance(5000000, username='testuser2')
        self.command('!createfirm foobar2', username='testuser2')

        replies = self.command('!invite testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.invite_in_firm_failure_org)

    def test_invite(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm foobar')
        self.command('!setprivate')

        self.command('!create', username='testuser2')

        replies = self.command('!invite testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_invite(MockInvestor('testuser2', ''), MockFirm('foobar')))

    def test_assoc_invite(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm foobar')
        self.command('!setprivate')

        self.command('!create', username='testuser2')
        self.command('!invite testuser2')
        self.command('!joinfirm foobar', username='testuser2')
        self.command('!promote testuser2')

        self.command('!create', username='testuser3')
        self.command('!joinfirm foobar', username='testuser3')

        replies = self.command('!invite testuser3', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_invite(MockInvestor('testuser3', ''), MockFirm('foobar')))

class TestUpgrade(Test):
    def test_not_in_firm(self):
        self.command('!create')

        replies = self.command('!upgrade')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.nofirm_failure_org)

    def test_not_ceo_or_cfo(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        replies = self.command('!upgrade', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_or_cfo_org)

    def test_insufficient_funds(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')
        replies = self.command('!upgrade')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_upgrade_insufficient_funds_org(MockFirm('Foobar', balance=1000), 4000000))

    def test_upgrade(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')
        self.set_firm_balance('Foobar', 5000000)

        replies = self.command('!upgrade')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.modify_upgrade(MockFirm('Foobar', balance=1000, rank=1), 16, 4, 6))

        sess = self.Session()
        firm = sess.query(Firm).filter(Firm.name == 'Foobar').first()
        self.assertEqual(firm.balance, 1000000)

class TestTax(Test):
    def test_not_in_firm(self):
        self.command('!create')

        replies = self.command('!tax 50')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.nofirm_failure_org)

    def test_not_ceo_or_cfo(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foobar')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Foobar', username='testuser2')

        replies = self.command('!tax 50', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.not_ceo_or_cfo_org)

    def test_tax_too_high(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foohigh')
        replies = self.command('!tax 100')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.TAX_TOO_HIGH)

    def test_tax_too_low(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foolow')
        replies = self.command('!tax 0')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.TAX_TOO_LOW)

    def test_tax_neg_value(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Fooneg')
        replies = self.command('!tax -99')
        self.assertEqual(len(replies), 0)

    def test_tax_no_value(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foonoval')
        replies = self.command('!tax')
        self.assertEqual(len(replies), 0)

    def test_tax_not_numerical(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Foononum')
        replies = self.command('!tax garbage_value')
        self.assertEqual(len(replies), 0)

    def test_tax_success(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Footaxsucc')
        replies = self.command('!tax 37')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.TAX_SUCCESS)

        sess = self.Session()
        firm = sess.query(Firm).filter(Firm.name == 'Footaxsucc').first()
        self.assertEqual(firm.tax, 37)

    def test_tax_cfo_success(self):
        self.command('!create')
        self.set_balance(5000000)
        self.command('!createfirm Footaxsucc')

        self.command('!create', username='testuser2')
        self.command('!joinfirm Footaxsucc', username='testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')
        self.command('!promote testuser2')

        replies = self.command('!tax 37', username='testuser2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], message.TAX_SUCCESS)

        sess = self.Session()
        firm = sess.query(Firm).filter(Firm.name == 'Footaxsucc').first()
        self.assertEqual(firm.tax, 37)
