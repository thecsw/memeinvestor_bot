import time
import datetime
import logging
import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import praw
import prawcore

import config
import formula
import message
from kill_handler import KillHandler
from models import Investment, Investor
from stopwatch import Stopwatch

logging.basicConfig(level=logging.INFO)

BalanceCap = 1000*1000*1000*1000*1000*1000 # One quintillion MemeCoins

class EmptyResponse(object):
    def __init__(self):
        self.body = "[fake response body]"

    def edit_wrap(self, body):
        logging.info(" -- editing fake response")
        logging.info(body)

def edit_wrap(self, body):
    logging.info(" -- editing response")

    if config.post_to_reddit:
        try:
            return self.edit(body)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            return False
    else:
        logging.info(body)
        return False

def main():
    logging.info("Starting calculator")

    killhandler = KillHandler()

    engine = create_engine(config.db, pool_recycle=60)
    sm = sessionmaker(bind=engine)
    
    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)

    praw.models.Comment.edit_wrap = edit_wrap

    stopwatch = Stopwatch()

    logging.info("Monitoring active investments...")

    while not killhandler.killed:
        try:
            sess = sm()

            then = int(time.time()) - config.investment_duration
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

            logging.info(f"New mature investment: {investment.comment}")
            logging.info(f" -- by {investor.name}")

            # Retrieve the post the user invested in (lazily, no API call)
            post = reddit.submission(investment.post)

            # Retrieve the post's current upvote count (triggers an API call)
            upvotes_now = post.ups
            investment.final_upvotes = upvotes_now

            # Updating the investor's balance
            factor = formula.calculate(upvotes_now, investment.upvotes)
            amount = investment.amount
            balance = investor.balance

            new_balance = int(balance + (amount * factor))
            change = new_balance - balance
            profit = change - amount
            percent_str = f"{int((profit/amount)*100)}%"

            # Updating the investor's variables
            investor.completed += 1

            # Retrieve the bot's original response (lazily, no API call)
            if investment.response != "0":
                response = reddit.comment(id=investment.response)
            else:
                response = EmptyResponse()

            if new_balance < BalanceCap:
                investor.balance = new_balance

                # Edit the bot's response (triggers an API call)
                if profit > 0:
                    logging.info(f" -- profited {profit}")
                elif profit == 0:
                    logging.info(f" -- broke even")
                else:
                    logging.info(f" -- lost {profit}")
                response.edit_wrap(message.modify_invest_return(investment.amount, investment.upvotes, upvotes_now, change, profit, percent_str, investor.balance))
            else:
                # This investment pushed the investor's balance over the cap
                investor.balance = BalanceCap

                # Edit the bot's response (triggers an API call)
                logging.info(f" -- profited {profit} but got capped")
                response.edit_wrap(message.modify_invest_capped(investment.amount, investment.upvotes, upvotes_now, change, profit, percent_str, investor.balance))

            investment.success = (profit > 0)
            investment.profit = profit
            investment.done = True

            sess.commit()

            # Measure how long processing took
            duration = stopwatch.measure()
            logging.info(f" -- processed in {duration:5.2f}s")

            # Report the Reddit API call stats
            rem = int(reddit.auth.limits['remaining'])
            res = int(reddit.auth.limits['reset_timestamp'] - time.time())
            logging.info(f" -- API calls remaining: {rem:3d}, resetting in {res:3d}s")

        except prawcore.exceptions.OAuthException as e_creds:
            traceback.print_exc()
            logging.error(e_creds)
            logging.critical("Invalid login credentials. Check your .env!")
            logging.critical("Fatal error. Cannot continue or fix the problem. Bailing out...")
            exit()
    
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            time.sleep(10)
        finally:
            sess.close()

if __name__ == "__main__":
    main()
