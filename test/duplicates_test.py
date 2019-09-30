import unittest
import os
from application import init_config
from subscriptions import Subscriptions, FakeSubscription
from index import FakeIndex
from episode import Episode
from downloader import FakeDownloader


class DuplicatesTest(unittest.TestCase):

    def setUp(self):
        # All known episodes
        # The following is a list of all episode titles for a hypothetical podcast subscription
        self.episode_titles = """
        Alpha Bravo Charlie Delta Echo Foxtrot Golf Delta Hotel India
        Juliett Kilo Lima Delta Mike November Oscar Delta Papa Quebec
        Romeo Delta Sierra Tango Delta Uniform Victor Delta Whiskey XRay
        Yankee Zulu""".split()

        self._construct_fake_subscription_object()
        self._prepare_synthetic_episodes()

    def test_establish_nominal_operation(self):
        self.assertEqual( self.episodes[-1].title, "Zulu")
        self.assertEqual( self.episodes[-1].guid, len(self.episodes)-1)

    def test_first_duplicate_appears_in_window(self):
        actual = self._advance_download_history_by(0)
        expected = \
        """Alpha Bravo Charlie Delta Echo Foxtrot Golf Delta-2 Hotel India"""
        self._assert_correct(expected, actual)

    def test_second_duplicate_appears(self):
        actual = self._advance_download_history_by(5)
        expected = \
        "Foxtrot Golf Delta-2 Hotel India Juliett Kilo Lima Delta Mike"
        self._assert_correct(expected, actual)

    def test_third_duplicate_appears(self):
        actual = self._advance_download_history_by(12)
        expected = \
        "Lima Delta Mike November Oscar Delta-2 Papa Quebec Romeo Delta-3"
        self._assert_correct(expected, actual)

    def test_fourth_duplicate_appears(self):
        actual = self._advance_download_history_by(20)
        expected = \
        "Romeo Delta-3 Sierra Tango Delta Uniform Victor Delta-2 Whiskey XRay"
        self._assert_correct(expected, actual)

    def test_full_gamut(self):
        for i in range(0, len(self.episode_titles)):
            self.sub.maxeps = i

            actual = self._advance_download_history_by(0)
            expected = \
            """Alpha Bravo Charlie Delta Echo Foxtrot Golf Delta-2 Hotel India
            Juliett Kilo Lima Delta-3 Mike November Oscar Delta-4 Papa
            Quebec Romeo Delta-5 Sierra Tango Delta-6 Uniform Victor
            Delta-7 Whiskey XRay Yankee Zulu Delta-8"""

            es = expected.split()[0:i]
            expected = ' '.join(es)

            self.assertEqual(i, len(actual))
            self._assert_correct(expected, actual)

    def _advance_download_history_by(self, n):
        stream_pointer = 0
        episodes = None
        for i in range(0, n+1):
            episodes = self._simulate_download(stream_pointer)
            stream_pointer = stream_pointer + 1
        return episodes

    def _construct_fake_subscription_object(self):
        self.standardpath = init_config()
        
        downloader = FakeDownloader()
        subscriptions = Subscriptions(None, downloader, self.standardpath )
        rssfile = 'dummy' 
        dummy_rss = "blah"
        url = "http://foo.bar.com"
        maxeps = 4
        
        fs = FakeSubscription(
            subscriptions,
            rssfile,
            url,
            maxeps,
            downloader)

        fs.index = FakeIndex()
        fs.maxeps = 10
        self.sub = fs

    def _prepare_synthetic_episodes(self):
        self.episodes = []
        count = 0
        for t in self.episode_titles:
            e = Episode(self.sub)
            e.guid = count
            e.title = t
            e.url = 'http://www.example.com/foo/bar/baz.mp3'
            count = count + 1
            self.episodes.append(e)

    def _assert_correct(self, expected, actual):
        expected = expected.split()
        for i in range(self.sub.maxeps):
            title = expected[i] + ".mp3"
            expected_basename = os.path.join(self.sub._podcasts_subdir(), title)
            actual_basename = actual[i].locallink()
            self.assertEqual(expected_basename, actual_basename)

    def _simulate_download(self, stream_pointer):
        fakedownloader = FakeDownloader()

        # create a batch of episodes
        new = []
        for i in range(stream_pointer, stream_pointer + self.sub.maxeps):
            new.append(self.episodes[i])
        old = []
        for i in range(0, stream_pointer):
            old.append(self.episodes[i])
        episodes = self.sub.release_old_and_download_new(old,
                                                   new,
                                                   self.standardpath,
                                                   fakedownloader)

        return episodes

if __name__ == '__main__':
    unittest.main()
