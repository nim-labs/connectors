#!/bin/env python
#******************************************************************************
#
# Filename: exportHook.py
#
# Copyright (c) 2014 Autodesk Inc.
# All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


from PySide.QtGui import *
from PySide.QtCore import *

import os,sys,re

nim_app = 'Flame'
os.environ['NIM_APP'] = str(nim_app)

# Relative path to append for NIM Scripts
nimFlameScriptPath = os.path.dirname(os.path.realpath(__file__))
nimFlameScriptPath = nimFlameScriptPath.replace('\\','/')
nimScriptPath = re.sub(r"\/plugins/Flame/python$", "", nimFlameScriptPath)
print "NIM Script Path: %s" % nimScriptPath

# If relocating these scripts uncomment the line below and enter the fixed path
# to the NIM Connector Root directory
#
# nimScriptPath = [NIM_CONNECTOR_ROOT]
#

sys.path.append(nimScriptPath)

import nimFlameExport



# Hooks in this files are called in the following order:
#
# preCustomExport ( optional depending on getCustomExportProfiles )
#  preExport
#   preExportSequence
#    preExportAsset
#    postExportAsset  ( could be done in backburner depending of useBackburnerPostExportAsset )
#    ...
#   postExportSequence
#   ...
#  postExport
# postCustomExport ( optional depending on getCustomExportProfiles  )

# Hook called before a custom export begins. This can be used to fill
# information that would have normally been extracted from the export window.
#
# info [Dictionary] [Modifiable]
#    Information about the export,
#
#    Keys:
#
#    destinationHost: [String] [Modifiable]
#       Host name where the exported files will be written to.
#       Defaults to localhost.
#
#    destinationPath: [String] [Modifiable]
#       Export path root.
#       Defaults to /tmp
#
#    presetPath: [String] [Modifiable]
#       Path to the preset used for the export.
#       Most be defined by this method.
#
#    useTopVideoTrack: [Boolean] [Modifiable]
#       Use only the top video track and ignore the other ones.
#       (False if not defined)
#
#    exportBetweenMarks: [Boolean] [Modifiable]
#       Export between the In  and Out marks, excluding the marked frames.
#       If there is no In, export from start of sequence to Out;
#       if there is no Out, export from the In to the end of the sequence.
#       (False if not defined)
#
#    isBackground: [Boolean] [Modifiable]
#       Perform the export in background.
#       (True if not defined)
#
#    abort: [Boolean] [Modifiable]
#       Hook can set this to True if the custom export process should be
#       aborted.
#
#    abortMessage: [String] [Modifiable]
#       Error message to be displayed to the user when the export process has
#       been aborted
#
# userData [Dictionary] [Modifiable]
#   Dictionary that could have been populated by previous export hooks and that
#   will be carried over into the subsequent export hooks.
#   This can be used by the hook to pass black box data around.
#
def preCustomExport( info, userData ):
   '''
   print "preCustomExport - start"
   print info
   print userData
   print "preCustomExport - end"
   '''
   pass


# Hook called after a custom export ends.
#
# info [Dictionary] [Modifiable]
#    Information about the export,
#
#    Keys:
#
#    destinationHost: [String]
#       Host name where the exported files were written to.
#
#    destinationPath: [String]
#       Export path root.
#
#    presetPath: [String]
#       Path to the preset used for the export.
#
# userData [Dictionary] [Modifiable]
#   Dictionary that could have been populated by previous export hooks and that
#   will be carried over into the subsequent export hooks.
#   This can be used by the hook to pass black box data around.
#
def postCustomExport( info, userData ):
   '''
   print "postCustomExport - start"
   print info
   print userData
   print "postCustomExport - end"
   '''
   pass


