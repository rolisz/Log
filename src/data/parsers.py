import os
import warnings
import re
import html
import logging
import json
import datetime
import unicodedata
import traceback
from bs4 import BeautifulSoup
from lxml import etree
try:
    import urllib.parse as urlparse
except:
    import urlparse
import collections
import itertools


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
        contacts = set()
        for line in f:
            match = re.match(self.regex, line)
            if not match:
                continue
            try:
                message = {
                    'timestamp':match.groups()[0],
                    'contact': match.groups()[1],
                    'message': match.groups()[2],
                    'source': self.__class__.__name__
                }
                file_name = f.name.lower()
                if 'gmail' in file_name or 'google' in file_name:
                    # Because some of the Hangouts discussions in Trillian
                    # Have my email adress (but only mine) with a weird HEX
                    # suffix
                    if 'rolisz@gmail.com' in message['contact']:
                        message['contact'] = 'rolisz@gmail.com'
                    message['protocol'] = 'Hangouts'
                elif 'facebook' in file_name:
                    message['protocol'] = 'Facebook'
                elif 'yahoo' in file_name:
                    message['protocol'] = 'Yahoo'
                else:
                    print(file_name)
                for msg_filter in self.filters:
                    message = msg_filter(message)
                contact = message['contact']
                message['nick'] = message['contact']

                contacts.add(message['contact'])
                if type(message['timestamp']) == float:
                    message['timestamp'] = datetime.datetime.fromtimestamp(message['timestamp'])
                if type(message['timestamp']) == datetime.datetime:
                    message['timestamp'] = message['timestamp'].isoformat()
                messages.append(message)
            except Exception as e:
                logging.warning("Error in file %s at line %s: %s because %s", f.name,
                                line, str(e), traceback.format_exc())
        if len(messages) == 0:
            return
        return contacts, messages

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
            logging.info("Processing file %s", f)
            try:
                result = self.parse_file(open(f))
                if result:
                    yield result
            except UnicodeDecodeError as e:
                logging.warning("Unicode !@#$ in file %s: %s", f, str(e))
            except IOError as e:
                logging.warning("Can't open file %s: %s", f, str(e))
                continue

warnings.filterwarnings('ignore', ".+ looks like a URL. Beautiful Soup is not an HTTP client. .*")
warnings.filterwarnings('ignore', ".+ looks like a filename, not markup. You should probably open this file and pass the filehandle into Beautiful .*")

def DigsbyParser(msg):
    orig = msg['message']
    # Stupid hack for Yahoo emoticon that got XML-ified
    text = msg['message'].replace("<:-p></:-p>", "PRTY_EMOJI")
    soup = etree.HTML(text)
    if soup is not None:
        msg['message'] = soup.xpath("string()")
    msg['message'] = msg['message'].replace("PRTY_EMOJI", "<:-p")
    return msg

def HTMLParse(msg):
    soup = BeautifulSoup(msg['message'], 'html.parser')
    msg['message'] = soup.get_text()
    return msg

def Unquote(msg):
    msg['message'] = urlparse.unquote(msg['message'])
    msg['contact'] = urlparse.unquote(msg['contact'])
    return msg

def HTMLEscaper(msg):
    msg['message'] = html.unescape(msg['message'])
    return msg

def DateTimer(msg):
    dt = datetime.datetime.strptime(msg['timestamp'], "%d %b %Y %I:%M:%S %p")
    msg['timestamp'] = dt
    return msg

def FloatTimestamp(msg):
    msg['timestamp'] = float(msg['timestamp'])
    return msg

def ISOTimer(msg):
    msg['timestamp'] = msg['timestamp'].replace(" ", "T")
    return msg

