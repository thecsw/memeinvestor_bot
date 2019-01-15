import json
import logging
import re
import time
import traceback
import os

from sqlalchemy import func, desc, and_

import praw

import config
import message
from models import Investment, Investor, Firm, Invite
import utils

REDDIT = None

if not config.TEST:
    REDDIT = praw.Reddit(client_id=config.CLIENT_ID,
                         client_secret=config.CLIENT_SECRET,
                         username=config.USERNAME,
                         password=config.PASSWORD,
                         user_agent=config.USER_AGENT)

# Decorator to mark a commands that require a user
# Adds the investor after the comment when it calls the method (see broke)
def req_user(wrapped_function):
    """
    This is a wrapper function that ensures user exists
    """
    def wrapper(self, sess, comment, *args):
        investor = sess.query(Investor).\
            filter(Investor.name == comment.author.name).\
            first()

        if not investor:
            logging.info(" -- autocreating")
            self.create(sess, comment)
            investor = sess.query(Investor).\
                filter(Investor.name == comment.author.name).\
                first()

        return wrapped_function(self, sess, comment, investor, *args)
    return wrapper


# Monkey patch exception handling
def reply_wrap(self, body):
    """
    Wrapper function to make a reddit reply
    """
    logging.info(" -- replying")

    if config.POST_TO_REDDIT:
        try:
            return self.reply(body)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            return False
    else:
        logging.info(body)
        return "0"

def edit_wrap(self, body):
    logging.info(" -- editing response")

    if config.POST_TO_REDDIT:
        try:
            return self.edit(body)
        # TODO: get rid of this broad except
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            return False
    else:
        logging.info(body)
        return False

praw.models.Comment.reply_wrap = reply_wrap
praw.models.Comment.edit_wrap = edit_wrap

