import os
import logging

from downloadqueue import DownloadQueue
from index import episode_is_registered


class EpisodeQueue:

    def __init__(self, subscription, filesystem):
        self.subscription = subscription
        self.filesystem = filesystem
        self.queue = DownloadQueue()

    def clear(self):
        self.queue.clear()

    def enqueue(self, episode, db):
        if not episode_is_registered(db, episode):
            self._generate_filename_and_queue_episode(episode, db)
        else:
            self._queue_anyway_if_file_is_missing(db, episode)

    def _generate_filename_and_queue_episode(self, episode, db):
        filename = self._generate_file_name(episode, db)
        self.queue.queue(episode, filename)

    def _generate_file_name(
        self,
        episode,
        db,
    ):
        """

        Generate a new file name that is not yet in use

        A file name is typically the text of an episode's TITLE
        element.  However sometimes there are duplicate (repeating)
        TITLEs, e.g. "Week in Review". In this case a modified version
        must be generated to avoid the exception by the filesystem
        when a second file with the same name is created.  A numerical
        suffix is appended to the filename to avoid duplication.


        """
        max = len(self.subscription.episodes())
        count = 1

        proposal = episode.basename()
        while True:
            if count > max:
                raise RuntimeError
            count = count + 1
            if not self._in_use(db, proposal):
                break
            proposal = episode.numerify_filename(count)
        return proposal

    def _in_use(self, db, filename):
        if db.has(filename):
            return True
        if self.queue.in_use(filename):
            return True
        return False

    def _queue_anyway_if_file_is_missing(self, db, episode):
        registered_filename = db.get(episode)
        if self._file_of_registered_episode_is_missing(episode, registered_filename):
            self.queue.queue(episode, os.path.basename(registered_filename))

    def _download_episode_queue(self, db, downloader):
        for tuple in self.queue._queue:

            episode, destination_filename = tuple

            fullpath = self.filesystem._full_path(destination_filename)

            if self.filesystem.path_exists(fullpath):
                logging.info("Target file already exists: %s", fullpath)
            else:
                try:
                    downloader.download_impl(episode, destination_filename)
                except Exception as e:
                    logging.exception(
                        "Error downloading %s: %s", destination_filename, e
                    )
            if self.filesystem.path_exists(fullpath):
                db.set(episode, fullpath)

    def _file_of_registered_episode_is_missing(self, episode, registered_filename):
        return not self.filesystem.path_exists(registered_filename)
