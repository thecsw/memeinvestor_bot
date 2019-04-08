import datetime
import time

import config
import utils

INVESTMENT_DURATION_VAR = utils.investment_duration_string(config.INVESTMENT_DURATION)

# This message will be sent if an account has been
# successfully created
CREATE_ORG = """
*Account created!*

Thank you %USERNAME% for creating a bank account in r/MemeEconomy!

Your starting balance is **%BALANCE% MemeCoins**.
"""


def modify_create(username, balance):
    return CREATE_ORG. \
        replace("%USERNAME%", str(username)). \
        replace("%BALANCE%", format(balance, ",d"))


# This message will be sent if a user tries to create an account but already
# has one.
CREATE_EXISTS_ORG = """
I love the enthusiasm, but you've already got an account!
"""

# This message will be sent when an investment
# was successful

INVEST_ORG = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

Your investment is active. I'll evaluate your return in %TIME%and update this comment. Stay tuned!

Your current balance is **%BALANCE% MemeCoins**.
""".replace("%TIME%", INVESTMENT_DURATION_VAR). \
    replace("%UPVOTES_WORD%", utils.upvote_string())


def modify_invest(amount, initial_upvotes, new_balance):
    return INVEST_ORG. \
        replace("%AMOUNT%", format(amount, ",d")). \
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")). \
        replace("%BALANCE%", format(new_balance, ",d"))


INVEST_WIN_ORG = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Your investment has matured. It was successful! You profited %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins returned @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Your new balance is **%BALANCE% MemeCoins**.
""".replace("%UPVOTES_WORD%", utils.upvote_string())

INVEST_LOSE_ORG = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Your investment has matured. It was unsuccessful! You lost %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins returned @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Your new balance is **%BALANCE% MemeCoins**.
""".replace("%UPVOTES_WORD%", utils.upvote_string())

INVEST_BREAK_EVEN_ORG = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Your investment has matured. It broke even! You profited %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins returned @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Your new balance is **%BALANCE% MemeCoins**.
""".replace("%UPVOTES_WORD%", utils.upvote_string())


def modify_invest_return(amount, initial_upvotes,
                         final_upvotes, returned,
                         profit, percent_str, new_balance):
    if profit > 0:
        original = INVEST_WIN_ORG
    elif profit < 0:
        original = INVEST_LOSE_ORG
        profit *= -1
    else:
        original = INVEST_BREAK_EVEN_ORG

    return original. \
        replace("%AMOUNT%", format(amount, ",d")). \
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")). \
        replace("%FINAL_UPVOTES%", format(final_upvotes, ",d")). \
        replace("%RETURNED%", format(returned, ",d")). \
        replace("%PROFIT%", format(profit, ",d")). \
        replace("%PERCENT%", format(percent_str)). \
        replace("%BALANCE%", format(int(new_balance), ",d"))


INVEST_CAPPED_ORG = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Your investment has matured at %FINAL_UPVOTES% %UPVOTES_WORD%, profiting %PROFIT% MemeCoins (%PERCENT%).

**Congratulations,** you've reached the maximum balance! You've triumphed over your competition in the
meme marketplace, and your wealth is inconceivable! Indeed, future generations shall remember you as a titan
of meme industry.

*"And Alexander wept, for there were no more worlds to conquer."* (...yet)

Your current balance is **%BALANCE% MemeCoins** (the maximum balance).
""".replace("%UPVOTES_WORD%", utils.upvote_string())


def modify_invest_capped(amount, initial_upvotes,
                         final_upvotes, returned,
                         profit, percent_str, new_balance):
    return INVEST_CAPPED_ORG. \
        replace("%AMOUNT%", format(amount, ",d")). \
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")). \
        replace("%FINAL_UPVOTES%", format(final_upvotes, ",d")). \
        replace("%PROFIT%", format(profit, ",d")). \
        replace("%PERCENT%", str(percent_str)). \
        replace("%BALANCE%", format(new_balance, ",d"))


# If funds are insufficient to make an investment
# say that
INSUFF_ORG = """
You do not have enough MemeCoins to make that investment.

Your current balance is **%BALANCE% MemeCoins**.

