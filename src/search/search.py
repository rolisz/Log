import os
import logging
import collections
import itertools
import sqlite3
# from src.data import mappings
# from src.data.mappings import canonicalize
import sys
import datetime


sqlite_path = "/home/rolisz/Projects/Log/data/processed/messages2.db"
conn = sqlite3.connect(sqlite_path)

c = conn.cursor()
c2 = conn.cursor()

query = ('%%%s%%' % sys.argv[1], )

for contact, date in c.execute("SELECT contact, datetime FROM messages WHERE message LIKE ?", query):
    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
    start_date = (date - datetime.timedelta(seconds=600)).isoformat()
    end_date = (date + datetime.timedelta(seconds=600)).isoformat()
    print("orig", contact, date, start_date, end_date)
    for row in c2.execute("SELECT * FROM messages WHERE contact=? AND datetime > ?\
            AND datetime < ?", (contact, start_date, end_date)):
        print(row)

