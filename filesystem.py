import os

import logging
logger = logging.getLogger()
# logger.setLevel(logging.INFO)

class FileSystem:

    def __init__(self):
        pass

    def link_creation_test(self, src, dst):
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

    def mkdir(self, path):
        os.mkdir(path)

    def path_join(self, a, b):
        return os.path.join(a,b)

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
        # if directory doesn't yet exist
        if path not in self._ffs:
            # mkdir the dir
            self._ffs[path] = []
        else:
            # if it already exists, I guess it is an error to call mkdir on a directory that already exists.
            raise Exception(path)

    def touch(self, directory, filename):

        if directory in self._ffs:
            files = self._ffs[directory]
            files.append(filename)
        else:
            files = []
            files.append(filename)
            self._ffs[directory] = files 

    def path_exists(self, path):
        if path in self._ffs.keys():
            return True

        dir = self._directory_portion_of_full_path(path)
        filename = self._filename_portion_of_full_path(path)

        if dir in self._ffs:
            files = self._ffs[dir]
            if filename in files:
                return True
            else:
                return False 
        return False

    def rename(self, old, new):
        # First consider the case of renaming a file to the same directory 
        olddir = self._directory_portion_of_full_path(old)
        oldfilename = self._filename_portion_of_full_path(old)
        if olddir not in self._ffs.keys():
            raise Exception("Rename: no such directory: [%s]" % olddir ) 
        # get file listing of directory
        oldfiles = self._ffs[self._directory_portion_of_full_path(old)]
        if oldfilename  not in oldfiles:
            raise Exception("Rename: no such file: [%s]" % oldfilename) 
        newfilelist = []
        newfilename = self._filename_portion_of_full_path(new)
        for o in oldfiles:
            if o != oldfilename:
                newfilelist.append(o)
            newfilelist.append(newfilename)
        self._ffs[self._directory_portion_of_full_path(old)] = newfilelist
        
    def listdir(self, path):
        dir = self._ffs[path]
        return dir

    def prune_link(self, fullpath):
        self.prune_file(fullpath)

    def prune_file(self, fullpath):
        path = self._directory_portion_of_full_path(fullpath)
        filename = self._filename_portion_of_full_path(fullpath)

        if path in self._ffs:
            filelist = self._ffs[path]
            if filename in filelist:
                filelist.remove(filename)

    def exists(self, filename):
        return self.path_exists(filename)


if __name__ == '__main__':
    pass
