import os
import tempfile
import unittest
import xml

import Command
from Application import get_list_of_subscriptions, get_latest_episodes
from Subscriptions import Subscriptions
from Library import create_links

class ApplicationTest (unittest.TestCase):
    def setUp(self):
        if 'PODCASTROOT' in os.environ:
            self.standardpath = os.environ['PODCASTROOT']
        else:
            self.standardpath = os.path.expanduser('~/podcasts')
        pass

    def test_dirs_exist(self):
        subs = Subscriptions(self.standardpath)
        asub = subs.find("tvo_the_agenda")
        self.assertTrue( os.path.exists(asub.subscriptions.podcastsdir()))

    def test_minidom_parse_success(self):
        matchpattern = 'wbur'
        basedir = self.standardpath
        subs = get_list_of_subscriptions(basedir, matchpattern)
        for s in subs:
            try:
                s.minidom_parse(s.get_rss_path())
            except xml.parsers.expat.ExpatError:
                self.assertFalse(True)

    def test_minidom_parse_fail(self):
        basedir = self.standardpath
        s = get_list_of_subscriptions(basedir)[0]
        temp = tempfile.mktemp()
        f = open(temp, 'w')
        f.write('blah blah blah blah blah')
        partial = open(s.get_rss_path(), 'r').read()
        f.write(partial)
        f.close()
        try:
            s.minidom_parse(temp)
        except xml.parsers.expat.ExpatError:
            self.assertTrue(True)

    def test_create_links(self):
        subs = Subscriptions(self.standardpath)
        asub = subs.find("tvo_the_agenda")
        filename = asub.get_rss_file(  True )
        eps = get_all_ep(filename, asub)


        self.assertTrue('agenda' in filename)
        self.assertEqual( asub.subscriptions.datadir(), os.path.expanduser('~/.podcasts-data'))
        asub.subscriptions._podcastdir = '/tmp/blahfoo'
        self.assertEqual('/tmp/blahfoo', asub.subscriptions.podcastsdir())

        os.system('find /tmp/blahfoo/ -type f -iname \*mp4 > /tmp/blahfoofiles')
        newfiles = open('/tmp/blahfoofiles', 'r').read()

        Library.create_links(eps, asub )

        newfiles = newfiles.split("\n")

        for n in newfiles:
            m = re.match('.*(/tmp.*mp4).*', n )
            if m:
                file= m.group(1)
                print file
                self.assertTrue(os.path.exists(file))

if __name__ == '__main__':
    unittest.main()
