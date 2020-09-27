import unittest
from subscription import Subscription
from filesystem import FakeFileSystem
from downloader import FakeDownloader
from index import FakeIndex

class DownloaderTest(unittest.TestCase):

    def setUp(self):
        self.sub = Subscription(None, 'The Agenda with Steve Paikin (Video)')
        self.ffs = FakeFileSystem()
        self.fdl = FakeDownloader(self.ffs, self.sub)
        self.sub.maxeps = 6
        self.dbfile = FakeIndex()

    def test_downloading(self):

        self.sub.rssfile = "test/data/TheAgendawithStevePaikinVideo/012820.rss"
        expected_files ="""Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4
Meeting Canadas Greenhouse Gas Targets.mp4
Infrastructure Challenges in Ontario.mp4
New Supports for Northern Farmers.mp4
Conservative Leadership Race Begins.mp4""".splitlines()
        self.download_and_test( expected_files) 

        self.sub.rssfile = "test/data/TheAgendawithStevePaikinVideo/013020.rss"
        expected_files = """Old Age The Secret to Happiness.mp4
Daniel Levitin How to Age Well.mp4
Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4
Meeting Canadas Greenhouse Gas Targets.mp4
Infrastructure Challenges in Ontario.mp4""".splitlines()
        self.download_and_test( expected_files)

        self.sub.rssfile = "test/data/TheAgendawithStevePaikinVideo/013120.rss"
        expected_files="""Passing on Political Leadership.mp4
Forgery Morrisseau and Indigenous Art.mp4
Old Age The Secret to Happiness.mp4
Daniel Levitin How to Age Well.mp4
Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4""".splitlines()
        self.download_and_test(expected_files)
        
    def download_and_test(self,expected_files):
        self.fdl.dodownload(self.dbfile)
        n = len(self.ffs.listdir(self.sub.podcasts_subdir()))
        self.assertEqual(self.sub.maxeps, n)

        for f in expected_files:
            t = self.ffs.path_join( self.sub.podcasts_subdir(), f, ) 
            self.assertTrue(self.ffs.path_exists(t))

        
if __name__ == '__main__':
    unittest.main()


   


'''>>> dumpx('/home/tomb/u/code/pyc2/test/data/TheAgendawithStevePaikinVideo/012820.rss')
Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4
Meeting Canadas Greenhouse Gas Targets.mp4
Infrastructure Challenges in Ontario.mp4
New Supports for Northern Farmers.mp4
Conservative Leadership Race Begins.mp4
>>> dumpx('/home/tomb/u/code/pyc2/test/data/TheAgendawithStevePaikinVideo/013020.rss')
Old Age The Secret to Happiness.mp4
Daniel Levitin How to Age Well.mp4
Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4
Meeting Canadas Greenhouse Gas Targets.mp4
Infrastructure Challenges in Ontario.mp4
>>> dumpx('/home/tomb/u/code/pyc2/test/data/TheAgendawithStevePaikinVideo/013120.rss')
Passing on Political Leadership.mp4
Forgery Morrisseau and Indigenous Art.mp4
Old Age The Secret to Happiness.mp4
Daniel Levitin How to Age Well.mp4
Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4
>>> 
'''
