import unittest
import io
from src.data import parsers

conv = """<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8"><title>Conversation with Person 1 at Tue 31 Jul 2013 02:19:13 PM EEST on person2@gmail.com/ (jabber)</title></head><body><h3>Conversation with Person 1 at Tue 31 Jul 2012 02:19:13 PM EEST on person2@gmail.com/ (jabber)</h3>
<font color="#A82F2F"><font size="2">(02:19:32 PM)</font> <b>Person 1:</b></font> <html xmlns='http://jabber.org/protocol/xhtml-im'><body xmlns='http://www.w3.org/1999/xhtml'><span style='font-family: Arial; font-size: 10pt; color: #000000;'>Hello there</span></body></html><br/>
<font color="#16569E"><font size="2">(02:20:44 PM)</font> <b>person2@gmail.com/09AC6EA0:</b></font>...<br/>
<font color="#A82F2F"><font size="2">(02:30:43 PM)</font> <b>Person 1:</b></font> <html xmlns='http://jabber.org/protocol/xhtml-im'><body xmlns='http://www.w3.org/1999/xhtml'><span style='font-family: Arial; font-size: 10pt; color: #000000;'>what'sup</span></body></html><br/>
<font color="#16569E"><font size="2">(02:30:54 PM)</font> <b>person2@gmail.com/09AC6EA0:</b></font>riiight<br/>
<font color="#16569E"><font size="2">(04:48:09 PM)</font> <b>person2@gmail.com/09AC6EA0:</b></font> :&gt;:&gt;<br/>
<font color="#16569E"><font size="2">(04:42:11 PM)</font> <b>Person 1:</b></font> <a href="http://www.test.org">http://www.test.org</a><br/>
</body></html>
"""


class PidginTest(unittest.TestCase):

    def setUp(self):
        self.pidgin = parsers.Pidgin()

    def testNormal(self):
        fake = io.StringIO(conv)
        fake.name = "me@gmail.com"
        contacts, lines = self.pidgin.parse_file(fake)
        # Person 2 has address in messages. If ever changed to take contacts
        # from header, this test should change
        self.assertSetEqual(contacts,
                            {"Person 1", "person2@gmail.com/09AC6EA0"})
        self.assertEqual(len(lines), 6)
        # Has space prefix because of inline HTML. If ever looking into doing it
        # more correctly, this can go away too.
        self.assertEqual(lines[0]['message'], " Hello there")
        self.assertEqual(lines[1]['contact'], "person2@gmail.com/09AC6EA0")
        self.assertEqual(lines[0]['protocol'], "Hangouts")
        self.assertEqual(lines[1]['source'], "Pidgin")
        self.assertEqual(lines[0]['timestamp'], "2013-07-31T14:19:32")
        self.assertEqual(lines[4]['message'], " :>:>")
        self.assertEqual(lines[5]['message'], " http://www.test.org")
