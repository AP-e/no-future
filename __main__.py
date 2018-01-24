import os
import pathlib
import shutil
import decompress
import release

ARCHIVES_DIR='archives' # music archives found here
STAGING_DIR='staging'# to decompress into and work from
OUTPUT_DIR='music' # formatted directories moved here

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

def format_release_path(artist=None, title=None, label=None, year=None, catno=None,
                            **extra_fields):
    """Construct path object with format 'label/[catno] artist - title (year)'."""
    artist = sanitise_path_component(artist)
    title = sanitise_path_component(title)
    label = sanitise_path_component(label)
    release_dir = f'[{catno}] {artist} - {title} ({year})'
    return pathlib.Path(label).joinpath(release_dir)

def get_release_information(archives_dir, staging_dir):
    releases = {}
    failed = []
    for i, dirname in enumerate(os.listdir(staging_dir)):
        dirname = pathlib.Path(dirname)
        try:
            releases[dirname] = release.Release.from_dirname(dirname)
        except IndexError:
            failed.append(dirname)
    return releases, failed

def format_release_directories(releases, staging_dir, output_dir):
    for dirname, release_ in sorted(releases.items()):
        input_path = staging_dir.joinpath(dirname)
        release_dir = format_release_path(artist=release_.artist, title=release_.title, label=release_.label, year=release_.year, catno=release_.catno)
        output_path = output_dir.joinpath(release_dir)
        moved = shutil.move(str(input_path), str(output_path))

archives_dir, staging_dir, output_dir = (pathlib.Path(path)
    for path in (ARCHIVES_DIR, STAGING_DIR, OUTPUT_DIR))
# Ensure output directories exist
for path in (staging_dir, output_dir):
    try:
        path.mkdir()
    except(FileExistsError):
        pass

decompress.decompress(archives_dir, staging_dir)
releases, failed = get_release_information(archives_dir, staging_dir)
format_release_directories(releases, staging_dir, output_dir)
