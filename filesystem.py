import os
import lib


class FileSystem:

    def __init__(self):
        pass

    def path_exists(self, path):
        return os.path.exists(path)

    def unlink(filename):
        os.unlink(filename)

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

    def _directory_portion_of_full_path(self, fullpath):
        segments = fullpath.split("/")
        path = "/".join(segments[0:len(segments)-1])
        return path

    def _filename_portion_of_full_path(self, fullpath):
        return lib.basename(fullpath) 



if __name__ == '__main__':
    pass
