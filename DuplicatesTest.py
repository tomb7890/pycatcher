import unittest
import os
from Application import init_config
from Subscriptions import Subscriptions, FakeSubscription
from Episode import Episode


class DuplicatesTest(unittest.TestCase):

    def setUp(self):
        self.standardpath = init_config()
        subscriptions = Subscriptions(self.standardpath)
        self.sub = subscriptions.find("Agenda")
    def prepare_materials_for_test(self, episode_titles):
        self.assertEqual( episode_titles[3], "Delta")
        episode_objects = []
        count = 0
        self.standardpath = init_config()
        subscriptions = Subscriptions(self.standardpath)
        fs = FakeSubscription(subscriptions, "foobar")
        fs.maxeps = 10
        for e in episode_titles:
            episode_object = Episode(fs)
            episode_object.guid = count
            episode_object.title = e
            episode_object.url = 'http://www.example.com/foo/bar/baz.mp3'
            count = count + 1
            episode_objects.append( episode_object )
        return fs, episode_objects


    def test_the_gamut(self):
        # set up some episodes with duplicate titles

        def z():
            """ Advance the stream of podcast episodes and run the application code """
            episode_stream = []
            for i in range(stream_pointer, stream_pointer + maxeps):
                episode_stream.append(episode_objects[i])
            fs._fake_episode_list = episode_stream
            processed = fs.get_all_episodes()
            return processed

        def yassertEqual(a, b):
            c = os.path.join(os.path.expanduser("~/podcasts/foobar"), a)
            d = b
            self.assertEqual(c, d)


        # All known episodes
        episode_titles = """Alpha Bravo Charlie Delta Echo Foxtrot Golf Delta Hotel India Juliett Kilo
Lima Delta Mike November Oscar Delta Papa Quebec Romeo Delta Sierra Tango Uniform Victor
Whiskey X Yankee Zulu""".split()

        fs, episode_objects = self.prepare_materials_for_test(episode_titles)

        # sanity checking, ok
        self.assertEqual( episode_objects[-1].title, "Zulu")
        self.assertEqual( episode_objects[-1].guid, len(episode_objects)-1)

        maxeps = 10
        stream_pointer = 0
        processed = z()

        # TODO push some new episodes onto the stream and reprocess
        # such that the oldest of maxeps scrolls away
        # assert the oldest dupe scrolls away ( & freeing up one of the dupe name mods )

        # tweak the second title dupe as expected
        modified_expected_link_base_titles = \
        """Alpha Bravo Charlie Delta Echo Foxtrot Golf Delta-2 Hotel India""".split()

        for i in range (maxeps):
            title = modified_expected_link_base_titles[i] + ".mp3"
            yassertEqual(title, processed[i].locallink())

        # advance the stream pointer in way that results in some overlapping
        stream_pointer = stream_pointer + 5
        episode_stream = z()
        fs._fake_episode_list = episode_stream
        processed = fs.get_all_episodes()

        modified_expected_link_base_titles = \
        "Foxtrot Golf Delta-2 Hotel India Juliett Kilo Lima Delta Mike".split()

        for i in range (maxeps):
            title = modified_expected_link_base_titles[i] + ".mp3"
            yassertEqual(title, processed[i].locallink())
