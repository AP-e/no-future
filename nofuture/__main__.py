import os
import pathlib
from . import decompress
from . import nofuture
from .config import ARCHIVES_DIR, STAGING_DIR, OUTPUT_DIR, ARCHIVE_FORMATS

def main():
    # Set up input, working and output directories
    archives_dir, staging_dir, output_dir = (pathlib.Path(path)
        for path in (ARCHIVES_DIR, STAGING_DIR, OUTPUT_DIR))
    nofuture.touch_directories(staging_dir, output_dir)
    
    # Decompress archives to release directories
    decompressed, non_decompressed = decompress.decompress(
        archives_dir, staging_dir, ARCHIVE_FORMATS)
    
    # Match release directories to Discogs releases
    releases, failed = nofuture.get_releases_in_staging(staging_dir)
    
    # Rename release directories accordingly
    formatted = nofuture.format_release_directories(releases, staging_dir, output_dir)
    
    # Clean up decompressed archives
    for fpath in decompressed:
        os.remove(fpath)

main()
