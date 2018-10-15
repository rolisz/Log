from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import DocType, String, Date, Integer
from elasticsearch_dsl.connections import connections
import logging
import sqlite3
import parsers
import collections
import itertools
import json
from datetime import datetime
import mappings

# logging.basicConfig(level=logging.INFO)
# messages = collections.defaultdict(list)
# for contact, text in parsers.Digsby("./data/raw/Digsby Logs"):
#     messages[contact].append(text)
# print("Digsby")
# for contact, text in parsers.Trillian("./data/raw/Trillian"):
#     messages[contact].append(text)
# print("Trillian")
# for contact, text in parsers.Pidgin("./data/raw/Pidgin"):
#     messages[contact].append(text)
# print("Pidgin")
# for contact, text in parsers.Whatsapp("./data/raw/Whatsapp"):
#     messages[contact].append(text)
# print("Whatsapp")
# for contact, text in parsers.Facebook(files=["./data/interim/Facebook/cleaned.html"]):
#     messages[contact].append(text)
# print("Facebook")
# for contact in messages:
#     messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
#     messages[contact].sort(key=lambda x: x['timestamp'])
# print("Sorting")

# print(messages)
# for k in messages:
#     print k, len(messages[k])
# f = open("./logs/messages.json", "w")
# json.dump(messages, f, indent=2, ensure_ascii=False)
# f.close()

conn = sqlite3.connect("data/interim/messages.db")

conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM messages")
rows = cur.fetchall()
# Define a default Elasticsearch client
connections.create_connection(hosts=['localhost'])


class Message(DocType):
    message = String()
    contact = String(index="not_analyzed")
    sender = String(index="not_analyzed")
    datetime = Date()
    source = String(index="not_analyzed")
    protocol = String(index="not_analyzed")
    nick = String(index="not_analyzed")
    gender = String(index="not_analyzed")
    length = Integer()
    friendship = Integer()
    age_group = Integer()

    class Meta:
        index = 'chat'

    def save(self, **kwargs):
        self.length = len(self.message)
        return super(Message, self).save(**kwargs)


# create the mappings in elasticsearch
Message.init()
es = Elasticsearch()


def lines():
    for row in rows:
        d = {k: row[k] for k in row.keys()}
        d['_op_type'] = 'index'
        d['_index'] = 'chat'
        d['_type'] = 'message'
        yield d


bulk(es, lines())

# Display cluster health
print(connections.get_connection().cluster.health())
