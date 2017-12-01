import os

import logging


class FileSystem:

    def __init__(self):
        pass

    def link_creation_test(self, src, dst):
        logging.info("link_creation_test: %s and %s " % (src, dst))
        if self.path_exists(src) and not self.path_exists(dst):
            return True
        else:
            return False
    

    def path_exists(self, path):
        return os.path.exists(path)

    def prune_file(self, filename):
        if os.path.exists(filename):
            os.unlink(filename)

    def prune_link(self, filename):
        if os.path.exists(filename):
            os.unlink(filename)

    def link(self, src, dest):
        os.link(src, dest)

    def rename(self, old, new):
        os.rename(old, new)


class FakeFileSystem (FileSystem):

    def _directory_portion_of_full_path(self, fullpath):
        segments = fullpath.split("/")
        path = "/".join(segments[0:len(segments)-1])
        return path

    def _filename_portion_of_full_path(self, fullpath):
        segments = fullpath.split("/")
        basename = segments[-1]
        return basename

    def __init__(self):
        FileSystem.__init__(self)
        self._ffs = {}

    def link(self, src, dest):

        basename = self._filename_portion_of_full_path(dest)
        directory = self._directory_portion_of_full_path(dest)
        dir = self._ffs[directory]
        if basename in dir:
            raise ValueError
        dir.append(basename)

    def mkdir(self, path):

        if path not in self._ffs:
            self._ffs[path] = []
        else:
            raise Exception

    def touch(self, directory, filename):
        dir = None
        if directory in self._ffs:
            files = self._ffs[directory]
            files.append(filename)
        else:
            files = []
            files.append(filename)
            self._ffs[directory] = files 

    def path_exists(self, path):
        x = False 
        dirq = self._directory_portion_of_full_path(path)
        filename = self._filename_portion_of_full_path(path)
        if dirq in self._ffs:
            dir = self._ffs[dirq]
            if filename in dir:
                x= True
        return x 

    def listdir(self, path):
        dir = self._ffs[path]
        return dir

    def prune_link(self, fullpath):
        self.prune_file(fullpath)

    def prune_file(self, fullpath):
        dirq = self._directory_portion_of_full_path(fullpath)
        filename = self._filename_portion_of_full_path(fullpath)

        if dirq in self._ffs:
            dir = self._ffs[dirq]
            if filename in dir:
                dir.remove(filename)

    def exists(self, filename):
        return self.path_exists(filename)


if __name__ == '__main__':
    pass
