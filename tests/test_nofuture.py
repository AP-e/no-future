import pytest
from pathlib import Path
import os
import json
import patoolib
import unittest.mock
import nofuture.decompress, nofuture.release, nofuture.nofuture
from nofuture.config import ARCHIVES_DIR, STAGING_DIR, ARCHIVE_FORMATS

# Discogs release id of testing release
RELEASE_ID = 6666365

# Expected formatting of release details
FORMATTED_RELEASE = {'id': 6666365,
                     'title': "X / Don't Get Me Started",
                     'artist': "Hodge, Acre",
                     'label': "Wisdom Teeth",
                     'catno': "WSDM002",
                     'year': 2015}

# Archive information
ARCHIVE = {'dirname': "Hodge & Acre - X _ Don't Get Me Started [2015] [EP]",
           'archivename': "HAXDGMS", # as per NoFuture
           'files': ("01 Hodge - X.mp3", "02 Acre - Don't Get Me Started.mp3"),
           'full_title': "Hodge & Acre - X _ Don't Get Me Started",
           'tags': ['2015', 'EP']}

@pytest.fixture
def archives_dir(tmpdir):
    return tmpdir.mkdir(ARCHIVES_DIR)

@pytest.fixture
def staging_dir(tmpdir):
    return tmpdir.mkdir(STAGING_DIR)

@pytest.fixture
def decompressed_dir(tmpdir):
    """Return path of artificial release directory (i.e. contents of downloaded archive)."""
    dir_ = tmpdir.mkdir(ARCHIVE['dirname'])
    for fname in ARCHIVE['files']:
        p = dir_.join(fname).write('')
    return dir_

@pytest.fixture
def staging(staging_dir, decompressed_dir):
    decompressed_dir.move(staging_dir.join(decompressed_dir.basename))
    return staging_dir

@pytest.fixture()
def archive(archives_dir, decompressed_dir, request):
    """Return path of archive created from release directory."""
    archive = archives_dir.join(ARCHIVE['archivename']).new(ext=request.param)
    patoolib.create_archive(str(archive), [str(decompressed_dir)])
    return archive

@pytest.fixture()
def corrupted_archive(archive):
    """Return path of a corrupted archive."""
    with open(archive, 'rb') as o:
        contents = o.read()
    with open(archive, 'wb') as o:
        o.write(contents[::2])
    return archive

@pytest.fixture(scope='module')
def release_data():
    """Return the locally stored version of the Discogs release data."""
    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '.'.join([str(RELEASE_ID), 'json']))
    return json.load(open(fpath, 'r'))

@pytest.fixture()
def release(monkeypatch, release_data):
    """Return a Release object initialised using local data."""
    def get_release_data(self, release_id):
        """Replacement for `nofuture.release.Release.get_release_data` to bypass discogs client."""
        if release_id != release_data['id']:
            raise ValueError
        return release_data
    monkeypatch.setattr('nofuture.release.Release.get_release_data',
                        get_release_data)
    return nofuture.release.Release(RELEASE_ID)

@pytest.mark.parametrize('archive', ARCHIVE_FORMATS, indirect=True)
def test_decompression(archive, archives_dir, staging_dir):
    """Can all formats be decompressed from archives to staging?"""
    decompressed, failed = nofuture.decompress.decompress(
        Path(archives_dir), Path(staging_dir), ARCHIVE_FORMATS)
    *_, (fpath, *_) = os.walk(staging_dir) # get deepest dir (synthetic rars include full path)
    assert Path(fpath).name == ARCHIVE['dirname']

@pytest.mark.parametrize('archive', ARCHIVE_FORMATS, indirect=True)
def test_failed_decompression(corrupted_archive, archives_dir, staging_dir):
    """Is the failed decompression of corrupt archives caught and reported?"""
    decompressed, failed = nofuture.decompress.decompress(
        Path(archives_dir), Path(staging_dir), ARCHIVE_FORMATS)
    failed, = failed
    assert failed == corrupted_archive and not decompressed

def test_discogs_client_works(release):
    """Can the Discogs client retrieve real release information?"""
    client = nofuture.release.make_client()
    real_release = client.release(RELEASE_ID)
    assert real_release.title == release.title

def test_Release_attributes_are_correct(release):
    """Does the Release object present release details as expected?"""
    for field in ['artist', 'catno', 'id', 'label', 'title', 'year']:
        assert getattr(release, field) == FORMATTED_RELEASE[field]

def test_release_created_from_search_term(release):
    """Can Release be initialised using a search term?"""
    real_release = nofuture.release.Release.from_search(ARCHIVE['full_title'])
    assert real_release.id == release.id

def test_release_creation_from_staging(monkeypatch, staging, release):
    """Is a release created from a directory in the staging directory?"""
    # Bypass discogs API call
    monkeypatch.setattr('nofuture.nofuture.release.Release.client.search',
        lambda *args, **kwargs: [unittest.mock.MagicMock(id=RELEASE_ID,
            name='mock discogs_client.models.models.Release')])
    releases, failed = nofuture.nofuture.get_releases_in_staging(staging)
    assert releases and not failed
