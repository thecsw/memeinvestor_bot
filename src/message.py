
# This is the general bot description, used in
# every message
bot_desc = """
_______________________
^(I am a MemeInvestor. I help investing in memes.
Improve me by contributing to source code!)

[Source code](https://github.com/thecsw/prequelmemes_bot)
"""

help_mess = """
^(For more information type !help)
"""

# This message will be sent if an account has been
# successfully created
create_org = """
*Account created!*

Thank you %USERNAME% for creating a bank account in r/MemeEconomy!

Your current balance is %BALANCE% MemeCoins.
%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

def modify_create(username, balance):
    create = create_org
    create = create.replace("%USERNAME%", str(username))
    create = create.replace("%BALANCE%", str(balance))
    return create

# This message will be sent when an investment
# was successfull

invest_org = """
*%AMOUNT% MemeCoins were successfully invested!*

You new balance is %BALANCE%

In 6 hours your investment will be evaluated and
depending on how well the memes does, your investment
can be returned with bonuses or your would just lose
your MemeCoins.
%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

def modify_invest(amount, balance):
    invest = invest_org
    invest = invest.replace("%AMOUNT%", str(amount))
    invest = invest.replace("%BALANCE%", str(balance))
    return invest

# If funds are insufficient to make an investment
# say that
insuff_org = """
You do not have enough MemeCoins to make the investment.
%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

# Message if you are broke
broke_org = """
Welp, you are broke.

Your balance has been resetted to 100 MemeCoins. Be careful
next time.
%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

# Message if you are broke and have active investments
broke_active_org = """
You still have %ACTIVE% investment(s).

You need to wait until they are fully 
evaluated.
%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

def modify_broke_active(active):
    broke_active = broke_active_org
    broke_active = broke_active.replace("%ACTIVE%", str(active))

# Message if you are broke and have more than 100 MemeCoins
broke_money_org = """
You are not broke. You still have %AMOUNT% MemeCoins.

%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

def modify_broke_money(amount):
    broke_money = broke_money_org
    broke_money = broke_money.replace("%AMOUNT%", str(amount))
    
help_org = """
*Welcome to MemeInvestment!*

I am a bot that will help you investing in memes and make
a fortune out of it!

Here is a list of commands that summon me:

1. !create - creates a bank account for you with a new balance
of 1000 MemeCoins

2. !invest AMOUNT - invests AMOUNT in the meme (post). After 6
hours after the investment, the meme growth will be evaluated
and your investment can profit you or make you bankrupt. Minimum
possible investment is 100 MemeCoins.

3. !balance - returns your current balance, if you have and account.

4. !broke - only if your balance is less than 100 MemeCoins and you 
do not have any active investments, declares bankruptcy on your 
account and sets your balance to 100 MemeCoins(Minumum possible
 investment).

5. !help - returns this help message
%DESCRIPTION% 
""".replace("%DESCRIPTION%", bot_desc)

no_account_org = """
You do not have permission to make this operation.

Please create an account with !create command.
%DESCRIPTION% 
""".replace("%DESCRIPTION%", help_mess)

balance_org = """
Currently, your account balance is %BALANCE%

%DESCRIPTION% 
""".replace("%DESCRIPTION%", help_mess)

def modify_balance(balance):
    balance = balance_org
    balance = balance.replace("%BALANCE%", str(balance))
