import unittest
import os
from application import init_config
from subscriptions import Subscriptions, FakeSubscription
from index import FakeIndex
from episode import Episode
from downloader import FakeDownloader


class DuplicatesTest(unittest.TestCase):

    def setUp(self):
        self.standardpath = init_config()
        subscriptions = Subscriptions(self.standardpath)
        self.sub = subscriptions.find("Agenda")

    def construct_fake_subscription_object(self, episode_titles):
        self.standardpath = init_config()
        subscriptions = Subscriptions(self.standardpath)
        dummy_rss = "blah"
        fs = FakeSubscription(subscriptions, dummy_rss)
        fs.lut = FakeIndex()
        fs.maxeps = 10
        return fs

    def prepare_synthetic_episodes(self, sub, episode_titles):
        episodes = []
        count = 0
        for e in episode_titles:
            episode_object = Episode(sub)
            episode_object.guid = count
            episode_object.title = e
            episode_object.url = 'http://www.example.com/foo/bar/baz.mp3'
            count = count + 1
            episodes.append( episode_object )
        return episodes

    def test_modifying_link_names_when_duplicated_(self):

        def assert_correct(fs, expected_linknames, episodes):
            expected = expected_linknames.split()
            for i in range (fs.maxeps):
                title = expected[i] + ".mp3"
                c = os.path.join(fs._podcasts_subdir(), title)
                d = episodes[i].locallink()
                self.assertEqual(c, d)

        def simulate_download(stream_pointer, fs, episodes ):
            fakedownloader = FakeDownloader()
            new = []
            for i in range(stream_pointer, stream_pointer + fs.maxeps):
                new.append(episodes[i])
            old = []
            for i in range(0, stream_pointer):
                old.append(episodes[i])
            eps = fs.release_old_and_download_new(old,
                                            new,
                                            self.standardpath,
                                            fakedownloader)
            return eps

        # All known episodes
        episode_titles = """
        Alpha Bravo Charlie Delta Echo Foxtrot Golf Delta Hotel India
        Juliett Kilo Lima Delta Mike November Oscar Delta Papa Quebec
        Romeo Delta Sierra Tango Delta Uniform Victor Delta Whiskey XRay
        Yankee Zulu""".split()

        fs = self.construct_fake_subscription_object(episode_titles)
        episodes = self.prepare_synthetic_episodes(fs,episode_titles)

        # sanity checking
        self.assertEqual( episodes[-1].title, "Zulu")
        self.assertEqual( episodes[-1].guid, len(episodes)-1)

        stream_pointer = 0
        processed = simulate_download(stream_pointer, fs, episodes)
        expected_linknames = \
        """Alpha Bravo Charlie Delta Echo Foxtrot Golf Delta-2 Hotel India"""
        assert_correct(fs, expected_linknames, processed)

        stream_pointer = stream_pointer + 5
        processed = simulate_download(stream_pointer, fs, episodes)
        expected_linknames = \
        "Foxtrot Golf Delta-2 Hotel India Juliett Kilo Lima Delta Mike"
        assert_correct(fs, expected_linknames, processed)

        stream_pointer = stream_pointer + 7
        processed = simulate_download(stream_pointer, fs, episodes)
        expected_linknames = \
        "Lima Delta Mike November Oscar Delta-2 Papa Quebec Romeo Delta-3"
        assert_correct(fs, expected_linknames, processed)

        stream_pointer = stream_pointer + 8
        processed = simulate_download(stream_pointer, fs, episodes)
        expected_linknames = \
        "Romeo Delta-3 Sierra Tango Delta Uniform Victor Delta-2 Whiskey XRay"
        assert_correct(fs, expected_linknames, processed)


if __name__ == '__main__':
    unittest.main()
