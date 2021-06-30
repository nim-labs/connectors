#!/bin/env python

# Hook called when an archive is successfully restored
#
#   archiveName: name of the archive that was entered when
#            formatting the archive -- String
def archiveRestored( archiveName ):
   pass


# Hook called when an archive operation completes successfully
#
#   archiveName: name of the archive that was entered when
#            formatting the archive -- String
def archiveComplete( archiveName ):
   pass


# Hook called when an archive segment completes
#
#   segmentPath: path to the file segment that just completed 
#            (empty string for non-file archives) -- String
#   archiveName: name of the archive that was entered when 
#            formatting the archive -- String
#   archivePath: path to the archive that was entered when 
#            formatting the archive -- String
#   status: zero if successful, non-zero if there was an error -- Integer
#   statusMessage: description of the error 
#            (empty string if status is 0) -- String
#   archiveComplete: True if all segments of the archive are complete -- Boolean
def archiveSegmentComplete( segmentPath, archiveName, archivePath, status, 
                            statusMessage, archiveComplete ):
   pass


# Hook called when archive selection information is updated.
#
# segmentInfo: map of segment id to file path (or device type in the case
#        of non-file-based archives) -- Dictionary{ Integer, String }
# numFrames: number of frames -- Long
# numClips: number of clips -- Integer
# dataSize: size of data (in MB) -- Float
# metadataSize: size of metadata (in MB) -- Float 
#
def archiveSelectionUpdated( segmentInfo, numFrames, numClips, 
                             dataSize, metadataSize ):
   pass 
