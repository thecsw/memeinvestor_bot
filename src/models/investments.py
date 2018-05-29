from models.base import BaseTable, timeframed


class Investments(BaseTable):
    _primkey = "id"
    _primkey_auto = True

    def __init__(self, db):
        super().__init__(db)
        # FOREIGN KEY(name) REFERENCES Investors(name) maybe?
        self._exec("""
            CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                post CHAR(11),
                upvotes INTEGER,
                comment CHAR(11),
                name VARCHAR(20),
                amount INTEGER,
                time INT DEFAULT (unix_timestamp(curtime())),
                done BIT DEFAULT 0,
                response CHAR(11),
                success BIT DEFAULT 0
            )
        """)
        self._dbconn.commit()

    def todo(self):
        self._exec("SELECT * FROM {table} WHERE (unix_timestamp(curtime()) - time) > 14400 AND (done = 0 OR done IS NULL)")
        return self._db.fetchall()

    def invested_coins(self):
        self._exec("SELECT COALESCE(SUM(amount),0) FROM {table} WHERE done = 0")
        return self._db.fetchone()[self._primkey]

    def active(self):
        self._exec("SELECT COUNT(id) FROM {table} WHERE done = 0")
        return self._db.fetchone()[self._primkey]

    @timeframed
    def total(self, qfrom, qto):
        self._exec("SELECT COUNT(id) FROM {table} WHERE {from} AND {to}", fmt={
            "from": qfrom,
            "to": qto
        })
        return self._db.fetchone()[self._primkey]
