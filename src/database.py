import sqlite3

conn = sqlite3.connect("data.db")

c = conn.cursor()

def data_init():

    c.execute('''
    CREATE TABLE IF NOT EXISTS Investors 
    (ID INTEGER AUTOINCREMENT, Name CHAR(8), Balance INT, Active SMALLINT, Completed SMALLINT)''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS Investments
    (ID INTEGER AUTOINCREMENT, Post CHAR(8), Upvotes INT, Comment CHAR(8), Name CHAR(8), Amount INT, Time INT, Done BIT)''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS Comments
    (ID INTEGER AUTOINCREMENT, Comment CHAR(8))''')

    conn.commit()

# Investor operations
    
def investor_insert(name, balance):
    c.execute("""
    INSERT INTO Investors 
    VALUES (?, ?, 0, 0)""", (name, balance))
    conn.commit()
    
def investor_update_balance(name, balance):
    c.execute("UPDATE Investors SET Balance = ? WHERE Name = ?", balance, name)
    conn.commit()

def investor_update_active(name, active):
    c.execute("UPDATE Investors SET Active = ? WHERE Name = ?", active, name)
    conn.commit()

def investor_update_completed(name, completed):
    c.execute("UPDATE Investors SET Completed = ? WHERE Name = ?", completed, name)
    conn.commit()
    
def investor_get_balance(name):
    c.execute("SELECT Balance FROM Investors WHERE Name = ?", name)
    balance = c.fetchone()[0]
    return balance
    

def investor_get_active(name):
    c.execute("SELECT Active FROM Investors WHERE Name = ?", name)
    active = c.fetchone()[0]
    return active
    
def investor_get_completed(name):
    c.execute("SELECT Completed FROM Investors WHERE Name = ?", name)
    
# Investment operations

def investment_insert(post, upvotes, comment, name, amount, unix):
    c.execute("""INSERT INTO Investments 
    VALUES (?, ?, ?, ?, ?, ?, 0)""", (post, upvotes, comment, name, amount, unix))
    conn.commit()

def investment_update_done(name):
    c.execute("UPDATE Investments SET Done = 1 WHERE Name = ?", name)
    conn.commit()

# Big important queries

def market_user_coins():
    c.execute("SELECT SUM(Balance) FROM Investors")
    user_coins = c.fetchone()[0]
    return user_coins
    
def market_invest_coins():
    c.execute("SELECT SUM(Amount) FROM Investments WHERE Done = 0")
    invest_coins = c.fetchone()[0]
    return invest_coins

def market_count_investments():
    c.execute("SELECT COUNT(ID) FROM Investments WHERE Done = 0")
    active_investments = c.fetchone()[0]
    return active_investments

def find_investor(name):
    c.execute("SELECT COUNT(ID) FROM Investors WHERE Name = ?", name)
    result = c.fetchone()[0]
    return result

# Comment logging

def log_comment(comment):
    c.execute("INSERT INTO Comments VALUES (?)", comment)
    conn.commit()

def find_comment(comment):
    c.execute("SELECT COUNT(ID) FROM Comments WHERE Comment = ?", comment)
    result = c.fetchone()[0]
    return result
