import sys
import os
import unittest

#if in main directory: python -m unittest discover -s tests
#if in tests directory: python -m unittest discover -t ..
if __name__ == '__main__':
    test_dir = os.path.dirname(os.path.abspath(__file__))
    suite = unittest.defaultTestLoader.discover(test_dir, top_level_dir= test_dir + '/..')
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
