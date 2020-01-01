import sqlite3
from contextlib import closing

from ..config import get_config

def get_db_path()
    config = get_config()

    if path is None:
        path = config["db_name"]

    return path

def open_db(path=None):

    conn = sqlite3.connect(get_db_path())

    # SEE: https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    return conn, c

# FROM: https://stackoverflow.com/a/46519449
def query(self, sql):
    with closing(sqlite3.connect(get_db_path())) as con, con,  \
            closing(con.cursor()) as cur:
        cur.execute(sql)
        return cur.fetchall()

def dict_to_json_blob(dct):
    return json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')