If you have less than 100 MemeCoins and no active investments, try running `!broke`!
"""


def modify_insuff(balance_t):
    return INSUFF_ORG. \
        replace("%BALANCE%", format(balance_t, ",d"))


# Message if you are broke
BROKE_ORG = """
Welp, you are broke.

Your balance has been reset to 100 MemeCoins. Be careful next time.

You have gone bankrupt %NUMBER% time(s).
"""


def modify_broke(times):
    return BROKE_ORG. \
        replace("%NUMBER%", str(times))


# Message if you are broke and have active investments
BROKE_ACTIVE_ORG = """
You still have %ACTIVE% investment(s).

You need to wait until they are fully evaluated.
"""


def modify_broke_active(active):
    return BROKE_ACTIVE_ORG. \
        replace("%ACTIVE%", str(active))


# Message if you are broke and have more than 100 MemeCoins
BROKE_MONEY_ORG = """
You are not broke. You still have **%AMOUNT% MemeCoins**.
"""


def modify_broke_money(amount):
    return BROKE_MONEY_ORG. \
        replace("%AMOUNT%", format(amount, ",d"))


HELP_ORG = """
*Welcome to MemeInvestment!*

I am a bot that will help you invest in memes and make a fortune out of it!

Here is a list of commands that summon me:

### GENERAL COMMANDS
- `!active`
- `!balance`
- `!broke`
- `!create`
- `!help`
- `!invest <amount>`
- `!market`
- `!top`
- `!version`
- `!template https://imgur.com/...` **(OP Only)**

### FIRM COMMANDS
- `!firm`
- `!createfirm <name>`
- `!joinfirm <name>`
- `!leavefirm`
- `!invite <username>` **(Associate and up)**
- `!promote <username>` **(Executive and up)**
- `!demote <username>` **(Executive and up)**
- `!fire <username>` **(Executive and up)**
- `!upgrade` **(CEO and CFO only)**
- `!tax <percent>` **(CEO and CFO only)**
- `!setprivate` **(CEO and COO only)**
- `!setpublic` **(CEO and COO only)**

To get help on a specific command, simply invoke `!help command`
"""

BALANCE_ORG = """
Currently, your account balance is **%BALANCE% MemeCoins**.
"""


def modify_balance(balance):
    return BALANCE_ORG. \
        replace("%BALANCE%", format(balance, ",d"))


ACTIVE_ORG = """
You have %NUMBER% active investments:

%INVESTMENTS_LIST%
"""


def modify_active(active_investments):
    if not active_investments:
        return "You don't have any active investments right now."

    investments_strings = []
    i = 1
    for inv in active_investments:
        seconds_remaining = inv.time + config.INVESTMENT_DURATION - time.time()
        if seconds_remaining > 0:
            td = datetime.timedelta(seconds=seconds_remaining)
            remaining_string = str(td).split(".")[0] + " remaining"
        else:
            remaining_string = "processing"
        post_url = f"https://www.reddit.com/r/MemeEconomy/comments/{inv.post}/_/{inv.comment}"
        inv_string = f"[#{i}]({post_url}): {inv.amount} M¢ @ {inv.upvotes} %UPVOTES_WORD% ({remaining_string})" \
            .replace("%UPVOTES_WORD%", utils.upvote_string())
        investments_strings.append(inv_string)
        i += 1
    investments_list = "\n\n".join(investments_strings)

    return ACTIVE_ORG. \
        replace("%NUMBER%", str(len(active_investments))). \
        replace("%INVESTMENTS_LIST%", investments_list)


MIN_INVEST_ORG = """
The minimum possible investment is %MIN% MemeCoins (1% of your balance) or 100 memecoins, whatever is higher.
"""


def modify_min_invest(minim):
    return MIN_INVEST_ORG. \
        replace("%MIN%", format(int(minim), ",d"))


MARKET_ORG = """
The market has **%NUMBER%** active investments.

All investors currently possess **%MONEY% MemeCoins**.

