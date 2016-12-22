import os
import warnings
import re
import logging
import datetime
import unicodedata
import traceback
from bs4 import BeautifulSoup
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
                try:
                    message['timestamp'] = datetime.datetime.fromtimestamp(message['timestamp'])
                except:
                    pass
                finally:
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
        msg['timestamp'] = dt
        return msg
    return inner

def FloatTimestamp(msg):
    msg['timestamp'] = float(msg['timestamp'])
    return msg

DateTimer = DateToTS("%d %b %Y %I:%M:%S %p")
ISOTimer = DateToTS("%Y-%m-%d %H:%M:%S")
DigsbyTimer = DateToTS("%Y-%m-%d %H:%M:%S")

def USATimer(msg):
    msg['timestamp'] = msg['timestamp'].replace(',', '')
    try:
        dt = datetime.datetime.strptime(msg['timestamp'], "%m/%d/%Y %I:%M %p")
    except Exception:
        dt = datetime.datetime.strptime(msg['timestamp'], "%d/%m/%y %H:%M:%S")

    msg['timestamp'] = dt
    return msg

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
    if len(line) < 8:
        return line
    try:
        if line[0:2].isalpha() and line[4].isdigit() and (line[7].isdigit() or line[8].isdigit()):
            sp = line.split(",", 1)
            date = datetime.datetime.strptime(sp[0], "%b %d")
            date = date.replace(year=2015)
            new_fmt = date.strftime("%m/%d/%Y")
            return "%s,%s" % (new_fmt, sp[1])
        line = re.sub("^(\d{1,2}/\d{1,2}/)(\d\d) (\d{1,2}:\d\d [AP]M)", "\\g<1>20\\2 \\3", line)
        return line
    except Exception as e:
        print(line)
        print(len(line))
        raise e

class Whatsapp(Parser):

    def parse_file_name(self, filename):
        """Filename is of the form with "WhatsApp Chat with NAME.txt"""""
        # Not on iOS backups
        return filename[30:].split(".")[0]

    regex = '^(\d{1,2}/\d{1,2}/\d{2,4},? \d{1,2}:\d{2}(?::\d{2})?(?: [AP]M)?)(?: -|:) (.+?): (.+?)$'
    filters = [USATimer]

    def parse_file(self, f):
        messages = []
        contacts = set()
        for line in f:
            line = NameToDate(line)
            match = re.match(self.regex, line)
            if not match:
                try:
                    message['message'] += "\n"+line
                # If message has not been defined yet, we're at the beginning
                # of the file
                except UnboundLocalError:
                    pass
                continue
            try:
                message = {
                    'timestamp':match.groups()[0],
                    'contact': match.groups()[1],
                    'message': match.groups()[2],
                    'protocol': 'Whatsapp',
                    'source': 'Whatsapp',
                    'nick': match.groups()[1],
                }
                for msg_filter in self.filters:
                    message = msg_filter(message)
                contacts.add(message['contact'])
                message['timestamp'] = message['timestamp'].isoformat()
                messages.append(message)
            except Exception as e:
                logging.warning("Error in file %s at line %s: %s", f.name,
                                line, str(e))
        if len(messages) == 0:
            return "", []
        return contacts, messages

    def filter_func(self, filename):
        root, ext = os.path.splitext(filename)
        return ext == '.txt'

class Facebook(Parser):

    def __iter__(self):
        for filename in self.files():
            with open(filename) as f:
                file_content = f.read()
            soup = BeautifulSoup(file_content, 'lxml')
            logging.info("Finished loading HTML file %s", filename)
            threads = soup.find_all(class_='thread')
            for thread in threads:
                result = self.parse_thread(thread)
                if result:
                    yield result

    def parse_thread(self, thread):
        it = iter(thread.children)
        # First child is just the names concatenated
        first = next(it)
        contacts = set(s.strip() for s in first.string.split(","))
        # After that the children are: message_header, new_line,
        # message in a p, new_line
        messages = []
        errors = 0
        for header, m1, message, m2 in zip(it, it, it, it):
            try:
                user = header.find(class_='user').string.strip()
                contacts.add(user)
            except Exception as e:
                logging.warning("Couldn't parse user %s because %s", header, e)
                errors +=1
                continue
            try:
                date = header.find(class_='meta').string.strip()[:-7]
                date = datetime.datetime.strptime(date, "%A, %B %d, %Y at %I:%M%p")
            except Exception as e:
                logging.warning("Couldn't parse date %s because %s", header, e)
                errors +=1
                continue
            try:
                message = message.string.strip()
            except Exception as e:
                logging.warning("Couldn't parse message %s because %s", message, e)
                print(m1,m2)
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    messages = collections.defaultdict(list)
    for contact, text in Digsby("./Digsby Logs"):
        messages[contact].append(text)
    # print("Digsby")
    # for contact, text in Trillian("./Trillian"):
    #     messages[contact].append(text)
    # print("Trillian")
    # for contact, text in Trillian("./Trillian2"):
    #     messages[contact].append(text)
    print("Trillian2")
    for contact, text in Pidgin("./Pidgin"):
        messages[contact].append(text)
    print("Pidgin")
    for contact, text in Whatsapp("./Whatsapp"):
        messages[contact].append(text)
    print("Whatsapp")
    # for contact, text in Facebook(files=["./Facebook/cleaned.html"]):
    #     messages[contact].append(text)
    for contact in messages:
        messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
        messages[contact].sort(key=lambda x: x['timestamp'])
    for k in messages:
        print(k, len(messages[k]))
    # f = open("./logs/messages.json", "w")
    # json.dump(messages, f, indent=2, ensure_ascii=False)
    # f.close()
