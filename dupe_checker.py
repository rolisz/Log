import logging
import parsers
import collections
import itertools
import json
from datetime import datetime

messages = collections.defaultdict(list)
# for contact, text in parsers.Digsby("./Digsby Logs"):
#     messages[contact].append(text)
# for contact, text in parsers.Trillian("./Trillian"):
#     messages[contact].append(text)
# for contact, text in parsers.Trillian("./Trillian2"):
#     messages[contact].append(text)
# for contact, text in parsers.Pidgin("./Pidgin"):
#     messages[contact].append(text)
for contact, text in parsers.Whatsapp("./Whatsapp"):
    messages[contact].append(text)
for contact, text in parsers.Facebook(files=["./Facebook/cleaned.html"]):
    messages[contact].append(text)
print("Done reading")

all_messages = set()
dupes = set()
for contact in messages:
    msgs = set()
    messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
    messages[contact].sort(key=lambda x: x['timestamp'])
    print(contact, len(messages[contact]))
    prev = False
    for msg in messages[contact]:
        message = msg['message']
        if message not in msgs:
            all_messages.add(message)
            msgs.add(message)
            prev = False
        else:
            if not prev:
                all_messages.add(message)
                if len(message) > 6:
                    prev = True
            else:
                prev = True
                dupes.add(message)

print(len(dupes))
print(len(all_messages))


# print(messages)
# for k in messages:
#     print k, len(messages[k])
# f = open("./logs/messages.json", "w")
# json.dump(messages, f, indent=2, ensure_ascii=False)
# f.close()

