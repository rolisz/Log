import os
import re
import logging
import datetime


class Parser(object):
    def __init__(self, folder):
        self.folder = folder

    def filter_func(self, filename):
        return True

    def parse_file_name(self, f):
        return NotImplementedError("")

    def parse_file(self, f):
        return NotImplementedError("")

    def files(self):
        """Generator that returns recursively all the files in a folder.

        If filter_func is given, only the ones for which it returns true will be
        returned. It should take one parameter, the name of the file.
        """
        for root, dirs, files in os.walk(self.folder):
            for file in files:
                f = os.path.join(root, file)
                if self.filter_func(f):
                    yield f
            if '.git' in dirs:  # still needed?
                logging.warning(dirs)
                dirs.remove('.git')

    def __iter__(self):
        for f in self.files():
            logging.info("Got contact %s out of file %s",
                         self.parse_file_name(f), f)
            try:
                for message in self.parse_file(open(f)):
                    yield message
            except UnicodeDecodeError as e:
                logging.warning("Unicode !@#$ in file %s: %s", f, str(e))
            except IOError as e:
                logging.warning("Can't open file %s: %s", f, str(e))
                continue

class Digsby(Parser):

    def parse_file_name(self, filename):
        # The contact name is written in the last folder, followed by _protocol
        return os.path.split(os.path.split(filename)[0])[1].split("_")[0]

    def parse_file(self, f):
        for line in f:
            match = re.match('<div class=".+? message" .+? timestamp="(.+?)"><span class="buddy">(.+?)</span> <span class="msgcontent">(.+?)</span>', line)
            if not match:
                continue
            try:
                yield {
                    'timestamp': match.groups()[0],
                    'contact': match.groups()[1],
                    'message': match.groups()[2]
                }
            except Exception as e:
                logging.warning("Digsby error in file %s at line %s: %s",
                                f.name, line, str(e))

class Trillian(Parser):

    def filter_func(self, filename):
        root, ext = os.path.splitext(filename)
        return ext == '.xml' and root[-7:] != "-assets"

    def parse_file_name(self, filename):
        return os.path.splitext(os.path.split(filename)[1])[0]

    def parse_file(self, f):
        for line in f:
            match = re.match('<message type=".+?_privateMessage(Offline)?" time="(.+?)" ms=".+?" medium="(.+?)" to=".+?" from="(.+?)" from_display=".+?" text="(.+?)"/>', line)
            if not match:
                continue
            try:
                yield {
                    'timestamp':datetime.datetime.fromtimestamp(int(match.groups()[1])).isoformat(sep=" "),
                    'contact': match.groups()[3],
                    'message': match.groups()[4]
                }
            except Exception as e:
                logging.warning("Trillian error in file %s at line %s: %s",
                                f.name, line, str(e))

class Pidgin(Parser):

    def parse_file_name(self, filename):
        return os.path.split(os.path.split(filename)[0])[1]

    def parse_file(self, f):
        lines = f.readlines()
        head = lines[0]
        try:
            date = re.search('at [^ ]+ (\d{2} [a-zA-Z]* \d{4}) \d{2}:\d{2}:\d{2} [AP]M EEST', head).group(1)
        except AttributeError:
            logging.error("Couldn't find date in line %s", head)
        for line in lines[1:]:
            match = re.match('<font color=".+?"><font size="2">\((\d\d:\d\d\:\d\d [AP]M)\)</font> <b>(.+?)</b></font>(.+?)<br/>', line)
            if not match:
                continue
            try:
                yield {
                    'timestamp': "%s %s" % (date, match.groups(0)),
                    'contact': match.groups(1),
                    'message': match.groups(2)
                }
            except Exception as e:
                logging.warning("Pidgin error in file %s at line %s: %s",
                                f.name, line, str(e))

if __name__ == "__main__":
    for text in Digsby("./Digsby Logs"):
        print(str(text))
    for text in Trillian("./Trillian"):
        print(str(text))
    for text in Pidgin("./Pidgin"):
        print(str(text))