There are **%HODL% MemeCoins** detained in investments.
"""


def modify_market(inves, cap, invs_cap):
    return MARKET_ORG. \
        replace("%NUMBER%", format(int(inves), ",d")). \
        replace("%MONEY%", format(int(cap), ",d")). \
        replace("%HODL%", format(int(invs_cap), ",d"))


# Message used for !top command
TOP_ORG = """
Investors with the highest net worth (balance + active investments):

%TOP_STRING%
"""


def modify_top(leaders):
    top_string = ""
    for leader in leaders:
        top_string = f"{top_string}\n\n{leader.name}: {int(leader.networth)} MemeCoins"

    top_response = TOP_ORG
    top_response = top_response.replace("%TOP_STRING%", top_string)
    return top_response


DELETED_COMMENT_ORG = """
Where did he go?

Whatever, investment is lost.
"""

TEMPLATE_HINT_ORG = """
---

Psst, %NAME%, you can invoke `!template https://imgur.com/...` command to publicly post your template!
"""

INVEST_PLACE_HERE_NO_FEE = """
**INVESTMENTS GO HERE - ONLY DIRECT REPLIES TO ME WILL BE PROCESSED**

To prevent thread spam and other natural disasters, I only respond to direct replies. Other commands will be ignored and may be penalized. Let's keep our marketplace clean!

---

