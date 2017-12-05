""" no-future """
import glob
import os
import shutil
import subprocess

SOURCE='nodata' # dir containing archives
DEST='music' # dir to decompress into

# archive extension: command line arguments
EXT_ARGS = {'zip': lambda fpath: ['unzip', '-n', fpath, '-d', DEST],
            'rar': lambda fpath: ['unrar', '-o-', 'x', fpath, DEST]}

def decompress(archives):
    """Uncompress archives using command-line utilities."""
    failed = []
    removed = []
    for ext, fpaths in archives.items():
        for fpath in fpaths:
            args = EXT_ARGS[ext](fpath)
            try:
                subprocess.run(args, check=True)
            except subprocess.CalledProcessError:
                failed.append(fpath)
            else:
                os.remove(fpath)
                removed.append(fpath)
    
    return removed, failed

if __name__ == '__main__':
    archives = {ext: glob.glob(os.path.join(SOURCE, '*.'+ext))
                for ext in EXT_ARGS.keys()}
    removed, failed = decompress(archives)
    print(f'Decompressed and removed {len(removed)} archives')
    if failed:
        print('Could not decompress:\n\t' + '\n\t'.join(failed))
