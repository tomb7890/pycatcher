import os.path


class FileSystem:

    def __init__(self):
        pass

    def path_exists(self, path):
        return os.path.exists(path)

    def unlink(self, filename):
        os.unlink(filename)

    def mkdir(self, path):
        os.mkdir(path)

    def path_join(self, a, b):
        return os.path.join(a, b)


class FakeFileSystem(FileSystem):
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

        dir = os.path.dirname(path)
        filename = os.path.basename(path)

        if dir in self._ffs:
            files = self._ffs[dir]
            if filename in files:
                return True
        return False

    def listdir(self, path):
        if path is None:
            raise FileNotFoundError("Cannot list directory: path is None")
        dir = self._ffs[path]
        return dir

    def unlink(self, fullpath):

        path = os.path.dirname(fullpath)
        filename = os.path.basename(fullpath)

        if path in self._ffs:
            filelist = self._ffs[path]
            if filename in filelist:
                filelist.remove(filename)
                return

        raise FileNotFoundError

    def _dump(self):
        for k in self._ffs.keys():
            print("key: [%s], \t\t\t value: [%s]." % (k, self._ffs[k]))


if __name__ == "__main__":
    pass
