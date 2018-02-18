""" release """
import os
import discogs_client
import re
import ratelimit

DISCOGS_USER_AGENT = 'nofuture/0.1'
DISCOGS_USER_TOKEN = None

# Rate-limit Discogs API calls
discogs_client.Client._get = ratelimit.rate_limited(60, 65)(discogs_client.Client._get)

def make_client():
    """Initialise single-user authorised discogs client."""
    user_token = os.environ.get('DISCOGS_USER_TOKEN')
    if user_token is None:
        user_token = DISCOGS_USER_TOKEN
    if user_token is None:
            raise ValueError('You must specify a valid discogs user token')
    return discogs_client.Client(DISCOGS_USER_AGENT, user_token=user_token)

class Release:
    """A wrapper around Discogs release data."""
    client = make_client()

    def __init__(self, release_id):
        self._data = self.get_release_data(release_id)

    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self):
        return ['id', 'title', 'year', 'label', 'catno', 'artist']

    @classmethod
    def from_search(cls, search_term):
        """Initialise from first discogs release matching search term."""
        releases = cls.client.search(search_term, type='release')
        try:
            release = releases[0] # assume first result is best match
        except IndexError:
            raise ValueError(f"Nothing found for {search_term}")
        return cls(release.id)

    def get_release_data(self, release_id):
        """Retrieve the dict of data from a Discogs release."""
        discogs_release = self.client.release(release_id)
        discogs_release.refresh() # request all data
        return discogs_release.data

    @property
    def id(self):
        """Discogs release id."""
        return self._data['id']

    @property
    def title(self):
        """Release title."""
        return self._data['title']

    @property
    def year(self):
        """Release year."""
        return self._data['year']

    @property
    def label(self):
        """Name of the release's primary record label."""
        return _strip_suffix(self._data['labels'][0]['name'])

    @property
    def catno(self):
        """Catalog number of release on primary record label."""
        return self._data['labels'][0]['catno']

    @property
    def artist(self):
        """Release artist, or artists joined by commas."""
        artists = [_strip_suffix(artist['name']) for artist in self._data['artists']]
        return ', '.join(artists)

def _strip_suffix(field):
    """Strip release field of any Discogs numerical suffix."""
    suffix = re.compile(r' \(([2-9]|[1-9][0-9]+)\)$')
    try: # 'Klaus (25) -> 'Klaus'
        return field[:suffix.search(field).start()]
    except AttributeError: # no suffix
        return field
