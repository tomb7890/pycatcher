import unittest
from Application import init_config, get_list_of_subscriptions
import tempfile
import xml
import Subscriptions


class SubscriptionsTest (unittest.TestCase):
    def setUp(self):
        self.standardpath = init_config()

    def test_assertion_raised_when_match_attempt_fails(self):
        with self.assertRaises(ValueError):
            basedir = self.standardpath
            match = 'nklfewcjdisoafsdklewjidso'
            s = Subscriptions.Subscriptions(basedir, match)

    def test_junk_in_header(self):
        '''test processing an RSS file with junk at the top of the header'''
        s = self.set_up_minidom_test()
        temp = tempfile.mktemp()
        f = open(temp, 'w')
        f.write('blah blah blah blah blah')
        partial = open(s.get_rss_path(), 'r').read()
        f.write(partial)
        f.close()

        try:
            s.parse_rss_file(temp)
        except xml.etree.ElementTree.ParseError, e:
            self.assertTrue(True)

    def test_empty_rss_file(self):
        '''test processing an empty RSS file'''
        s = self.set_up_minidom_test()
        temp = tempfile.mktemp()
        f = open(temp, 'w')
        f.write('')
        f.close()

        try:
            s.parse_rss_file(temp)
        except xml.etree.ElementTree.ParseError, e:
            self.assertTrue(True)

    def set_up_minidom_test(self):
        basedir = self.standardpath
        s = get_list_of_subscriptions(basedir)[0]
        return s

    def test_get_rss_file(self):
        pass


if __name__ == '__main__':
    unittest.main()
