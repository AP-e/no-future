""" get_info """
import os
import discogs_client
import re
import ratelimit

DISCOGS_USER_AGENT = 'nofuture/0.1'
DISCOGS_USER_TOKEN = None

# Rate-limit Discogs API calls
discogs_client.Client._get = ratelimit.rate_limited(1)(discogs_client.Client._get)

def make_client():
    """Initialise single-user authorised discogs client."""
    user_token = os.environ.get('DISCOGS_USER_TOKEN')
    if user_token is None:
        user_token = DISCOGS_USER_TOKEN
    if user_token is None:
            raise ValueError('You must specify a valid discogs user token')
    return discogs_client.Client(DISCOGS_USER_AGENT, user_token=user_token)

def find_release(client, dirname):
    """Return Discogs release matching directory name."""
    full_title, tags = split_dirname(dirname)
    releases = client.search(full_title, type='release')
    try:
        return releases[0].id # assume first result is best match
    except IndexError:
        return None

def split_dirname(dirname):
    """Split dirname into full title string and list of debracketed tags."""
    p = re.compile(r'\[\w+\]')
    m = p.search(dirname)
    if m is None:
        full_title, tags = dirname, []
    else:
        full_title = dirname[:m.start()].strip()
        tags = [tag.strip('[]') for tag in p.findall(dirname, m.start())]
    return full_title, tags
