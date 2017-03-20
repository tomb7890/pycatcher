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
        self.episodes = self.sub.get_all_episodes()
        self.dupes = self.gather_dupe_indices(self.episodes)

    def xassertEqual(self, a, b):
        self.assertEqual(os.path.join(self.sub._podcasts_subdir(), a), b)

    def test_number_not_append(self):
        index_of_folower_of_first_dupe = self.dupes[1]+1
        first_follower = self.episodes[index_of_folower_of_first_dupe]
        self.xassertEqual("Ontarios Pothole Pains.mp4",
                          first_follower.locallink())

    def test_number_appended(self):
        third_duplicate_episdode = self.episodes[self.dupes[2]]
        self.xassertEqual("The Agendas Week in Review-3.mp4",
                          third_duplicate_episdode.locallink())

    def gather_dupe_indices(self, episodes):
        '''
        Scan the list of all episodes which have recurring titles.
        Store their indices in the array self.dupes.
        '''
        unique_titles = []
        duplicates_titles = []
        dupes = []

        for i in range(len(episodes)):
            title = episodes[i].title
            if title not in unique_titles:
                unique_titles.append(title)
            else:
                duplicates_titles.append(title)

        for i in range(len(episodes)):
            if episodes[i].title in duplicates_titles:
                dupes.append(i)

        return dupes

    def test_first_occurrence_of_dupe_is_as_normal(self):
        first_dupe = self.episodes[self.dupes[0]]
        self.assertEqual("The Agendas Week in Review.mp4", first_dupe.basename())

    def test_follower_of_dupe(self):
        index_of_folower_of_first_dupe = self.dupes[1]+1
        first_follower = self.episodes[index_of_folower_of_first_dupe]
        self.assertEqual("Ontarios Pothole Pains.mp4", first_follower.basename())

    def test_of_locallink(self):
        # make sure I don't break anything while extracting basename from locallink
        first_dupe = self.episodes[self.dupes[0]]
        expected = 'The Agendas Week in Review.mp4'
        actual = first_dupe.locallink()
        self.xassertEqual(os.path.expanduser(expected), actual)

    def test_second_dupe_has_disambiguator(self):
        second_dupe = self.episodes[self.dupes[1]]
        self.xassertEqual("The Agendas Week in Review-2.mp4",
                          second_dupe.locallink())



    def test_the_gamut(self):
        # set up some episodes with duplicate titles



        episode_titles = """Alfa Bravo Charlie Delta Echo Foxtrot Golf Hotel India Delta Juliett Kilo
Lima Mike November Oscar Papa Quebec Delta  Romeo Sierra Tango Uniform Victor
Whiskey X Yankee Zulu""".split()

        self.assertEqual( episode_titles[3], "Delta")

        episode_objects = []
        count = 0

        self.standardpath = init_config()
        subscriptions = Subscriptions(self.standardpath)
        fs = FakeSubscription(subscriptions, "foobar")

        for e in episode_titles:
            episode_object = Episode(fs)
            episode_object.guid = count
            episode_object.title = e
            episode_object.url = 'http://www.example.com/foo/bar/baz.mp3'
            count = count + 1
            episode_objects.append( episode_object )

        self.assertEqual( episode_objects[-1].title, "Zulu")
        self.assertEqual( episode_objects[-1].guid, len(episode_objects)-1)

        fs._fake_episode_list = episode_objects
        processed = fs.get_all_episodes()

        # call "get_all_episodes" to engage the processing
        # assert that dupes have modifed episode names

        def yassertEqual(a, b):
            c = os.path.join(os.path.expanduser("~/podcasts/foobar"), a)
            d = b
            self.assertEqual(c, d)

        yassertEqual('Alfa.mp3', processed[0].locallink() )
        yassertEqual('Delta.mp3', processed[3].locallink() )
        yassertEqual('Delta-2.mp3', processed[9].locallink() )

        # push some new episodes onto the stream
        # such that the oldest of maxeps scrolls away
        # note the oldest dupe scrolls away ( & freeing up one of the dupe name mods )
