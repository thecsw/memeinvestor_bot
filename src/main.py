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
import sqlite3
import math

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
subreddit_name = "memeinvestor_test"
subreddit = reddit.subreddit(subreddit_name)

# Starter money
starter = 1000

# Commands that require an account!
commands = ["!invest",
            "!broke",
            "!balance",
            "!active"]

database.init_investors()
database.init_investments()
database.init_comments()

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

    # Sending a confirmation
    response = comment.reply(message.modify_invest(invest_amount, upvotes, new_balance))

    # Filling the database
    database.investment_insert(postID, upvotes, comment, author, invest_amount, unix, response)
    database.investor_update_balance(author, new_balance)
    database.investor_update_active(author, active)
    
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

        print("{}\n{}\n".format(author, text))
        
        # We don't serve bots
        if ("_bot" in author):
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

        if ("!broke" in text):
            broke(comment, author)
            continue
        
        if ("!active" in text):
            activity(comment, author)
            continue

# This method is taken from old investor.py
def calculate(new, old):
    new = int(float(new))
    old = int(float(old))
    du = new - old
    
    """
    Investment return multiplier was previously determined with a block of if statements.
    Performed a linear fit to a log-log plot of mutliplier vs upvotes based on the original values for the if block.
    Used the gradient/intercept to generate a power function that approximates (and extends) the original mutliplier
    calculation to all upvote values.
    
    Functional form: y = (10^c)x^m ;
        y = multiplier,
        x = du (change in upvotes),
        m = gradient of linear fit to log-log plot (= 0.2527),
        c = intercept of linear fit to log-log plot (= -0.7603).
    """
    #Allow custom upper du limit to cap maximum investment profit multiplier (set as desired)
    success_cap = 750000
    
    if (du >= success_cap):
        capped_mult = 0.17366 * math.pow(success_cap, 0.2527)
        return capped_mult
      
    #Safeguard: if du is negative, function cannot be evaluated and mult remains zero.
    mult = 0
    if (du >= 0):
       mult = 0.17366 * math.pow(du, 0.2527)

    # We are kind
    if (mult < 0.95):
        return 0
    else:
        return mult

def check_investments():
    while True:
        time.sleep(1)
        done_ids = database.investment_find_done()
        print(len(done_ids))
        for id_number in done_ids:
            # I know that everything can be compacted in a tuple
            # This way it is more understandable
            name = database.investment_get_name(id_number)
            postID = database.investment_get_post(id_number)
            upvotes_old = database.investment_get_upvotes(id_number)
            amount = database.investment_get_amount(id_number)
            responseID = database.investment_get_response(id_number)
            response = reddit.comment(id=responseID)
            
            # If comment is deleted, skip it
            try:
                commentID = database.investment_get_comment(id_number)
                comment = reddit.comment(id=commentID)
            except:
                response.edit(message.deleted_comment_org)
                continue
            
            post = reddit.submission(postID)
            upvotes_now = post.ups
            
            # Updating the investor's balance
            factor = calculate(upvotes_now, upvotes_old)
            balance = database.investor_get_balance(name)
            new_balance = balance + (amount * factor)
            database.investor_update_balance(name, new_balance)
            change = new_balance - balance
            
            # Updating the investor's variables
            active = database.investor_get_active(name)
            active -= 1
            database.investor_update_active(name, active)
            
            completed = database.investor_get_completed(name)
            completed += 1
            database.investor_update_completed(name, completed)
            
            # Marking the investment as done
            database.investment_update_done(id_number)
            
            # Editing the comment as a confirmation
            text = response.body
            if (factor > 0):
                response.edit(message.modify_invest_return(text, change))
            else:
                response.edit(message.modify_invest_lose(text))    
        
def threads():
    Thread(name="Comments", target=comment_thread).start()
    Thread(name="Investments", target=check_investments).start()

if __name__ == "__main__":
    threads()
