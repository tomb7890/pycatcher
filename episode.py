from dataclasses import dataclass
import re
import string


@dataclass
class Episode:
    title: str = None
    guid: str = None
    description: str = None
    image: str = None

    def filename_base(self):
        validchars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        basename = ""
        for char in self.title:
            if char in validchars:
                basename = basename + char
        return basename

    def basename(self):
        return self.filename_base() + self.filename_extension()

    def filename_extension(self):
        thedot = self.url.rfind(".")
        extension = self.url[thedot:]
        extension = re.sub(r"(.*)\?(.*)", "\\1", extension)
        return extension

    def numerify_filename(self, count):
        return self.filename_base() + "-%d" % count + self.filename_extension()


if __name__ == "__main__":
    pass