am_conv = {'AM': 0,'PM': 12, 'am': 0, 'pm': 12}
def USATimer(ts):
    ts = ts.replace(',', '')
    if ts.count(" ") == 2:
        # %m/%d/%Y %I:%M %p
        date, time, am = ts.split(" ")
        month, day, year = date.split("/")
        hour, minute = time.split(":")
        year, month, day, minute = int(year), int(month), int(day), int(minute)
        if year < 2000:
            year += 2000
        hour = int(hour) % 12 + am_conv[am]
        second = 0
    else:
        # %d/%m/%y %H:%M:%S
        date, time = ts.split(" ")
        day, month, year = date.split("/")
        hour, minute, second = time.split(":")
        year, month, day = int(year) + 2000, int(month), int(day)
        hour, minute, second = int(hour), int(minute), int(second)
    return datetime.datetime(year, month, day, hour, minute, second)

class Digsby(Parser):

    regex = '<div class=".+? message" .+? timestamp="(.+?)"><span class="buddy">(.+?)</span> <span class="msgcontent">(.+?)</span>'
    filters = [DigsbyParser, ISOTimer]

class Trillian(Parser):

    def filter_func(self, filename):
        root, ext = os.path.splitext(filename)
        return ext == '.xml' and root[-7:] != "-assets"

    regex = '<message type=".+?_privateMessage(?:Offline)?" time="(.+?)" ms=".+?" medium=".+?" to=".+?" from="(.+?)" from_display=".+?" text="(.+?)"/>'
    # filters = [Unquote, FloatTimestamp, HTMLParse]
    filters = [Unquote, FloatTimestamp, HTMLEscaper]

class Pidgin(Parser):

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
    if len(line) < 8:
        return line
    try:
        if line[0:2].isalpha() and line[4].isdigit() and (line[7].isdigit() or line[8].isdigit()):
            sp = line.split(",", 1)
            date = datetime.datetime.strptime(sp[0], "%b %d")
            date = date.replace(year=2015)
            new_fmt = date.strftime("%m/%d/%Y")
            return "%s,%s" % (new_fmt, sp[1])
        return line
    except Exception as e:
        print(line)
        print(len(line))
        raise e

class Whatsapp(Parser):

    regex = '^(\d{1,2}/\d{1,2}/\d{2,4},? \d{1,2}:\d{2}(?::\d{2})?(?: [AP]M)?)(?: -|:) (.+?): (.+?)$'

    def parse_file(self, f):
        messages = []
        contacts = set()
        message = {'message': []}
        for line in f:
            line = NameToDate(line)
            match = re.match(self.regex, line)
            if not match:
                try:
                    # message['message'] += "\n"+line
                    message['message'].append(line)
                # If message has not been defined yet, we're at the beginning
                # of the file
                except UnboundLocalError:
                    pass
                continue
            message['message'] = "\n".join(message['message'])
            try:
                message = {
                    'timestamp': USATimer(match.groups()[0]).isoformat(),
                    'contact': match.groups()[1],
                    'message': [match.groups()[2]],
                    'protocol': 'Whatsapp',
                    'source': 'Whatsapp',
                    'nick': match.groups()[1],
                }
                contacts.add(message['contact'])
                messages.append(message)
            except Exception as e:
                logging.warning("Error in file %s at line %s: %s", f.name,
                                line, str(e))
        message['message'] = "\n".join(message['message'])
        if len(messages) == 0:
            return "", []
        return contacts, messages

    def filter_func(self, filename):
        root, ext = os.path.splitext(filename)
        return ext == '.txt'

months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June':6,
        'July':7, 'August': 8, 'September': 9, 'October': 10, 'November': 11,
        'December':12}
def parseDate(date):
    # "%A, %B %d, %Y at %I:%M%p"
    _, day, rest = date.split(",")
    month, day = day.strip().split()
    month, day = months[month], int(day)
    year, _, time = rest.strip().split()
    year = int(year)
    hour, minute = time[:-2].split(":")
    hour, minute = int(hour) % 12 + am_conv[time[-2:]], int(minute)
    return datetime.datetime(year, month, day, hour, minute, 0)

