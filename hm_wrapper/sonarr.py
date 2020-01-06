# -*- coding: utf-8 -*-
import json

import requests


class Sonarr(object):

    def __init__(self, host_url: str, api_key: str):
        """Constructor requires Host-URL and API-KEY
        :type api_key: object
        :type host_url: str
        """

        if host_url.rstrip('/').endswith('api'):
            self.host_url = host_url.rstrip('/')
        else:
            self.host_url = host_url.rstrip('/') + '/api'

        self.Commands = self._Commands(self)
        self.api_key = api_key

    # ENDPOINT CALENDAR
    def get_calendar(self):
        # optional params: start (date) & end (date)
        """Gets upcoming episodes, if start/end are not supplied episodes airing today and tomorrow will be returned,
        Returns Json """
        res = self.request_get("{}/calendar".format(self.host_url))
        return res.json()

    # ENDPOINT COMMAND
    def run_command(self, **kwargs):
        ags = dict()
        for key, value in kwargs.items():
            if value is not None:
                ags[key] = value
        res = self.request_post(f'{self.host_url}/command', data=ags)
        return res.json()

    def get_command(self, command_id: int = None):
        """Without an id argument, returns the status of all currently started commands;
        if id argument is supplied, it will return the status of just that run_command"""
        id_string = str()
        if command_id is not None:
            id_string += "/" + command_id
        res = self.request_get(f"{self.host_url}/run_command{id_string}")
        return res.json()

    # ENDPOINT DISKSPACE
    def get_diskspace(self):
        """Return Information about Diskspace"""
        res = self.request_get("{}/diskspace".format(self.host_url))
        return res.json()

    # ENDPOINT EPISODE
    def get_episodes_by_series_id(self, series_id):
        """Returns all episodes for the given series"""
        res = self.request_get("{}/episode?seriesId={}".format(self.host_url, series_id))
        return res.json()

    def get_episode_by_episode_id(self, episode_id):
        """Returns the episode with the matching id"""
        res = self.request_get("{}/episode/{}".format(self.host_url, episode_id))
        return res.json()

    def upd_episode(self, data):
        # TEST THIS
        """Update the given episodes, currently only monitored is changed, all other modifications are ignored"""
        '''NOTE: All parameters (you should perform a GET/{id} and submit the full body with the changes,
        as other values may be editable in the future.'''
        res = self.request_put("{}/episode".format(self.host_url, data))
        return res.json()

    # ENDPOINT EPISODE FILE
    def get_episode_files_by_series_id(self, series_id):
        """Returns all episode files for the given series"""
        res = self.request_get("{}/episodefile?seriesId={}".format(self.host_url, series_id))
        return res.json()

    # TEST THIS
    def get_episode_file_by_episode_id(self, episode_id):
        """Returns the episode file with the matching id"""
        res = self.request_get("{}/episodefile/{}".format(self.host_url, episode_id))
        return res.json()

    # TEST THIS
    def rem_episode_file_by_episode_id(self, episode_id):
        """Delete the given episode file"""
        res = self.request_del("{}/episodefile/{}".format(self.host_url, episode_id))
        return res.json()

    # ENDPOINT HISTORY
    def get_history(self):
        """Gets history (grabs/failures/completed)"""
        res = self.request_get("{}/history".format(self.host_url))
        return res.json()

    # ENDPOINT HISTORY SIZE
    def get_history_size(self, page_size):
        """Gets history (grabs/failures/completed)"""
        res = self.request_get("{}/history?pageSize={}".format(self.host_url, page_size))
        return res.json()

    # ENDPOINT WANTED MISSING
    # DOES NOT WORK
    def get_wanted_missing(self):
        """Gets missing episode (episodes without files)"""
        res = self.request_get("{}/wanted/missing/".format(self.host_url))
        return res.json()

    # ENDPOINT QUEUE
    def get_queue(self):
        """Gets current downloading info"""
        res = self.request_get("{}/queue".format(self.host_url))
        return res.json()

    # ENDPOINT PROFILE
    def get_quality_profiles(self):
        """Gets all quality profiles"""
        res = self.request_get("{}/profile".format(self.host_url))
        return res.json()

    # ENDPOINT RELEASE

    # ENDPOINT RELEASE/PUSH
    def push_release(self, title, download_url, protocol, publish_date):
        """Notifies Sonarr of a new release.
            title: release name
            download_url: .torrent file URL
            protocol: usenet / torrent
            publish_date: ISO8601 date string
        """
        res = self.request_post(
            "{}/release/push".format(self.host_url),
            {
                'title': title,
                'download_url': download_url,
                'protocol': protocol,
                'publish_date': publish_date
            })
        return res.json()

    # ENDPOINT ROOTFOLDER
    def get_root_folder(self):
        """Returns the Root Folder"""
        res = self.request_get("{}/rootfolder".format(self.host_url))
        return res.json()

    # ENDPOINT SERIES
    def get_series(self):
        # """Return all series in your collection"""
        res = self.request_get("{}/series".format(self.host_url))
        return res.json()

    def get_series_by_series_id(self, series_id):
        # """Return the series with the matching ID or 404 if no matching series is found"""
        res = self.request_get("{}/series/{}".format(self.host_url, series_id))
        return res.json()

    # noinspection PyPep8Naming
    def construct_series_json(self, tvdbId, quality_profile):
        """Searches for new shows on trakt and returns Series object to add"""
        res = self.request_get("{}/series/lookup?term={}".format(self.host_url, 'tvdbId:' + str(tvdbId)))
        s_dict = res.json()[0]

        # get root folder path
        root = self.get_root_folder()[0]['path']
        series_json = {
            'title': s_dict['title'],
            'seasons': s_dict['seasons'],
            'path': root + s_dict['title'],
            'qualityProfileId': quality_profile,
            'seasonFolder': True,
            'monitored': True,
            'tvdbId': tvdbId,
            'images': s_dict['images'],
            'titleSlug': s_dict['titleSlug'],
            "addOptions": {
                "ignoreEpisodesWithFiles": True,
                "ignoreEpisodesWithoutFiles": True
            }
        }
        return series_json

    def add_series(self, series_json):
        """Add a new series to your collection"""
        res = self.request_post("{}/series".format(self.host_url), data=series_json)
        return res.json()

    def upd_series(self, data):
        """Update an existing series"""
        res = self.request_put("{}/series".format(self.host_url), data)
        return res.json()

    def rem_series(self, series_id, rem_files=False):
        """Delete the series with the given ID"""
        # File deletion does not work
        data = {
            # 'id': series_id,
            'deleteFiles': 'true'
        }
        res = self.request_del("{}/series/{}".format(self.host_url, series_id), data)
        return res.json()

    # ENDPOINT SERIES LOOKUP
    def lookup_series(self, query):
        """Searches for new shows on trakt"""
        res = self.request_get("{}/series/lookup?term={}".format(self.host_url, query))
        return res.json()

    # ENDPOINT SYSTEM-STATUS
    def get_system_status(self):
        """Returns the System Status"""
        res = self.request_get("{}/system/status".format(self.host_url))
        return res.json()

    # REQUESTS STUFF
    def request_get(self, url, data=None):
        # """Wrapper on the requests.get"""
        if data is None:
            data = {}
        headers = {
            'X-Api-Key': self.api_key
        }
        res = requests.get(url, headers=headers, json=data)
        return res

    def request_post(self, url, data):
        # """Wrapper on the requests.post"""
        headers = {
            'X-Api-Key': self.api_key
        }
        res = requests.post(url, headers=headers, json=data)
        return res

    def request_put(self, url, data):
        # """Wrapper on the requests.put"""
        headers = {
            'X-Api-Key': self.api_key
        }
        data2 = json.loads(data)
        res = requests.put(url, headers=headers, json=data2)
        return res

    def request_del(self, url, data):
        # """Wrapper on the requests.delete"""
        headers = {
            'X-Api-Key': self.api_key
        }
        res = requests.delete(url, headers=headers, json=data)
        return res

    class _Commands(object):
        def __init__(self, parent):
            assert isinstance(parent, Sonarr)
            self._sonarr = parent

        def refresh_series(self, series_id: int = None):
            """
            Refresh series information from trakt and rescan disk
            :series_id: if not set all series will be refreshed and scanned
            """
            return self._sonarr.run_command(name='RefreshSeries', seriesId=series_id)

        def rescan_series(self, series_id: int = None):
            """Rescan disk for movies
            :movie_id: if not set all movies will be scanned
            """
            return self._sonarr.run_command(name='RescanSeries', seriesId=series_id)

        def episode_search(self, episode_ids: list = None):
            """
            Search for one or more movies
            :type episode_ids: list
            :parameter episode_ids: one or more episodeIds in an array Not 100% sure on this run_command variable
            """
            return self._sonarr.run_command(name='EpisodeSearch', episodeIds=episode_ids)

        def season_search(self, series_id: int, season_number: int):
            """
            Search for all episodes of a particular season
            :param series_id:
            :param season_number:
            """
            return self._sonarr.run_command(name='SeasonSearch', seriesId=series_id, seasonNumber=season_number)

        def series_search(self, series_id: int):
            """
            Search for all episodes in a series
            :param series_id:
            """
            return self._sonarr.run_command(name='SeriesSearch', seriesId=series_id)

        def downloaded_episodes_scan(self, path: str = None, download_client_id: str = None, import_mode: str = None):
            """
            Update: Due to a deprecated Drone Factory, this command should only be used in combination with the 'path'
            set in the POSTed json body.

            Instruct Sonarr to scan and import the DroneFactoryFolder or another folder defined by the path variable.
            Each file and folder in the DroneFactoryFolder is interpreted as a separate download (job). A folder
            specified by the path variable is assumed to be a single download (job) and the folder name should be the
            release name. The downloadClientId can be used to support this API endpoint in conjunction with Completed
            Download Handling, so Sonarr knows that a particular download has already been imported. Optionally the
            'importMode' can be used to specify whether Sonarr should Hardlink/Copy or Move the imported files.
            :param path:
            :param download_client_id: - nzoid for sabnzbd ; special 'drone' attribute value for nzbget;
            - uppercase infohash for torrents
            :param import_mode: Move or Copy
            - Copy = Copy or Hardlink depending on Sonarr configuration
            - Can be used to override the default Copy for torrents with external preprocessing/transcoding/unrar.
            """
            return self._sonarr.run_command(name='DownloadedEpisodesScan', path=path,
                                            downloadClientId=download_client_id
                                            , importMode=import_mode)

        def rss_sync(self):
            """Instruct Sonarr to perform an RSS sync with all enabled indexers"""
            return self._sonarr.run_command(name='RssSync')

        def rename_files(self, files: list = None):
            """Instruct Sonarr to rename the list of files provided.
            :type files: list
            :param files: List of File IDs to rename
            """
            return self._sonarr.run_command(name='RenameFiles', files=files)

        def rename_series(self, series_ids: list):
            """Instruct Sonarr to rename all files in the provided series.
            :type series_ids: list
            :param series_ids: List of Movie IDs to rename
            """
            return self._sonarr.run_command(name='RenameMovie', seriesIds=series_ids)

        def backup(self):
            """
            Instruct Sonarr to perform a backup of its database and config file (nzbdrone.db and config.xml)
            """
            return self._sonarr.run_command(name='Backup')

        def missing_episode_search(self):
            """
            Instruct Sonarr to perform a backlog search of missing episodes (Similar functionality to Sickbeard)
            """
            return self._sonarr.run_command(name='missingEpisodeSearch')
