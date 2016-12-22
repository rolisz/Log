import unittest
from src.data import parsers

# Exported from Android in 2015 until about July
no_year_format = """Jun 17, 9:47 PM - Person 1: Hello
Jul 18, 3:58 PM - Person 2: Hi""".splitlines()

# Exported from Android from July 2015
month_day_format = """7/1/15 10:44 PM - Person 1: What's up?
7/1/15 10:45 PM - Person 2: Nothing
7/1/15 10:45 PM - Person 2: With you""".splitlines()

# Exported from iOS from February 2016
day_month_format = """04/03/16 00:50:41: Person 1: Bye
04/03/16 10:24:13: Person 2: Auf wiedersehen.""".splitlines()

multiline_message = """11/11/16 23:37:55: Person 1: Long
Message

Is
Long""".splitlines()
class WhatsappTest(unittest.TestCase):

    def setUp(self):
        self.whatsapp = parsers.Whatsapp()

    def testNoYear(self):
        contacts, lines = self.whatsapp.parse_file(no_year_format)
        self.assertSetEqual(contacts, {"Person 1", "Person 2"})
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]['message'], "Hello")
        self.assertEqual(lines[1]['contact'], "Person 2")
        self.assertEqual(lines[0]['protocol'], "Whatsapp")
        self.assertEqual(lines[1]['source'], "Whatsapp")
        self.assertEqual(lines[0]['timestamp'], "2015-06-17T21:47:00")

    def testMonthDay(self):
        contacts, lines = self.whatsapp.parse_file(month_day_format)
        self.assertSetEqual(contacts, {"Person 1", "Person 2"})
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0]['message'], "What's up?")
        self.assertEqual(lines[2]['contact'], "Person 2")
        self.assertEqual(lines[1]['timestamp'], "2015-07-01T22:45:00")
        self.assertEqual(lines[0]['timestamp'], "2015-07-01T22:44:00")

    def testDayMonth(self):
        contacts, lines = self.whatsapp.parse_file(day_month_format)
        self.assertSetEqual(contacts, {"Person 1", "Person 2"})
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[1]['message'], "Auf wiedersehen.")
        self.assertEqual(lines[0]['contact'], "Person 1")
        self.assertEqual(lines[0]['timestamp'], "2016-03-04T00:50:41")
        self.assertEqual(lines[1]['timestamp'], "2016-03-04T10:24:13")

    def testMultiline(self):
        contacts, lines = self.whatsapp.parse_file(multiline_message)
        self.assertSetEqual(contacts, {"Person 1"})
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]['timestamp'], "2016-11-11T23:37:55")
        self.assertEqual(lines[0]['message'], "Long Message Is Long")