class Facebook(Parser):

    def __iter__(self):
        for filename in self.files():
            with open(filename) as f:
                file_content = f.read()
            soup = etree.HTML(file_content)
            logging.info("Finished loading HTML file %s", filename)
            threads = soup.cssselect('div.thread')
            for thread in threads:
                result = self.parse_thread(thread)
                if result:
                    yield result

    def parse_thread(self, thread):
        it = iter(thread.getchildren())
        contacts = set()
        # After that the children are: message_header,message in a p
        messages = []
        errors = 0
        for header, message in zip(it, it):
            try:
                user = header.cssselect('span.user')[0].text.strip()
                contacts.add(user)
            except Exception as e:
                logging.warning("Couldn't parse user %s because %s", etree.tostring(header), e)
                errors +=1
                continue
            try:
                date = header.cssselect('span.meta')[0].text.strip()[:-7]
                date = parseDate(date)
            except Exception as e:
                logging.warning("Couldn't parse date %s because %s", header, e)
                errors +=1
                continue
            try:
                message = message.text.strip()
            except Exception as e:
                logging.warning("Couldn't parse message %s because %s", message, e)
                errors +=1
                continue
            message = {
                'timestamp': date,
                'contact': user,
                'message': message,
                'protocol': 'Facebook',
                'source': 'Facebook',
                'nick': user,
            }
            message['timestamp'] = date.isoformat()
            messages.append(message)
            if errors > 15:
                logging.error("Too many errors for %s", contacts)
                break
        return contacts, reversed(messages)

class Hangouts(Parser):

    def __iter__(self):
        for filename in self.files():
            data = json.load(open(filename))['conversation_state']
            logging.info("Finished loading JSON file %s", filename)
            for contact in data:
                result = self.parse_thread(contact)
                if result:
                    yield result

    def parse_thread(self, thread):
        conv = thread["conversation_state"]["conversation"]
        participants = {}
        for part in conv["participant_data"]:
            if "fallback_name" in part:
                participants[part["id"]["gaia_id"]] = part["fallback_name"]
            else:
                participants[part["id"]["gaia_id"]] = ("Unknown_%s"
                        % part["id"]["gaia_id"])

        events = thread["conversation_state"]["event"]

        messages = []
        for event in events:
            gaia_id = event["sender_id"]["gaia_id"]
            if gaia_id in participants:
                sender = participants[gaia_id]
            else:
                sender = "Unknown_%s" % gaia_id
            date = datetime.datetime.fromtimestamp(float(event["timestamp"])/1000000)
            if event["event_type"] == "REGULAR_CHAT_MESSAGE":
                if "segment" in event["chat_message"]["message_content"]:
                    message = " ".join(p["text"]
                            for p in event["chat_message"]["message_content"]
                                ["segment"] if "text" in p)
                    messages.append({
                        'timestamp': date.isoformat(),
                        'contact': sender,
                        'message': message,
                        'protocol': 'Hangouts',
                        'source': 'Hangouts',
                        'nick': sender,
                    })
        return set(participants.values()), messages


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    messages = collections.defaultdict(list)
    # for contact, text in Digsby("./data/raw/Digsby Logs"):
    #     messages[frozenset(contact)].append(text)
    # print("Digsby")
    for contact, text in Trillian("./data/raw/Trillian"):
        messages[frozenset(contact)].append(text)
    print("Trillian")
    # for contact, text in Pidgin("./data/raw/Pidgin"):
    #     messages[frozenset(contact)].append(text)
    # print("Pidgin")
    # for contact, text in Whatsapp("./data/raw/Whatsapp"):
    #     messages[frozenset(contact)].append(text)
    # print("Whatsapp")
    # for contact, text in Facebook(files=["./data/interim/Facebook/cleaned.html"]):
    #     messages[frozenset(contact)].append(text)
    # print("Facebook")
    # for contact, text in Hangouts(files=["./data/raw/Hangouts/Hangouts.json"]):
    #     messages[frozenset(contact)].append(text)
    # print("Hangouts")
    for contact in messages:
        messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
        messages[contact].sort(key=lambda x: x['timestamp'])
    total = 0
    for k in messages:
        # print(k, len(messages[k]))
        total += len(messages[k])
    print(total)
    # f = open("./logs/messages.json", "w")
    # json.dump(messages, f, indent=2, ensure_ascii=False)
    # f.close()
