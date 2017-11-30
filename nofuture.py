""" no-future """
import glob
import os
import shutil
import subprocess

# archive extension: command line arguments
EXT_ARGS = {'zip': ['unzip', '-n'],
            'rar': ['unrar', '-o-', 'x']}

def decompress(archives):
    """Uncompress archives using command-line utilities."""
    failed = []
    removed = []
    for ext, fpaths in archives.items():
        for fpath in fpaths:
            args = EXT_ARGS[ext] + [fpath]
            try:
                subprocess.run(args, check=True)
            except subprocess.CalledProcessError:
                failed.append(fpath)
            else:
                os.remove(fpath)
                removed.append(fpath)
    return removed, failed

if __name__ == '__main__':
    archives = {ext: glob.glob('*.'+ext) for ext in EXT_ARGS.keys()}
    removed, failed = decompress(archives)
