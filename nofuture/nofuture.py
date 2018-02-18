import os
import pathlib
import re
import shutil
from . import release

def format_release_path(artist=None, title=None, label=None, year=None, catno=None,
                            **extra_fields):
    """Construct path object with format 'label/[catno] artist - title (year)'."""
    artist = sanitise_path_component(artist)
    title = sanitise_path_component(title)
    label = sanitise_path_component(label)
    release_dir = f'[{catno}] {artist} - {title} ({year})'
    return pathlib.Path(label).joinpath(release_dir)

def sanitise_path_component(string):
    """Return string sanitised for use in portable file paths.
    
    Removes:
        < > : " \ | ?  *
    Changes:
        `Untitled / Footloose` -> Untitled _ Footloose`.
        `Untitled ` -> `Untitled`
        `Untitled.` -> `Untitled`
    """
    old_string = string
    for bad_char in '<>:"\|?*':
        string = string.replace(bad_char, '')
    string = string.replace('/', '_')
    string = string.rstrip(' .')
    if not string:
        raise ValueError(f"'{old_string}' cannot be coerced to a valid filepath component")
    return string

def get_release_information(staging_dir):
    releases = {}
    failed = []
    for i, dirname in enumerate(os.listdir(staging_dir)):
        dirname = pathlib.Path(dirname)
        full_title, tags = split_release_dir(dirname)
        try:
            releases[dirname] = release.Release.from_search(full_title)
        except IndexError:
            failed.append(dirname)
    return releases, failed

def format_release_directories(releases, staging_dir, output_dir):
    for dirname, release_ in sorted(releases.items()):
        input_path = staging_dir.joinpath(dirname)
        release_dir = format_release_path(**release_)
        output_path = output_dir.joinpath(release_dir)
        moved = shutil.move(str(input_path), str(output_path))

def touch_directories(staging_dir, output_dir):
    """Create specified staging and output directories, if necessary.""" 
    for path in (staging_dir, output_dir):
        try:
            path.mkdir()
        except(FileExistsError):
            pass

def split_release_dir(release_dir):
    """Split release directory into full title and list of debracketed tags."""
    release_dir = str(release_dir)
    p = re.compile(r'\[\w+\]')
    m = p.search(release_dir)
    if m is None:
        full_title, tags = release_dir, []
    else:
        full_title = release_dir[:m.start()].strip()
        tags = [tag.strip('[]') for tag in p.findall(release_dir, m.start())]
    return full_title, tags
