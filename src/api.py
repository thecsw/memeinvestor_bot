import json
import time
import logging
import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func

import config
from models import Investor, Investment

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.db
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
CORS(app)


def get_pagination():
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


@app.route("/coins/invested")
def coins_invested():
    then = int(time.time()) - 14400
    res = db.session.query(func.coalesce(func.sum(Investment.amount), 0)).\
          filter(Investment.done == 0).filter(Investment.time < then).\
          scalar()
    return jsonify({"coins": str(res)})


@app.route("/coins/total")
def coins_total():
    res = db.session.query(func.coalesce(func.sum(Investor.balance), 0)).\
          scalar()
    return jsonify({"coins": str(res)})


@app.route("/investments")
def investments():
    time_from, time_to = get_timeframes()
    page, per_page = get_pagination()
    sql = db.session.query(Investment)

    if time_from > 0:
        sql = sql.filter(Investment.time > time_from)
    if time_to > 0:
        sql = sql.filter(Investment.time < time_to)

    sql_res = sql.order_by(Investment.id.desc()).\
              limit(per_page).offset(page*per_page).all()

    if not sql_res:
        return not_found("No investments found")

    res = [{
        "id": x.id,
        "post": x.post,
        "upvotes": x.upvotes,
        "name": x.name,
        "amount": x.amount,
        "time": x.time,
        "done": x.done,
        "response": x.response,
        "success": x.success,
    } for x in sql_res]

    return jsonify(res)


@app.route("/investments/active")
def investments_active():
    then = datetime.datetime.utcnow() - datetime.timedelta(hours=4)
    res = db.session.query(func.count(Investment.id)).\
          filter(Investment.done == 0).filter(Investment.time < then).\
          scalar()
    return jsonify({"investments": str(res)})


@app.route("/investments/amount")
def investments_amount():
    res = db.session.query(func.coalesce(func.sum(Investment.amount), 0))
    time_from, time_to = get_timeframes()

    if time_from > 0:
        res = res.filter(Investment.time > time_from)
    if time_to > 0:
        res = res.filter(Investment.time < time_to)

    return jsonify({"coins": str(res.scalar())})


@app.route("/investments/total")
def investments_total():
    res = db.session.query(func.count(Investment.id))
    time_from, time_to = get_timeframes()

    if time_from > 0:
        res = res.filter(Investment.time > time_from)
    if time_to > 0:
        res = res.filter(Investment.time < time_to)

    return jsonify({"investments": str(res.scalar())})


@app.route("/investors/top")
@app.route("/investors/top/<string:field>")
def investors_top(field="balance"):
    page, per_page = get_pagination()

    sql = db.session.query(Investor).order_by(desc(field)).\
          limit(per_page).offset(page*per_page).all()

    res = [{
        "name": x.name,
        "balance": x.balance,
        "completed": x.completed,
        "broke": x.broke,
    } for x in sql]

    return jsonify(res)


@app.route("/investor/<string:name>")
def investor(name):
    sql = db.session.query(Investor).\
        filter(Investor.name == name).\
        first()

    if not sql:
        return not_found("User not found")

    res = {
        "name": sql.name,
        "balance": sql.balance,
        "completed": sql.completed,
        "broke": sql.broke,
    }

    return jsonify(res)


@app.route("/investor/<string:name>/investments")
def investor_investments(name):
    page, per_page = get_pagination()
    time_from, time_to = get_timeframes()
    sql = db.session.query(Investment).\
        filter(Investment.name == name)

    if time_from > 0:
        sql = sql.filter(Investment.time > time_from)
    if time_to > 0:
        sql = sql.filter(Investment.time < time_to)

    sql_res = sql.order_by(Investment.id.desc()).\
              limit(per_page).offset(page*per_page).all()

    if not sql_res:
        return not_found("No investments found")

    res = [{
        "id": x.id,
        "post": x.post,
        "upvotes": x.upvotes,
        "name": x.name,
        "amount": x.amount,
        "time": x.time,
        "done": x.done,
        "response": x.response,
        "success": x.success,
    } for x in sql_res]

    return jsonify(res)



@app.route("/investor/<string:name>/active")
def investor_active(name):
    then = datetime.datetime.utcnow() - datetime.timedelta(hours=4)
    page, per_page = get_pagination()
    time_from, time_to = get_timeframes()
    sql = db.session.query(Investment).\
        filter(Investment.name == name).\
        filter(Investment.done == 0).\
        filter(Investment.time < then)

    if time_from > 0:
        sql = sql.filter(Investment.time > time_from)
    if time_to > 0:
        sql = sql.filter(Investment.time < time_to)

    sql_res = sql.order_by(Investment.id.desc()).\
              limit(per_page).offset(page*per_page).all()

    if not sql_res:
        return not_found("No investments found")

    res = [{
        "id": x.id,
        "post": x.post,
        "upvotes": x.upvotes,
        "name": x.name,
        "amount": x.amount,
        "time": x.time,
        "done": x.done,
        "response": x.response,
        "success": x.success,
    } for x in sql_res]

    return jsonify(res)


@app.route("/")
def index():
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


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=404, text=str(e)), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0")
