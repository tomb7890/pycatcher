import os
import unittest
import random
from filesystem import FakeFileSystem


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

    def test_fake_file_system_tests(self):

        hypothetical_path = "/home/tomb/foo-bar/quux.mp3"
        hypothetical_filename = hypothetical_path.split("/")[-1]
        hypothetical_dir = "/".join(hypothetical_path.split("/")[0:-1])

        self.assertFalse(self.ffs.path_exists(hypothetical_dir))
        self.assertFalse(self.ffs.path_exists(hypothetical_path))

        self.ffs.touch(hypothetical_dir, hypothetical_filename)

        self.assertEqual(1, len(self.ffs.listdir(hypothetical_dir)))
        self.assertTrue(self.ffs.path_exists(hypothetical_path))

        self.ffs.prune_file(hypothetical_path)

        self.assertFalse(self.ffs.path_exists(hypothetical_path))
        self.assertEqual(0, len(self.ffs.listdir(hypothetical_dir)))

        known_unknown = "/home/tomb/foo-bar/known_unknown.mp3"
        self.assertFalse(self.ffs.path_exists(known_unknown))


if __name__ == '__main__':
    unittest.main()
