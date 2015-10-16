import logging
import collections
import datetime

Message = collections.namedtuple('Message', ['contact', 'timestamp', 'message'])

class Conversation(object):

    def __init__(self, messages, me="Roland Szabo", other=None):
        if type(messages[0]) == dict:
            messages = [Message(**m) for m in messages]
        contacts = set(m.contact for m in messages)
        self.me = me
        if other is not None:
            self.other = other
        else:
            try:
                contacts.remove(me)
                self.other = contacts.pop()
            except KeyError:
                logging.warning("Couldn't identify conversation participants: %s",
                                contacts)
        self.messages = messages

    def _segment(self, break_length):
        """Splits the conversation up when a break longer than x happened"""

    def char_length(self):
        lengths = collections.defaultdict(int)
        for reply in self.messages:
            lengths[reply.contact] += len(reply.message)
        return lengths

    def reply_length(self):
        lengths = collections.defaultdict(int)
        for reply in self.messages:
            lengths[reply.contact] += 1
        return lengths

    def avg_reply_length(self):
        lengths = collections.defaultdict(int)
        counts = collections.defaultdict(int)
        avgs = {}
        for reply in self.messages:
            counts[reply.contact] += 1
            lengths[reply.contact] += len(reply.message)
        for name in lengths:
            avgs[name] = lengths[name]*1.0/counts[name]
        return avgs

    def char_ratio(self):
        chars = self.char_length()
        return chars[self.other]*1.0/chars[self.me]

    def reply_ratio(self):
        chars = self.reply_length()
        return chars[self.other]*1.0/chars[self.me]

    def __len__(self):
        return sum(len(m.message) for m in self.messages)

    def days(self):
        """Returns the messages grouped by days, as Conversation objects"""
        days = collections.defaultdict(list)
        for message in self.messages:
            day = message.timestamp.strftime("%Y-%m-%d")
            days[day].append(message)
        for day in days:
            days[day] = Conversation(days[day], self.me, self.other)
        return days

    def starters(self):
        pass

    def serialize(self):
        pass

    def deserialize(self):
        pass

    def dedupe(self):
        pass


if __name__ == "__main__":
    import parsers
    import itertools
    messages = collections.defaultdict(list)
    for contact, text in parsers.Whatsapp("./Whatsapp"):
        messages[contact].append(text)
    for contact in messages:
        messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
        messages[contact].sort(key=lambda x: x['timestamp'])
    # for k in messages:
    #     print k, len(messages[k])
    # for k in messages:
    #     print k, Conversation(messages[k]).reply_ratio()
    # for k in messages:
    #     print k, Conversation(messages[k]).char_ratio()
    # for k in messages:
    #     print k, len(Conversation(messages[k]).days().values()[-1])
