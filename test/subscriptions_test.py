import unittest
from application import init_config, get_list_of_subscriptions
import tempfile
import xml
import subscriptions

from index import FakeIndex
from downloader import FakeDownloader

class SubscriptionsTest (unittest.TestCase):
    def setUp(self):
        self.standardpath = init_config()
        
    def get_temp_file(self):
        filename = tempfile.mktemp()
        f = open(filename, 'w')
        return f, filename

    def test_assertion_raised_when_match_attempt_fails(self):
        with self.assertRaises(ValueError):
            basedir = self.standardpath
            match = 'nklfewcjdisoafsdklewjidso'
            dl  = FakeDownloader()
            s = subscriptions.Subscriptions(dl, basedir, program=match)

    def test_download_rss_file(self):
        dl = FakeDownloader(verbose=True)
        basedir = self.standardpath
        s = subscriptions.Subscriptions(dl, basedir, program='wbur')
        wbur=s.items[0]
        self.assertNotEqual(None, wbur)
        wbur.refresh(dl)
        cmd = 'wget  --output-document="/home/tomb/.podcasts-data/rss/on_point_wbur.xml"  "http://www.npr.org/rss/podcast.php?id=510053" '
        self.assertEqual(cmd, dl.getCmd())

        wbur.dodownload(dl)
        expected = 'wget  --input-file="urls.dat"  --directory-prefix="/home/tomb/.podcasts-data/on_point_wbur" '
        
        self.assertEqual(expected, dl.getCmd())


    def test_junk_in_header(self):
        '''test processing an RSS file with junk at the top of the header'''
        with self.assertRaises(xml.etree.ElementTree.ParseError):
            s = self.set_up_minidom_test()
            f, filename = self.get_temp_file()
            f.write('blah blah blah blah blah')
            partial = open(s.get_rss_path(), 'r').read()
            f.write(partial)
            f.close()
            s.parse_rss_file(filename)

    def test_reject_blanks_in_header(self):
        '''test rejecting an RSS file with a blank line at the top'''
        with self.assertRaises(xml.etree.ElementTree.ParseError):
            s = self.set_up_minidom_test()
            f, filename = self.get_temp_file()
            f.write('\n')
            partial = open(s.get_rss_path(), 'r').read()
            f.write(partial)
            f.close()
            s.parse_rss_file(filename)

    def test_tolerate_blanks_in_header(self):
        '''test tolerating an RSS file with a blank line at the top'''
        s = self.set_up_minidom_test()
        s.set_strict_parsing(False)
        f, filename = self.get_temp_file()
        f.write('\n')
        partial = open(s.get_rss_path(), 'r').read()
        f.write(partial)
        f.close()
        s.parse_rss_file(filename)

    def test_empty_rss_file(self):
        '''test processing an empty RSS file'''
        with self.assertRaises(xml.etree.ElementTree.ParseError):
            s = self.set_up_minidom_test()
            f, filename = self.get_temp_file()
            f.write('')
            f.close()
            s.parse_rss_file(filename)

    def set_up_minidom_test(self):
        basedir = self.standardpath
        dl = FakeDownloader()
        s = get_list_of_subscriptions(basedir, dl)[0]
        return s

    def setup_additional(self):
        self.program_string = 'freakon'
        self.standardpath = init_config()
        self._prepare_subscription_object()
        self.sub.index = FakeIndex()

    def _prepare_subscription_object(self):
        fd = FakeDownloader()
        subs = get_list_of_subscriptions(self.standardpath, fd,
                                         program=self.program_string)
        self.sub = subs[0]
        self.assertEqual(1, len(subs))

    def test_main(self):
        self.setup_additional()
        self.assertEqual(0,
                         len(self.sub.downloader.fs.listdir(
                             self.sub._podcasts_subdir()
                         )))

        self.sub.dodownload(init_config())

        self.assertEqual(self.sub.maxeps,
                         len(self.sub.downloader.fs.listdir(
                             self.sub._podcasts_subdir()
                         )))

        self.sub.dodownload(init_config())

        dircont = ' '.join(self.sub.downloader.fs.listdir(
            self.sub._podcasts_subdir()
        ))

        self.assertEqual(self.sub.maxeps,
                         len(self.sub.downloader.fs.listdir(
                             self.sub._podcasts_subdir()
                         )))


if __name__ == '__main__':
    unittest.main()
