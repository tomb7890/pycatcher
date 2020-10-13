import os
import lib
import logging
logger = logging.getLogger()
# logger.setLevel(logging.INFO)

class FileSystem:

    def __init__(self):
        pass

    def path_exists(self, path):
        return os.path.exists(path)

    def unlink(filename):
        os.unlink(filename)

    def rename(self, old, new):
        os.rename(old, new)

    def mkdir(self, path):
        os.mkdir(path)

    def path_join(self, a, b):
        return os.path.join(a,b)

class FakeFileSystem (FileSystem):
    def __init__(self):
        FileSystem.__init__(self)
        self._ffs = {}

    def reset(self):
        self._ffs = {}

    def mkdir(self, path):
        if path not in self._ffs:
            self._ffs[path] = []
        else:
            raise FileExistsError

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

    def dump(self):
        for k in self._ffs.keys():
            print("key: [%s], \t\t\t value: [%s]." % ( k, self._ffs[k]))

    def unlink(self, fullpath):
    
        path = self._directory_portion_of_full_path(fullpath)
        filename = self._filename_portion_of_full_path(fullpath)

        if path in self._ffs:
            filelist = self._ffs[path]
            if filename in filelist:
                filelist.remove(filename)
                return 

        raise FileNotFoundError 

    def exists(self, filename):
        return self.path_exists(filename)

    def _directory_portion_of_full_path(self, fullpath):
        segments = fullpath.split("/")
        path = "/".join(segments[0:len(segments)-1])
        return path

    def _filename_portion_of_full_path(self, fullpath):
        return lib.basename(fullpath) 



if __name__ == '__main__':
    pass
