import coucheventjoiner
import requests
from httmock import HTTMock, all_requests, urlmatch
import unittest

@urlmatch(netloc=r'(.*\.)?couchsurfing\.org$', path='^/n/auth/?')
def login_ok(url, request):
    return {'status_code': 200, 'content': ''}

@urlmatch(netloc=r'(.*\.)?couchsurfing\.org$', path='^/n/auth/?')
def login_invalid(url, request):
    return {'status_code': 406, 'content': '{"errors":"Invalid username/password","username":"foo"}'}

@urlmatch(netloc=r'(.*\.)?couchsurfing\.org$', path='^/n/events/[^/]+/join/?')
def join_ok(url, request):
    return {'status_code': 200, 'content': ''}

@all_requests
def event_full(url, request):
    return {'status_code': 200, 'content': '{"error":"This event is full."}'}

#TODO complete
class TestNetwork(unittest.TestCase):

    def test_login_ok(self):
        with HTTMock(login_ok):
            s = coucheventjoiner.login('username', 'password')
            self.assertIsInstance(s, requests.Session)

    def test_exception_if_wrong_auth(self):
        with HTTMock(login_invalid):
            with self.assertRaises(coucheventjoiner.LoginException):
                coucheventjoiner.login('username', 'password')

    def test_join(self):
        with HTTMock(join_ok):
            self.assertTrue(coucheventjoiner.join_event(requests.Session(),
                                        'https://www.couchsurfing.org/n/events/eventname'))
    def test_join_full(self):
        with HTTMock(event_full):
            self.assertFalse(coucheventjoiner.join_event(requests.Session(),
                                        'https://www.couchsurfing.org/n/events/eventname'))
            
            

if __name__ == '__main__':
    unittest.main()
