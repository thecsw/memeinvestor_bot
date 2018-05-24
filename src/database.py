import sqlite3
import time

def init_investors():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS Investors 
    (ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    Name CHAR(8), 
    Balance INTEGER, 
    Active INTEGER, 
    Completed INTEGER, 
    Broke INTEGER)''')
    c.close()
    conn.close()
        
# Investor operations
    
def investor_insert(name, balance):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""
    INSERT INTO Investors (Name, Balance, Active, Completed, Broke)
    VALUES (?, ?, ?, ?, ?)""", (name, balance, 0, 0, 0))
    conn.commit()
    c.close()
    conn.close()
    
def investor_update_balance(name, balance):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE Investors SET Balance = ? WHERE Name = ?", (balance, name,))
    conn.commit()
    c.close()
    conn.close()
    
def investor_update_active(name, active):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE Investors SET Active = ? WHERE Name = ?", (active, name,))
    conn.commit()
    c.close()
    conn.close()
    
def investor_update_completed(name, completed):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE Investors SET Completed = ? WHERE Name = ?", (completed, name,))
    conn.commit()
    c.close()
    conn.close()

def investor_update_broke(name, broke):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE Investors SET Broke = ? WHERE Name = ?", (broke, name,))
    conn.commit()
    c.close()
    conn.close()
    
def investor_get_balance(name):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT Balance FROM Investors WHERE Name = ?", (name,))
    balance = c.fetchone()[0]
    c.close()
    conn.close()
    return balance

def investor_get_active(name):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT Active FROM Investors WHERE Name = ?", (name,))
    active = c.fetchone()[0]
    c.close()
    conn.close()
    return active
    
def investor_get_completed(name):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT Completed FROM Investors WHERE Name = ?", (name,))
    completed = c.fetchone()[0]
    c.close()
    conn.close()
    return completed

def investor_get_broke(name):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT Broke FROM Investors WHERE Name = ?", (name,))
    completed = c.fetchone()[0]
    c.close()
    conn.close()
    return completed

# Investment operations

def init_investments():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS Investments
    (ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    Post CHAR(8), 
    Upvotes INTEGER, 
    Comment CHAR(8), 
    Name CHAR(8), 
    Amount INTEGER, 
    Time INTEGER, 
    Done BIT, 
    Response CHAR(8), 
    Success BIT)''')
    c.close()
    conn.close()

def investment_insert(post, upvotes, comment, name, amount, unix, response):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""INSERT INTO Investments (Post, Upvotes, Comment, Name, Amount, Time, Done, Response, Success)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (post.id, upvotes, comment.id, name, amount, unix, 0, response.id, 0,))
    conn.commit()
    c.close()
    conn.close()

def investment_update_done(number):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE Investments SET Done = 1 WHERE ID = ?", (number,))
    conn.commit()
    c.close()
    conn.close()

def investment_update_success(number):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE Investments SET Success = 1 WHERE ID = ?", (number,))
    conn.commit()
    c.close()
    conn.close()
    
def investment_get_name(number):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT Name FROM Investments WHERE ID = ?", (number,))
    name = c.fetchone()[0]
    c.close()
    conn.close()
    return name

def investment_get_post(number):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT Post FROM Investments WHERE ID = ?", (number,))
    postid = c.fetchone()[0]
    c.close()
    conn.close()
    return postid

def investment_get_comment(number):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT Comment FROM Investments WHERE ID = ?", (number,))
    comment = c.fetchone()[0]
    c.close()
    conn.close()
    return comment

def investment_get_amount(number):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT Amount FROM Investments WHERE ID = ?", (number,))
    amount = c.fetchone()[0]
    c.close()
    conn.close()
    return amount

def investment_get_upvotes(number):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT Upvotes FROM Investments WHERE ID = ?", (number,))
    upvotes = c.fetchone()[0]
    c.close()
    conn.close()
    return upvotes

def investment_get_response(number):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT Response FROM Investments WHERE ID = ?", (number,))
    response = c.fetchone()[0]
    c.close()
    conn.close()
    return response

# Return Investments

def investment_find_done():
    unix = time.time()
    # Four hour difference
    ready = unix + (4 * 3600)
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT ID From Investments WHERE Time < ? AND Done = 0", (ready,))
    arr = c.fetchall()
    arr = [x[0] for x in arr]
    print(arr)
    c.close()
    conn.close()
    return arr


# Big important queries

def market_user_coins():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT SUM(Balance) FROM Investors")
    user_coins = c.fetchone()[0]
    c.close()
    conn.close()
    return user_coins
    
def market_invest_coins():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT SUM(Amount) FROM Investments WHERE Done = 0")
    invest_coins = c.fetchone()[0]
    c.close()
    conn.close()
    return invest_coins

def market_count_investments():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(ID) FROM Investments WHERE Done = 0")
    active_investments = c.fetchone()[0]
    c.close()
    conn.close()
    return active_investments

def find_investor(name):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(ID) FROM Investors WHERE Name = ?", (name, ))
    result = c.fetchone()[0]
    c.close()
    conn.close()
    return result

# Comment logging

def init_comments():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS Comments
    (ID INTEGER PRIMARY KEY AUTOINCREMENT, Comment CHAR(8))''')
    c.close()
    conn.close()

def log_comment(comment):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO Comments (Comment) VALUES (?)", (comment.id,))
    conn.commit()
    c.close()
    conn.close()
    
def find_comment(comment):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(ID) FROM Comments WHERE Comment = ?", (comment.id,))
    result = c.fetchone()[0]
    c.close()
    conn.close()
    return result

# Submission logging

def init_submissions():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS Submissions
    (ID INTEGER PRIMARY KEY AUTOINCREMENT, Submission CHAR(8))''')
    c.close()
    conn.close()

def log_submission(submission):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO Submissions (Submission) VALUES (?)", (submission.id,))
    conn.commit()
    c.close()
    conn.close()
    
def find_submission(submission):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(ID) FROM Submissions WHERE Submissions = ?", (submission.id,))
    result = c.fetchone()[0]
    c.close()
    conn.close()
    return result
