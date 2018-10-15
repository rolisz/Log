import logging
from pprint import pprint
import sqlite3
import collections
import itertools
import json
from datetime import datetime

con = sqlite3.connect("./data/processed/messages.db")
c = con.cursor()
l = c.execute(
    "select * from messages where contact IN (select contact from messages group by"
    " contact having count(contact) > 5000)")
messages = [
    {l.description[i][0]: v for i, v in enumerate(row)} for row in l.fetchall()
]

for k, g in itertools.groupby(messages, lambda msg: msg['contact']):
    g = list(g)
    g.sort(key=lambda x: x['datetime'])
    print(k, len(g))
    print(g[0]['datetime'])
    h = {}
    dupes = 0
    for msg in g:
        if msg['source'] == 'Whatsapp' or len(msg['message']) < 4\
            or sum(c.isalnum() for c in msg['message']) < 2:
            continue
        key = (msg['datetime'][:16], msg['sender'], msg['message'])
        if key in h:
            h[key].append((msg['datetime'], msg['message'], msg['source']))
            dupes += 1
        else:
            h[key] = [(msg['datetime'], msg['message'], msg['source'])]
    print(dupes)
    h = {k: v for k, v in h.items() if len(v) > 1}
    h = {k: v for k, v in h.items() if v[0][2] != v[1][2]}
    daily_map = {}
    for k in h:
        day = k[0][:10]
        if day not in daily_map:
            daily_map[day] = []
        daily_map[day].append((k[2], len(h[k])))
    # print(sum(len(v) for v in h.values()))
    # pprint(daily_map)
    print(len(daily_map))
    print(sum(len(daily_map[k]) for k in daily_map))

    # pprint(h)
