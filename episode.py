import re, string

class Episode:
    def __init__(self=None, s=None):
        pass

    def filename_base(self):
        validchars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        basename = ''
        for char in self.title:
            if char in validchars:
                basename = basename + char
        return basename

    def basename(self):
        return self.filename_base() + self.filename_extension()

    def filename_extension(self):
        thedot = self.url.rfind(".")
        extension = self.url[thedot:]
        extension = re.sub(r'(.*)\?(.*)', '\\1', extension )
        return extension


if __name__ == '__main__':
    pass
