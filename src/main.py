
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
subreddit_name = "memeeconomy"
subreddit = reddit.subreddit(subreddit_name)

# Starter money
starter = 1000

# Commands that require an account!
commands = ["!invest",
            "!broke",
            "!balance",
            "!active"]

# Database initialization
database.init_investors()
print("Investors table created!")
database.init_investments()
print("Investments table created!")
database.init_comments()
print("Comments table created!")
database.init_submissions()
print("Submissions table created!")

def send_reply(comment, string):
    # We already check if comments exist or not
    # But one time, one comment got through the
    # deleted comment validation and then in a
    # fraction of a second got deleted and raised
    # an exception. To be safe, I added just a try
    # operator
    try:
        comment.reply(string)
    except:
        return False
    return True

def create(comment, author):
    database.investor_insert(author, starter)
    send_reply(comment, message.modify_create(author, starter))
    
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
        send_reply(comment, comment,message.min_invest_org)
        return False
    
    # Balance operations
    balance = database.investor_get_balance(author)
    active = database.investor_get_active(author)
    new_balance = balance - invest_amount

    if (new_balance < 0):
        send_reply(comment, message.insuff_org)
        return False

    active += 1

    # Sending a confirmation
    response = send_reply(comment, message.modify_invest(invest_amount, upvotes, new_balance))

    # Filling the database
    database.investment_insert(post, upvotes, comment, author, invest_amount, unix, response)
    database.investor_update_balance(author, new_balance)
    database.investor_update_active(author, active)
    
def balance(comment, author):
    balance_amount = database.investor_get_balance(author)
    send_reply(comment, message.modify_balance(balance_amount))

def activity(comment, author):
    active = database.investor_get_active(author)
    send_reply(comment, message.modify_active(active))

def broke(comment, author):
    balance_amount = database.investor_get_balance(author)
    active_number = database.investor_get_active(author)

    if (balance_amount < 100):
        if (active_number < 1):
            # Indeed, broke
            database.investor_update_balance(author, 100)
            database.investor_update_active(author, 0)
            broke_times = database.investor_get_broke(author)
            broke_times += 1
            database.investor_update_broke(author, broke_times)
            # Sure, you can do it like
            # database.investor_get_broke(author, database.investor_get_broke(author) + 1)
            # But it is way to messy, we are for the code understandability
            
            send_reply(comment, message.modify_broke(broke_times))
        else:
            # Still has investments
            send_reply(comment, message.modify_broke_active(active_number))
    else:
        # Still can invest
        send_reply(comment, message.modify_broke_money(balance_amount))

def market(comment):
    user_cap = database.market_user_coins()
    invest_cap = database.market_invest_coins()
    active_number = database.market_count_investments()
    send_reply(comment, message.modify_market(active_number, user_cap, invest_cap))

def comment_thread():
    print("Started the comment_thread()...")
    for comment in subreddit.stream.comments():

        author = comment.author.name.lower()
        text = comment.body.lower()
        checked = database.find_comment(comment)
        if (checked):
            continue     
        database.log_comment(comment)

        submission = reddit.submission(comment.submission)

        # The thread is locked
        if (submission.locked):
            continue

        # If the comment is deleted
        if (not comment.banned_by == None):
            continue

 
        # We don't serve bots
        if ("_bot" in author):
            continue

        exist = database.find_investor(author)

        print(f"Comment ID: {comment.id}\n\tAuthor: {author}\n\tText: {text}\n\tExist?: {exist}\n\tPost Locked?: {submission.locked}\n")
        
        if ("!ignore" in text):
            continue
        
        if ("!help" in text):
            send_reply(comment, message.help_org)
            continue
        
        if ("!market" in text):
            market(comment)
            continue
                
        if (("!create" in text) and (not exist)):
            create(comment, author)
            continue
        
        command_present = 0
        for comm in commands:
            if comm in text:
                command_present = 1
                
        if ((not exist) and (command_present)):
            send_reply(comment, message.no_account_org)
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
# Thanks to jimbobur for adding this feature.
def calculate(new, old):
    new = int(float(new))
    old = int(float(old))
    du = new - old
    
    """
    Investment return multiplier is detemined by a power function of the change in upvotes since the investment was made.
    The coefficients of this function were originally set to emulate the old if-else block method for determining 
    investment return, but have now been changed to set the break-even point at +500 upvotes since the investment was made.
    Functional form: y = A*x^m ;
        y = multiplier,
        x = du (change in upvotes),
        A = 0.17366,
        m = 0.2818 (break even at ~500 upvotes).
    """
    #Set constants to define function
    A_mult=0.17366
    m_mult=0.2818

    #Allow custom upper du limit to cap maximum investment profit multiplier (set as desired)
    success_cap = 750000
    
    if (du >= success_cap):
        capped_mult = A_mult * math.pow(success_cap, m_mult)
        return capped_mult

    #Safeguard: if du is -ve function cannot be evaluated and mult remains zero.
    mult = 0
    if (du >= 0):
        mult = A_mult * math.pow(du, m_mult)

    return mult

def check_investments():
    print("Starting checking investments...")
    while True:
        time.sleep(60)
        done_ids = database.investment_find_done()
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
            new_balance = int(balance + (amount * factor))
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
            if (factor > 1):
                response.edit(message.modify_invest_return(text, change))
                database.investment_update_success(id_number)
            else:
                lost_memes = int(amount - (amount * factor))
                response.edit(message.modify_invest_lose(text, lost_memes))

def submission_thread():
    for submission in subreddit.stream.submissions():
        checked = database.find_submission(submission)
        if (checked):
            continue
        database.log_submission(submission)

        commentID = submission.reply(message.invest_place_here)

        # Making the comment sticky
        commentID.mod.distinguish(how='yes', sticky=True)
        
def threads():
    Thread(name="Comments", target=comment_thread).start()
    Thread(name="Investments", target=check_investments).start()

if __name__ == "__main__":
    threads()