class CommentWorker():
    """
    This class is responsible for everything that happens
    in the comment. With some regex rules, it sees all of
    the commands and it has methods to execute on demand
    """
    multipliers = {
        'k': 1e3,
        'm': 1e6,
        'b': 1e9,
        't': 1e12,
        'quad': 1e15,
        # Has to be above q, or regex will stop at q instead of searching for quin/quad
        'quin': 1e18,
        'q': 1e15
    }

    commands = [
        r"!active",
        r"!balance",
        r"!broke",
        r"!create",
        r"!help",
        r"!ignore",
        r"!invest\s+([\d,.]+)\s*(%s)?(?:\s|$)" % "|".join(multipliers),
        r"!market",
        r"!top",
        r"!version",
        r"!grant\s+(\S+)\s+(\S+)",
        r"!template\s+(https://imgur.com/.+)",
        r"!firm",
        r"!createfirm\s+(.+)",
        r"!joinfirm\s+(.+)",
        r"!leavefirm",
        r"!promote\s+(.+)",
        r"!fire\s+(.+)",
        r"!upgrade",
        r"!invite\s+(.+)",
        r"!setprivate",
        r"!setpublic"
    ]

    # allowed: alphanumeric, spaces, dashes
    firm_name_format = r"[^\w \-]"

    def __init__(self, sm):
        self.regexes = [re.compile(x, re.MULTILINE | re.IGNORECASE)
                        for x in self.commands]
        self.firm_name_regex = re.compile(self.firm_name_format)
        self.Session = sm

    def __call__(self, comment):
        # Ignore items that aren't Comments (i.e. Submissions)
        # (And skip this check in the tests since we use a mock)
        if not isinstance(comment, praw.models.Comment) | (os.getenv("TEST") != ""):
            return

        # Ignore comments at the root of a Submission
        if comment.is_root:
            return

        # Ignore comments without an author (deleted)
        if not comment.author:
            return

        # Ignore comments by other bots
        if comment.author.name.lower().endswith("_bot"):
            return

        # Ignore comments older than a threshold
        max_age = 60*15 # fifteen minutes
        comment_age = time.time() - int(comment.created_utc)
        if comment_age > max_age:
            return

        # Parse the comment body for a command
        for reg in self.regexes:
            matches = reg.fullmatch(comment.body.strip())
            if not matches:
                continue

            cmd = matches.group()
            attrname = cmd.split(" ")[0][1:].lower()

            if not hasattr(self, attrname):
                continue

            logging.info(" -- %s: %s", comment.author.name, cmd)

            try:
                sess = self.Session()
                getattr(self, attrname)(sess, comment, *matches.groups())
                # TODO: make this except more narrow
            except Exception as e:
                logging.error(e)
                traceback.print_exc()
                sess.rollback()
            else:
                sess.commit()

            sess.close()
            break

    def ignore(self, sess, comment):
        """
        Just ignore function
        """
        pass

    def help(self, sess, comment):
        """
        Returns help information
        """
        comment.reply_wrap(message.HELP_ORG)

    def market(self, sess, comment):
        """
        Return the meme market's current state
        """
        total = sess.query(
            func.coalesce(func.sum(Investor.balance), 0)
        ).scalar()

        invested, active = sess.query(
            func.coalesce(func.sum(Investment.amount), 0),
            func.count(Investment.id)
        ).filter(Investment.done == 0).first()

        comment.reply_wrap(message.modify_market(active, total, invested))

    def top(self, sess, comment):
        """
        Returns the top users in the meme market
        """
        leaders = sess.query(
            Investor.name,
            func.coalesce(Investor.balance+func.sum(Investment.amount), Investor.balance).label('networth')).\
            outerjoin(Investment, and_(Investor.name == Investment.name, Investment.done == 0)).\
        group_by(Investor.name).\
        order_by(desc('networth')).\
        limit(5).\
        all()

        comment.reply_wrap(message.modify_top(leaders))

    def create(self, sess, comment):
        """
        This one is responsible for creating a new user
        """
        author = comment.author.name
        user_exists = sess.query(Investor).filter(Investor.name == author).exists()

        # Let user know they already have an account
        if sess.query(user_exists).scalar():
            comment.reply_wrap(message.CREATE_EXISTS_ORG)
            return

        # Create new investor account
        sess.add(Investor(name=author))
        # TODO: Make the initial balance a constant
        comment.reply_wrap(message.modify_create(comment.author, config.STARTING_BALANCE))

    @req_user
    def invest(self, sess, comment, investor, amount, suffix):
        """
        This function invests
        """
        if config.PREVENT_INSIDERS:
            if comment.submission.author.name == comment.author.name:
                comment.reply_wrap(message.INSIDE_TRADING_ORG)
                return

        try:
            amount = float(amount.replace(',', ''))
            amount = int(amount * CommentWorker.multipliers.get(suffix, 1))
        except ValueError:
            return

        if amount < 100:
            comment.reply_wrap(message.MIN_INVEST_ORG)
            return

        author = comment.author.name
        new_balance = investor.balance - amount

        if new_balance < 0:
            comment.reply_wrap(message.modify_insuff(investor.balance))
            return

        # Sending a confirmation
        response = comment.reply_wrap(message.modify_invest(
            amount,
            comment.submission.ups,
            new_balance
        ))

        sess.add(Investment(
            post=comment.submission,
            upvotes=comment.submission.ups,
            comment=comment,
            name=author,
            amount=amount,
            response=response,
            done=False,
        ))

        investor.balance = new_balance

    @req_user
    def balance(self, sess, comment, investor):
        """
        Returns user's balance
        """
        comment.reply_wrap(message.modify_balance(investor.balance))

    @req_user
    def broke(self, sess, comment, investor):
        """
        Checks if the user is broke. If he is, resets his/her balance to 100 MemeCoins
        """
        if investor.balance >= 100:
            return comment.reply_wrap(message.modify_broke_money(investor.balance))

        active = sess.query(func.count(Investment.id)).\
            filter(Investment.done == 0).\
            filter(Investment.name == investor.name).\
            scalar()

        if active > 0:
            return comment.reply_wrap(message.modify_broke_active(active))

        # Indeed, broke
        investor.balance = 100
        investor.broke += 1

        comment.reply_wrap(message.modify_broke(investor.broke))

    @req_user
    def active(self, sess, comment, investor):
        """
        Returns a list of all active investments made by the user
        """
        active_investments = sess.query(Investment).\
            filter(Investment.done == 0).\
            filter(Investment.name == investor.name).\
            order_by(Investment.time).\
            all()

        comment.reply_wrap(message.modify_active(active_investments))

    def grant(self, sess, comment, grantee, badge):
        """
        This is how admins can grant badges manually
        """
        author = comment.author.name
        badge = badge.lower().replace('\\', '')
        grantee_unescaped = grantee.replace('\\', '')

        if author in config.ADMIN_ACCOUNTS:
            investor = sess.query(Investor).\
                filter(Investor.name == grantee_unescaped).\
                first()

            if not investor:
                return comment.reply_wrap(message.modify_grant_failure("no such investor"))

            badge_list = json.loads(investor.badges)
            if badge in badge_list:
                return comment.reply_wrap(message.modify_grant_failure("already owned"))

            badge_list.append(badge)
            investor.badges = json.dumps(badge_list)
            return comment.reply_wrap(message.modify_grant_success(grantee, badge))

    def template(self, sess, comment, link):
        """
        OP can submit the template link to the bot's sticky
        """

        # Type of comment is praw.models.reddit.comment.Comment, which
        # does not have a lot of documentation in the docs, for more
        # informationg go to
        # github.com/praw-dev/praw/blob/master/praw/models/reddit/comment.py
        comment.refresh()
        if not comment.is_submitter:
            return comment.reply_wrap(message.TEMPLATE_NOT_OP)

        # Checking if the upper comment is the bot's sticky
        if not comment.parent().stickied:
            return comment.reply_wrap(message.TEMPLATE_NOT_STICKY)

        # What if user spams !template commands?
        if comment.parent().edited:
            return comment.reply_wrap(message.TEMPLATE_ALREADY_DONE)

        # If OP posted a template, replace the hint
        edited_response = comment.parent().body.replace(message.TEMPLATE_HINT_ORG.
                                                        replace("%NAME%", f"u/{comment.author.name}"), '')
        edited_response += message.modify_template_op(link, f"u/{comment.author.name}")

        return comment.parent().edit_wrap(edited_response)

    def version(self, sess, comment):
        """
        Return the date when the bot was deployed
        """
        return comment.reply_wrap(message.modify_deploy_version(utils.DEPLOY_DATE))

    @req_user
    def firm(self, sess, comment, investor):
        if investor.firm == 0:
            return comment.reply_wrap(message.firm_none_org)

        firm = sess.query(Firm).\
            filter(Firm.id == investor.firm).\
            first()

        ceo = "/u/" + sess.query(Investor).\
            filter(Investor.firm == firm.id).\
            filter(Investor.firm_role == "ceo").\
            first().\
            name
        execs = concat_names(
            sess.query(Investor).\
                filter(Investor.firm == firm.id).\
                filter(Investor.firm_role == "exec").\
                all())
        traders = concat_names(
            sess.query(Investor).\
                filter(Investor.firm == firm.id).\
                filter(Investor.firm_role == "").\
                all())

        return comment.reply_wrap(
            message.modify_firm(
                investor.firm_role,
                firm,
                ceo,
                execs,
                traders))

    @req_user
    def createfirm(self, sess, comment, investor, firm_name):
        if investor.firm != 0:
            existing_firm = sess.query(Firm).\
                filter(Firm.id == investor.firm).\
                first()
            return comment.reply_wrap(message.modify_createfirm_exists_failure(existing_firm.name))

        if investor.balance < 1000000:
            return comment.reply_wrap(message.createfirm_cost_failure_org)
        investor.balance -= 1000000

        firm_name = firm_name.strip()

        if (len(firm_name) < 4) or (len(firm_name) > 32):
            return comment.reply_wrap(message.createfirm_format_failure_org)

        if self.firm_name_regex.search(firm_name):
            return comment.reply_wrap(message.createfirm_format_failure_org)

        existing_firm = sess.query(Firm).\
            filter(Firm.name == firm_name).\
            first()

        if existing_firm:
            return comment.reply_wrap(message.createfirm_nametaken_failure_org)

        sess.add(Firm(name=firm_name))
        firm = sess.query(Firm).\
            filter(Firm.name == firm_name).\
            first()
        investor.firm = firm.id
        investor.firm_role = "ceo"
        firm.size += 1

        # Setting up the flair in subreddits
        # Hardcoded CEO string because createfirm makes a user CEO
        if not config.TEST:
            for subreddit in config.SUBREDDITS:
                REDDIT.subreddit(subreddit).flair.set(investor.name, f"{firm_name} | CEO")
        return comment.reply_wrap(message.createfirm_org)

    @req_user
    def leavefirm(self, sess, comment, investor):
        if investor.firm == 0:
            return comment.reply_wrap(message.leavefirm_none_failure_org)

        if investor.firm_role == "ceo":
            members = sess.query(Investor).\
                filter(Investor.firm == investor.firm).\
                count()
            if members > 1:
                return comment.reply_wrap(message.leavefirm_ceo_failure_org)
        firm = sess.query(Firm).\
            filter(Firm.id == investor.firm).\
            first()

        investor.firm = 0
        firm.size -= 1

        if investor.firm_role == 'exec':
            firm.execs -= 1

        # Removing the flair in subreddits
        if not config.TEST:
            for subreddit in config.SUBREDDITS:
                REDDIT.subreddit(subreddit).flair.set(investor.name, "")
        return comment.reply_wrap(message.leavefirm_org)

    @req_user
    def promote(self, sess, comment, investor, to_promote):
        if investor.firm == 0:
            return comment.reply_wrap(message.firm_none_org)

        if investor.firm_role != "ceo":
            return comment.reply_wrap(message.not_ceo_org)

        user = sess.query(Investor).\
            filter(Investor.name == to_promote).\
            first()
        if (user is None) or (user.firm != investor.firm):
            return comment.reply_wrap(message.promote_failure_org)

        firm = sess.query(Firm).\
            filter(Firm.id == user.firm).\
            first()

        if user.firm_role == "":
            max_execs = max_execs_for_rank(firm.rank)
            if firm.execs >= max_execs:
                return comment.reply_wrap(message.modify_promote_full(firm))

            user.firm_role = "exec"
            firm.execs += 1
        elif user.firm_role == "exec":
            # Swapping roles
            investor.firm_role = "exec"
            user.firm_role = "ceo"

        # Updating the flair in subreddits
        flair_role = ''
        if user.firm_role == "ceo":
            flair_role = "CEO"
        else:
            flair_role = "Executive"
        if not config.TEST:
            for subreddit in config.SUBREDDITS:
                REDDIT.subreddit(subreddit).flair.set(user.name, f"{firm.name} | {flair_role}")

        return comment.reply_wrap(message.modify_promote(user))

    @req_user
    def fire(self, sess, comment, investor, to_fire):
        if investor.firm == 0:
            return comment.reply_wrap(message.firm_none_org)

        if investor.firm_role == "":
            return comment.reply_wrap(message.not_ceo_or_exec_org)

        user = sess.query(Investor).\
            filter(Investor.name == to_fire).\
            first()
        if (user == None) or (user.name == investor.name) or (user.firm != investor.firm):
            return comment.reply_wrap(message.fire_failure_org)

        if (investor.firm_role != "ceo") and (user.firm_role != ""):
            return comment.reply_wrap(message.not_ceo_org)

        firm = sess.query(Firm).\
            filter(Firm.id == investor.firm).\
            first()

        user.firm_role = ""
        user.firm = 0
        firm.size -= 1

        if investor.firm_role == 'exec':
            firm.execs -= 1

        # Clear the firm flair
        if not config.TEST:
            for subreddit in config.SUBREDDITS:
                REDDIT.subreddit(subreddit).flair.set(user.name, '')
        return comment.reply_wrap(message.modify_fire(user))

    @req_user
    def joinfirm(self, sess, comment, investor, firm_name):
        if investor.firm != 0:
            return comment.reply_wrap(message.joinfirm_exists_failure_org)

        firm = sess.query(Firm).\
            filter(Firm.name == firm_name).\
            first()
        if firm == None:
            return comment.reply_wrap(message.joinfirm_failure_org)

        max_members = max_members_for_rank(firm.rank)
        if firm.size >= max_members:
            return comment.reply_wrap(message.modify_joinfirm_full(firm))

        if firm.private:
            invite = sess.query(Invite).\
                filter(Invite.investor == investor.id).\
                filter(Invite.firm == firm.id).\
                first()
            if invite == None:
                return comment.reply_wrap(message.joinfirm_private_failure_org)

        investor.firm = firm.id
        investor.firm_role = ""
        firm.size += 1

        # Updating the flair in subreddits
        if not config.TEST:
            for subreddit in config.SUBREDDITS:
                REDDIT.subreddit(subreddit).flair.set(investor.name, f"{firm_name} | Floor Trader")

        return comment.reply_wrap(message.modify_joinfirm(firm))

    @req_user
    def invite(self, sess, comment, investor, invitee_name):
        if investor.firm == 0:
            return comment.reply_wrap(message.no_firm_failure_org)

        if investor.firm_role == "":
            return comment.reply_wrap(message.not_ceo_or_exec_org)

        firm = sess.query(Firm).\
            filter(Firm.id == investor.firm).\
            first()

        if not firm.private:
            return comment.reply_wrap(message.invite_not_private_failure_org)

        invitee = sess.query(Investor).\
            filter(Investor.name == invitee_name).\
            first()
        if invitee == None:
            return comment.reply_wrap(message.invite_no_user_failure_org)
        if invitee.firm != 0:
            return comment.reply_wrap(message.invite_in_firm_failure_org)

        sess.add(Invite(firm=firm.id, investor=invitee.id))

        return comment.reply_wrap(message.modify_invite(invitee, firm))

    @req_user
    def setprivate(self, sess, comment, investor):
        if investor.firm == 0:
            return comment.reply_wrap(message.no_firm_failure_org)

        if investor.firm_role != "ceo":
            return comment.reply_wrap(message.not_ceo_org)

        firm = sess.query(Firm).\
            filter(Firm.id == investor.firm).\
            first()

        firm.private = True

        return comment.reply_wrap(message.setprivate_org)

    @req_user
    def setpublic(self, sess, comment, investor):
        if investor.firm == 0:
            return comment.reply_wrap(message.no_firm_failure_org)

        if investor.firm_role != "ceo":
            return comment.reply_wrap(message.not_ceo_org)

        firm = sess.query(Firm).\
            filter(Firm.id == investor.firm).\
            first()

        firm.private = False

        return comment.reply_wrap(message.setprivate_org)

    @req_user
    def upgrade(self, sess, comment, investor):
        if investor.firm == 0:
            return comment.reply_wrap(message.nofirm_failure_org)

        if investor.firm_role != "ceo":
            return comment.reply_wrap(message.not_ceo_org)

        firm = sess.query(Firm).\
            filter(Firm.id == investor.firm).\
            first()

        # level 1 = 4,000,000
        # level 2 = 16,000,000
        # level 3 = 64,000,000
        # etc.
        upgrade_cost = 4 ** (firm.rank + 1) * 1000000
        if firm.balance < upgrade_cost:
            return comment.reply_wrap(message.modify_upgrade_insufficient_funds_org(firm, upgrade_cost))

        firm.rank += 1
        firm.balance -= upgrade_cost

        max_members = max_members_for_rank(firm.rank)
        max_execs = max_execs_for_rank(firm.rank)

        return comment.reply_wrap(message.modify_upgrade(firm, max_members, max_execs))

def concat_names(investors):
    names = ["/u/" + i.name for i in investors]
    return ", ".join(names)

def max_members_for_rank(rank):
    # level 1 = 8
    # level 2 = 16
    # level 3 = 32
    # etc.
    return 2 ** (rank + 3)

def max_execs_for_rank(rank):
    # level 1 = 2
    # level 2 = 4
    # level 3 = 8
    # etc.
    return 2 ** (rank + 1)
