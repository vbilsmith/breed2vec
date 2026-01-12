import sqlite3
from breed2vec.config import DB_PATH

def connect_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    return con
