import unittest
from src.data import parsers

conv = """06/10/2014,09:22:56 PM,Me,+001,Hey
06/10/2014,09:23:45 PM,Person 2,+002,How are you?
06/10/2014,09:24:16 PM,Me,+001,Good :d
""".splitlines()


class ViberTest(unittest.TestCase):

    def setUp(self):
        self.viber = parsers.Viber()

    def testNormal(self):
        contacts, lines = self.viber.parse_file(conv)
        self.assertSetEqual(contacts, {"Me", "Person 2"})
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0]['message'], "Hey")
        self.assertEqual(lines[1]['contact'], "Person 2")
        self.assertEqual(lines[0]['protocol'], "Viber")
        self.assertEqual(lines[1]['source'], "Viber")
        self.assertEqual(lines[0]['timestamp'], "2014-10-06T21:22:56")
        self.assertEqual(lines[2]['message'], "Good :d")
