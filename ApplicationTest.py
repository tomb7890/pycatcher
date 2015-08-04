import unittest, os, sys, re

from Subscriptions import Subscriptions
import Command
import Library
import argparse
class ApplicationTest (unittest.TestCase):

    def setUp(self):
        self.standardpath = os.environ['PODCASTROOT']
        pass

    def test_minidom_parse(self):
        parser = Command.getparser()
        argstring = "--verbose --debug --localrss --program=wbur"
        a = argstring.split(" ")
        Command.args = parser.parse_args(a)
        subs = Subscriptions(self.standardpath)
        for s in subs.items:
            s.minidom_parse(s.get_rss_path())

        # test something weird
        f = open('/tmp/tmp123456789.txt', 'w')
        f.write('blah blah blah blah blah')
        partial = open(s.get_rss_path(), 'r').read()
        f.write(partial)
        f.close()

        # expected behavior; print out a message but don't
        # stop the application
        s.minidom_parse('/tmp/tmp123456789.txt')

    def test_create_links(self):
        subs = Subscriptions(self.standardpath)
        asub = subs.find("tvo_the_agenda")
        filename = asub.get_rss_file(  True )
        eps = Library.get_all_ep(filename, asub)

        parser = Command.getparser()
        argstring = "--debug --localrss"
        a = argstring.split(" ")
        Command.args = parser.parse_args(a)

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
