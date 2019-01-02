# Welcome to meme investments!

Welcome to the source code repository of [/u/MemeInvestor_bot](https://www.reddit.com/user/MemeInvestor_bot). 
This bot has been developed exclusively for [/r/MemeEconomy](https://reddit.com/r/MemeEconomy/). It allows users
to create investment accounts with fictional MemeCoins, invest those MemeCoins in specific memes, and automatically
evaluate meme performance resulting in positive or negative returns.

# 1 Contributing

We welcome contributions from the public! If you'd like to help improve the bot, please fork
our project and feel free to tackle any [Issues](https://github.com/MemeInvestor/memeinvestor_bot/issues).
We also welcome feedback in the form of new issues, so feel free to create new ones for discussion.

[![Waffle.io - Columns and their card count](https://badge.waffle.io/MemeInvestor/memeinvestor_bot.svg?columns=all)](https://waffle.io/MemeInvestor/memeinvestor_bot)

# 2 Overview

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

# 3 Prerequisites

In order to run the bot, you'll need to install [Docker](https://www.docker.com/community-edition).
You may also need to generate Reddit API credentials for the bot (see below).

# 4 Configuration

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
include steps for generating Reddit bot credentials, which are necessary for clients
to fully access the Reddit API.

Once you've finished, save `.env` and exit. You're now ready to deploy the bot locally.

# 5 Deployment

From the root of the project directory, use `docker-compose build` to build all the
microservices described above. Then use `docker-compose up -d` to launch them. This
will spawn an empty investors database, spin up agents to monitor Reddit, and begin
serving the informational website.

You should be able to view the website at http://localhost:2015. By default the stats will be
boring (no investors and no investments) but you can interact with your test bot on Reddit to
populate the database. Alternatively you can manually set up investor accounts by modifying the
database with Python or a database manager like `adminer`.

# 6 Maintenance

## Backing up the database

With the setup dockerized environment should work autonomously and non-stop. However, I would highly
recommend to make regular database backups with our `backup.sh` script. The best way to do it is to
install a cron job and make it run daily.

Here is the cron job that is running on our production server with crontab

``` bash
0 0 * * * /path/to/memeinvestor_bot/backup.sh /path/to/memeinvestor_bot/backups
```

This job will be triggered every day at exactly 0 minutes and 0 hours.

## Updating the deployment

Important thing is how you update the production database with the git repository. Here is the general way
to do it.

``` bash
git pull
docker-compose build
docker-compose up -d
```

It pulls the git repository, please make sure that you have the `origin` remote pointing to `https://github.com/MemeInvestor/memeinvestor_bot`
After that it rebuilds all images and replaces the currently running ones with the freshly built. All the database
data and other running containers' data will be safe in docker volumes. Do not forget to get rid of orphan images by `docker image prune`

And after that you can start tailing logs to see if everything is working smoothly with `docker-compose logs -f --tail 10`
Also, you can build individual modules by appending their alias to the `docker-compose` commands.

## Working with the website container

**Warning!** When you rebuild your containers all the logs are lost. If you want to save them and especially the HTTP logs to track the
website's stats, please follow the steps below to update HTTP separately and you can just append all other containers' names to the
build procedure above

``` bash
docker logs memeinvestor_bot_http_1 | tee -a ./http.log
docker-compose build http
docker-compose up -d http
```

Logs are saved to `http.log` that you can visualize them with `goaccess` and our `.goaccess.caddy.conf`

``` bash
goaccess -f ./http.log -p ~/.goaccess.caddy.conf -o html > /tmp/report.html
```

Feel free to open the produced html file with any compatible browser. Even Netscape.

# 7 Built with

  - [praw](https://github.com/praw-dev/praw), a Python package that allows for simple access to Reddit's API.
  - [fastnumbers](https://pypi.org/project/fastnumbers/), super-fast and clean conversions to numbers.
  - [Flask](http://flask.pocoo.org/), a microframework for Python based on Werkzeug, Jinja 2 and good intentions.
  - [gunicorn](http://gunicorn.org/), a Python WSGI HTTP Server for UNIX.
  - [mysqlclient](https://github.com/PyMySQL/mysqlclient-python), a MySQL database connector for Python (with Python 3 support).
  - [SQLAlchemy](http://www.sqlalchemy.org/), a Python SQL toolkit and Object Relational Mapper. 

# 8 Contributions

MemeInvestor_bot is a community-driven and community-supported project. We need *you* to keep it live and well. Thank you for all your support!

Here is a graph of some recent contributions:

[![Throughput Graph](https://graphs.waffle.io/MemeInvestor/memeinvestor_bot/throughput.svg)](https://waffle.io/MemeInvestor/memeinvestor_bot/metrics/throughput)

# 9 Authors

## Active contributors

  - *Sagindyk Urazayev* - Core developer. Founder. Server, database, and system maintainer. - [thecsw](https://github.com/thecsw)
  - *Alberto Ventafridda* - Main front-end and web developer. Made our beautiful website. - [robalb](https://github.com/robalb)

## Past contributors

  - *Dimitris Zervas* - Main back-end developer. Wrote our API module and introduced Docker. - [dzervas](https://github.com/dzervas)
  - *jimbobur* - Our maths guy. Can make really pretty graphs. - [jimbobur](https://github.com/jimbobur)
  - *rickles42* - Back-end and infrastructure developer. Heavy new features and debugging. - [rickles42](https://github.com/rickles42)
  - *TwinProduction* - Heavy outside contributor. - [TwinProduction](https://github.com/TwinProduction)
  - *Leo Wilson* - Ported our calculator to locally executed javascript.- [leomwilson](https://github.com/leomwilson)
  - *tcmal* - Added the daily profit ticker to our website.- [tcmal](https://github.com/tcmal)
  - *Matthew Sanetra* - Added suffixes support to the invest commands.- [matthewsanetra](https://github.com/matthewsanetra)
  - *Dylan Hanson* - Various contributions to the API module.- [jovialis](https://github.com/jovialis)

# 10 License

This project is licensed under the The GNU General Public License (see the [LICENSE](./LICENSE) file for details), it explains everything pretty well.
