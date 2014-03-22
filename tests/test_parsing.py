import coucheventjoiner
import unittest
from mock import Mock
import lxml.html

#There are files representing event page in various states
class TestParsing(unittest.TestCase):
    
    #Do not bother closing opened files
    @classmethod
    def setUpClass(cls):
        cls.event_ok = lxml.html.fromstring(open('event_logged_freespot_notjoined.html').read())
        cls.event_full = lxml.html.fromstring(open('event_logged_full_notjoined.html').read())
        cls.event_unlogged = lxml.html.fromstring(open('event_unlogged_past_nospotlimit.html').read())
        cls.event_attending = lxml.html.fromstring(open('event_attending_over.html').read())

    def test_logged_in(self):
        self.assertTrue(coucheventjoiner.is_logged_in(self.event_ok))

    def test_unlogged(self):
        self.assertFalse(coucheventjoiner.is_logged_in(self.event_unlogged))

    def test_event_not_over(self):
        self.assertFalse(coucheventjoiner.is_event_over(self.event_ok))

    def test_event_over(self):
        self.assertTrue(coucheventjoiner.is_event_over(self.event_attending))

    def test_attending(self):
        self.assertFalse(coucheventjoiner.is_attending(self.event_ok))

    def test_attending(self):
        self.assertTrue(coucheventjoiner.is_attending(self.event_attending))

    def test_full(self):
        self.assertTrue(coucheventjoiner.is_event_full(self.event_full))

    def test_not_full(self):
        self.assertFalse(coucheventjoiner.is_event_full(self.event_ok))

    def test_no_spot_limit(self):
        self.assertFalse(coucheventjoiner.is_event_full(self.event_unlogged))
