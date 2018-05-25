import re
import math
import time
from threading import Thread

import praw
from bottr.bot import AbstractCommentBot

import config
import database
import message

STARTER = 1000


# Decorator to mark a commands that require a user
def req_user(func):
    def wrapper(self, comment, *args):
        if database.find_investor(comment.author.fullname):
            return func(self, comment, *args)
        return self.no_such_user(comment)
    return wrapper


# Monkey patch exception handling
def reply_wrap(self, body):
    try:
        return self.reply(body)
    except praw.exceptions.APIException:
        return False


praw.models.Comment.reply_wrap = reply_wrap


class CommentParser(AbstractCommentBot):
    commands = [
        r"!active",
        r"!balance",
        r"!broke",
        r"!create",
        r"!help",
        r"!ignore",
        r"!invest (\d+)",
        r"!market",
    ]

    def __init__(self, reddit: praw.Reddit, subreddits, name, n_jobs = 4):
        super().__init__(reddit, subreddits, name, n_jobs)
        print(self.commands)
        self.regexes = [re.compile(x, re.MULTILINE | re.IGNORECASE) for x in self.commands]
        self.reddit = reddit

    def _process_comment(self, comment: praw.models.Comment):
        if str(comment.author).lower().endswith("_bot"):
            return

        text = comment.body.lower()

        for reg in self.regexes:
            matches = reg.search(comment.body)
            if matches:
                try:
                    print("%s: %s" % (comment.author, matches.group()))
                    text = matches.group().split(" ")[0]

                    try:
                        getattr(self, text[1:])(comment, *matches.groups())
                    except IndexError:
                        getattr(self, text[1:])(comment)
                except AttributeError:
                    pass

    def ignore(self, comment):
        pass

    def help(self, comment):
        comment.reply_wrap(message.help_org)

    def market(self, comment):
        user_cap = database.market_user_coins()
        invest_cap = database.market_invest_coins()
        active_number = database.market_count_investments()
        comment.reply_wrap(message.modify_market(active_number, user_cap, invest_cap))

    def create(self, comment):
        author = comment.author.fullname
        if not database.find_investor(author):
            database.investor_insert(author, STARTER)
            comment.reply_wrap(message.modify_create(comment.author, STARTER))

    @req_user
    def invest(self, comment, amount):
        # Post related vars
        post = self.reddit.submission(comment.submission)
        postID = post.id
        upvotes = post.ups

        try:
            amount = int(amount)
        except ValueError:
            return

        if amount < 100:
            comment.reply_wrap(message.min_invest_org)
            return

        # Balance operations
        balance = database.investor_get_balance(comment.author.fullname)
        active = database.investor_get_active(comment.author.fullname)
        new_balance = balance - amount

        if new_balance < 0:
            comment.reply_wrap(message.insuff_org)
            return

        active += 1

        # Sending a confirmation
        response = comment.reply_wrap(message.modify_invest(amount, upvotes,
                                                       new_balance))

        # Filling the database
        database.investment_insert(postID, upvotes, comment, comment.author.fullname,
                                   time.time(), amount, response)
        database.investor_update_balance(comment.author.fullname, new_balance)
        database.investor_update_active(comment.author.fullname, active)

    @req_user
    def balance(self, comment):
        balance_amount = database.investor_get_balance(comment.author.fullname)
        comment.reply_wrap(message.modify_balance(balance_amount))

    @req_user
    def broke(self, comment):
        balance_amount = database.investor_get_balance(comment.author.fullname)
        active_number = database.investor_get_active(comment.author.fullname)

        if balance_amount < 100:
            if active_number < 1:
                # Indeed, broke
                database.investor_update_balance(comment.author.fullname, 100)
                database.investor_update_active(comment.author.fullname, 0)
                broke_times = database.investor_get_broke(comment.author.fullname)
                broke_times += 1
                database.investor_update_broke(comment.author.fullname, broke_times)

                comment.reply_wrap(message.modify_broke(broke_times))
            else:
                # Still has investments
                comment.reply_wrap(message.modify_broke_active(active_number))
        else:
            # Still can invest
            comment.reply_wrap(message.modify_broke_money(balance_amount))

    @req_user
    def active(self, comment):
        active = database.investor_get_active(comment.author.fullname)
        comment.reply_wrap(message.modify_active(active))

    def no_such_user(self, comment):
        comment.reply_wrap(message.no_account_org).lock()


def calculate(new, old):
    new = int(float(new))
    old = int(float(old))
    du = new - old

    """
    Investment return multiplier was previously determined with a block of if statements.
    Performed a linear fit to a log-log plot of mutliplier vs upvotes based on the original values for the if block.
    Used the gradient/intercept to generate a power function that approximates (and extends) the original mutliplier
    calculation to all upvote values.

    Functional form: y = (10^c)x^m ;
        y = multiplier,
        x = du (change in upvotes),
        m = gradient of linear fit to log-log plot (= 0.2527),
        c = intercept of linear fit to log-log plot (= -0.7603).
    """
    #Allow custom upper du limit to cap maximum investment profit multiplier (set as desired)
    success_cap = 750000


    if (du >= success_cap):
        capped_mult = 0.17366 * math.pow(success_cap, 0.2527)
        return capped_mult

    #Safeguard: if du is -ve function cannot be evaluated and mult remains zero.
    mult = 0
    if (du >= 0):
        mult = 0.17366 * math.pow(du, 0.2527)

    return mult


def check_investments(reddit):
    print("Starting checking investments...")
    while True:
        time.sleep(60)
        done_ids = database.investment_find_done()
        for id_number in done_ids:
            # I know that everything can be compacted in a tuple
            # This way it is more understandable
            name = database.investment_get_name(id_number)
            postID = database.investment_get_post(id_number)
            upvotes_old = database.investment_get_upvotes(id_number)
            amount = database.investment_get_amount(id_number)
            responseID = database.investment_get_response(id_number)
            response = reddit.comment(id=responseID)

            # If comment is deleted, skip it
            try:
                commentID = database.investment_get_comment(id_number)
                comment = reddit.comment(id=commentID)
            except:
                response.edit(message.deleted_comment_org)
                continue

            post = reddit.submission(postID)
            upvotes_now = post.ups

            # Updating the investor's balance
            factor = calculate(upvotes_now, upvotes_old)
            balance = database.investor_get_balance(name)
            new_balance = int(balance + (amount * factor))
            database.investor_update_balance(name, new_balance)
            change = new_balance - balance

            # Updating the investor's variables
            active = database.investor_get_active(name)
            active -= 1
            database.investor_update_active(name, active)

            completed = database.investor_get_completed(name)
            completed += 1
            database.investor_update_completed(name, completed)

            # Marking the investment as done
            database.investment_update_done(id_number)

            # Editing the comment as a confirmation
            text = response.body
            if (factor > 1):
                response.edit(message.modify_invest_return(text, change))
                database.investment_update_success(id_number)
            else:
                lost_memes = int(amount - (amount * factor))
                response.edit(message.modify_invest_lose(text, lost_memes))

if __name__ == "__main__":
    database.init_investors()
    print("Investors table created!")
    database.init_investments()
    print("Investments table created!")
    database.init_comments()
    print("Comments table created!")
    database.init_submissions()
    print("Submissions table created!")

    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)
    bot = CommentParser(reddit, config.subreddits, config.name, n_jobs=1)

    t = Thread(name="Investments", target=check_investments, args=[reddit]).start()
    bot.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        bot.stop()
        t.stop()