# Hook called before an export begins.
#
# info [Dictionary] [Modifiable]
#    Information about the export,
#
#    Keys:
#
#    destinationHost: [String]
#       Host name where the exported files will be written to.
#
#    destinationPath: [String]
#       Export path root.
#
#    presetPath: [String]
#       Path to the preset used for the export.
#
#    abort: [Boolean] [Modifiable]
#       Hook can set this to True if the export process should be aborted.
#
#    abortMessage: [String] [Modifiable]
#       Error message to be displayed to the user when the export process has
#       been aborted
#
# userData [Dictionary] [Modifiable]
#   Dictionary that could have been populated by previous export hooks and that
#   will be carried over into the subsequent export hooks.
#   This can be used by the hook to pass black box data around.
#
def preExport( info, userData ):
   '''
   print "preExport - start"
   print info
   print userData
   print "preExport - end"
   '''
   pass


# Hook called after an export ends.
#
# info [Dictionary] [Modifiable]
#    Information about the export,
#
#    Keys:
#
#    destinationHost: [String]
#       Host name where the exported files were written to.
#
#    destinationPath: [String]
#       Export path root.
#
#    presetPath: [String]
#       Path to the preset used for the export.
#
# userData [Dictionary] [Modifiable]
#   Dictionary that could have been populated by previous export hooks.
#   This can be used by the hook to pass black box data around.
#
def postExport( info, userData ):
   print "postExport - start"
   print info
   print userData
   print "postExport - end"
   pass


# Hook called before a sequence export begins.
#
# info [Dictionary] [Modifiable]
#    Information about the export,
#
#    Keys:
#
#    destinationHost: [String]
#       Host name where the exported files will be written to.
#
#    destinationPath: [String]
#       Export path root.
#
#    sequenceName: [String]
#       Name of the exported sequence.
#
#    shotNames: [String]
#       Tuple of all shot names in the exported sequence. Multiple segments
#       could have the same shot name.
#
#    thumbnailFrameNb: [Int]
#       Frame index of the active thumnbnail
#
#    abort: [Boolean] [Modifiable]
#       Hook can set this to True if the export sequence process should
#       be aborted. If other sequences are exported in the same export session
#       they will still be exported even if this export sequence is aborted.
#
#    abortMessage: [String] [Modifiable]
#       Error message to be displayed to the user when the export sequence
#       process has been aborted
#
# userData [Dictionary] [Modifiable]
#   Dictionary that could have been populated by previous export hooks and that
#   will be carried over into the subsequent export hooks.
#   This can be used by the hook to pass black box data around.
#
def preExportSequence( info, userData ):
   print "preExportSequence - start *****************************************************************"
   print info
   print userData

   msgBox = QMessageBox()
   msgBox.setTextFormat(Qt.RichText)
   result = msgBox.information(None, "Export Sequence to NIM?", "Export Sequence to NIM?", QMessageBox.Ok | QMessageBox.Cancel)
   if result == QMessageBox.Ok:
      print "NIM - Exporting to NIM"
      userData['nim_export_sequence'] = True

      exportDlg = nimFlameExport.NimExportDialog()
      exportDlg.show()
      if exportDlg.exec_() :
         print "NIM - showID: %s" % exportDlg.nim_showID
         userData['nim_showID'] = exportDlg.nim_showID
   else:
      print "NIM - Skipping Export to NIM"
      userData['nim_export_sequence'] = False

   


   print "preExportSequence - end *****************************************************************"
   pass


# Hook called after a sequence export ends.
#
# info [Dictionary] [Modifiable]
#    Information about the export,
#
#    Keys:
#
#    destinationHost: [String]
#       Host name where the exported files were written to.
#
#    destinationPath: [String]
#       Export path root.
#
#    sequenceName: [String]
#       Name of the exported sequence.
#
#    shotNames: [String]
#       Tuple of all shot names in the exported sequence. Multiple segment
#       could have the same shot name.
#
#    thumbnailFrameNb: [Int]
#       Frame index of the active thumnbnail
#
# userData [Dictionary] [Modifiable]
#   Dictionary that could have been populated by previous export hooks and that
#   will be carried over into the subsequent export hooks.
#   This can be used by the hook to pass black box data around.
#
def postExportSequence( info, userData ):
   print "postExportSequence - start *****************************************************************"
   print info
   print userData

   userData['nim_export_sequence'] = False

   print "postExportSequence - end *****************************************************************"
   pass


