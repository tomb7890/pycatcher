import unittest
from episode import Episode
from subscriptions import Subscriptions
from application import init_config

class EpisodeTest (unittest.TestCase):
    def setUp(self):
        self.standardpath = init_config()

    def test_episodes(self):
        pass

if __name__ == '__main__':
    unittest.main()
