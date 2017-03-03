import unittest
from Application import init_config, get_list_of_subscriptions
import tempfile
import xml
import Subscriptions


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
            s = Subscriptions.Subscriptions(basedir, match)

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
        s = get_list_of_subscriptions(basedir)[0]
        return s

    def test_get_rss_file(self):
        pass


if __name__ == '__main__':
    unittest.main()
