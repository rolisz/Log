import logging
import collections
import datetime

Message = collections.namedtuple('Message',
                                 ['datetime', 'contact', 'sender', 'message'])


class Conversation(object):

    def __init__(self, messages, me="Roland Szabo"):
        self.me = me
        self.contacts = set(m.sender for m in messages)
        self.participants = self.contacts.copy()
        try:
            self.contacts.remove(me)
        except KeyError:
            logging.info("Found discussion where you're not talking at all!")
        self.messages = messages

    def conversations(self, break_length=7200):
        """Splits the conversation up when a break longer than break_length in seconds happened"""
        conv = []
        prev_timestamp = 0
        curr_conv = []
        for message in self.messages:
            ts = time.mktime(
                time.strptime(message.datetime, '%Y-%m-%dT%H:%M:%S'))
            if ts - prev_timestamp > break_length:
                if len(curr_conv):  # Should be empty only for the first list
                    conv.append(Conversation(curr_conv, self.me))
                curr_conv = []
            curr_conv.append(message)
            prev_timestamp = ts
        if len(curr_conv):
            conv.append(Conversation(curr_conv, self.me))
        return conv

    def char_length(self):
        lengths = collections.defaultdict(int)
        for reply in self.messages:
            lengths[reply.sender] += len(reply.message)
        return lengths

    def reply_length(self):
        lengths = collections.defaultdict(int)
        for reply in self.messages:
            lengths[reply.sender] += 1
        return lengths

    def avg_reply_length(self):
        lengths = collections.defaultdict(int)
        counts = collections.defaultdict(int)
        avgs = {}
        for reply in self.messages:
            counts[reply.sender] += 1
            lengths[reply.sender] += len(reply.message)
        for name in lengths:
            avgs[name] = lengths[name] / counts[name]
        return avgs

    def char_ratio(self):
        """Return the ratio between 'me' and how much others wrote"""
        chars = self.char_length()
        return sum(chars[o] for o in self.contacts) / chars[self.me]

    def char_percentage(self):
        """Returns the percentage from the total how much each participant wrote."""
        chars = self.char_length()
        total = sum(chars.values())
        return {c: chars[c] / total for c in self.participants}

    def reply_ratio(self):
        chars = self.reply_length()
        return sum(chars[o] for o in self.contacts) / chars[self.me]

    def reply_percentage(self):
        """Returns the percentage from the total how much each participant wrote."""
        chars = self.reply_length()
        total = sum(chars.values())
        return {c: chars[c] / total for c in self.participants}

    def __len__(self):
        return sum(len(m.message) for m in self.messages)

    def days(self):
        """Returns the messages grouped by days, as Conversation objects"""
        days = collections.defaultdict(list)
        for message in self.messages:
            day = message.datetime[:10]
            days[day].append(message)
        for day in days:
            days[day] = Conversation(days[day], self.me)
        return days

    def __str__(self):
        return "Participants: %s. Messages: %s" % (self.participants,
                                                   len(self.messages))

    __repr__ = __str__

    def average_gap(self):
        """Returns the average number of seconds between messages."""
        gaps = self.gaps()
        if len(gaps) == 0:
            return 0
        return sum(gaps) / len(gaps)

    def gaps(self):
        gaps = []
        for i in range(1, len(self.messages)):
            ts1 = time.mktime(
                time.strptime(self.messages[i - 1].datetime,
                              '%Y-%m-%dT%H:%M:%S'))
            ts2 = time.mktime(
                time.strptime(self.messages[i].datetime, '%Y-%m-%dT%H:%M:%S'))
            gaps.append(ts2 - ts1)
        return gaps

    def starters(self):
        pass

    def serialize(self):
        pass

    def deserialize(self):
        pass

    def dedupe(self):
        pass
