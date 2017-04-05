import unittest, os
from Episode import Episode
from Subscriptions import Subscriptions

from Application import init_config

class EpisodeTest (unittest.TestCase):
    def setUp(self):
        self.standardpath = init_config()

    def test_episodes(self):
        pass

if __name__ == '__main__':
    unittest.main()
