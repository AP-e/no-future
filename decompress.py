""" decompress """
import pathlib
import os
import shutil
import subprocess
import itertools

# archive extension: command line arguments
def p7zip_decompress(fpath, destination=''):
    """Decompress specified file using p7zip."""
    command_args = ['7z', 'x', fpath, '-y']
    if destination:
        command_args.append(f'-o{destination}')
    subprocess.run(command_args, check=True)

def decompress(source, output, exts=['zip', 'rar']):
    """Decompress specified archives using command-line utilities."""
    archives = sorted(itertools.chain.from_iterable(
        source.glob(f'*.{ext}') for ext in exts))
    
    failed, removed = [], []
    for fpath in archives:
        try:
            p7zip_decompress(fpath, output)
        except subprocess.CalledProcessError:
            failed.append(fpath)
        else:
            os.remove(fpath)
            removed.append(fpath)
    
    print(f'Decompressed and removed {len(removed)} archives')
    if failed:
        print('Could not decompress:\n\t' + 
              '\n\t'.join((fpath.name for fpath in failed)))

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
