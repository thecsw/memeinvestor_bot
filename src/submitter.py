import time
import logging
import traceback

import praw
import prawcore

import config
import message
from kill_handler import KillHandler
from main import reply_wrap
from stopwatch import Stopwatch

praw.models.Submission.reply_wrap = reply_wrap
logging.basicConfig(level=logging.INFO)

def main():
    killhandler = KillHandler()

    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         username=config.username,
                         password=config.password,
                         user_agent=config.user_agent)

    logging.info("Starting checking submissions...")

    stopwatch = Stopwatch()

    while not killhandler.killed:
        try:
            for submission in reddit.subreddit('+'.join(config.subreddits)).stream.submissions(skip_existing=True):
                duration = stopwatch.measure()

                logging.info(f"New submission: {submission}")
                logging.info(f" -- retrieved in {duration:5.2f}s")

                # We don't need to post a sticky on stickied posts
                if submission.stickied:
                    logging.info(f" -- skipping (stickied)")
                    continue

                # Post a comment to let people know where to invest
                bot_reply = submission.reply_wrap(message.invest_place_here)

                # Sticky the comment
                if config.is_moderator:
                    bot_reply.mod.distinguish(how='yes', sticky=True)

                # Measure how long processing took
                duration = stopwatch.measure()
                logging.info(f" -- processed in {duration:5.2f}s")

                if killhandler.killed:
                    logging.info("Termination signal received - exiting")
                    break

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

if __name__ == "__main__":
    main()
