# TODO: add docstrin here
import time
import logging
import traceback

from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker
import praw

import config
import utils
import formula
import message
from kill_handler import KillHandler
from models import Investment, Investor, Firm
from stopwatch import Stopwatch

logging.basicConfig(level=logging.INFO)

BALANCE_CAP = 1000*1000*1000*1000*1000*1000 # One quintillion MemeCoins

# TODO: add classes docstring
class EmptyResponse():
    def __init__(self):
        self.body = "[fake response body]"

    def edit_wrap(self, body):
        logging.info(" -- editing fake response")
        logging.info(body)

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

# TODO: rethink how to structure this main
# TODO: add docstring
def main():
    logging.info("Starting calculator...")
    logging.info("Sleeping for 8 seconds. Waiting for the database to turn on...")
    time.sleep(8)

    killhandler = KillHandler()

    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = sessionmaker(bind=engine)

    reddit = praw.Reddit(client_id=config.CLIENT_ID,
                         client_secret=config.CLIENT_SECRET,
                         username=config.USERNAME,
                         password=config.PASSWORD,
                         user_agent=config.USER_AGENT)

    # We will test our reddit connection here
    if not utils.test_reddit_connection(reddit):
        exit()

    praw.models.Comment.edit_wrap = edit_wrap

    stopwatch = Stopwatch()

    logging.info("Monitoring active investments...")

    while not killhandler.killed:
        sess = session_maker()

        then = int(time.time()) - config.INVESTMENT_DURATION
        investment = sess.query(Investment).\
            filter(Investment.done == 0).\
            filter(Investment.time < then).\
            order_by(Investment.time.asc()).\
            first()

        if not investment:
            # Nothing matured yet; wait a bit before trying again
            time.sleep(5)
            continue

        duration = stopwatch.measure()

        investor = sess.query(Investor).filter(Investor.name == investment.name).one()
        net_worth = sess.\
            query(func.sum(Investment.amount)).\
            filter(and_(Investment.name == investor.name, Investment.done == 0)).\
            scalar()\
            + investor.balance

        logging.info("New mature investment: %s", investment.comment)
        logging.info(" -- by %s", investor.name)

        # Retrieve the post the user invested in (lazily, no API call)
        post = reddit.submission(investment.post)

        # Retrieve the post's current upvote count (triggers an API call)
        upvotes_now = post.ups
        investment.final_upvotes = upvotes_now

        # Updating the investor's balance
        factor = formula.calculate(upvotes_now, investment.upvotes, net_worth)
        amount = investment.amount
        balance = investor.balance

        new_balance = int(balance + (amount * factor))
        change = new_balance - balance
        if investor.firm != 0:
            firm = sess.query(Firm).\
                filter(Firm.id == investor.firm).\
                first()
            original_profit = change - amount
            # Display user profit, then add firm profit
            profit = int(profit * ((100 - firm.tax) / 100))
        else:
            profit = change - amount
        percent_str = f"{int((profit/amount)*100)}%"

        # Updating the investor's variables
        investor.completed += 1

        # Retrieve the bot's original response (lazily, no API call)
        if investment.response != "0":
            response = reddit.comment(id=investment.response)
        else:
            response = EmptyResponse()

        firm_profit = 0
        if new_balance < BALANCE_CAP:
            # If investor is in a firm and he profits,
            # 15% goes to the firm
            firm_name = ''
            if investor.firm != 0 and profit >= 0:
                firm = sess.query(Firm).\
                    filter(Firm.id == investor.firm).\
                    first()
                firm_name = firm.name

                user_profit = int(original_profit * ((100 - firm.tax) / 100))
                investor.balance += user_profit + amount

                firm_profit = int(original_profit * (firm.tax / 100))
                firm.balance += firm_profit
            else:
                investor.balance = new_balance

            # Edit the bot's response (triggers an API call)
            if profit > 0:
                logging.info(" -- profited %s", profit)
            elif profit == 0:
                logging.info(" -- broke even")
            else:
                logging.info(" -- lost %s", profit)

            edited_response = message.modify_invest_return(investment.amount, investment.upvotes,
                                                           upvotes_now, change, profit,
                                                           percent_str, investor.balance)
            if investor.firm != 0:
                edited_response += message.modify_firm_tax(firm_profit, firm_name)

            response.edit_wrap(edited_response)
        else:
            # This investment pushed the investor's balance over the cap
            investor.balance = BALANCE_CAP

            # Edit the bot's response (triggers an API call)
            logging.info(" -- profited %s but got capped", profit)
            response.edit_wrap(message.modify_invest_capped(investment.amount, investment.upvotes,
                                                            upvotes_now, change, profit,
                                                            percent_str, investor.balance))

        investment.success = (profit > 0)
        investment.profit = profit
        investment.firm_profit = firm_profit
        investment.done = True

        sess.commit()

        # Measure how long processing took
        duration = stopwatch.measure()
        logging.info(" -- processed in %.2fs", duration)

        # Report the Reddit API call stats
        rem = int(reddit.auth.limits['remaining'])
        res = int(reddit.auth.limits['reset_timestamp'] - time.time())
        logging.info(" -- API calls remaining: %s, resetting in %.2fs", rem, res)

        sess.close()

if __name__ == "__main__":
    main()
