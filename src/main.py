import re
import math
import time
from queue import Queue
from threading import Thread, get_ident

# import sqlite3
import MySQLdb
import praw
from bottr.bot import AbstractCommentBot, BotQueueWorker

import config
import models
import message

STARTER = 1000
REDDIT = None


# Decorator to mark a commands that require a user
# Adds the investor after the comment when it calls the method (see broke)
def req_user(func):
    def wrapper(self, comment, *args):
        try:
            investor = self.investors[comment.author.fullname]
            return func(self, comment, investor, *args)
        except IndexError:
            return self.no_such_user(comment)
    return wrapper


# Monkey patch exception handling
def reply_wrap(self, body):
    if config.dry_run:
        print("[%s] Immitating reply %s" % (time.strftime("%d-%m-%Y %H:%M:%S"), body))
        return True

    try:
        return self.reply(body)
    except praw.exceptions.APIException:
        return False


praw.models.Comment.reply_wrap = reply_wrap


class CommentWorker(BotQueueWorker):
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

    def __init__(self, *args, **kwargs):
        global REDDIT

        super().__init__(target=self._process_comment, *args, **kwargs)
        print(self.commands)

        self.db = MySQLdb.connect(**config.dbconfig)

        self.regexes = [re.compile(x, re.MULTILINE | re.IGNORECASE)
                        for x in self.commands]
        self.reddit = REDDIT

        self.investments = models.Investments(self.db)
        self.investors = models.Investors(self.db)
        self.comments = models.Comments(self.db)
        self.submissions = models.Submissions(self.db)

    def stop(self):
        self.db.commit()
        self.db.close()
        super().stop()

    def _process_comment(self, comment: praw.models.Comment):
        if str(comment.author).lower().endswith("_bot"):
            return

        text = comment.body.lower()

        for reg in self.regexes:
            matches = reg.search(comment.body)
            if matches:
                try:
                    text = matches.group().split(" ")[0]
                    print("%s: %s" % (comment.author.fullname, text))

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
        user_cap = self.investors.total_coins()
        invest_cap = self.investments.invested_coins()
        active = len(self.investments)
        comment.reply_wrap(message.modify_market(active, user_cap, invest_cap))

    def create(self, comment):
        author = comment.author.fullname
        try:
            return self.investors[author]
        except IndexError:
            self.investors.append(author)
            comment.reply_wrap(message.modify_create(comment.author, STARTER))

    @req_user
    def invest(self, comment, investor, amount):
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
        author = comment.author.fullname
        balance = investor["balance"]
        new_balance = balance - amount

        if new_balance < 0:
            comment.reply_wrap(message.insuff_org)
            return

        # Sending a confirmation
        response = comment.reply_wrap(message.modify_invest(amount, upvotes,
                                                            new_balance))

        # Filling the database
        self.investments.append({
            "post": postID,
            "upvotes": upvotes,
            "comment": comment,
            "name": author,
            "amount": amount,
            "response": response
        })
        investor["balance"] = new_balance
        investor["active"] += 1

    @req_user
    def balance(self, comment, investor):
        comment.reply_wrap(message.modify_balance(investor["balance"]))

    @req_user
    def broke(self, comment, investor):
        active = investor["active"]
        balance = investor["balance"]

        if balance < 100:
            if active < 1:
                # Indeed, broke
                investor["balance"] = 100
                investor["active"] = 0
                broke = investor["broke"] + 1
                investor["broke"] = broke

                comment.reply_wrap(message.modify_broke(broke))
            else:
                # Still has investments
                comment.reply_wrap(message.modify_broke_active(active))
        else:
            # Still can invest
            comment.reply_wrap(message.modify_broke_money(balance))

    @req_user
    def active(self, comment, investor):
        comment.reply_wrap(message.modify_active(investor["active"]))

    def no_such_user(self, comment):
        comment.reply_wrap(message.no_account_org)


class CommentBot(AbstractCommentBot):
    def _process_comment(self, comment):
        # This code is never reached
        pass

    # Duplicate the whole code to change the worker... -.-
    def _listen_comments(self):
        # Collect comments in a queue
        comments_queue = Queue(maxsize=self._n_jobs * 4)
        threads = []  # type: List[BotQueueWorker]

        try:
            # Create n_jobs CommentsThreads
            for i in range(self._n_jobs):
                t = CommentWorker(name='CommentThread-t-{}'.format(i),
                                   jobs=comments_queue)
                t.start()
                threads.append(t)

            # Iterate over all comments in the comment stream
            for comment in self._reddit.subreddit('+'.join(self._subs)).stream.comments():
                # Check for stopping
                if self._stop:
                    self._do_stop(comments_queue, threads)
                    break

                comments_queue.put(comment)

            self.log.debug('Listen comments stopped')
        except Exception as e:
            # self._do_stop(comments_queue, threads)
            raise e


def calculate(new, old):
    """
    Investment return multiplier is detemined by a power function of the relative change in upvotes since the investment
    was made.
    Functional form: y = x^m ;
        y = multiplier,
        x = relative growth: (change in upvotes) / (upvotes at time of investment),
        m = scale factor: allow curtailing high-growth post returns to make the playing field a bit fairer
    """
    new = float(new)
    old = float(old)

    # Scale factor for multiplier
    scale_factor = 1 / float(3)

    # Calculate relative change
    if old != 0:
        rel_change = (new - old) / abs(old)
    # If starting upvotes was zero, avoid dividing by zero
    else:
        rel_change = new

    mult = pow((rel_change+1), scale_factor)

    return mult


def check_investments(reddit):
    db = MySQLdb.connect(**config.dbconfig)

    investments = models.Investments(db)
    investors = models.Investors(db)
    comments = models.Comments(db)
    submissions = models.Submissions(db)

    print("Starting checking investments...")
    while True:
        time.sleep(60)

        for row in investments.done():
            investor = investors[row.name]
            response = reddit.comment(id=row.response)

            # If comment is deleted, skip it
            try:
                reddit.comment(id=comments[row.comment])
            except:
                response.edit(message.deleted_comment_org)
                continue

            post = reddit.submission(row.post)
            upvotes_now = post.ups

            # Updating the investor's balance
            factor = calculate(upvotes_now, row.upvotes)
            balance = investor["balance"]
            new_balance = balance + (row.amount * factor)
            investor["balance"] = new_balance
            change = new_balance - balance

            # Updating the investor's variables
            investor["active"] -= 1
            investor["completed"] += 1

            # Marking the investment as done
            row.done = 1

            # Editing the comment as a confirmation
            text = response.body
            if factor > 1:
                response.edit(message.modify_invest_return(text, change))
                row.success = 1
            else:
                lost_memes = int(row.amount - (row.amount * factor))
                response.edit(message.modify_invest_lose(text, lost_memes))


def main():
    global REDDIT

    REDDIT = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)
    bot = CommentBot(REDDIT, config.subreddits, config.name, n_jobs=4)

    t = Thread(name="Investments", target=check_investments, args=[REDDIT]).start()
    bot.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        bot.stop()
        t.stop()


if __name__ == "__main__":
    main()
