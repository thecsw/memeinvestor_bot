import os

post_to_reddit      = int(os.environ['BOT_POST_TO_REDDIT'])
is_moderator        = int(os.environ['BOT_IS_MODERATOR'])
prevent_insiders    = int(os.environ['BOT_PREVENT_INSIDERS'])
investment_duration = int(os.environ['BOT_INVESTMENT_DURATION'])
submission_fee      = int(os.environ['BOT_SUBMISSION_FEE'])
admin_accounts      = os.environ['BOT_ADMIN_REDDIT_ACCOUNTS'].split(',')

client_id     = os.environ['BOT_CLIENT_ID']
client_secret = os.environ['BOT_CLIENT_SECRET']
user_agent    = os.environ['BOT_USER_AGENT']
username      = os.environ['BOT_USERNAME']
password      = os.environ['BOT_PASSWORD']

maintenance = os.environ['BOT_MAINTENANCE']

subreddits = [os.environ['BOT_SUBREDDIT']]

mysql_user     = os.environ['MYSQL_USER']
mysql_password = os.environ['MYSQL_PASSWORD']
mysql_host     = os.environ['MYSQL_HOST']
mysql_port     = os.environ['MYSQL_PORT']
mysql_database = os.environ['MYSQL_DATABASE']

db = f"mysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
