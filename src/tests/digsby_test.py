import unittest
import io
from src.data import parsers

conv = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd">
<HTML>
   <HEAD>
      <meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
      <TITLE>IM Logs with -person1@chat.facebook.com on 2011-01-17</TITLE>
   </HEAD>
   <BODY onload="utc_to_local()">
<div class="outgoing message" auto="False" timestamp="2011-01-17 17:23:58"><span class="buddy">person2@chat.facebook.com</span> <span class="msgcontent"><span style="font-family: arial; font-size: 10pt; color: #000000;">serus</span></span></div>
<div class="outgoing message" auto="False" timestamp="2011-01-17 17:24:00"><span class="buddy">person2@chat.facebook.com</span> <span class="msgcontent"><span style="font-family: arial; font-size: 10pt; color: #000000;">ce faci?</span></span></div>
<div class="incoming message" auto="False" timestamp="2011-12-25 20:59:53"><span class="buddy">-person1@chat.facebook.com</span> <span class="msgcontent">bine</span></div>
<div class="incoming message" auto="False" timestamp="2011-12-25 20:59:54"><span class="buddy">-person1@chat.facebook.com</span> <span class="msgcontent">&gt;:D&lt;</span></div>
"""


class DigsbyTest(unittest.TestCase):

    def setUp(self):
        self.digsby = parsers.Digsby()

    def testNormal(self):
        fake = io.StringIO(conv)
        fake.name = "me@facebook.com"
        contacts, lines = self.digsby.parse_file(fake)
        self.assertSetEqual(
            contacts,
            {"-person1@chat.facebook.com", "person2@chat.facebook.com"})
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0]['message'], "serus")
        self.assertEqual(lines[1]['contact'], "person2@chat.facebook.com")
        self.assertEqual(lines[0]['protocol'], "Facebook")
        self.assertEqual(lines[1]['source'], "Digsby")
        self.assertEqual(lines[0]['timestamp'], "2011-01-17T17:23:58")
        self.assertEqual(lines[3]['message'], ">:D<")
