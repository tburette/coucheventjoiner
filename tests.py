import sys
import os
import unittest

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover('./tests' )
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
