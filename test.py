import unittest
from main import app, Matches

class TestMatching(unittest.TestCase):
    def testMatches(self):
        with app.test_request_context():
            testMatches = Matches.get(self)
            # Should return a single match by default
            self.assertEqual(len(testMatches), 1)