# Hook called before an asset export begins.
#
# info [Dictionary] [Modifiable]
#    Information about the export,
#
#    Keys:
#
#    destinationHost: [String]
#       Host name where the exported files will be written to.
#
#    destinationPath: [String]
#       Export path root.
#
#    namePattern: [String]
#       List of optional naming tokens.
#
#    resolvedPath: [String] [Modifiable]
#       File pattern (relative to destinationPath) that will be exported
#       with all the tokens resolved.
#
#    assetName: [String]
#       Name of the exported asset.
#
#    sequenceName: [String]
#       Name of the sequence the asset is part of.
#
#    shotName: [String]
#       Name of the shot the asset is part of.
#
#    tapeName: [String]
#       Name of the tape the asset is part of.
#
#    assetType: [String]
#       Type of exported asset.
#       ( 'video', 'audio', 'batch', 'openClip', 'batchOpenClip' )
#
#    width: [Long]
#       Frame width of the exported asset.
#
#    height: [Long]
#       Frame height of the exported asset.
#
#    aspectRatio: [Double]
#       Frame aspect ratio of the exported asset.
#
#    depth: [String]
#       Frame depth of the exported asset.
#       ( '8-bits', '10-bits', '12-bits', '16 fp' )
#
#    scanFormat: [String]
#       Scan format of the exported asset.
#       ( 'FIELD_1', 'FIELD_2', 'PROGRESSIVE' )
#
#    fps: [Double]
#       Frame rate of exported asset.
#
#    sequenceFps: [Double]
#       Frame rate of the sequence the asset is part of.
#
#    sourceIn: [Integer]
#       The source in point as a frame, using the asset frame rate (fps key).
#
#    sourceOut: [Integer]
#       The source out point as a frame, using the asset frame rate (fps key).
#
#    recordIn: [Integer]
#       The record in point as a frame, using the sequence frame rate
#       (sequenceFps key).
#
#    recordOut: [Integer]
#       The record out point as a frame, using the sequence frame rate
#       (sequenceFps key).
#
#    handleIn: [Integer]
#       Head as a frame, using the asset frame rate (fps key).
#
#    handleOut: [Integer]
#       Tail as a frame, using the asset frame rate (fps key).
#
#    track: [String]
#       ID of the sequence's track that contains the asset.
#
#    trackName: [String]
#       Name of the sequence's track that contains the asset.
#
#    segmentIndex: [Integer]
#       Asset index (1 based) in the track.
#
#    versionName: [String]
#       Current version name of export (Empty if unversioned).
#
#    versionNumber: [Integer]
#       Current version number of export (0 if unversioned).
#
# userData [Dictionary] [Modifiable]
#   Dictionary that could have been populated by previous export hooks and that
#   will be carried over into the subsequent export hooks.
#   This can be used by the hook to pass black box data around.
#
def preExportAsset( info, userData ):
   print "preExportAsset - start 2 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
   print info
   print userData

   print "destinationPath: %s" % info['destinationPath']
   print "resolvedPath: %s" % info['resolvedPath']
   print "shotName: %s" % info['shotName']

   print "preExportAsset - end 2 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
   pass


