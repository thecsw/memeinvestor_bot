import os

dry_run 		= int(os.environ['BOT_DRY_RUN'])

client_id 		= os.environ['BOT_CLIENT_ID']
client_secret 	= os.environ['BOT_CLIENT_SECRET']
user_agent 		= os.environ['BOT_USER_AGENT']

username 		= os.environ['BOT_USERNAME']
password 		= os.environ['BOT_PASSWORD']

subreddits 		= [os.environ['BOT_SUBREDDIT']]

MYSQL_USER 		= os.environ['MYSQL_USER']
MYSQL_PASSWORD 	= os.environ['MYSQL_PASSWORD']
MYSQL_HOST 		= os.environ['MYSQL_HOST']
MYSQL_PORT 		= os.environ['MYSQL_PORT']
MYSQL_DATABASE 	= os.environ['MYSQL_DATABASE']

db = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
