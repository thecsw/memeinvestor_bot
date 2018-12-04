"""
json allows us to wrap database return into a json format
time allows us to compare times with the current time

flask is the basic way of webbing, haha

config has all our environmental configs
models has our db models
"""
import json
import time

from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func, and_

import config
from models import Investor, Investment
from formula import calculate

APP = Flask(__name__)
APP.config["SQLALCHEMY_DATABASE_URI"] = config.DB
APP.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
APP.config["SQLALCHEMY_POOL_RECYCLE"] = 60

# Create a simple cache to store the results of some of our API calls
CACHE = Cache(APP, config={'CACHE_TYPE': 'simple'})

DB = SQLAlchemy(APP)
CORS(APP)

def get_pagination():
    """
    Wraps pages
    """
    try:
        page = int(request.args.get("page"))
    except TypeError:
        page = 0

    try:
        per_page = int(request.args.get("per_page"))
    except TypeError:
        per_page = 100

    if per_page > 100 or per_page < 0:
        per_page = 100
    if page < 0:
        page = 0

    return (page, per_page)

def get_timeframes():
    try:
        time_from = int(float(request.args.get("from")))
    except (TypeError, ValueError):
        time_from = -1

    try:
        time_to = int(float(request.args.get("to")))
    except (TypeError, ValueError):
        time_to = -1

    return (time_from, time_to)

@APP.route("/coins/invested")
def coins_invested():
    """
    Returns all invested memecoins in the market
    """
    res = DB.session.query(func.coalesce(func.sum(Investment.amount), 0)).\
          filter(Investment.done == 0).scalar()
    return jsonify({"coins": str(res)})

@APP.route("/coins/total")
def coins_total():
    """
    Returns all active memecoins in the market
    """
    res = DB.session.query(func.coalesce(func.sum(Investor.balance), 0)).\
        scalar()
    return jsonify({"coins": str(res)})

@APP.route("/investments")
def investments():
    """
    Returns all investments
    """
    time_from, time_to = get_timeframes()
    page, per_page = get_pagination()
    sql = DB.session.query(Investment)

    if time_from > 0:
        sql = sql.filter(Investment.time > time_from)
    if time_to > 0:
        sql = sql.filter(Investment.time < time_to)

    sql_res = sql.order_by(Investment.id.desc()).\
              limit(per_page).offset(page*per_page).all()

    res = [{
        "id": x.id,
        "post": x.post,
        "upvotes": x.upvotes,
        "final_upvotes": x.final_upvotes,
        "name": x.name,
        "amount": x.amount,
        "time": x.time,
        "done": x.done,
        "response": x.response,
        "success": x.success,
        "profit": x.profit,
    } for x in sql_res]

    return jsonify(res)

@APP.route("/investments/active")
def investments_active():
    """
    Returns all active investments
    """
    res = DB.session.query(func.count(Investment.id)).\
          filter(Investment.done == 0).scalar()
    return jsonify({"investments": str(res)})

@APP.route("/investments/amount")
def investments_amount():
    """
    Returns investments coins
    """
    res = DB.session.query(func.coalesce(func.sum(Investment.amount), 0))
    time_from, time_to = get_timeframes()

    if time_from > 0:
        res = res.filter(Investment.time > time_from)
    if time_to > 0:
        res = res.filter(Investment.time < time_to)

    return jsonify({"coins": str(res.scalar())})

@APP.route("/investments/total")
def investments_total():
    """
    Returns number of investments
    """
    res = DB.session.query(func.count(Investment.id))
    time_from, time_to = get_timeframes()

    if time_from > 0:
        res = res.filter(Investment.time > time_from)
    if time_to > 0:
        res = res.filter(Investment.time < time_to)

    return jsonify({"investments": str(res.scalar())})


@APP.route("/investments/post/<string:id>")
def investments_post(id):
    """
    Returns all investments of a specific submission
    Takes a submission.id from praw
    """
    time_from, time_to = get_timeframes()
    page, per_page = get_pagination()

    sql = DB.session.query(Investment).\
        filter(Investment.post == id)

    if time_from > 0:
        sql = sql.filter(Investment.time > time_from)
    if time_to > 0:
        sql = sql.filter(Investment.time < time_to)

    sql_res = sql.order_by(Investment.time.desc()).\
              limit(per_page).offset(page*per_page).all()

    res = [{
        "id": x.id,
        "post": x.post,
        "upvotes": x.upvotes,
        "final_upvotes": x.final_upvotes,
        "name": x.name,
        "amount": x.amount,
        "time": x.time,
        "done": x.done,
        "response": x.response,
        "success": x.success,
        "profit": x.profit,
    } for x in sql_res]

    return jsonify(res)