- Visit [meme.market](https://meme.market) for help, market statistics, and investor profiles.

- Visit /r/MemeInvestor_bot for questions or suggestions about me.

- Support the project via our [patreon](https://www.patreon.com/memeinvestor_bot)

- New user? Lost or confused? Reply `!help` to this message, or visit the [Wiki](https://www.reddit.com/r/MemeEconomy/wiki/index) for a more in depth explanation.
"""


def invest_no_fee(name):
    return INVEST_PLACE_HERE_NO_FEE + TEMPLATE_HINT_ORG. \
        replace("%NAME%", name)


INVEST_PLACE_HERE = """
**INVESTMENTS GO HERE - ONLY DIRECT REPLIES TO ME WILL BE PROCESSED**

To prevent thread spam and other natural disasters, I only respond to direct replies. Other commands will be ignored and may be penalized. Let's keep our marketplace clean!

The author of this post paid **%MEMECOIN% MemeCoins** to post this.

---

- Visit [meme.market](https://meme.market) for help, market statistics, and investor profiles.

- Visit /r/MemeInvestor_bot for questions or suggestions about me.

- Support the project via our [patreon](https://www.patreon.com/memeinvestor_bot)

- New user? Lost or confused? Reply `!help` to this message, or visit the [Wiki](https://www.reddit.com/r/MemeEconomy/wiki/index) for a more in depth explanation.
""" + TEMPLATE_HINT_ORG


def modify_invest_place_here(amount, name):
    return INVEST_PLACE_HERE. \
               replace("%MEMECOIN%", format(int(amount), ",d")) + TEMPLATE_HINT_ORG. \
               replace("%NAME%", name)


INSIDE_TRADING_ORG = """
You can't invest in your own memes, insider trading is not allowed!
"""


def modify_grant_success(grantee, badge):
    return f"Successfully granted badge `{badge}` to {grantee}!"


def modify_grant_failure(failure_message):
    return f"Oops, I couldn't grant that badge ({failure_message})"


NO_ACCOUNT_POST_ORG = """
You need an account to post a meme. Please reply to one of my comments with `!create`.

For more information please type `!help`
"""

PAY_TO_POST_ORG = """
Due to latest regulations, in order to post a meme you should pay 6% tax with minimum of 250 MemeCoins.

If you can't afford it, your post will be deleted. Nothing personal, kiddo. Only Meme Street business.

When you get enough cash, resubmit your meme with a new post.

Your current balance is **%MEMECOINS% MemeCoins**.
"""


def modify_pay_to_post(balance):
    return PAY_TO_POST_ORG.\
        replace("%MEMECOINS%", format(int(balance), ",d"))


MAINTENANCE_ORG = """
**The bot is under maintenance due to technical reasons.**

**Expect it to be back online soon. (Several hours)**

**Sorry for any inconvenience caused.**
"""

firm_none_org = """
You are not in a firm.

You can create a new one with the **!createfirm <FIRM NAME>** command, or request to join one with **!joinfirm <FIRM NAME>**.
"""

firm_other_org = """
Firm: [**%FIRM_NAME%**](https://meme.market/firm.html?firm=%FIRM_ID%)

Firm balance: **%BALANCE%** Memecoins

Firm level: **%LEVEL%**

----

## Members:

*CEO:*
%CEO%

*COO:*
%COO%

*CFO:*
%CFO%

*Executives:*
%EXECS%

*Associates:*
%ASSOCS%

*Floor Traders:*
%TRADERS%
"""


def modify_firm_other(firm, ceo, coo, cfo, execs, assocs, traders):
    return firm_other_org. \
        replace("%FIRM_NAME%", firm.name). \
        replace("%FIRM_ID%", str(firm.id)). \
        replace("%CEO%", ceo). \
        replace("%COO%", coo). \
        replace("%CFO%", cfo). \
        replace("%EXECS%", execs). \
        replace("%ASSOCS%", assocs). \
        replace("%TRADERS%", traders). \
        replace("%BALANCE%", "{:,}".format(firm.balance)). \
        replace("%LEVEL%", str(firm.rank + 1))


firm_self_org = """
Firm: [**%FIRM_NAME%**](https://meme.market/firm.html?firm=%FIRM_ID%)

Firm balance: **%BALANCE%** Memecoins

Firm level: **%LEVEL%**

Your Rank: **%RANK%**

----

## Members:

*CEO:*
%CEO%

*COO:*
%COO%

*CFO:*
%CFO%

*Executives:*
%EXECS%

*Associates:*
%ASSOCS%

*Floor Traders:*
%TRADERS%

----

You can leave this firm with the **!leavefirm** command.
"""


def modify_firm_self(rank, firm, ceo, coo, cfo, execs, assocs, traders):
    rank_str = rank_strs[rank]
    return firm_self_org. \
        replace("%RANK%", rank_str). \
        replace("%FIRM_NAME%", firm.name). \
        replace("%FIRM_ID%", str(firm.id)). \
        replace("%CEO%", ceo). \
        replace("%COO%", coo). \
        replace("%CFO%", cfo). \
        replace("%EXECS%", execs). \
        replace("%ASSOCS%", assocs). \
        replace("%TRADERS%", traders). \
        replace("%BALANCE%", "{:,}".format(firm.balance)). \
        replace("%LEVEL%", str(firm.rank + 1))


firm_notfound_org = """
No firm was found with this name.
"""

rank_strs = {
    "ceo": "CEO",
    "coo": "COO",
    "cfo": "CFO",
    "exec": "Executive",
    "assoc": "Associate",
    "": "Floor Trader"
}

createfirm_exists_failure_org = """
You are already in a firm: **%FIRM_NAME%**

Please leave this firm using the *!leavefirm* command before creating a new one.
"""

createfirm_cost_failure_org = """
Creating a firm costs 1,000,000 Memecoins, you don't have enough. Earn some more first!
"""


def modify_createfirm_exists_failure(firm_name):
    return createfirm_exists_failure_org. \
        replace("%FIRM_NAME%", firm_name)


createfirm_format_failure_org = """
Firm names must be between 4 and 32 characters long, using only alphanumeric characters, spaces, dashes, and underscores.
"""

createfirm_nametaken_failure_org = """
This firm name is already taken, please try again with a new one.
"""

createfirm_org = """
The new firm has been created successfully.

You are the firm's CEO and you have the ability to
"""

nofirm_failure_org = leavefirm_none_failure_org = """
You are not in a firm.
"""
no_firm_failure_org = leavefirm_none_failure_org

leavefirm_ceo_failure_org = """
You are currently the CEO of your firm, so you are not allowed to leave.

If you really want to leave, you will need to first demote yourself by promoting a COO or CFO member to CEO with the **!promote <username>** command.
"""

leavefirm_org = """
You have left your firm.
"""

not_ceo_org = """
Only the CEO can do that.
"""

not_ceo_or_coo_org = """
Only the CEO or COO can do that.
"""

not_ceo_or_cfo_org = """
Only the CEO or CFO can do that.
"""

not_ceo_or_exec_org = """
Only a member of the board or an executive can do that.
"""

not_assoc_org = """
Floor Traders cannot send invites.
"""

promote_failure_org = """
Couldn't promote user, make sure you used the correct username.
"""

promote_coo_full_org = """
Could not promote this employee since the firm already has a COO.
"""

promote_cfo_full_org = """
Could not promote this employee since the firm already has a CFO.
"""

promote_execs_full_org = """
Could not promote this employee since the firm is at its maximum executive limit.
**Number of executives:** %EXECS%
**Firm level:** %LEVEL%

The CEO or CFO of the firm can raise this limit by upgrading with `!upgrade`.
"""


def modify_promote_execs_full(firm):
    return promote_execs_full_org. \
        replace("%EXECS%", str(firm.execs)). \
        replace("%LEVEL%", str(firm.rank + 1))


promote_assocs_full_org = """
Could not promote this employee since the firm is at its maximum associate limit.
**Number of associates:** %ASSOCS%
**Firm level:** %LEVEL%

The CEO or CFO of the firm can raise this limit by upgrading with `!upgrade`.
"""


def modify_promote_assocs_full(firm):
    return promote_assocs_full_org. \
        replace("%ASSOCS%", str(firm.assocs)). \
        replace("%LEVEL%", str(firm.rank + 1))


promote_org = """
Successfully promoted **/u/%NAME%** from **%OLDRANK%** to **%NEWRANK%**.
"""


def modify_promote(user, old_role):
    return promote_org. \
        replace("%NAME%", user.name). \
        replace("%OLDRANK%", rank_strs[old_role]). \
        replace("%NEWRANK%", rank_strs[user.firm_role])


demote_failure_org = """
Failed to demote user, make sure you used the correct username.
"""

demote_failure_trader_org = """
Failed to demote user, they are already a Floor Trader. Use `!fire <username>` if you would like to remove them from the firm.
"""

demote_cfo_full_org = """
Could not demote this employee since the firm already has a CFO.
"""

demote_execs_full_org = """
Could not demote this employee since the firm is at its maximum executive limit.
**Number of executives:** %EXECS%
**Firm level:** %LEVEL%

The CEO or CFO of the firm can raise this limit by upgrading with `!upgrade`.
"""


def modify_demote_execs_full(firm):
    return demote_execs_full_org. \
        replace("%EXECS%", str(firm.execs)). \
        replace("%LEVEL%", str(firm.rank + 1))


demote_assocs_full_org = """
Could not demote this employee since the firm is at its maximum associate limit.
**Number of associates:** %ASSOCS%
**Firm level:** %LEVEL%

The CEO or CFO of the firm can raise this limit by upgrading with `!upgrade`.
"""


def modify_demote_assocs_full(firm):
    return demote_assocs_full_org. \
        replace("%ASSOCS%", str(firm.assocs)). \
        replace("%LEVEL%", str(firm.rank + 1))


demote_org = """
Successfully demoted **/u/%NAME%** from **%OLDRANK%** to **%NEWRANK%**.
"""


def modify_demote(user, old_role):
    return demote_org. \
        replace("%NAME%", user.name). \
        replace("%OLDRANK%", rank_strs[old_role]). \
        replace("%NEWRANK%", rank_strs[user.firm_role])


fire_org = """
Successfully fired **/u/%NAME%** from the firm.
"""


def modify_fire(user):
    return fire_org. \
        replace("%NAME%", user.name)


fire_failure_org = """
Couldn't fire user, make sure you used the correct username.
"""

joinfirm_exists_failure_org = """
Can't join a firm because you are already in one. Use the *!leavefirm* command to leave your firm before joining a new one.
"""

joinfirm_private_failure_org = """
Can't join this firm because it is set to private and you have not been invited.

A member of the firm must first invite you with the `!invite <username>` command.
"""

joinfirm_failure_org = """
Could not join firm, are you sure you got the name right?
"""

joinfirm_full_org = """
Could not join the firm, since it is at its maximum member limit.
**Number of employees:** %MEMBERS%
**Firm level:** %LEVEL%

The CEO or CFO of the firm can raise this limit by upgrading with `!upgrade`.
"""


def modify_joinfirm_full(firm):
    return joinfirm_full_org. \
        replace("%MEMBERS%", str(firm.size)). \
        replace("%LEVEL%", str(firm.rank + 1))


joinfirm_org = """
You are now a floor trader of the firm **%NAME%**. If you'd like to leave, use the *!leavefirm* command.
"""


def modify_joinfirm(firm):
    return joinfirm_org. \
        replace("%NAME%", firm.name)


FIRM_TAX_ORG = """

--

%AMOUNT% MemeCoins were sent to the firm - %NAME%.
"""


def modify_firm_tax(tax_amount, firm_name):
    return FIRM_TAX_ORG.\
        replace("%AMOUNT%", format(int(tax_amount), ",d")). \
        replace("%NAME%", firm_name)


TEMPLATE_NOT_OP = """
Sorry, but you are not the submission's Original Poster.
"""

TEMPLATE_ALREADY_DONE = """
Sorry, but you already submitted the template link.
"""

TEMPLATE_NOT_STICKY = """
Sorry, you have to *directly* reply to the bot's sticky.
"""

TEMPLATE_OP = """
---

OP %NAME% has posted *[THE LINK TO THE TEMPLATE](%LINK%)*, Hurray!
"""


def modify_template_op(link, name):
    return TEMPLATE_OP. \
        replace("%LINK%", link). \
        replace("%NAME%", name)


invite_not_private_failure_org = """
You don't need to invite anyone since your firm is not private.

That investor can join with the `!joinfirm <firm_name>` command.

If you're the CEO or COO and you would like the firm to be invite-only, use the `!setprivate` command.
"""

invite_no_user_failure_org = """
Couldn't invite user, make sure you used the right username.
"""

invite_in_firm_failure_org = """
This user is already in a firm. They will need to leave before you can invite them.
"""

invite_org = """
You have invited /u/%NAME% to the firm.

They can accept this request using the `!joinfirm %FIRM%` command.
"""


def modify_invite(invitee, firm):
    return invite_org. \
        replace("%NAME%", invitee.name). \
        replace("%FIRM%", firm.name)


setprivate_org = """
The firm is now private. Users can only join after a member of the firm sends an invite with the `!invite <user>` command.

If you'd like to reverse this, use the `!setpublic` command.
"""

setpublic_org = """
The firm is now public. Users can join your command without being invited using the `!joinfirm <firm_name>` command.

If you'd like to reverse this, use the `!setprivate` command.
"""
upgrade_insufficient_funds_org = """
The firm does not have enough funds to upgrade.

**Firm balance:** %BALANCE%
**Cost to upgrade to level %LEVEL%:** %COST%
"""


def modify_upgrade_insufficient_funds_org(firm, cost):
    return upgrade_insufficient_funds_org. \
        replace("%BALANCE%", format(int(firm.balance), ",d")). \
        replace("%LEVEL%", str(firm.rank + 2)). \  
        replace("%COST%", format(int(cost), ",d"))


upgrade_org = """
You have succesfully upgraded the firm to **level %LEVEL%**!

The firm may now have up to **%MAX_MEMBERS% employees**, including up to **%MAX_EXECS% executives** and **%MAX_ASSOCS% associates**.
"""


def modify_upgrade(firm, max_members, max_execs, max_assocs):
    return upgrade_org. \
        replace("%LEVEL%", str(firm.rank + 1)). \
        replace("%MAX_MEMBERS%", str(max_members)). \
        replace("%MAX_EXECS%", str(max_execs)). \
        replace("%MAX_ASSOCS%", str(max_assocs))


DEPLOY_VERSION = """
Current version of the bot is deployed since `%DATE%`
"""


def modify_deploy_version(date):
    return DEPLOY_VERSION. \
        replace("%DATE%", date)


TAX_TOO_HIGH = """
The tax rate is too high. The tax should be between 5% and 75%.
"""

TAX_TOO_LOW = """
The tax rate is too low. The tax should be between 5% and 75%.
"""

TAX_SUCCESS = """
The new tax rate has been set successfully.
"""

TEMPLATE_SUCCESS = """
Template posted successfully! Thank you for making r/MemeEconomy a better place!
"""
