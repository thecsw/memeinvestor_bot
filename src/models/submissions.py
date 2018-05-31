from models.base import BaseTable


class Submissions(BaseTable):
    _primkey = "submission"

    def __init__(self, db):
        super().__init__(db)
        self._exec("""CREATE TABLE IF NOT EXISTS {table} (
                        submission CHAR(11) PRIMARY KEY UNIQUE
                    )""")
        self._dbconn.commit()

    def __setitem__(self, key, value):
        raise NotImplementedError()
