"""
 __  __                     ___                     _             
|  \/  | ___ _ __ ___   ___|_ _|_ ____   _____  ___| |_ ___  _ __ 
| |\/| |/ _ \ '_ ` _ \ / _ \| || '_ \ \ / / _ \/ __| __/ _ \| '__|
| |  | |  __/ | | | | |  __/| || | | \ V /  __/\__ \ || (_) | |   
|_|  |_|\___|_| |_| |_|\___|___|_| |_|\_/ \___||___/\__\___/|_|   
                                                                  
"""

# Standard scripts
import time
from threading import Thread

# Third-party library
import praw

# Our own scripts and files
import config
import message
import database

# Reddit instance initialization
reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     username=config.username,
                     password=config.password,
                     user_agent=config.user_agent)

# Subreddit initialization
subreddit_name = "pewds_test"
subreddit = reddit.subreddit(subreddit_name)
starter = 1000

# Commands that require an account!
commands = ["!invest",
            "!broke",
            "!balance",
            "!active"]

database.data_init()

def create(comment, author):
    database.investor_insert(author, starter)
    comment.reply(message.modify_create(author, starter))

def invest(comment, author):

    # Post related vars
    post = reddit.submission(comment.submission)
    postID = post.id
    upvotes = post.ups

    # UNIX timestamp
    unix = time.time() 

    # The invest amount, if fails, return False
    text = comment.body.lower()
    invest_string = text.replace("!invest", "").replace(" ", "")
    try:
        invest_amount = int(float(invest_string))
    except ValueError:
        return False
    if (invest_amount < 100):
        comment.reply(message.min_invest_org)
        return False
    
    # Balance operations
    balance = database.investor_get_balance(author)
    active = database.investor_get_active(author)
    new_balance = balance - invest_amount

    if (new_balance < 0):
        comment.reply(message.insuff_org)
        return False

    active += 1

    # Filling the database
    database.investment_insert(postID, upvotes, comment, author, invest_amount, unix)
    database.investor_update_balance(author, new_balance)
    database.investor_update_active(author, active)

    # Sending a confirmation
    comment.reply(message.modify_invest(invest_amount, upvotes, new_balance))
    
def balance(comment, author):
    balance_amount = database.investor_get_balance(author)
    comment.reply(message.modify_balance(balance_amount))

def activity(comment, author):
    active = database.investor_get_active(author)
    comment.reply(message.modify_active(active))

def broke(comment, author):
    balance_amount = database.investor_get_balance(author)
    active_number = database.investor_get_active(author)

    if (balance_amount < 100):
        if (active_number < 1):
            # Indeed, broke
            database.investor_update_balance(author, 100)
            database.investor_update_active(author, 0)
            comment.reply(message.broke_org)
        else:
            # Still has investments
            comment.reply(message.modify_broke_active(active_number))
    else:
        # Still can invest
        comment.reply(message.modify_broke_money(balance_amount))

def market(comment):
    user_cap = database.market_user_coins()
    invest_cap = database.market_invest_coins()
    active_number = database.market_count_investments()
    comment.reply(message.modify_market(active_number, user_cap, invest_cap))

def comment_thread():
    for comment in subreddit.stream.comments():
        author = comment.author.name.lower()
        text = comment.body.lower()
        
        checked = database.find_comment(comment)
        if (checked):
            continue
        
        database.log_comment(comment)

        # We don't serve bots
        if ("_bot" in text):
            continue

        if ("!ignore" in text):
            continue
        
        if ("!help" in text):
            comment.reply(message.help_org)
            continue
        
        if ("!market" in text):
            market(comment)
            continue
        
        exist = database.find_investor(author)
        
        if (("!create" in text) and (not exist)):
            create(comment, author)
            continue
        
        command_present = 0
        for comm in commands:
            if comm in text:
                command_present = 1
                
        if ((not exist) and (command_present)):
            comment.reply(message.no_account_org)
            continue
                
        if ("!invest" in text):
            invest(comment, author)
            continue
                
        if ("!balance" in text):
            balance(comment, author)
            continue
                
        if ("!active" in text):
            activity(comment, author)
            continue

def check_investments():
    
        
def threads():
    Thread(name="Comments", target=comment_thread).start()
