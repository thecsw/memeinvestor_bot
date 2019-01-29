"""
os allows us to access the environment variables list
"""
import json
import os

with open(os.path.join('..', 'cfg.json'), 'r', encoding='utf-8') as config_file:
    config_data = json.load(config_file)

POST_TO_REDDIT = int(config_data['BOT_POST_TO_REDDIT'])
IS_MODERATOR = int(config_data['BOT_IS_MODERATOR'])
PREVENT_INSIDERS = int(config_data['BOT_PREVENT_INSIDERS'])
INVESTMENT_DURATION = int(config_data['BOT_INVESTMENT_DURATION'])
SUBMISSION_FEE = int(config_data['BOT_SUBMISSION_FEE'])
ADMIN_ACCOUNTS = config_data['BOT_ADMIN_REDDIT_ACCOUNTS']

STARTING_BALANCE = int(config_data['BOT_STARTING_BALANCE'])
SUBMISSION_FEE_PERCENT = int(config_data['BOT_SUBMISSION_FEE_PERCENT'])
SUBMISSION_MIN_FEE = int(config_data['BOT_SUBMISSION_MIN_FEE'])

LEADERBOARD_INTERVAL = int(config_data['BOT_LEADERBOARD_INTERVAL'])

CLIENT_ID = config_data['BOT_CLIENT_ID']
CLIENT_SECRET = config_data['BOT_CLIENT_SECRET']
USER_AGENT = config_data['BOT_USER_AGENT']
USERNAME = config_data['BOT_USERNAME']
PASSWORD = config_data['BOT_PASSWORD']

MAINTENANCE = int(config_data['BOT_MAINTENANCE'])

SUBREDDITS = config_data['BOT_SUBREDDITS']

DBFILE = config_data['DBFILE']

TEST = 0

DB = "sqlite:///{db}".format(db=DBFILE)
