import time
import logging
from functools import lru_cache

import MySQLdb
import praw
from bottr.bot import AbstractCommentBot, BotQueueWorker, SubmissionBot
from fastnumbers import fast_float

import config
import message
import models

logging.basicConfig(level=logging.INFO)


class EmptyResponse(object):
    body = ""

    def edit(*args, **kwargs):
        pass


@lru_cache(maxsize=10240)
def calculate(new, old):
    """
    Investment return multiplier is detemined by a power function of the relative change in upvotes since the investment
    was made.
    Functional form: y = x^m ;
        y = multiplier,
        x = relative growth: (change in upvotes) / (upvotes at time of investment),
        m = scale factor: allow curtailing high-growth post returns to make the playing field a bit fairer
    """

    new = fast_float(new)
    old = fast_float(old)

    # Scale factor for multiplier
    scale_factor = 1 / fast_float(3)

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

    logging.info("Starting checking investments...")
    if config.dry_run:
        praw.models.Comment.edit = logging.info

    while True:
        for row in investments.done():
            investor = investors[row[4]]

            if not investor:
                continue

            if row[8] != "0":
                response = reddit.comment(id=row[8])
            else:
                response = EmptyResponse()

            # If comment is deleted, skip it
            try:
                reddit.comment(id=row[3])
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
                investments[row[0]]["success"] = 1
                logging.info("%s won %d memecoins!" % (investor, change))
                response.edit(message.modify_invest_return(text, change))
            else:
                lost_memes = int(row[5] - (row[5] * factor))
                logging.info("%s lost %d memecoins..." % (investor, lost_memes))
                response.edit(message.modify_invest_lose(text, lost_memes))

        time.sleep(60)

def main():
    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)

    check_investments(reddit)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error(e)
            time.sleep(10)
