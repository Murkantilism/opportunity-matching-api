import unittest
from main import app, Matches, MATCH_RESULT_LIMIT

class TestMatching(unittest.TestCase):
    def testMatches(self):
        with app.test_request_context():
            testMatches = Matches.get(self)
            # Should return the default number of matches
            self.assertEqual(len(testMatches), MATCH_RESULT_LIMIT)