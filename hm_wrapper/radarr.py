# -*- coding: utf-8 -*-
import json
import requests

from hm_wrapper import _utils


class Radarr(object):

    def __init__(self, host_url: str, api_key: str):
        """Constructor requires Host-URL and API-KEY
        :type api_key: object
        :type host_url: str
        """

        if host_url.rstrip('/').endswith('api'):
            self.host_url = host_url.rstrip('/')
        else:
            self.host_url = host_url.rstrip('/') + '/api'
        self.api_key = api_key
        self.Commands = self._Commands(self)

    # ENDPOINT CALENDAR
    def get_calendar(self, start_date=None, end_date=None):
        """Gets upcoming episodes, if start/end are not supplied episodes airing today and tomorrow will be returned,
        Returns Json
            will attempt to parse date strings """
        query_params = dict()
        if start_date is not None:
            query_params['start'] = _utils.parse_date_input(start_date)
        if end_date is not None:
            query_params['end'] = _utils.parse_date_input(end_date)

        res = self.request_get("{}/calendar".format(self.host_url), params=query_params)
        return res.json()

    # ENDPOINT COMMAND

    def run_command(self, **kwargs):
        ags = dict()
        for key, value in kwargs.items():
            if value is not None:
                ags[key] = value
        data = None
        if len(ags) > 0:
            # for some reason the api is only accepting json after being serialized and then deserialized again
            # ... not sure why, possibly due to the way that requests encodes json
            data = json.dumps(ags)
        # with io.StringIO() as f:
        #     json.dumps(ags, fp=f)
        #     data = f.getvalue()
        #     f.close()

        res = self.request_post(f'{self.host_url}/command?name={ags["name"]}', data=data)
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

    # ENDPOINT HISTORY
    def get_history(self, page: int = 0, page_size: int = 10, sort_key: str = None, sort_dir: str = None):
        """Gets history (grabs/failures/completed)
        :param page:  1-indexed
        :param page_size: Default: 0
        :param sort_dir: asc or desc - Default: asc
        :param sort_key: movie.title or date
        """
        query_string = "?"
        query_string += f'page={page}'
        if page_size is not None:
            query_string += f'&pageSize={page_size}'
        if sort_key is not None:
            query_string += f'&sortKey={sort_key}'
        if sort_dir is not None:
            query_string += f'&sortDir={sort_dir}'

        res = self.request_get(f"{self.host_url}/history{query_string}")
        return res.json()

    # ENDPOINT MOVIE
    def get_movie(self, movie_id: int = None):
        """If no arguments: Gets all movies in your collection, otherwise will attempt to find the movie id specified
        :param movie_id: the id of the movie to lookup"""
        movieid = str()
        if movie_id is not None:
            movieid = f'/{movie_id}'
        res = self.request_get(f'{self.host_url}/movie{movieid}')
        return res.json()

    def add_movie(self, title: str, quality_profile_id: str, title_slug: str, tmdb_id: int, year: int,
                  path: str,
                  images: list = None,
                  monitored: bool = None,
                  search_for_movie: bool = None) -> object:
        """
        Adds a new movie to your collection
        NOTE: if you do not add the required params, then the movie addition wont function. Some of these without the others
         can indeed make a "movie". But it wont function properly in Radarr.
        :param title:
        :param quality_profile_id:
        :param title_slug:
        :param images:
        :param tmdb_id:
        :param year: release year. Very important needed for the correct path!
        :param path: full path to the movie on disk or rootFolderPath (string) - full path will be created by combining
         the rootFolderPath with the movie title
        :param monitored: whether the movie should be monitored or not.
        :param search_for_movie: whether Radarr should search for the movie upon being added.
        """
        jsonbody = dict()
        jsonbody['title'] = title
        jsonbody['qualityProfileId'] = quality_profile_id
        jsonbody['titleSlug'] = title_slug
        jsonbody['tmdbId'] = tmdb_id
        jsonbody['year'] = year
        jsonbody['path'] = path
        if images is not None:
            jsonbody['images'] = images
        if search_for_movie is not None:
            op = {
                "searchForMovie": search_for_movie
            }

            jsonbody['addOptions'] = op
        if monitored is not None:
            jsonbody['monitored'] = monitored
        data = json.dumps(jsonbody)
        res = self.request_post(f'{self.host_url}/movie', data=data)
        return res.json()

    def update_movie(self):
        # TODO
        raise NotImplemented

    def delete_movie(self, movie_id: int, delete_files: bool = None, add_exclusion: bool = None):
        """
        Delete the movie with the given ID
        :param movie_id: the id of the movie
        :param delete_files: if true the movie folder and all files will be deleted when the movie is deleted
        :param add_exclusion: if true the movie TMDBID will be added to the import exclusions list when the movie is deleted
        """
        jsonBody = dict()

        if delete_files is None and add_exclusion is None:
            jsonBody = None
        else:
            query_string = "?"
            if delete_files is not None:
                jsonBody['deleteFiles'] = delete_files
            if add_exclusion is not None:
                jsonBody['addExclusion'] = add_exclusion
            data = json.dumps(jsonBody)
        res = self.request_del(f'{self.host_url}/movie/{movie_id}', data=data)
        return res.json()

    # ENDPOINT MOVIE LOOKUP
    def movie_lookup_by_name(self, term: str):
        """
        Searches for new movies on trakt
        :param term: the Movie's name
        """
        query_string = f"?term={term.replace(' ', '%20')}"
        res = self.request_get(f'{self.host_url}/movie/lookup{query_string}')
        return res.json()

    def movie_lookup_by_id(self, tmdb_id: int):
        """

        :param tmdb_id:
        """
        res = self.request_get(f'{self.host_url}/movie/lookup/tmdb?tmdbId={tmdb_id}')
        return res.json()

    def movie_lookup_by_imdb_id(self, imdb_id: str):
        """

        :param imdb_id:
        """
        res = self.request_get(f'{self.host_url}/movie/lookup/imdb?imdbId={imdb_id}')
        return res.json()

    # ENDPOINT QUEUE
    def get_queue(self):
        """
        Gets queue info (downloading/completed, ok/warning)
        """
        res = self.request_get(f'{self.host_url}/queue')
        return res.json()

    def delete_queue_item(self, queue_id: int, blacklist: bool = False):
        """
        Deletes an item from the queue and download client. Optionally blacklist item after deletion.
        :param queue_id: Unique ID of the command
        :param blacklist: Set to 'true' to blacklist after delete
        """
        json_body = dict()
        json_body['id'] = queue_id
        json_body['blacklist'] = blacklist
        data = json.dumps(json_body)
        res = self.request_del(f'{self.host_url}/queue', data=data)
        return res.json()

    # ENDPOINT HISTORY SIZE
    def get_history_size(self, page_size):
        """Gets history (grabs/failures/completed)"""
        res = self.request_get("{}/history?pageSize={}".format(self.host_url, page_size))
        return res.json()

    # ENDPOINT PROFILE
    def get_quality_profiles(self):
        """Gets all quality profiles"""
        res = self.request_get("{}/profile".format(self.host_url))
        return res.json()

    # ENDPOINT RELEASE

    # ENDPOINT RELEASE/PUSH
    def push_release(self, title, download_url, protocol, publish_date):
        """Notifies Radarr of a new release.
            title: release name
            download_url: .torrent file URL
            protocol: usenet / torrent
            publish_date: ISO8601 date string
        """
        json_body = {
            'title': title,
            'download_url': download_url,
            'protocol': protocol,
            'publish_date': publish_date
        }
        data = json.dumps(json_body)
        res = self.request_post(
            "{}/release/push".format(self.host_url), data=data)
        return res.json()

    # ENDPOINT ROOTFOLDER
    def get_root_folder(self):
        """Returns the Root Folder"""
        res = self.request_get("{}/rootfolder".format(self.host_url))
        return res.json()

    # ENDPOINT SYSTEM-STATUS
    def get_system_status(self):
        """Returns the System Status"""
        res = self.request_get("{}/system/status".format(self.host_url))
        return res.json()

    # REQUESTS STUFF
    def request_get(self, url, data=None, params=None):
        # """Wrapper on the requests.get"""
        if data is None:
            data = {}
        headers = {
            'X-Api-Key': self.api_key
        }

        query_string = str()
        if params is not None:
            query_string += '?'
            for key, value in params.items():
                query_string += f'&{key}={value}'
        res = requests.get(url + query_string, headers=headers, json=data)
        return res

    def request_post(self, url, data):
        # """Wrapper on the requests.post"""
        headers = {
            'X-Api-Key': self.api_key
        }
        data2 = json.loads(data)
        res = requests.post(url, headers=headers, json=data2)
        return res

    def request_put(self, url, data):
        # """Wrapper on the requests.put"""
        headers = {
            'X-Api-Key': self.api_key
        }
        res = requests.put(url, headers=headers, json=data)
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
            self.radarr = parent

        def refresh_movie(self, movie_id: int = None):
            """
            Refresh movie information from TMDb and rescan disk
            :movie_id: if not set all movies will be refreshed and scanned
            """
            return self.radarr.run_command(name='RefreshMovie', movieId=movie_id)

        def rescan_movie(self, movie_id: int = None):
            """Rescan disk for movies
            :movie_id: if not set all movies will be scanned
            """
            return self.radarr.run_command(name='RescanMovie', movieId=movie_id)

        def movie_search(self, movie_ids: list = None):
            """
            Search for one or more movies
            :type movie_ids: list
            :parameter movie_ids: one or more episodeIds in an array Not 100% sure on this run_command variable
            """
            return self.radarr.run_command(name='MoviesSearch', movieIds=movie_ids)

        def downloaded_movies_scan(self, path: str = None, download_client_id: str = None, import_mode: str = None):
            """Instruct Radarr to scan the DroneFactoryFolder or a folder defined by the path variable.
            Each file and folder in the DroneFactoryFolder is interpreted as separate download.

            But a folder specified by the path variable is assumed to be a single download (job) and the folder name should be
            the release name.

            The downloadClientId can be used to support this API endpoint in conjunction with Completed Download Handling,
            so Radarr knows that a particular download has already been imported.
            :param import_mode: Move or Copy (Copy = Copy
            Or Hardlink depending on Radarr configuration) Can be used to override the default Copy for torrents with external
            preprocessing/transcoding/unrar.
            :param path:
            :param download_client_id: (nzoid for sabnzbd, special 'drone'
            attribute value for nzbget, uppercase infohash for torrents),
            """
            return self.radarr.run_command(name='DownloadedMoviesScan', path=path, downloadClientId=download_client_id,
                                           importMode=import_mode)

        def rss_sync(self):
            """Instruct Radarr to perform an RSS sync with all enabled indexers"""
            return self.radarr.run_command(name='RssSync')

        def rename_files(self, files: list = None):
            """Instruct Radarr to rename the list of files provided.
            :type files: list
            :param files: List of File IDs to rename
            """
            return self.radarr.run_command(name='RenameFiles', files=files)

        def rename_movie(self, movie_ids: list):
            """Instruct Radarr to rename all files in the provided movies.
            :type movie_ids: list
            :param movie_ids: List of Movie IDs to rename
            """
            return self.radarr.run_command(name='RenameMovie', movieIds=movie_ids)

        def cut_off_unmet_movies_search(self, filter_key: str, filter_value: str):
            """Instructs Radarr to search all cutoff unmet movies (Take care, since it could go over your indexers
            api limits!)
            :param filter_key:  Key by which to further filter cutoff unmet movies. (Possible values:
            monitored (recommended), all, status)
            :param filter_value: Value by which to further filter cutoff unmet
            movies. This must correspond to the filterKey. (Possible values with respect to the ones for the
            filterKey above: (true (recommended), false), (all), (available, released, inCinemas, announced)
            """
            return self.radarr.run_command(name='CutOffUnmetMoviesSearch', filterKey=filter_key,
                                           filterValue=filter_value)

        def net_import_sync(self):
            """Instructs Radarr to search all lists for movies not yet added to Radarr."""
            return self.radarr.run_command(name='NetImportSync')

        def missing_movies_search(self, filter_key: str, filter_value: str):
            """Instructs Radarr to search all missing movies. This functionality is similar to what CouchPotato does
            and runs a backlog search for all your missing movies. For example You can use this api with curl and
            crontab to instruct Radarr to run a backlog search on 1 AM everyday.
            :type filter_key: str
            :type filter_value: str
            :param filter_value: Key by which to
            further filter missing movies. (Possible values: monitored (recommended), all, status)
            :param filter_key:
            Key by which to further filter missing movies. (Possible values: monitored (recommended), all, status)
            """
            return self.radarr.run_command(self, filterKey=filter_key, filterValue=filter_value)
