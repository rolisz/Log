import unittest
from src.data import parsers

conv = """<html><head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
  <title>
   Person 1 - Messages
  </title>
 </head>
 <body>
  <div class="nav"></div>
  <div class="contents">
   <h1>
    Person 1
   </h1>
   <div>
    <div class="thread">
     person1@facebook.com, person2@facebook.com
     <div class="message">
      <div class="message_header">
       <span class="user">
        Person 1
       </span>
       <span class="meta">
        Monday, March 18, 2013 at 1:26pm UTC+01
       </span>
      </div>
     </div>
     <p>
      si dupaia container :&gt;:&gt;
     </p>
     <div class="message">
      <div class="message_header">
       <span class="user">
        Person 2
       </span>
       <span class="meta">
        Monday, March 18, 2013 at 1:25pm UTC+01
       </span>
      </div>
     </div>
     <p>
      thanks
     </p>
    </div>
  <div class="footer">
   Downloaded by Person 1 on Thursday, February 23, 2014 at 2:34pm UTC+01
  </div>
 </body>
</html>
"""


class FacebookTest(unittest.TestCase):

    def setUp(self):
        self.facebook = parsers.Facebook()

    def testNormal(self):
        contacts, lines = next(self.facebook.parse_file(conv))
        lines = list(lines)
        self.assertSetEqual(contacts, {"Person 1", "Person 2"})
        self.assertEqual(lines[0]['message'], "thanks")
        self.assertEqual(lines[1]['message'], "si dupaia container :>:>")
        self.assertEqual(lines[1]['contact'], "Person 1")
        self.assertEqual(lines[0]['protocol'], "Facebook")
        self.assertEqual(lines[1]['source'], "Facebook")
        self.assertEqual(lines[0]['timestamp'], "2013-03-18T13:25:00")
