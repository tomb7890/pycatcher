# Pycatcher
### Simple podcast subscription and downloading

Pycatcher is a Python command-line podcast client designed to be used with a preferred media player application. Pycatcher processes a configuration file for subscription information, and downloads media content as ordinary files. Individual media items (episodes) are written to disk with filenames derived from the text of the RSS TITLE elements.

### Configuration
A `pycatcher.conf` configuration file is used to adjust
file system location to find the podcast programs(links). Within this file, there is a main section `[general]` in which to set the `podcasts-directory`, the root directory where podcasts will be downloaded to, and an optional `podcasts-directory`, which can be set as the location of primary data storage.

An additional section is used to describe each feed, or subscription of interest.  The option of primary importance under these sections is the `url` option; this is used to indicate the internet address of a the feed.  An `rssfile` option is used to specify a name for the local copy of the RSS file.  A `maxeps` option for a feed will specify the total number of items, or episodes, that will be downloaded.  As new items appear in a given feed, the oldest episodes that exceed `maxeps` will be removed from the disk.

Optionally,  a `data-directory` option may be used override the location of primary media storage.  Add URLs for as many feeds as you like and, for each feed, an optional integer in `maxeps`  if you would like other than the default of three of the latest episodes.

By default, downloaded media will be stored in the "~/podcasts" directory. Set the `PODCASTROOT` environment variable to overrride this preference.



### Installation
Rename the provided `pycatcher.conf.example` and modify accordingly.

### Execution
`$ python application.py`
