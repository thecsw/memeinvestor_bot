"""
os allows us to access the environment variables list
"""
import os

POST_TO_REDDIT      = int(os.environ['BOT_POST_TO_REDDIT'])
IS_MODERATOR        = int(os.environ['BOT_IS_MODERATOR'])
PREVENT_INSIDERS    = int(os.environ['BOT_PREVENT_INSIDERS'])
INVESTMENT_DURATION = int(os.environ['BOT_INVESTMENT_DURATION'])
SUBMISSION_FEE      = int(os.environ['BOT_SUBMISSION_FEE'])
ADMIN_ACCOUNTS      = os.environ['BOT_ADMIN_REDDIT_ACCOUNTS'].split(',')

CLIENT_ID     = os.environ['BOT_CLIENT_ID']
CLIENT_SECRET = os.environ['BOT_CLIENT_SECRET']
USER_AGENT    = os.environ['BOT_USER_AGENT']
USERNAME      = os.environ['BOT_USERNAME']
PASSWORD      = os.environ['BOT_PASSWORD']

MAINTENANCE = int(os.environ['BOT_MAINTENANCE'])

SUBREDDITS = os.environ['BOT_SUBREDDIT'].split(',')

MYSQL_USER     = os.environ['MYSQL_USER']
MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
MYSQL_HOST     = os.environ['MYSQL_HOST']
MYSQL_PORT     = os.environ['MYSQL_PORT']
MYSQL_DATABASE = os.environ['MYSQL_DATABASE']

DB = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
