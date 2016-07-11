from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import DocType, String, Date, Integer
from elasticsearch_dsl.connections import connections
import logging
import parsers
import collections
import itertools
import json
from datetime import datetime

# logging.basicConfig(level=logging.INFO)
messages = collections.defaultdict(list)
for contact, text in parsers.Digsby("./Digsby Logs"):
    messages[contact].append(text)
print("Digsby")
for contact, text in parsers.Trillian("./Trillian"):
    messages[contact].append(text)
print("Trillian")
for contact, text in parsers.Trillian("./Trillian2"):
    messages[contact].append(text)
print("Trillian")
for contact, text in parsers.Pidgin("./Pidgin"):
    messages[contact].append(text)
print("Pidgin")
for contact, text in parsers.Whatsapp("./Whatsapp"):
    messages[contact].append(text)
print("Whatsapp")
for contact, text in parsers.Facebook(files=["./Facebook/cleaned.html"]):
    messages[contact].append(text)
print("Facebook")
for contact in messages:
    messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
    messages[contact].sort(key=lambda x: x['timestamp'])
print("Sorting")

# print(messages)
# for k in messages:
#     print k, len(messages[k])
# print(messages['Eliza'])
# f = open("./logs/messages.json", "w")
# json.dump(messages, f, indent=2, ensure_ascii=False)
# f.close()


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
    length = Integer()

    class Meta:
        index = 'chat'

    def save(self, ** kwargs):
        self.length = len(self.message)
        return super(Message, self).save(** kwargs)

# create the mappings in elasticsearch
Message.init()
es = Elasticsearch()

def lines():
    for contact in messages:
        for line in messages[contact]:
            yield {'_op_type': 'index', '_index': 'chat', '_type': 'message',
                    'message': line['message'], 'contact': contact,
                    'sender': line['contact'], 'datetime': line['timestamp'],
                    'protocol': line['protocol'], 'source': line['source'],
                    'length': len(line['message']), 'nick': line['nick']}

bulk(es,lines())

# Display cluster health
print(connections.get_connection().cluster.health())
