# /u/MemeInvestor_bot Documentation

## Welcome to meme investment!

Welcome to the source code repository of [/u/MemeInvestor_bot](https://www.reddit.com/user/MemeInvestor_bot). 
This bot has been developed exclusively for [/r/MemeEconomy](https://reddit.com/r/MemeEconomy/). It allows users
to create investment accounts with fictional MemeCoins, invest those MemeCoins in specific memes, and automatically
evaluate meme performance resulting in positive or negative returns.

## Contributing

We welcome contributions from the public! If you'd like to help improve the bot, [please fork
our project](https://services.github.com/on-demand/github-cli/open-pull-request-github) and feel free to tackle any [Issues](https://github.com/MemeInvestor/memeinvestor_bot/issues).
We also welcome feedback in the form of new issues, so feel free to create new ones for discussion.

## Overview

The bot is implemented as a set of loosely-connected microservices written in Python and
deployed with Docker. Each component handles a single job, such as:

- Monitoring /r/MemeEconomy for new meme submissions
- Monitoring /r/MemeEconomy for new commands to the bot
- Running the database of investor and investment data
- Monitoring the database for matured investments
- Serving the website
- Serving the REST API that provides data to the website

The following instructions will get a copy of the project up and running on your local
machine for development and testing purposes.

## Prerequisites

In order to run the bot, you'll need to install [Docker](https://www.docker.com/community-edition).
You may also need to generate Reddit API credentials for the bot (see below).

## Configuration

After installing the prerequisites and cloning the project, you'll need to configure
the bot. To do so, copy the `.env.example` file to `.env` and open it in the editor
of your choice:

```
git clone https://github.com/MemeInvestor/memeinvestor_bot.git
cd memeinvestor_bot
cp .env.example .env
nano .env
```

Follow the instructions in `.env` to configure your test deployment. The instructions
include [steps for generating Reddit bot credentials](https://praw.readthedocs.io/en/latest/getting_started/quick_start.html), which are necessary for clients
to fully access the Reddit API.

Once you've finished, save `.env` and exit. You're now ready to deploy the bot locally.

## Deployment

From the root of the project directory, use `docker-compose build` to build all the
microservices described above. Then use `docker-compose up -d` to launch them. This
will spawn an empty investors database, spin up agents to monitor Reddit, and begin
serving the informational website.

You should be able to view the website at http://localhost:2015. By default the stats will be
boring (no investors and no investments) but you can interact with your test bot on Reddit to
populate the database. Alternatively you can manually set up investor accounts by modifying the
database with Python or a database manager like `adminer`.

## Built with

 - [praw](https://github.com/praw-dev/praw), a Python package that allows for simple access to Reddit's API.
 - [fastnumbers](https://pypi.org/project/fastnumbers/), super-fast and clean conversions to numbers.
 - [Flask](http://flask.pocoo.org/), a microframework for Python based on Werkzeug, Jinja 2 and good intentions.
 - [gunicorn](http://gunicorn.org/), a Python WSGI HTTP Server for UNIX.
 - [mysqlclient](https://github.com/PyMySQL/mysqlclient-python), a MySQL database connector for Python (with Python 3 support).
 - [SQLAlchemy](http://www.sqlalchemy.org/), a Python SQL toolkit and Object Relational Mapper. 

## Authors

 - *Sagindyk Urazayev* - Core developer. Founder. Server, database, and system maintainer. - [thecsw](https://github.com/thecsw)
 - *Dimitris Zervas* - Main back-end developer. Wrote our API module and introduced Docker. - [dzervas](https://github.com/dzervas)
 - *jimbobur* - Our maths guy. Can make really pretty graphs. - [jimbobur](https://github.com/jimbobur)
 - *Alberto Ventafridda* - Main front-end and web developer. Made our beautiful website. - [robalb](https://github.com/robalb)
 - *rickles42* - Back-end and infrastructure developer. Heavy new features and debugging. - [rickles42](https://github.com/rickles42)
 - *TwinProduction* - Heavy outside contributor. - [TwinProduction](https://github.com/TwinProduction)

## License

This project is licensed under the The GNU General Public License (see the
[LICENSE](./LICENSE) file for details), it explains everything pretty well.
