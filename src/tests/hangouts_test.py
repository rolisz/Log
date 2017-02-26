import unittest
from src.data import parsers

conversation = {
    "conversation_state" : {
      "conversation" : {
        "participant_data" : [ {
          "id" : {
            "gaia_id" : "1",
            "chat_id" : "1"
          },
          "fallback_name" : "Person 1",
        }, {
          "id" : {
            "gaia_id" : "2",
            "chat_id" : "2"
          },
          "fallback_name" : "Person 2",
        } ],
      },
      "event" : [ {
        "sender_id" : {
          "gaia_id" : "1",
          "chat_id" : "1"
        },
        "timestamp" : "1453583984620495",
        "chat_message" : {
          "message_content" : {
            "segment" : [ {
              "type" : "TEXT",
              "text" : "Hi."
            } ]
          }
        },
        "event_type" : "REGULAR_CHAT_MESSAGE",
      }, {
        "sender_id" : {
          "gaia_id" : "2",
          "chat_id" : "2"
        },
        "timestamp" : "1453583990786037",
        "chat_message" : {
          "message_content" : {
            "segment" : [ {
              "type" : "TEXT",
              "text" : "How are you?"
            } ]
          }
        },
        "event_type" : "REGULAR_CHAT_MESSAGE",
      }]}}

conversationWithUnk = {
    "conversation_state" : {
      "conversation" : {
        "participant_data" : [ {
          "id" : {
            "gaia_id" : "1",
            "chat_id" : "1"
          },
          "fallback_name" : "Person 1",
        }, {
          "id" : {
            "gaia_id" : "2",
            "chat_id" : "2"
          }
        } ],
      },
      "event" : [ {
        "sender_id" : {
          "gaia_id" : "1",
          "chat_id" : "1"
        },
        "timestamp" : "1453583984620495",
        "chat_message" : {
          "message_content" : {
            "segment" : [ {
              "type" : "TEXT",
              "text" : "Hi."
            } ]
          }
        },
        "event_type" : "REGULAR_CHAT_MESSAGE",
      }, {
        "sender_id" : {
          "gaia_id" : "2",
          "chat_id" : "2"
        },
        "timestamp" : "1453583990786037",
        "chat_message" : {
          "message_content" : {
            "segment" : [ {
              "type" : "TEXT",
              "text" : "How are you?"
            } ]
          }
        },
        "event_type" : "REGULAR_CHAT_MESSAGE",
      }, {
        "sender_id" : {
          "gaia_id" : "2",
          "chat_id" : "2"
        },
        "timestamp" : "1453583990786037",
        "chat_message" : {
          "message_content" : {
            "segment" : [ {
              "type" : "TEXT",
              "text" : "I'm good"
            } ]
          }
        },
        "event_type" : "REGULAR_CHAT_MESSAGE",
      }]}}
class HangoutsTest(unittest.TestCase):

    def setUp(self):
        self.hangouts = parsers.Hangouts()

    def testNormal(self):
        contacts, lines = self.hangouts.parse_thread(conversation)
        self.assertSetEqual(contacts, {"Person 1", "Person 2"})
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]['message'], "Hi.")
        self.assertEqual(lines[1]['contact'], "Person 2")
        self.assertEqual(lines[0]['protocol'], "Hangouts")
        self.assertEqual(lines[1]['source'], "Hangouts")
        self.assertEqual(lines[0]['timestamp'], "2016-01-23T22:19:44.620495")

    def testUnknownContact(self):
        contacts, lines = self.hangouts.parse_thread(conversationWithUnk)
        self.assertSetEqual(contacts, {"Person 1", "Unknown_2"})
        self.assertEqual(len(lines), 3)
