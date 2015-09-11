
Message = namedtuple('Message', ['contact', 'timestamp', 'message'])

class Conversation(object):

    def __init__(self, messages):
        pass

    def _segment(self, break_length):
        """Splits the conversation up when a break longer than x happened"""

    def length(self):
        pass

    def ratio(self):
        pass

    def starters(self):
        pass

    def serialize(self):
        pass

    def deserialize(self):
        pass

    def dedupe(self):
        pass
