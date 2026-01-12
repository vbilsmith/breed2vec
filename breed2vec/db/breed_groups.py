import sqlite3
from breed2vec.db.connection import connect_db

def insert_breed_group(group_num: str, group_name: str, url: str) -> bool:
    sql = "INSERT INTO BreedGroups(groupNum, groupName, url) VALUES(?,?,?)"
    try:
        with connect_db() as con:
            con.execute(sql, (group_num, group_name, url))
        return True
    except sqlite3.IntegrityError:
        return False

def iter_breed_groups():
    with connect_db() as con:
        cur = con.execute("SELECT groupNum, url FROM BreedGroups")
        rows = cur.fetchall()
    yield from rows
