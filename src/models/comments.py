from models.base import BaseTable


class Comments(BaseTable):
    _primkey = "comment"

    def __init__(self, db):
        super().__init__(db)
        self._exec("""CREATE TABLE IF NOT EXISTS {table} (
                        comment CHAR(11) PRIMARY KEY UNIQUE
                    )""")
        self._dbconn.commit()

    def __setitem__(self, key, value):
        raise NotImplementedError()
