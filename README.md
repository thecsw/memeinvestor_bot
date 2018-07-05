# u/MemeInvestor_bot Documentation

## Contents

- [Welcome to meme investment!](#welcome-to-meme-investment)
- [Contributing](#contributing)
- [Investment behaviour](#investment-behaviour)
- [Commands](#commands)
- [Getting started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation and configuration](#installation-and-configuration)
- [Deployment](#deployment)
- [Source code](#source-code)
- [Authors](#authors)
- [License](#license)

## Welcome to meme investment!

Welcome to the source code repository of [u/MemeInvestor_bot](https://www.reddit.com/user/MemeInvestor_bot). 
This bot has been developed exclusively for [r/MemeEconomy](https://reddit.com/r/MemeEconomy/). It allows users
to create investment accounts with fictional MemeCoins, invest those MemeCoins in specific memes, and automatically
evaluate meme performance resulting in positive or negative returns.

The README below is a bit outdated. New version will be soon.

## Contributing

If you want to contribute, please do so! Check the [Issues](https://github.com/MemeInvestor/memeinvestor_bot/issues) list and help meme investments thrive!

## Commands

The bot has the following commands:

- `!create` - creates a bank account for you with a new balance of 1000
  MemeCoins.
- `!invest AMOUNT` - invests AMOUNT in the meme (post). 4 hours after the
  investment, the meme growth will be evaluated and your investment can profit
  you or make you bankrupt. Minimum possible investment is 100 MemeCoins.
- `!balance` - returns your current balance.
- `!active` - returns a number of active investments.
- `!broke` - only if your balance is less than 100 MemeCoins and you do not have
  any active investments, declares bankruptcy on your account and sets your
  balance to 100 MemeCoins (minimum possible investment). 
- `!market` - gives an overview for the whole Meme market.
- `!top` - gives a list of the users with the largest account balances.
- `!ignore` - ignores the whole message.
- `!help` - returns this help message.

To invoke a command, reply to either the top-level u/MemeInvestor_bot comment in the comment section of any
r/MemeEconomy post or to one of its subsequent replies to your command comment.

## Getting started 

These instructions will get you a copy of the project up and running on your
local machine for development and testing purposes.

### Prerequisites

In order to run this application, you need to install [Docker](https://www.docker.com/community-edition).

### Configuration

The only thing that needs to be done before execution is the config profile. For that please follow the
steps below:

```
git clone https://github.com/MemeInvestor/memeinvestor_bot.git
cd memeinvestor_bot
cp .env.example .env
nano .env
```

Follow the instructions in .env to configure your test deployment, save the file, and exit. You're
done with configuration.

### Deployment

From the root of the project directory, use `docker-compose build` followed by `docker-compose up -d`
to build and launch the various components of the bot, including an empty database of investor
accounts, the agents that monitor Reddit for new submissions and commands, and the informational
website.

You should be able to view the website at http://localhost:2015. By default the stats will be
boring (no investors and no investments) but you can interact with your test bot on Reddit to
populate the database, or you can manually set up investor accounts by interacting with the
database directly via Python code or a database manager like `adminer`.

## Built with
1. [praw](https://github.com/praw-dev/praw) an acronym for "Python Reddit API Wrapper",
is a python package that allows for simple access to Reddit's API.
2. [fastnumbers](https://pypi.org/project/fastnumbers/). Super-fast and clean conversions to numbers.
3. [Flask](http://flask.pocoo.org/) is a microframework for Python based on Werkzeug, Jinja 2 and good intentions.
4. [gunicorn](http://gunicorn.org/) is a Python WSGI HTTP Server for UNIX. 
5. [mysqlclient](https://github.com/PyMySQL/mysqlclient-python). MySQL database connector for Python (with Python 3 support).
6. [SQLAlchemy](http://www.sqlalchemy.org/) is the Python SQL toolkit and Object Relational Mapper that gives application
developers the full power and flexibility of SQL. 

## Authors

 - *Sagindyk Urazayev* - Core developer. Initial work & SQLite - [thecsw](https://github.com/thecsw)
 - *Dimitris Zervas* - Main back-end developer. MySQL, Docker, API and overall support - [dzervas](https://github.com/dzervas)
 - *jimbobur* - Our maths guy. Can make really pretty graphs - [jimbobur](https://github.com/jimbobur)
 - *Alberto Ventafridda* - Main front-end and web developer - [robalb](https://github.com/robalb)
 - *rickles42* - Back-end and infrastructure developer - [rickles42](https://github.com/rickles42)
 - *TwinProduction* - Heavy outside contributor - [TwinProduction](https://github.com/TwinProduction)
 - *ggppjj* - Minor fixes - [ggppjj](https://github.com/ggppjj)

## License

This project is licensed under the The GNU General Public License (see the
[LICENSE](./LICENSE) file for details), it explains everything pretty well.
