import os
import logging
import shutil

from filesystem import FakeFileSystem
logger = logging.getLogger()

from options import Options  

class AutoFile:
    def __init__(self, queue):
        self._set_up_for_using_input_file(queue)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._clean_up_input_file()

    def _set_up_for_using_input_file(self, queue):
        self.inputfile = 'urls.dat'
        f = open(self.inputfile, 'w')
        f.write('%s\n' % ('\n'.join([x.url for x in queue])))
        f.close()

    def _clean_up_input_file(self):
        if os.path.exists(self.inputfile):
             os.unlink(self.inputfile)


class Downloader:
    def __init__(self, args=None):
        self.cmd = ""
        self.args = args

    def getCmd(self):
        return self.cmd

    def prepare_command(self, o):
        cmd = "wget "

        for k in o._dict.keys():
            cmd = cmd + ' %s="%s" ' % (k, o._dict[k])

        verbosity = "--quiet"
        if self.args and self.args.verbose:
            verbosity = None

        if verbosity:
            cmd = cmd + " %s" % verbosity

        if self.url is not None:
            cmd = cmd + ' "%s" ' % self.url

        self.cmd = cmd

    def download_file(self, url, path):
        ''' Downloads an single url. '''
        o = Options()
        o.add_option('--output-document', path)
        self.url = url
        self.prepare_command(o)
        self._download_file(url, path)

    def download_queue(self, queue, o):
        self.url = None
        with AutoFile(queue) as af:
            o.add_option('--input-file', af.inputfile)
            self.prepare_command(o)
            logging.info('Downloader.download_queue(): %s' % self.getCmd())
            self._download_queue(queue, o)

    def _download_queue(self, queue, o):
        self.invoke_download_command()

    def invoke_download_command(self):
        os.system(self.getCmd())

    def _download_file(self, filename, url):
        self.invoke_download_command()


class FakeDownloader(Downloader):
    def __init__(self, args=None):
        Downloader.__init__(self, args)
        self.url = ''
        self.fs = FakeFileSystem()

    def _download_file(self, filename, url):
        dest = os.path.expanduser('~/.podcasts-data/rss/on_point_wbur.xml')
        if os.path.exists(dest):
            os.unlink(dest)
        src = os.path.join(os.getcwd(), 'test/data/foo')
        shutil.copyfile(src, dest)

    def _download_queue(self, queue, o):
        logging.info("FakeDownloader:download_queue(): %s" % self.getCmd())

        if queue:
            for episode in queue:
                logging.info("@" * 30 + " download_file" )
                datadir = o._dict['--directory-prefix']
                self.fs.touch(datadir, episode._filename_from_url())

    def invoke_download_command(self):
        pass
