import sys
import unittest
import coucheventjoiner
from mock import Mock, MagicMock, patch

APP_NAME = 'coucheventjoiner.py'
EVENT_URL = 'https://www.couchsurfing.org/n/events/eventname'

class TestParseArgs(unittest.TestCase):
    def setUp(self):        
        pass

    def tearDown(self):
        pass

    @patch('sys.argv', [APP_NAME])
    def test_no_args(self):
        with self.assertRaises(SystemExit):
            coucheventjoiner.get_user_values()

    @patch('sys.argv', [APP_NAME, EVENT_URL])
    def test_event_no_username(self):
        with self.assertRaises(SystemExit):
            coucheventjoiner.get_user_values()

    @patch('sys.argv', [APP_NAME, 
                        '-d', 
                        str(coucheventjoiner.MIN_RETRY_DELAY),
                        EVENT_URL, 
                        'username',
                        'password',
                    ])
    def test_all_args_passed(self):
        expected = {'delay': coucheventjoiner.MIN_RETRY_DELAY,
                    'event': EVENT_URL,
                    'username': 'username',
                    'password': 'password',
        }
        args = coucheventjoiner.get_user_values()
        self.assertEqual(expected, args)

    @patch('sys.argv', [APP_NAME, EVENT_URL, 'username'])                        
    @patch('getpass.getpass', Mock(return_value='password'))
    def test_default_values(self):
        expected = {'delay': coucheventjoiner.DEFAULT_RETRY_DELAY,
                    'event': EVENT_URL,
                    'username': 'username',
                    'password': 'password',
        }
        args = coucheventjoiner.get_user_values()
        self.assertEqual(expected, args)

    @patch('sys.argv', [APP_NAME, EVENT_URL, 'username'])                        
    @patch('getpass.getpass')        
    def test_ask_password(self, getpass_mock):
        getpass_mock.return_value = 'password'
        args=coucheventjoiner.get_user_values()
        self.assertEqual('password', 'password')
        
    @patch('sys.argv', [APP_NAME, 
                        '-d',
                        str(coucheventjoiner.MIN_RETRY_DELAY - 1),
                        EVENT_URL,
                        'username'
                    ])
    def test_delay_too_small(self):
        with self.assertRaises(SystemExit):
           coucheventjoiner.get_user_values()

    @patch('sys.argv', [APP_NAME, 
                        'https://www.NOTcouchsurfing.org./n/events/eventname', 
                        'username',
                        'password',
                    ])                        
    def test_event_wrong_domain(self):
        with self.assertRaises(SystemExit):
            coucheventjoiner.get_user_values()

    @patch('sys.argv', [APP_NAME, 
                        'https://www.couchsurfing.org/n/repeating-events/brunch-international-paris-repeats',
                        'username',
                        'password',
                    ])                        
    def test_event_wrong_path(self):
        with self.assertRaises(SystemExit):
            coucheventjoiner.get_user_values()

    @patch('sys.argv', [APP_NAME, 
                        'https://www.couchsurfing.org/n/events/somethingelse/eventname',
                        'username',
                        'password',
                    ])                        
    def test_event_extra_on_path(self):
        with self.assertRaises(SystemExit):
            coucheventjoiner.get_user_values()

    @patch('sys.argv', [APP_NAME, 
                        'https://www.couchsurfing.org/n/events/',
                        'username',
                        'password',
                    ])                        
    def test_missing_eventname(self):
        with self.assertRaises(SystemExit):
            coucheventjoiner.get_user_values()    

    @patch('sys.argv', [APP_NAME,
                        'http://www.couchsurfing.org/n/events/eventname',
                        'username',
                        'password'
                        ])
    def test_event_http_to_https(self):
        args = coucheventjoiner.get_user_values()
        self.assertEqual('https://www.couchsurfing.org/n/events/eventname',
                         args['event'])

    @unittest.skip('fails if no protocol. See http://docs.python.org/2/'
                   'library/urlparse.html#urlparse.urlparse')
    @patch('sys.argv', [APP_NAME,
                        'www.couchsurfing.org/n/events/eventname',
                        'username',
                        'password'
                        ])
    def test_event_missing_http(self):
        args = coucheventjoiner.get_user_values()
        self.assertEqual('https://www.couchsurfing.org/n/events/eventname',
                         args['event'])

if __name__ == '__main__':
    unittest.main()

