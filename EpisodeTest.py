import unittest, os
from Episode import Episode
from Subscriptions import Subscriptions

class EpisodeTest (unittest.TestCase):
    def setUp(self):
        self.standardpath = os.environ['PODCASTROOT']

    def test_episodes(self):
        pass

if __name__ == '__main__':
    unittest.main()
