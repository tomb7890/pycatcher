import unittest
from Application import init_config, get_list_of_subscriptions
import tempfile
import xml
import Subscriptions
import Command


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
        Command.Args().parse(' --tolerant '.split())
        s = self.set_up_minidom_test()
        f, filename = self.get_temp_file()
        f.write('\n')
        partial = open(s.get_rss_path(), 'r').read()
        f.write(partial)
        f.close()
        s.parse_rss_file(filename)

    def test_empty_rss_file(self):
        '''test processing an empty RSS file'''
        Command.Args().parse('')
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


if __name__ == '__main__':
    unittest.main()
