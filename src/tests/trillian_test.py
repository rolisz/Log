import unittest
import io
from src.data import parsers

conv = """<session type="start" time="1385563393" ms="559" medium="YAHOO" to="Person 1" from="Person 2"/>
<message type="outgoing_privateMessage" time="1385563396" ms="929" medium="YAHOO" to="Person 2" from="Person 1" from_display="Person 1" text="salut"/>
<message type="outgoing_privateMessage" time="1385563420" ms="355" medium="YAHOO" to="Person 2" from="Person 1" from_display="Person 1" text="imi%20poti%20trimite"/>
<message type="incoming_privateMessage" time="1385563548" ms="153" medium="YAHOO" to="Person 1" from="Person 2" from_display="Person 2" text="aicia"/>
<session type="stop" time="1385567767" medium="YAHOO" to="Person 1" from="Person 2"/>
"""

emojiLink = """<session type="start" time="1385563393" ms="559" medium="YAHOO" to="Person 1" from="Person 2"/>
<message type="outgoing_privateMessage" time="1385563396" ms="929" medium="YAHOO" to="Person 2" from="Person 1" from_display="Person 1" text=":p"/>
<message type="outgoing_privateMessage" time="1385563420" ms="355" medium="YAHOO" to="Person 2" from="Person 1" from_display="Person 1" text="%3C%3A-p"/>
<message type="incoming_privateMessage" time="1385563548" ms="153" medium="YAHOO" to="Person 1" from="Person 2" from_display="Person 2" text="%26gt%3B%3AD%26lt%3B"/>
<message type="outgoing_privateMessage" time="1346082561" ms="403" medium="YAHOO" to="Person 2" from="Person 1" from_display="Person 1" text="%3Ca%20href%3D%22http%3A%2F%2Fft%2Etrillian%2Eim%2F9e886c8deecf9ddc8aa38574089a032bdffe6ed5%2F6aexnjVRefl8Szc1Jo224sOujL283%2Ejpg%22%3Ehttp%3A%2F%2Fft%2Etrillian%2Eim%2F9e886c8deecf9ddc8aa38574089a032bdffe6ed5%2F6aexnjVRefl8Szc1Jo224sOujL283%2Ejpg%3C%2Fa%3E"/>
<session type="stop" time="1385567767" medium="YAHOO" to="Person 1" from="Person 2"/>
"""
class TrillianTest(unittest.TestCase):

    def setUp(self):
        self.trillian = parsers.Trillian()

    def testNormal(self):
        fake = io.StringIO(conv)
        fake.name = "me@yahoo.com"
        contacts, lines = self.trillian.parse_file(fake)
        self.assertSetEqual(contacts, {"Person 1", "Person 2"})
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0]['message'], "salut")
        self.assertEqual(lines[1]['contact'], "Person 1")
        self.assertEqual(lines[0]['protocol'], "Yahoo")
        self.assertEqual(lines[1]['source'], "Trillian")
        self.assertEqual(lines[0]['timestamp'], "2013-11-27T15:43:16")

    def testEmojis(self):
        fake = io.StringIO(emojiLink)
        fake.name = "me@yahoo.com"
        contacts, lines = self.trillian.parse_file(fake)
        self.assertSetEqual(contacts, {"Person 1", "Person 2"})
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0]['message'], ":p")
        self.assertEqual(lines[1]['message'], "<:-p")
        self.assertEqual(lines[2]['message'], ">:D<")
        # This can be also just the link, with the anchor tag stripped
        self.assertEqual(lines[3]['message'], '<a href="http://ft.trillian.im/9e886c8deecf9ddc8aa38574089a032bdffe6ed5/6aexnjVRefl8Szc1Jo224sOujL283.jpg">http://ft.trillian.im/9e886c8deecf9ddc8aa38574089a032bdffe6ed5/6aexnjVRefl8Szc1Jo224sOujL283.jpg</a>')
