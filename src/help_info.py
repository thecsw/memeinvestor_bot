"""
This module will be responsible for
providing help information on commands
"""

help_dict = {
    'active': "Shows a list of all of il tuo investimenti attivi.",
    'balance': "Shows the amount of Memecoins you have.",
    'broke': "If you have less than 100 Memecoins, this command will bring il tuo balance back up to 100.",
    'create': "Initializes il tuo account.",
    'createfirm': "Creates a new firm with the given name, and sets you as the CEO. This costs 1,000,000 Memecoins.",
    'fire': "Removes the member from il tuo firm. Only the CEO can fire Executives.",
    'firm': "Shows information about il tuo firm and rank.",
    'help': "Display some help text about the bot.",
    'invest': "Invests the specified number of Memecoins into the post. Depending on the amount of upvotes the post gets in the next 4 hours, you will either receive a return or lose il tuo investment.",
    'invite': "Invites the user with the given username to the firm. They are then able to join using the `!joinfirm` command.",
    'joinfirm': "Joins the firm with the given name. If the firm is private, you'll have to be invited by one of its leaders first.",
    'leavefirm': "Removes you from the firm you are in.",
    'market': "Shows some statistics about the market.",
    'promote': "Promotes the user with the given username (they must be a member of il tuo firm). If the user is a Floor Trader (default rank), they are promoted to Executive. If they are an Executive and you are the CEO, you swap ranks with them.",
    'setprivate': "Sets the firm to private mode. This prevents users from joining unless the CEO or an Executive has invited them (using the `!invite` command).",
    'setpublic': "Sets the firm to public mode (the default), letting anyone join.",
    'template': "Lets the OP of the post specify a link to the meme template. The link will be added to the bot's sticky comment.",
    'top': "Shows the top users in the market.",
    'upgrade': "Upgrades the firm to the next level, allowing the firm to have more members. This costs 4M Memecoins to upgrade to level 2, 16M to upgrade to level 3, 64M to upgrade to level 4, and so on.",
    'version': "Shows the time when the bot was deployed."
}
