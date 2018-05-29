import re
import time
import logging
from queue import Queue
from threading import Thread

import MySQLdb
import MySQLdb.cursors
import _mysql_exceptions
import praw
from bottr.bot import AbstractCommentBot, BotQueueWorker, SubmissionBot

import config
import models
import message

logging.basicConfig(level=logging.INFO)

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
        logging.info("[%s] Immitating reply %s" % (time.strftime("%d-%m-%Y %H:%M:%S"), body))
        return True

    try:
        return self.reply(body)
    except praw.exceptions.APIException:
        return False


praw.models.Comment.reply_wrap = reply_wrap


class CommentWorker(BotQueueWorker):
    db = None
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

        while not self.db:
            try:
                self.db = MySQLdb.connect(cursorclass=MySQLdb.cursors.DictCursor, **config.dbconfig)
            except _mysql_exceptions.OperationalError:
                logging.warning("Waiting 10s for MySQL to go up...")
                time.sleep(10)

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
                    logging.info("%s: %s" % (comment.author.name, text))

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
        active = self.investments.active()
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


def main():
    global REDDIT

    REDDIT = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)
    bot = CommentBot(REDDIT, config.subreddits, config.name, n_jobs=4)
    bot.start()


if __name__ == "__main__":
    main()
