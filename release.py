""" get_info """
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
        self.get_release_data(release_id)

    @classmethod
    def from_dirname(cls, dirname):
        """Initialise release matching specified directory name."""
        full_title, tags = _split_release_dir(dirname)
        releases = cls.client.search(full_title, type='release')
        release_id = releases[0].id # assume first result is best match
        return cls(release_id)

    def get_release_data(self, release_id):
        """Retrieve the dict of data from a Discogs release."""
        discogs_release = self.client.release(release_id)
        discogs_release.refresh() # request all data
        self._data = discogs_release.data

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

def _split_release_dir(release_dir):
    """Split release directory into full title and list of debracketed tags."""
    p = re.compile(r'\[\w+\]')
    m = p.search(release_dir)
    if m is None:
        full_title, tags = release_dir, []
    else:
        full_title = release_dir[:m.start()].strip()
        tags = [tag.strip('[]') for tag in p.findall(release_dir, m.start())]
    return full_title, tags

def _strip_suffix(field):
    """Strip release field of any Discogs numerical suffix."""
    suffix = re.compile(r' \(([2-9]|[1-9][0-9]+)\)$')
    try: # 'Klaus (25) -> 'Klaus'
        return field[:suffix.search(field).start()]
    except AttributeError: # no suffix
        return field
