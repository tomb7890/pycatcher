import requests
from tqdm import tqdm
from downloadqueue import DownloadQueue


class Downloader:
    def __init__(self, filesystem, subscription, args=None):
        self.filesystem = filesystem
        self.subscription = subscription
        self.args = args
        self.queue = DownloadQueue()

    def download_impl(self, episode, destination_filename):
        fetch(
            episode.url,
            self.filesystem._full_path(
                self.subscription.podcasts_subdir(), destination_filename
            ),
            self.subscription.title,
            self.args,
        )


class FakeDownloader(Downloader):
    def __init__(self, fs, subscription):
        Downloader.__init__(self, fs, subscription)

    def download_impl(self, episode, destination_filename):
        self.filesystem.touch(self.subscription.podcasts_subdir(), destination_filename)


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def fetch(url, output_path, program, args):

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    if response.status_code == 200:
        with open(output_path, "wb") as file, tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc=program + " " + url.split("/")[-1],
            ncols=80,
            disable=args.quiet,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))


if __name__ == "__main__":
    pass
