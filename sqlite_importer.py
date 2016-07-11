import logging
import parsers
import collections
import itertools
import json
from datetime import datetime
import sqlite3

def lines():
    for contact in messages:
        for line in messages[contact]:
            yield  (contact, line['contact'],line['timestamp'], line['source'],
                    line['protocol'],line['nick'],line['message'])

def grouper(n, iterable):
    it = iter(iterable)
    while True:
       chunk = tuple(itertools.islice(it, n))
       if not chunk:
           return
       yield chunk

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


sqlite_file = './messages.db'
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS messages')
c.execute('CREATE TABLE messages (contact TEXT, sender TEXT, datetime TEXT,'
        'source TEXT, protocol TEXT, nick TEXT, message TEXT)')

for gr in grouper(5000, lines()):
    conn.executemany("INSERT INTO messages (contact, sender, datetime, source,"
                "protocol, nick, message) values (?, ?, ?, ?, ?, ?, ?)", gr)
    print("Inserted 5000")

conn.commit()
conn.close()
