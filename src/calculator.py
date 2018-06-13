import time
import datetime
import logging
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import praw
from fastnumbers import fast_float

import config
import message
from models import Investment, Investor

logging.basicConfig(level=logging.INFO)


# Handles SIGTERM (15)
class KillHandler():
    killed=False
    
    def __init__(self):
        signal.signal(signal.SIGTERM, self.kill)
    def kill(self):
        killed=True

class EmptyResponse(object):
    body = ""

    def edit_wrap(*args, **kwargs):
        pass


def edit_wrap(self, body):
    if config.dry_run:
        return False

    try:
        return self.edit(body)
    except Exception as e:
        logging.error(e)
        return False


# @lru_cache(maxsize=10240)
def calculate(new, old):

    # Multiplier is detemined by a power function of the relative change in upvotes
    # since the investment was made.
    # Functional form: y = x^m ;
    #    y = multiplier,
    #    x = relative growth: (change in upvotes) / (upvotes at time of investment),
    #    m = scale factor: allow curtailing high-growth post returns to make the playing field a bit fairer

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

    # Investment must grow by more than a threshold amount to win. Decide if
    # investment was successful and whether you get anything back at all.
    win_threshold = 1.2
    if mult > win_threshold:
        investment_success = True
        return_money = True
    elif mult > 1:
        investment_success = False
        return_money = True
    else:
        investment_success = False
        return_money = False

    # Investor gains money only if investment was successful. If mult
    # was below win_threshold but above 1 return factor is ratio of
    # difference between mult and 1 and difference between win_threshold and 1.
    # Otherwise, if mult was 1 or lower, get back nothing.
    if investment_success:
        factor = mult
    elif return_money:
        factor = (mult - 1)/(win_threshold - 1)
    else:
        factor = 0

    return factor


def main():
    logging.info("Starting calculator")

    engine = create_engine(config.db)
    sm = sessionmaker(bind=engine)
    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)

    praw.models.Comment.edit_wrap = edit_wrap

    logging.info("Monitoring active investments...")

    while True:
        sess = sm()

        then = int(time.time()) - 14400
        q = sess.query(Investment).filter(Investment.done == 0).filter(Investment.time < then)
        
        for investment in q.limit(10).all():
            investor_q = sess.query(Investor).filter(Investor.name == investment.name)
            investor = investor_q.first()

            if not investor:
                continue

            logging.info(f"Processing mature investment by {investor.name}")

            if investment.response != "0":
                response = reddit.comment(id=investment.response)
            else:
                response = EmptyResponse()

            # If comment is deleted, skip it
            try:
                reddit.comment(id=investment.comment)
            except:
                response.edit_wrap(message.deleted_comment_org)
                continue

            post = reddit.submission(investment.post)
            upvotes_now = post.ups

            # Updating the investor's balance
            factor = calculate(upvotes_now, investment.upvotes)
            amount = investment.amount
            balance = investor.balance

            new_balance = int(balance + (amount * factor))
            change = new_balance - balance

            # Updating the investor's variables
            update = {
                Investor.completed: investor.completed + 1,
                Investor.balance: new_balance,
            }
            investor_q.update(update, synchronize_session=False)

            # Editing the comment as a confirmation
            text = response.body
            if change > amount:
                logging.info("%s won %d" % (investor.name, change))
                response.edit_wrap(message.modify_invest_return(text, change, new_balance))
            elif change == amount:
                logging.info("%s broke even and got back %d" % (investor.name, change))
                response.edit_wrap(message.modify_invest_break_even(text, change, new_balance))
            else:
                lost_memes = int( amount - change )
                logging.info("%s lost %d" % (investor.name, lost_memes))
                response.edit_wrap(message.modify_invest_lose(text, lost_memes, new_balance))

            sess.query(Investment).\
                filter(Investment.id == investment.id).\
                update({
                    Investment.success: change > amount,
                    Investment.done: True
                }, synchronize_session=False)
            
            sess.commit()
            
        sess.close()
        if killhandler.killed==True:
            print ("Exited \"calculator\" gracefully")
            break


if __name__ == "__main__":
    killhandler=KillHandler()
    while True:
        try:
            main()
        except Exception as e:
            logging.error(e)
            time.sleep(10)
