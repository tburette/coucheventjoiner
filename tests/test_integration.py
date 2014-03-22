import coucheventjoiner
import test_network
import test_parse_args
import unittest
from mock import Mock, MagicMock, patch
from httmock import HTTMock, urlmatch


#TODO complete
class TestIntegration(unittest.TestCase):
    
    @patch('sys.argv', [test_parse_args.APP_NAME, 
                        test_parse_args.EVENT_URL,
                        'username',
                        'password'
                        ])
    def test_join(self):
        with HTTMock(test_network.login_ok, test_network.join_ok):
            coucheventjoiner.main()

if __name__ == '__main__':
    unittest.main()
