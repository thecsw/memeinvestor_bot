import re
import math
import time
from queue import Queue
from threading import Thread, get_ident

# import sqlite3
import MySQLdb
import _mysql_exceptions
import praw
from bottr.bot import AbstractCommentBot, BotQueueWorker, SubmissionBot

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
            investor = self.investors[comment.author.name]
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
praw.models.Submission.reply_wrap = reply_wrap


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

    def stop(self):
        self.db.commit()
        self.db.close()
        super().stop()

    def _process_comment(self, comment: praw.models.Comment):
        if str(comment.author).lower().endswith("_bot"):
            return

        if comment in self.comments:
            return
        self.comments.append(comment)

        text = comment.body.lower()

        for reg in self.regexes:
            matches = reg.search(comment.body)
            if matches:
                try:
                    text = matches.group().split(" ")[0]
                    print("%s: %s" % (comment.author.name, text))

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
        author = comment.author.name
        try:
            return self.investors[author]
        except IndexError:
            self.investors.append(author)
            comment.reply_wrap(message.modify_create(comment.author, STARTER))

    @req_user
    def invest(self, comment, investor, amount):
        # Post related vars
        if not investor:
            return

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
        author = comment.author.name
        balance = investor["balance"]
        new_balance = balance - amount

        if new_balance < 0:
            comment.reply_wrap(message.insuff_org)
            return

        # Sending a confirmation
        response = comment.reply_wrap(message.modify_invest(amount, upvotes,
                                                            new_balance))
        self.investments[None] = {
            "post": postID,
            "upvotes": upvotes,
            "comment": comment,
            "name": author,
            "amount": amount,
            "response": response
        }
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

    print("Starting checking investments...")
    while True:
        time.sleep(60)

        for row in investments.done():
            investor = investors[row[4]]
            response = reddit.comment(id=row[8])

            # If comment is deleted, skip it
            try:
                reddit.comment(id=comments[row[3]])
            except:
                response.edit(message.deleted_comment_org)
                continue

            post = reddit.submission(row[1])
            upvotes_now = post.ups

            # Updating the investor's balance
            factor = calculate(upvotes_now, row[2])
            balance = investor["balance"]
            new_balance = balance + (row[5] * factor)
            investor["balance"] = new_balance
            change = new_balance - balance

            # Updating the investor's variables
            investor["active"] -= 1
            investor["completed"] += 1

            # Marking the investment as done
            investments[row[0]]["done"] = 1

            # Editing the comment as a confirmation
            text = response.body
            if factor > 1:
                response.edit(message.modify_invest_return(text, change))
                investments[row[0]]["success"] = 1
            else:
                lost_memes = int(row[5] - (row[5] * factor))
                response.edit(message.modify_invest_lose(text, lost_memes))


def submission_bot(submission, subsdb):
    if submission not in subsdb:
        print("New submission: %s" % submission)
        subsdb.append(submission)
        submission.reply_wrap(message.invest_place_here)


def main():
    global REDDIT

    REDDIT = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)
    bot = CommentBot(REDDIT, config.subreddits, config.name, n_jobs=4)

    db = MySQLdb.connect(**config.dbconfig)
    submissions = models.Submissions(db)
    subbot = SubmissionBot(REDDIT, subreddits=config.subreddits,
                           func_submission=submission_bot,
                           func_submission_args=[submissions], n_jobs=1)

    inv = Thread(name="Investments", target=check_investments, args=[REDDIT]).start()
    bot.start()
    subbot.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        bot.stop()
        inv.stop()
        subbot.stop()


if __name__ == "__main__":
    main()