@APP.route("/investors/top")
@CACHE.cached(timeout=10, query_string=True)
def investors_top():
    """
    Returns a list of tap investors (all-time)
    """
    page, per_page = get_pagination()

    sql = DB.session.query(
        Investor.name,
        Investor.balance,
        func.coalesce(Investor.balance+func.sum(Investment.amount), Investor.balance).label('networth'),
        Investor.completed,
        Investor.broke,
        Investor.badges).\
    outerjoin(Investment, and_(Investor.name == Investment.name, Investment.done == 0)).\
    group_by(Investor.name).\
    order_by(desc('networth')).\
    limit(per_page).\
    offset(page*per_page).\
    all()

    res = [{
        "name": x.name,
        "balance": x.balance,
        "networth": int(x.networth),
        "completed": x.completed,
        "broke": x.broke,
        "badges": json.loads(x.badges),
    } for x in sql]

    return jsonify(res)

@APP.route("/investors/last24")
@CACHE.cached(timeout=3600)
def investors_last24():
    """
    Returns top 5 investors in 24h
    """
    sql = DB.session.query(
        Investor.name,
        func.sum(Investment.profit).label('total_profit')
    ).\
    outerjoin(Investment, and_(
        Investor.name == Investment.name,
        Investment.done == 1,
        Investment.time > (time.time() - 86400),
        Investment.profit > 0)).\
    group_by(Investor.name).\
    order_by(desc('total_profit')).\
    limit(5).\
    all()

    res = [{
        "name": x.name,
        "profit": int(x.total_profit or 0)
    } for x in sql]

    return jsonify(res)

@APP.route("/investor/<string:name>")
def investor(name):
    """
    Returns basic info of a user
    """
    sql = DB.session.query(Investor).\
        filter(Investor.name == name).\
        first()

    if not sql:
        return not_found("User not found")

    actives_value = DB.session.query(func.coalesce(func.sum(Investment.amount), 0)).\
        filter(Investment.name == name).\
        filter(Investment.done == 0).\
        scalar()

    res = {
        "name": sql.name,
        "balance": sql.balance,
        "networth": int(sql.balance) + int(actives_value),
        "completed": sql.completed,
        "broke": sql.broke,
        "badges": json.loads(sql.badges),
    }

    return jsonify(res)

@APP.route("/investor/<string:name>/investments")
def investor_investments(name):
    """
    Returns all investments of a user
    """
    page, per_page = get_pagination()
    time_from, time_to = get_timeframes()
    sql = DB.session.query(Investment).\
        filter(Investment.name == name)

    if time_from > 0:
        sql = sql.filter(Investment.time > time_from)
    if time_to > 0:
        sql = sql.filter(Investment.time < time_to)

    sql_res = sql.order_by(Investment.id.desc()).\
              limit(per_page).offset(page*per_page).all()

    res = [{
        "id": x.id,
        "post": x.post,
        "upvotes": x.upvotes,
        "final_upvotes": x.final_upvotes,
        "name": x.name,
        "amount": x.amount,
        "time": x.time,
        "done": x.done,
        "response": x.response,
        "success": x.success,
        "profit": x.profit,
    } for x in sql_res]

    return jsonify(res)

@APP.route("/investor/<string:name>/active")
def investor_active(name):
    """
    Returns active investments of a user
    """
    page, per_page = get_pagination()
    time_from, time_to = get_timeframes()
    sql = DB.session.query(Investment).\
        filter(Investment.name == name).\
        filter(Investment.done == 0)

    if time_from > 0:
        sql = sql.filter(Investment.time > time_from)
    if time_to > 0:
        sql = sql.filter(Investment.time < time_to)

    sql_res = sql.order_by(Investment.id.desc()).\
              limit(per_page).offset(page*per_page).all()

    res = [{
        "id": x.id,
        "post": x.post,
        "upvotes": x.upvotes,
        "final_upvotes": x.final_upvotes,
        "name": x.name,
        "amount": x.amount,
        "time": x.time,
        "done": x.done,
        "response": x.response,
        "success": x.success,
        "profit": x.profit,
    } for x in sql_res]

    return jsonify(res)

@APP.route("/summary")
def index():
    """
    Just a summary
    """
    data = {
        "coins": {
            "invested": json.loads(coins_invested().get_data()),
            "total": json.loads(coins_total().get_data()),
        },
        "investments": {
            "active": json.loads(investments_active().get_data()),
            "total": json.loads(investments_total().get_data()),
        },
        "investors": {
            "top": json.loads(investors_top().get_data()),
        },
    }

    return jsonify(data)

@APP.route("/calculate")
def calculate_investment():
    """
    !!! DEPRECATED !!!
    Calculate investment
    """
    new = int(request.args.get('new'))
    old = int(request.args.get('old'))

    factor = calculate(new, old)

    res = {
        "factor": factor
    }

    return jsonify(res)

@APP.errorhandler(404)
def not_found(e):
    return jsonify(error=404, text=str(e)), 404


if __name__ == "__main__":
    APP.run(host="192.168.0.1")
