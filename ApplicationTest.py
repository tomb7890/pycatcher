import os
import unittest
import xml
import mock

from Application import get_list_of_subscriptions, doreport, init_config
from Episode import sort_rev_chron
from Subscriptions import Subscriptions
from Library import create_links


class ApplicationTest(unittest.TestCase):

    def setUp(self):
        self.standardpath = init_config()

    def test_dirs_exist(self):
        subs = Subscriptions(self.standardpath)
        asub = subs.find("tvo_the_agenda")
        self.assertTrue(os.path.exists(asub.subscriptions.podcastsdir()))

    def test_doreport(self):
        report = doreport(self.standardpath)
        self.assertTrue(len(report) > 0)
        self.assertTrue('<HTML>' in report)

    def test_minidom_parse_success(self):
        matchpattern = 'wbur'
        basedir = self.standardpath
        subs = get_list_of_subscriptions(basedir, matchpattern)
        for s in subs:
            try:
                s.minidom_parse(s.get_rss_path())
            except xml.etree.ElementTree.ParseError, p:
                self.assertFalse(True)


    @mock.patch('Library.os.link')
    def test_create_links(self, mock_link):
        # get a set of episodes
        episodes = self._get_list_of_eps()
        # get a subscriptions object
        sobj = episodes[0].subscription.subscriptions

        self.assertEqual(sobj.datadir(),
                         os.path.expanduser('~/.podcasts-data'))

        sobj._podcastdir = '/tmp/blahfoo'
        create_links(episodes, episodes[0].subscription)
        last_episode = episodes[-1]
        mock_link.assert_called_with(last_episode.localfile(),
                                     last_episode.locallink())

    def _get_list_of_eps(self):
        subs = get_list_of_subscriptions(self.standardpath, "agenda")
        asub = subs[0]
        eps = asub.get_all_ep()
        sort_rev_chron(eps)
        new = eps[:asub.maxeps]
        return new


if __name__ == '__main__':
    unittest.main()
