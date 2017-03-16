import unittest
from Application import init_config
from Subscriptions import Subscriptions
from Filesystem import FileSystem
from LookupTable import LookupTable


class DuplicatesTest(unittest.TestCase):

    def setUp(self):
        self.standardpath = init_config()
        subscriptions = Subscriptions(self.standardpath)
        self.sub = subscriptions.find("Agenda")
        self.sub.lut = LookupTable()
        self.episodes = self.sub.get_all_episodes()
        self.gather_dupe_indices()

    def test_number_not_append(self):
        index_of_folower_of_first_dupe = self.dupes[0]+1
        first_follower = self.episodes[index_of_folower_of_first_dupe]
        self.assertEqual("Ontarios Pothole Pains.mp4",
                         first_follower.basename())

    def g_test_number_appended(self):
        third_duplicate_episdode = self.episodes[self.dupes[2]]
        self.assertEqual("The Agendas Week in Review-3.mp4",
                         third_duplicate_episdode.basename())

    def gather_dupe_indices(self):
        '''
        Scan the list of all episodes which have recurring titles.
        Store their indices in the array self.dupes.
        '''
        unique_titles = []
        duplicates_titles = []
        self.dupes = []

        for i in range(len(self.episodes)):
            title = self.episodes[i].title
            if title not in unique_titles:
                unique_titles.append(title)
            else:
                duplicates_titles.append(title)

        for i in range(len(self.episodes)):
            if self.episodes[i].title in duplicates_titles:
                self.dupes.append(i)

    def test_first_occurrence_of_dupe_is_as_normal(self):
        first_dupe = self.episodes[self.dupes[0]]
        self.assertEqual("The Agendas Week in Review.mp4", first_dupe.basename())

    def test_follower_of_dupe(self):
        index_of_folower_of_first_dupe = self.dupes[0]+1
        first_follower = self.episodes[index_of_folower_of_first_dupe]
        self.assertEqual("Ontarios Pothole Pains.mp4", first_follower.basename())

    def test_of_locallink(self):
        # make sure I don't break anything while extracting basename from locallink
        first_dupe = self.episodes[self.dupes[0]]
        expected = '/home/tomb/podcasts/tvo_the_agenda/The Agendas Week in Review.mp4'
        actual = first_dupe.locallink()
        self.assertEqual(expected, actual)

    def gtest_second_dupe_has_disambiguator(self):
        second_dupe = self.episodes[self.dupes[1]]
        self.assertEqual("The Agendas Week in Review-2.mp4",
                         second_dupe.basename())

    def test_modifying_link_names(self):
        # Go through and simulate the writing to disk a big chunk of the episodes--at least
        # as many so as to include the first 3 occurrences of "Week in Review"

        fs = FileSystem()

        chunk = self.dupes[3]
        for i in range(chunk):
            ep = self.episodes[i]
            self.simulate_writing_episode_to_disk(ep, fs)

        first_dupe = self.episodes[self.dupes[0]]
        second_dupe = self.episodes[self.dupes[1]]

        self.assertEqual("The Agendas Week in Review.mp4", first_dupe.reallink())
        self.assertEqual("The Agendas Week in Review-2.mp4", second_dupe.reallink())

        # make sure that regular titles' names remain as normal
        index_of_folower_of_first_dupe = self.dupes[0]+1
        first_follower = self.episodes[index_of_folower_of_first_dupe]
        expected = "Ontarios Pothole Pains.mp4" # find out via inspection of RSS file
        self.assertEqual(expected, first_follower.reallink())

    def simulate_writing_episode_to_disk(self, episode, fs):
        table = episode.subscription.lut.table
        already_used_filenames = []
        for k in table.keys():
            already_used_filenames.append( table[k])
        count = 1
        proposed = episode.base_sans_extension() + episode._file_extension()
        while True:
            if proposed not in already_used_filenames:
                break
            count = count + 1
            proposed = episode.base_sans_extension() + "-%d" % count + episode._file_extension()
        table[episode.guid] = proposed
