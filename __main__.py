import pathlib
import decompress

ARCHIVES_DIR='archives' # music archives found here
STAGING_DIR='staging'# to decompress into and work from
OUTPUT_DIR='music' # formatted directories moved here

archives_dir, staging_dir, output_dir = (pathlib.Path(path)
    for path in (ARCHIVES_DIR, STAGING_DIR, OUTPUT_DIR))
# Ensure output directories exist
for path in (staging_dir, output_dir):
    try:
        path.mkdir()
    except(FileExistsError):
        pass

decompress.decompress(archives_dir, staging_dir)

