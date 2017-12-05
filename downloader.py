import os
import logging
import shutil
from filesystem import FakeFileSystem
logger = logging.getLogger()


class Downloader:
    def __init__(self, **args):
        self._dict = {}
        self.cmd = ""
        self.args = args

    def add_option(self, name, value):
        self._dict[name] = value

    def remove_option(self, name):
        if name in self._dict:
            del self._dict[name]

    def getCmd(self):
        return self.cmd

    def prepare_command(self):
        cmd = "wget "

        for k in self._dict.keys():
            cmd = cmd + ' %s="%s" ' % (k, self._dict[k])

        verbosity = "--quiet"
        if 'verbose' in self.args:
            if self.args['verbose']:
                verbosity = None

        if verbosity:
            cmd = cmd + " %s" % verbosity

        if self.url is not None:
            cmd = cmd + ' "%s" ' % self.url

        self.cmd = cmd

    def download_file(self, url, path):
        ''' Downloads an single url. '''
        self.add_option('--output-document', path)
        self.url = url
        self.prepare_command()
        self._download_file(url, path)

    def download_queue(self, queue):
        self._set_up_for_using_input_file(queue)
        self.prepare_command()
        logging.info('Downloader.download_queue(): %s' % self.getCmd())
        self._download_queue(queue)
        self._clean_up_input_file()

    def _set_up_for_using_input_file(self, queue):
        self.remove_option('--output-document')
        self.inputfile = 'urls.dat'
        self.add_option('--input-file', self.inputfile)
        self.url = None
        f = open(self.inputfile, 'w')
        f.write('%s\n' % ('\n'.join([x.url for x in queue])))
        f.close()

    def _clean_up_input_file(self):
        if os.path.exists(self.inputfile):
            os.unlink(self.inputfile)

    def _download_queue(self, queue):
        self.invoke_download_command()

    def invoke_download_command(self):
        os.system(self.getCmd())

    def _download_file(self, filename, url):
        self.invoke_download_command()


class FakeDownloader(Downloader):
    def __init__(self, **args):
        Downloader.__init__(self, **args)
        self.url = ''
        self.fs = FakeFileSystem()

    def _download_file(self, filename, url):
        dest = os.path.expanduser('~/.podcasts-data/rss/on_point_wbur.xml')
        if os.path.exists(dest):
            os.unlink(dest)
        src = os.path.join(os.getcwd(), 'test/data/foo')
        shutil.copyfile(src, dest)

    def _download_queue(self, queue):
        logging.info("FakeDownloader:download_queue(): %s" % self.getCmd())

        if queue:
            for episode in queue:
                logging.info("@" * 30 + " download_file" )
                datadir = self._dict['--directory-prefix']
                self.fs.touch(datadir, episode._filename_from_url())

    def invoke_download_command(self):
        pass
