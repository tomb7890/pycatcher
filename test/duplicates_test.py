import unittest
import os
from application import init_config
from subscriptions import Subscriptions, FakeSubscription
from index import FakeIndex
from episode import Episode
from downloader import FakeDownloader


class DuplicatesTest(unittest.TestCase):

    def construct_fake_subscription_object(self):
        self.standardpath = init_config()
        subscriptions = Subscriptions(self.standardpath)
        dummy_rss = "blah"
        fs = FakeSubscription(subscriptions, dummy_rss)
        fs.index = FakeIndex()
        fs.maxeps = 10
        self.fs = fs

    def prepare_synthetic_episodes(self):
        self.episodes = []
        count = 0
        for e in self.episode_titles:
            episode_object = Episode(self.fs)
            episode_object.guid = count
            episode_object.title = e
            episode_object.url = 'http://www.example.com/foo/bar/baz.mp3'
            count = count + 1
            self.episodes.append( episode_object )

    def assert_correct(self, fs, expected_linknames, processed):
        expected = expected_linknames.split()
        for i in range (fs.maxeps):
            title = expected[i] + ".mp3"
            c = os.path.join(fs._podcasts_subdir(), title)
            d = processed[i].locallink()
            self.assertEqual(c, d)

    def simulate_download(self, stream_pointer ):
        fakedownloader = FakeDownloader()

        # create a batch of episodes
        new = []
        for i in range(stream_pointer, stream_pointer + self.fs.maxeps):
            new.append(self.episodes[i])
        old = []
        for i in range(0, stream_pointer):
            old.append(self.episodes[i])
        eps = self.fs.release_old_and_download_new(old,
                                        new,
                                        self.standardpath,
                                        fakedownloader)

        return eps



    def setUp(self):
        # All known episodes
        # The following is a list of all episode titles for a hypothetical podcast subscription
        self.episode_titles = """
        Alpha Bravo Charlie Delta Echo Foxtrot Golf Delta Hotel India
        Juliett Kilo Lima Delta Mike November Oscar Delta Papa Quebec
        Romeo Delta Sierra Tango Delta Uniform Victor Delta Whiskey XRay
        Yankee Zulu""".split()

        self.construct_fake_subscription_object()
        self.prepare_synthetic_episodes()

    def test_establish_nominal_operation(self):
        self.assertEqual( self.episodes[-1].title, "Zulu")
        self.assertEqual( self.episodes[-1].guid, len(self.episodes)-1)

    def test_zero(self):
        processed = self._advance_download_history_by(0)
        expected_linknames = \
        """Alpha Bravo Charlie Delta Echo Foxtrot Golf Delta-2 Hotel India"""
        self.assert_correct(self.fs, expected_linknames, processed)

    def test_five(self):
        processed = self._advance_download_history_by(5)
        expected_linknames = \
        "Foxtrot Golf Delta-2 Hotel India Juliett Kilo Lima Delta Mike"
        self.assert_correct(self.fs, expected_linknames, processed)

    def test_twelve(self):
        processed = self._advance_download_history_by(12)
        expected_linknames = \
        "Lima Delta Mike November Oscar Delta-2 Papa Quebec Romeo Delta-3"
        self.assert_correct(self.fs, expected_linknames, processed)

    def test_twenty(self):
        processed = self._advance_download_history_by(20)
        expected_linknames = \
        "Romeo Delta-3 Sierra Tango Delta Uniform Victor Delta-2 Whiskey XRay"
        self.assert_correct(self.fs, expected_linknames, processed)

    def _advance_download_history_by(self,n):
        stream_pointer = 0
        processed = None
        for i in range(0,n+1):
            processed = self.simulate_download(stream_pointer)
            stream_pointer = stream_pointer + 1
        return processed




if __name__ == '__main__':
    unittest.main()