# Hook called after an asset export ends.
#
# info [Dictionary] [Modifiable]
#    Information about the export,
#
#    Keys:
#
#    destinationHost: [String]
#       Host name where the exported files were written to.
#
#    destinationPath: [String]
#       Export path root.
#
#    namePattern: [String]
#       List of optional naming tokens.
#
#    resolvedPath: [String]
#       File pattern (relative to destinationPath) that will be exported
#       with all the tokens resolved.
#
#    assetName: [String]
#       Name of the exported asset.
#
#    sequenceName: [String]
#       Name of the sequence the asset is part of.
#
#    shotName: [String]
#       Name of the shot the asset is part of.
#
#    assetType: [String]
#       Type of exported asset.
#       ( 'video', 'audio', 'batch', 'openClip', 'batchOpenClip' )
#
#    isBackground: [Boolean]
#       True if the export of the asset happened in the background.
#
#    backburnerManager: [String]
#       Backburner Manager handling the background job.
#       Empty if job is done in foreground.
#
#    backgroundJobId: [String]
#       Id of the background job given by the backburner Manager upon
#       submission. Empty if job is done in foreground.
#
#    width: [Long]
#       Frame width of the exported asset.
#
#    height: [Long]
#       Frame height of the exported asset.
#
#    aspectRatio: [Double]
#       Frame aspect ratio of the exported asset.
#
#    depth: [String]
#       Frame depth of the exported asset.
#       ( '8-bits', '10-bits', '12-bits', '16 fp' )
#
#    scanFormat: [String]
#       Scan format of the exported asset.
#       ( 'FIELD_1', 'FIELD_2', 'PROGRESSIVE' )
#
#    fps: [Double]
#       Frame rate of exported asset.
#
#    sequenceFps: [Double]
#       Frame rate of the sequence the asset is part of.
#
#    sourceIn: [Integer]
#       The source in point as a frame, using the asset frame rate (fps key).
#
#    sourceOut: [Integer]
#       The source out point as a frame, using the asset frame rate (fps key).
#
#    recordIn: [Integer]
#       The record in point as a frame, using the sequence frame rate
#       (sequenceFps key).
#
#    recordOut: [Integer]
#       The record out point as a frame, using the sequence frame rate
#       (sequenceFps key).
#
#    handleIn: [Integer]
#       Head as a frame, using the asset frame rate (fps key).
#
#    handleOut: [Integer]
#       Tail as a frame, using the asset frame rate (fps key).
#
#    track: [String]
#       ID of the sequence's track that contains the asset.
#
#    trackName: [String]
#       Name of the sequence's track that contains the asset.
#
#    segmentIndex: [Integer]
#       Asset index (1 based) in the track.
#
#    versionName: [String]
#       Current version name of export (Empty if unversioned).
#
#    versionNumber: [Integer]
#       Current version number of export (0 if unversioned).
#
# userData [Dictionary] [Modifiable]
#   Dictionary that could have been populated by previous export hooks and that
#   will be carried over into the subsequent export hooks.
#   This can be used by the hook to pass black box data around.
#
def postExportAsset( info, userData ):

   print "postExportAsset - start"
   print info
   print userData

   print "destinationPath: %s" % info['destinationPath']
   print "resolvedPath: %s" % info['resolvedPath']
   print "shotName: %s" % info['shotName']

   if userData['nim_export_sequence'] == True :
      success = nimFlameExport.nimExportShots(nim_showID=userData['nim_showID'], info=info)
   
   print "postExportAsset - end" 
   
   pass


# Indicates whether postExportAsset should be called from a backburner job or
# directly from the application.
#
# Warning: Not generating a postExportAsset backburner job for exports that are
# using backburner could result in postExportAsset being called before the
# export job is complete.
#
def useBackburnerPostExportAsset():
   # print "useBackburnerPostExportAsset - start"
   return True


# Hook returning the custom export profiles to display to the user in the
# contextual menu.
#
# profiles [Dictionary] [Modifiable]
#
#    A dictionary of userData dictionaries where the keys are the name
#    of the profiles to show in contextual menus.
#
def getCustomExportProfiles( profiles ):
   '''
   print "getCustomExportProfiles - start"
   print profiles
   print "getCustomExportProfiles - end"
   '''
   pass


if ( __name__ == "__main__" ):
   import sys

   # Call a hook from the command line:
   #
   #  exportHook.py <function> <args>
   #
   method = sys.argv[ 1 ]
   params = ( eval( p ) for p in sys.argv[ 2: ] )
   globals()[ method ]( * params )
