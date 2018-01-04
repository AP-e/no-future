""" get_info """
import os
import discogs_client
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
