from urllib.request import ProxyHandler, build_opener, install_opener, urlretrieve
from tqdm import tqdm

class Downloader:

    def __init__(self, f, s, a = None):
        self.fs = f
        self.sub = s
        self.args = a 

    def dodownload(self, db):

        # create directories 
        dirs = [ self.sub.base_podcasts_dir(), self.sub.podcasts_subdir() ]
        for d in dirs :
            if not self.fs.path_exists(d):
                self.fs.mkdir(d) 

        # load the database 
        db.load()

        self.episodes = self.sub.parse_rss_file()
        self.new = self.episodes[0:self.sub.maxeps]
        self.old = self.episodes[self.sub.maxeps:]

        for e in self.new:
            guid = e.guid
            if guid not in db.table:
                filename = self.generate_file_name(e, db, len(self.episodes))
                self.queue(e, filename)
            else:
                filename = db.table[e.guid]
                if not self.fs.path_exists(filename):
                    self.queue(e, filename)

        self.download_queue(db)

        # finish up 
        self.remove_oldones(db)
        db.save()
        self.delete_queue()
    
    def remove_oldones(self, db):
        for e in self.old:
            if e.guid in db.table:
                filename = db.table[e.guid]
                if self.fs.path_exists(filename):
                    self.fs.prune_file(filename)
                db.remove_entry(e.guid)
                    
    def delete_queue(self):
        if hasattr(self, '_queue'):
            del self._queue
        
    def queue(self, episode, filename):
        if not hasattr(self, '_queue'):
            self._queue = [] 
        
        item = episode, filename 
        self._queue.append(item)

    def generate_file_name(self, episode, db, max):

        ''''Generate a new file name that is not yet in use

        A file name is typically the text of an episode's TITLE
        element.  However sometimes there are duplicate (repeating)
        TITLEs, e.g. "Week in Review". In this case a modified version
        must be generated to avoid the exception by the filesystem
        when a second file with the same name is created.  A numerical
        suffix is appended to the filename to avoid duplication.
        '''

        count = 1

        proposal = episode.basename()
        while True:
            if count > max:
                raise RuntimeError
            count = count + 1
            if not self.in_use(db, proposal):
                break
            proposal = episode.filename_base() \
                       + "-%d" % count + episode.filename_extension()
        return proposal

    def in_use(self, db, filename):
        if filename in db.table.values():
            return True
        if hasattr(self, '_queue'):
            found = False 
            for q in self._queue:
                e, f  = q 
                if filename == f:
                    found = True
            return found
        return False
                
    def download_queue(self, db):
        if not hasattr(self, '_queue'):
            return 

        for tuple in self._queue:
            episode, destination_filename = tuple
            try:
                self.download_episode(episode, destination_filename)
            except Exception as e:
                print(e) 

            fullpath = self.fs.path_join(self.sub.podcasts_subdir(), destination_filename)
            if self.fs.path_exists(fullpath):
                db.table[episode.guid] = fullpath


    def download_episode(self, episode, destination_filename):
        target = self.fs.path_join(self.sub.podcasts_subdir(), destination_filename)
        if self.fs.path_exists(target):
            raise Exception("target file exists! " + target)

        self.download_impl(episode, destination_filename)

    def download_impl(self, episode, destination_filename  ):
        fetch( episode.url, self.fs.path_join(self.sub.podcasts_subdir(), destination_filename),
                      self.sub.title, self.args)

class FakeDownloader(Downloader):
    def __init__(self, fs, subscription ):
        Downloader.__init__(self, fs, subscription)

    def download_impl(self, episode, destination):
        self.fs.touch(self.sub.podcasts_subdir(), destination  )

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def fetch(url, output_path, program, args):

    if not args.quiet:
        with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=program + ' ' + url.split('/')[-1]) as t:

            # Some very popular podcasts reject the Python user agent.
            proxy = ProxyHandler({})
            opener = build_opener(proxy)
            opener.addheaders = [('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30')]
            install_opener(opener)
            urlretrieve(url, output_path, t.update_to)

    else:
        urlretrieve(url, output_path)

        
if __name__ == '__main__':
    pass




