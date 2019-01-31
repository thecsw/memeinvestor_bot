"""
datetime gives us access to current month
traceback flushes errors
logging is the general stdout for us

prawcore has the list of praw exceptions
"""
import datetime
import traceback
import logging
import time

import prawcore

logging.basicConfig(level=logging.INFO)

DEPLOY_DATE = time.strftime("%c")

def investment_duration_string(duration):
    """
    We may change the investment duration in the future
    and this function allows us to have agile strings
    depending on the duration from .env
    """
    hours = duration // 3600
    duration %= 3600
    minutes = duration // 60
    duration %= 60

    inv_string = ""
    if hours:
        inv_string += f"{hours} hour"
        if hours > 1:
            inv_string += "s"
        inv_string += " "
    if minutes:
        inv_string += f"{minutes} minute"
        if minutes > 1:
            inv_string += "s"
        inv_string += " "
    if duration:
        inv_string += f"{duration} second"
        if duration > 1:
            inv_string += "s"
        inv_string += " "

    return inv_string

def upvote_string():
    """
    We can make some funny replacements of upvotes
    depending on what month it is
    """
    return {
        10:"upd00ts",
    }.get(datetime.date.today().month, "upvotes")

def test_reddit_connection(reddit):
    """
    This function just tests connection to reddit
    Many things can happen:
     - Wrong credentials
     - Absolutly garbage credentials
     - No internet

    This function helps us to quickly check if we are online
    Return true on success and false on failure
    """
    try:
        reddit.user.me()
    except prawcore.exceptions.OAuthException as e_creds:
        traceback.print_exc()
        logging.error(e_creds)
        logging.critical("Invalid login credentials. Check il tuo .env!")
        logging.critical("Fatal error. Cannot continue or fix the problem. Bailing out...")
        return False
    except prawcore.exceptions.ResponseException as http_error:
        traceback.print_exc()
        logging.error(http_error)
        logging.critical("Received 401 HTTP response. Try checking il tuo .env!")
        logging.critical("Fatal error. Cannot continue or fix the problem. Bailing out...")
        return False
    return True
