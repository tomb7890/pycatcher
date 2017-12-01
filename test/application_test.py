import os
import unittest
import xml

from application import get_list_of_subscriptions, init_config, dodownload
from application import get_list_of_subscriptions_production, localrss_conditions
from episode import sort_rev_chron
from subscriptions import Subscriptions
from downloader import Downloader, FakeDownloader
from filesystem import FileSystem
import command
from report import make_report_text


class ApplicationTest(unittest.TestCase):

    def setUp(self):
        self.parser = command.Args().parse('--program  wbur'.split())
        self.standardpath = init_config()

    def test_localrss_option_suspends_download_of_rss_file(self):
        self.fake = FakeDownloader()
        self.parser = command.Args().parse('--localrss --program wbur   '.split())
        self.assertTrue(command.Args().parser.localrss)
        dodownload(self.standardpath, self.fake)
        self.assertFalse(self._wbur_rss_file_was_downloaded())
        
    def test_unmatched_program_halts_app_execution_with_exception(self):
        with self.assertRaises(ValueError):
            self.fake = FakeDownloader()
            self.parser = command.Args().parse(' --program asodmxcwew  '.split())
            dodownload(self.standardpath, self.fake)

    def test_localrss_conditions(self):
        localrss_flag_is_set = False
        local_rssfile_exists = False
        actual = localrss_conditions(local_rssfile_exists, localrss_flag_is_set)
        self.assertTrue(actual)

        localrss_flag_is_set = True
        local_rssfile_exists = False
        actual = localrss_conditions(local_rssfile_exists, localrss_flag_is_set)
        self.assertTrue(actual)

        localrss_flag_is_set = False
        local_rssfile_exists = True
        actual = localrss_conditions(local_rssfile_exists, localrss_flag_is_set)
        self.assertTrue(actual)

        localrss_flag_is_set = True
        local_rssfile_exists = True
        actual = localrss_conditions(local_rssfile_exists, localrss_flag_is_set)
        self.assertFalse(actual)

    def _wbur_rss_file_was_downloaded(self):
        x = True
        url = None
        downloader = FakeDownloader()
        for sub in get_list_of_subscriptions_production(downloader, self.standardpath):
            url = sub.url
        for el in self.fake.history:
            if url in el:
                x = False
        return x

    def test_dirs_exist(self):
        subs = Subscriptions(FakeDownloader(), self.standardpath )
        asub = subs.find("genes")
        self.assertTrue(os.path.exists(asub.subscriptions._podcasts_basedir()))

    def test_dirs_dont_exist(self):
        with self.assertRaises(AttributeError):
            subs = Subscriptions(self.standardpath)
            asub = subs.find("xgenes")
            self.assertTrue(os.path.exists(asub.subscriptions._podcasts_basedir()))

    def test_match_failure(self):
        downloader = FakeDownloader()
        with self.assertRaises(ValueError):
            subs = Subscriptions(downloader, self.standardpath, "foobar")

    def test_match_success(self):
        downloader = FakeDownloader()
        subs = Subscriptions(downloader, self.standardpath, "genes")
        self.assertEqual(1, len(subs.items))

    def test_get_list_of_subscriptions_with_match_failure(self):
        with self.assertRaises(ValueError):
            get_list_of_subscriptions(self.standardpath, FakeDownloader(), "quux")


    def test_get_list_of_subscriptions_with_match_success(self):
        items = get_list_of_subscriptions(self.standardpath, FakeDownloader(), "genes")
        self.assertEqual(1, len(items))
    
    def test_doreport(self):
        report = make_report_text(self.standardpath)
        self.assertTrue(len(report) > 0)
        self.assertTrue('<HTML>' in report)

    def test_dodownload(self):
        downloader = FakeDownloader()
        dodownload(self.standardpath, downloader)

    def test_minidom_parse_success(self):
        matchpattern = 'wbur'
        basedir = self.standardpath
        downloader = FakeDownloader()
        subs = get_list_of_subscriptions(basedir, downloader, matchpattern)
        for s in subs:
            try:
                s.parse_rss_file(s.get_rss_path())
            except xml.etree.ElementTree.ParseError, p:
                self.assertFalse(True)

    def test_fetch_latest_onpoints(self):
        basedir = self.standardpath
        downloader = Downloader()
        downloader.fs = FileSystem()
        subs = Subscriptions(downloader, self.standardpath)
        asub = subs.find("wbur")
        self.assertNotEqual(None,asub)

    
    def gtest_create_links(self, mock_link):
        # get a set of episodes
        episodes = self._get_list_of_eps()
        # get a subscriptions object
        sobj = episodes[0].subscription.subscriptions

        #self.assertEqual(sobj._data_basedir(),
                         # os.path.expanduser('~/.podcasts-data'))

        # sobj._podcastdir = '/tmp/blahfoo'
        create_links(episodes)
        last_episode = episodes[-1]
        # mock_link.assert_called_with(last_episode.localfile(),
        #                              last_episode.locallink())

    def _get_list_of_eps(self):
        subs = get_list_of_subscriptions(self.standardpath,
                                         FakeDownloader(), "genes")
        asub = subs[0]
        eps = asub.get_all_episodes()
        sort_rev_chron(eps)
        new = eps[:asub.maxeps]
        return new


if __name__ == '__main__':
    unittest.main()
