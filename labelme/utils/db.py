import sqlite3

from ..config import get_config

def open_db(path=None):

    config = get_config()

    if path is None:
        path = config["db_name"]

    conn = sqlite3.connect(path)

    # SEE: https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    return conn, c
