import os
import json
import re
import logging
import datetime
import unicodedata
from bs4 import BeautifulSoup
try:
    import urllib.parse as urlparse
except:
    import urlparse
import collections
import itertools

date_style = 'full'
# date_style = 'timestamp'

def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

class Parser(object):
    def __init__(self, folder=None, files=None):
        self.folder = folder
        self.file_list = files

    def filter_func(self, filename):
        return True

    def parse_file_name(self, f):
        return NotImplementedError("")

    def parse_file(self, f):
        messages = []
        for line in f:
            match = re.match(self.regex, line)
            if not match:
                continue
            try:
                message = {
                    'timestamp':match.groups()[0],
                    'contact': match.groups()[1],
                    'message': match.groups()[2]
                }
                for msg_filter in self.filters:
                    message = msg_filter(message)
                if date_style == 'full':
                    ts = datetime.datetime.fromtimestamp(message['timestamp'])
                    message['timestamp'] = ts.isoformat()
                messages.append(message)
            except Exception as e:
                logging.warning("Error in file %s at line %s: %s", f.name,
                                line, str(e))
        return messages

    def files(self):
        """Generator that returns recursively all the files in a folder.

        If filter_func is given, only the ones for which it returns true will be
        returned. It should take one parameter, the name of the file.
        """
        if self.folder is not None:
            for root, dirs, files in os.walk(self.folder):
                for file in files:
                    f = os.path.join(root, file)
                    if self.filter_func(f):
                        yield f
                if '.git' in dirs:  # still needed?
                    logging.warning(dirs)
                    dirs.remove('.git')
        elif self.file_list is not None:
            for f in self.file_list:
                yield f
        else:
            raise Exception("You didn't specify source files")

    def __iter__(self):
        for f in self.files():
            logging.info("Got contact %s out of file %s",
                         self.parse_file_name(f), f)
            try:
                conversations = self.parse_file(open(f))
                if len(conversations):
                    yield (self.parse_file_name(f), conversations)
            except UnicodeDecodeError as e:
                logging.warning("Unicode !@#$ in file %s: %s", f, str(e))
            except IOError as e:
                logging.warning("Can't open file %s: %s", f, str(e))
                continue

def HTMLParse(msg):
    soup = BeautifulSoup(msg['message'], 'html.parser')
    msg['message'] = soup.get_text()
    return msg

def Unquote(msg):
    msg['message'] = urlparse.unquote(msg['message'])
    msg['contact'] = urlparse.unquote(msg['contact'])
    return msg

def DateToTS(fmt):
    def inner(msg):
        dt = datetime.datetime.strptime(msg['timestamp'], fmt)
        try:
            msg['timestamp'] = dt.timestamp()
        except:
            msg['timestamp'] = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
        return msg
    return inner

def FloatTimestamp(msg):
    msg['timestamp'] = float(msg['timestamp'])
    return msg

DateTimer = DateToTS("%d %b %Y %I:%M:%S %p")
ISOTimer = DateToTS("%Y-%m-%d %H:%M:%S")
USATimer = DateToTS("%m/%d/%Y, %I:%M %p")

class Digsby(Parser):

    def parse_file_name(self, filename):
        # The contact name is written in the last folder, followed by _protocol
        return "_".join(os.path.split(os.path.split(filename)[0])[1].split("_")[0:-1])

    regex = '<div class=".+? message" .+? timestamp="(.+?)"><span class="buddy">(.+?)</span> <span class="msgcontent">(.+?)</span>'
    filters = [HTMLParse, ISOTimer]

class Trillian(Parser):

    def filter_func(self, filename):
        root, ext = os.path.splitext(filename)
        return ext == '.xml' and root[-7:] != "-assets"

    def parse_file_name(self, filename):
        return os.path.splitext(os.path.split(filename)[1])[0]

    regex = '<message type=".+?_privateMessage(?:Offline)?" time="(.+?)" ms=".+?" medium=".+?" to=".+?" from="(.+?)" from_display=".+?" text="(.+?)"/>'
    filters = [Unquote, FloatTimestamp, HTMLParse]

class Pidgin(Parser):

    def parse_file_name(self, filename):
        return os.path.split(os.path.split(filename)[0])[1]

    regex = '<font color=".+?"><font size="2">\((\d\d:\d\d\:\d\d [AP]M)\)</font> <b>(.+?):</b></font>(.+?)<br/>'
    filters = [DateTimer, HTMLParse]

    def parse_file(self, f):
        head = f.readline()
        try:
            date = re.search('at [^ ]+ (\d{2} [a-zA-Z]* \d{4}) \d{2}:\d{2}:\d{2} [AP]M EEST', head).group(1)
        except AttributeError:
            logging.error("Couldn't find date in line %s", head)
        old_filters = self.filters[:]
        def correct_date(msg):
            msg['timestamp'] = "%s %s" % (date, msg['timestamp'])
            return msg
        self.filters.insert(0, correct_date)
        messages = super(Pidgin, self).parse_file(f)
        self.filters = old_filters
        return messages

def NameToDate(line):
    if line[0:2].isalpha() and line[4].isdigit() :
        sp = line.split(",", 1)
        date = datetime.datetime.strptime(sp[0], "%b %d")
        date = date.replace(year=2015)
        new_fmt = date.strftime("%m/%d/%Y")
        return "%s,%s" % (new_fmt, sp[1])
    return line

class Whatsapp(Parser):

    def parse_file_name(self, filename):
        """Filename is of the form with "WhatsApp Chat with NAME.txt"""""
        return filename[30:].split(".")[0]

    regex = '^(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2} [AP]M) - (.+?): (.+?)$'
    filters = [USATimer]

    def parse_file(self, f):
        messages = []
        for line in f:
            line = NameToDate(line)
            match = re.match(self.regex, line)
            if not match:
                message['message'] += "\n"+line
                continue
            try:
                message = {
                    'timestamp':match.groups()[0],
                    'contact': match.groups()[1],
                    'message': match.groups()[2]
                }
                for msg_filter in self.filters:
                    message = msg_filter(message)
                if date_style == 'full':
                    ts = datetime.datetime.fromtimestamp(message['timestamp'])
                    message['timestamp'] = ts.isoformat()
                messages.append(message)
            except Exception as e:
                logging.warning("Error in file %s at line %s: %s", f.name,
                                line, str(e))
        return messages


if __name__ == "__main__":
    messages = collections.defaultdict(list)
    # for contact, text in Digsby("./Digsby Logs"):
    #     messages[contact].append(text)
    # for contact, text in Trillian("./Trillian"):
    #     messages[contact].append(text)
    # for contact, text in Trillian("./Trillian2"):
    #     messages[contact].append(text)
    # for contact, text in Pidgin("./Pidgin"):
    #     messages[contact].append(text)
    for contact, text in Whatsapp("./Whatsapp"):
        messages[contact].append(text)
    for contact in messages:
        messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
        messages[contact].sort(key=lambda x: x['timestamp'])
    for k in messages:
        print k, len(messages[k])
    # print(messages['Eliza'])
    # f = open("./logs/messages.json", "w")
    # json.dump(messages, f, indent=2, ensure_ascii=False)
    # f.close()
