import os
import unittest
import random
from filesystem import FakeFileSystem
import logging

logger = logging.getLogger()
# logger.setLevel(logging.INFO)

class FileSystemTest(unittest.TestCase):

    def _prepare_fake_versions_of_real_files(self):
        podcastroot = os.path.expanduser("~/podcasts")
        if os.path.exists(podcastroot):
            files = os.listdir(podcastroot)
            dirs = [os.path.join(podcastroot, f) for f in files if
                    os.path.isdir(os.path.join(podcastroot, f))]
            rdir = random.choice(dirs)
            self.podcastdir = rdir
            files = os.listdir(self.podcastdir)
            for f in files:
                self.ffs.touch(self.podcastdir, f)

    def setUp(self):
        self.ffs = FakeFileSystem()
        self._prepare_fake_versions_of_real_files()

    def test_fake_listdir(self):
        if len(self.ffs.listdir(self.podcastdir)) > 0:
            self.assertEqual(len(os.listdir(self.podcastdir)),
                             len(self.ffs.listdir(self.podcastdir)))

    def _set_up_(self):
        self.hypothetical_path = "~/foo-bar/quux.mp3"
        self.hypothetical_filename = self.hypothetical_path.split("/")[-1]
        self.hypothetical_dir = "/".join(self.hypothetical_path.split("/")[0:-1])

    def test_exception_from_making_redundant_link(self):
        with self.assertRaises(ValueError):
            self._set_up_()
            self.ffs.mkdir(self.hypothetical_dir)
            self.ffs.touch(self.hypothetical_dir, self.hypothetical_path)
            
            dest = "~/foo-bar/dest.mp3"
            self.ffs.link(self.hypothetical_path,
                          dest)

            self.ffs.link(self.hypothetical_path,
                          dest)


    def test_fake_file_system_tests(self):

        self._set_up_()

        self.assertFalse(self.ffs.path_exists(self.hypothetical_dir))
        self.assertFalse(self.ffs.path_exists(self.hypothetical_path))

        self.ffs.touch(self.hypothetical_dir, self.hypothetical_filename)

        self.assertEqual(1, len(self.ffs.listdir(self.hypothetical_dir)))
        self.assertTrue(self.ffs.path_exists(self.hypothetical_path))

        self.ffs.prune_file(self.hypothetical_path)

        self.assertFalse(self.ffs.path_exists(self.hypothetical_path))
        self.assertEqual(0, len(self.ffs.listdir(self.hypothetical_dir)))

        known_unknown = "~/foo-bar/known_unknown.mp3"
        self.assertFalse(self.ffs.path_exists(known_unknown))

    def test_link_creation_test(self):
        src = '~/.podcasts-data/freakonomics/freakonomics_podcast112917.mp3'
        dst = '~/podcasts/freakonomics/Are We Running Out of Ideas.mp3 '
        self.ffs.touch(self.ffs._directory_portion_of_full_path(src),
                       self.ffs._filename_portion_of_full_path(src))
        self.assertTrue(self.ffs.path_exists(src))
        self.assertFalse(self.ffs.path_exists(dst))
        self.assertTrue(self.ffs.link_creation_test(src, dst))
        self.ffs.mkdir(self.ffs._directory_portion_of_full_path(dst))
        self.ffs.link(src,dst)

        self.assertTrue(self.ffs.path_exists(dst))
        self.assertFalse(self.ffs.link_creation_test(src, dst)) 
        
    def test_pathexists_for_nested_empty_directory(self):
        dir = '/foo/bar'
        self.ffs.mkdir(dir)
        self.assertTrue(self.ffs.path_exists(dir))
        

    def g_test_file_rename(self):
        newname = "~/foo-bar/whizbang.mp3"
        self._set_up_()
        self.ffs.rename(self.hypothetical_path,
                        self.ffs.rename(self.hypothetical_path) )



if __name__ == '__main__':
    unittest.main()
