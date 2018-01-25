""" decompress """
import pathlib
import itertools
import patoolib

def decompress(archives_dir, staging_dir, exts=['zip', 'rar']):
    """Decompress specified archives using command-line utilities."""
    archives = sorted(itertools.chain.from_iterable(
        archives_dir.glob(f'*.{ext}') for ext in exts))
    
    decompressed, failed = [], []
    for fpath in archives:
        print(fpath)
        try:
            patoolib.extract_archive(str(fpath), outdir=str(staging_dir))
        except patoolib.util.PatoolError:
            failed.append(fpath)
        else:
            decompressed.append(fpath)
    return decompressed, failed
