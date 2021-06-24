#!/bin/env python

# Hook called when an archive is successfully restored
#
#   archive_name: name of the archive that was entered when
#            formatting the archive -- String
def archive_restored(archive_name):
    pass


# Hook called when an archive operation completes successfully
#
#   archive_name: name of the archive that was entered when
#            formatting the archive -- String
def archive_complete(archive_name):
    pass


# Hook called when an archive segment completes
#
#   segment_path: path to the file segment that just completed
#            (empty string for non-file archives) -- String
#   archive_name: name of the archive that was entered when
#                 formatting the archive -- String
#   archive_path: path to the archive that was entered when
#                 formatting the archive -- String
#   status: zero if successful, non-zero if there was an error -- Integer
#   status_message: description of the error
#                   (empty string if status is 0) -- String
#   archive_complete: True if all segments of the archive are complete -- Boolean
def archive_segment_complete(
    segment_path, archive_name, archive_path, status, status_message, archive_complete
):
    pass


# Hook called when archive selection information is updated.
#
# segment_info: map of segment id to file path (or device type in the case
#               of non-file-based archives) -- Dictionary{ Integer, String }
# num_frames: number of frames -- Long
# num_clips: number of clips -- Integer
# data_size: size of data (in MB) -- Float
# metadata_size: size of metadata (in MB) -- Float
#
def archive_selection_updated(
    segment_info, num_frames, num_clips, data_size, metadata_size
):
    pass