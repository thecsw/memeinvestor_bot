
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
from investor import *
import message
import utils

# Reddit instance initialization
reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     username=config.username,
                     password=config.password,
                     user_agent=config.user_agent)

# Subreddit initialization
subreddit_name = "MemeEconomy"
subreddit = reddit.subreddit(subreddit_name)

# A list of available commands:
commands = ["!create", "!invest", "!balance", "!help", "!broke"]

# The amount of MemeCoins given by default
starter = 1000

# Data folder
data_folder = "./data/"

# File to store all investors
investors_file = "investors.txt"

# File to store all awaiting investments
awaiting_file = "awaiting.txt"

# File to store all done investments
done_file = "done.txt"

# File to store checked comments
checked_file = "checked_comments.txt"

# DEBUG mode
# In the debug mode, instead of sending replies
# with praw, it just prints everything on tty
debug = 0

# Dictionary of all the investors
users = utils.read_investors(data_folder + investors_file)

print(users)

# Array to store done and awaiting investments
done = utils.read_investments(data_folder + done_file)
awaiting = utils.read_investments(data_folder + awaiting_file)

# Array to store IDs of parsed comment, so we won't parse the same
# comment multiple times
checked_comments = utils.read_array(data_folder + checked_file)

def save_data():
    global users, awaiting, done
    utils.write_investors(data_folder + investors_file, users)
    utils.write_investments(data_folder + awaiting_file, awaiting)
    utils.write_investments(data_folder + done_file, done)
    utils.write_array(data_folder + checked_file, checked_comments)

def send_not(comment, string, save):
    try:
        if (save):
            save_data()
        global debug
        commentID = 0
        if (debug):
            print(string)
        else:
            commentID = comment.reply(string)
            
            print("Sleeping for 1 sec")
            time.sleep(1)
            return commentID
    except Exception as e:
        print ("Caught an exception!{}".format(e))
        
def help(comment):
    if comment.author.name != config.username: 
        send_not(comment, message.help_org, False)

def create(comment, author):
    users[author] = Investor(author, starter)
    send_not(comment, message.modify_create(author, users[author].get_balance()), True)
    
def invest(comment, author, text):
    post = reddit.submission(comment.submission)
    post_ID = post.id
    upvotes = post.ups
    investor = users[author]
    
    # If it can't extract the invest amount, abandon the operation
    try:
        investm = int(float(text.replace("!invest", "").replace(" ", "")))
    except ValueError as ve:
        return False

    if (investm < 100):
        send_not(comment, message.min_invest_org, False)
        return False
    
    is_enough = investor.enough(investm)
    
    if (is_enough):
        commentID = send_not(comment, message.modify_invest(investm, upvotes, investor.get_balance() - investm), False)
        inv = investor.invest(post_ID, upvotes, commentID, investm)
        
        awaiting.append(inv)
        save_data()
        return True
    else:
        send_not(comment, message.insuff_org, False)
        return True
        
def balance(comment, author):
    investor = users[author] 
    balance = investor.get_balance()
    send_not(comment, message.modify_balance(balance), False)
    return True

def activity(comment, author):
    investor = users[author] 
    active = investor.get_active()
    send_not(comment, message.modify_active(active), False)
    return True

def all_balance():
    sum = 0
    keys_u = list(users.keys())
    for i in range(len(keys_u)):
        sum += users[keys_u[i]].get_balance()
    return sum
        
def all_investments():
    sum = 0
    for i in range(len(awaiting)):
        sum += awaiting[i].get_amount()
    return sum

def market(comment, author):
    number_of_invs = len(awaiting)
    users_balance = all_balance()
    invest_balance = all_investments()
    send_not(comment, message.modify_market(number_of_invs, users_balance, invest_balance), False)
    return True

def broke(comment, author):
    investor = users[author]
    balance = investor.get_balance()
    active = investor.get_active()

    if (balance < 100):
        if (active < 1):
            send_not(comment, message.broke_org, True)
            investor.set_balance(100)
            save_data()
        else:
            send_not(comment, message.modify_broke_active(active), False)
    else:
        send_not(comment, message.modify_broke_money(balance), False)
    return True
            
def comment_thread():

    for comment in subreddit.stream.comments():
        author = comment.author.name.lower()
        comment_ID = comment.id

        if (comment_ID in checked_comments):
            continue
        
        checked_comments.append(comment_ID)
        utils.write_array(data_folder + checked_file, checked_comments)

        # We don't serve your kind around here
        if ("_bot" in author):
            continue
        
        text = comment.body.lower()
        exist = author in list(users.keys())
        print("Author - {}\nText - {}\nExist? - {}\n\n".format(author, text, exist))

        if ("!help" in text):
            help(comment)
            continue
        
        # The !create command
        if (("!create" in text) and (not exist)):
            create(comment, author)
            continue

        if ((not exist) and (("!invest" in text) or ("!balance" in text) or ("!broke" in text) or ("!active" in text) or ("!market" in text))):
            send_not(comment, message.no_account_org, False)
            continue

        # The !invest command
        if ("!invest" in text):
            invest(comment, author, text)
            continue
                
        if ("!balance" in text):
            balance(comment, author)
            continue

        if ("!active" in text):
            activity(comment, author)
            continue
        
        if ("!market" in text):
            market(comment, author)
            continue

        if ("!broke" in text):
            broke(comment, author)
            continue
        
def check_investments():

    if (debug == 1):
        return
    
    while True:    
        if (len(awaiting) > 0):
            investment = awaiting[0]
            investor_id = investment.get_name()
            investor = users[investor_id]
            post = investment.get_ID()
            upvotes = reddit.submission(post).ups
            
            commentID = investment.get_comment()
            comment = reddit.comment(id=commentID)
            
            donep = investment.check()
            if (donep):
                win = investor.calculate(investment, upvotes)
                if (win > 0):
                    comment.edit(message.modify_invest_return(comment.body, win))
                else:
                    comment.edit(message.modify_invest_lose(comment.body))
                    
                done.append(awaiting.pop(0))
                print("Investment returned!")
#                save_data()
        
def threads():
    Thread(name="Comments", target=comment_thread).start()
    Thread(name="Investments", target=check_investments).start()

if __name__ == "__main__":
    threads()
