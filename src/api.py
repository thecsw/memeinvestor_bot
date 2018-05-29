import time
import logging

import MySQLdb
import MySQLdb.cursors
import _mysql_exceptions
from flask import Flask, jsonify, request

import config
import models

app = Flask(__name__)
db = None
investments = None
investors = None


@app.route('/market/invested_coins')
def invested_coins():
    return jsonify({'coins': str(investments.invested_coins())})


@app.route('/market/total_coins')
def total_coins():
    return jsonify({'coins': str(investors.total_coins())})


@app.route('/market/active_investments')
def active_investments():
    return jsonify({'investments': str(investments.active())})


@app.route('/market/total_investments')
def total_investments():
    time_from = int(request.args.get('from'))
    time_to = int(request.args.get('to'))

    return jsonify({'investments': str(investments.total(time_from=time_from, time_to=time_to))})


@app.route('/investors/top/<string:field>')
def top_investors(field):
    try:
        page = int(request.args.get('page'))
    except TypeError:
        page = 0

    try:
        per_page = int(request.args.get('per_page'))
    except TypeError:
        per_page = 100

    if per_page > 100 or per_page < 0:
        per_page = 100
    if page < 0:
        page = 0

    return jsonify({'investors' : investors.top(field, page=page, per_page=per_page)})


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=404, text=str(e)), 404


if __name__ == '__main__':
    while not db:
        try:
            db = MySQLdb.connect(cursorclass=MySQLdb.cursors.DictCursor, **config.dbconfig)
        except _mysql_exceptions.OperationalError:
            logging.warning("Waiting 10s for MySQL to go up...")
            time.sleep(10)

    investments = models.Investments(db)
    investors = models.Investors(db)

    app.run()
