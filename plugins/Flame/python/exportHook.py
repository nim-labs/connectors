#!/bin/env python
#******************************************************************************
#
# Filename: exportHook.py
#
'''
Create wiretap ID association with NIM Show
   Log all openClips from export

Options on right click to :
   Scan for versions
   Build OpenClips from Elements

Clip can be associated with a single shot or show(sequence)

__________________________________________________________________________

Custom Export....

   preCustomExport :
      get job/server/show and set in user data
      choose preset from NIM preset files


Generic export....

   preAssetExport :
      if custom export is not defined
         Check for nim keywords in template
         if keywords exist assume working with NIM
            if nim variables are not set 
               "NIM Keywords Detected"
               ask if export sequence to NIM
                  get job/show and set in user data
         
      create shot
      get root paths
      replace keywords with paths

   postAssetExport :
      update shotIcons
      log elements
      log files
      log openClip against shot
'''
# *****************************************************************************


from PySide.QtGui import *
from PySide.QtCore import *

import os,sys,re

nim_app = 'Flame'
os.environ['NIM_APP'] = str(nim_app)

# Relative path to append for NIM Scripts
nimFlamePythonPath = os.path.dirname(os.path.realpath(__file__))
nimFlamePythonPath = nimFlamePythonPath.replace('\\','/')
nimScriptPath = re.sub(r"\/plugins/Flame/python$", "", nimFlamePythonPath)
nimFlamePresetPath = os.path.join(re.sub(r"\/python$", "", nimFlamePythonPath),'presets')

print "NIM Script Path: %s" % nimScriptPath
print "NIM Python Path: %s" % nimFlamePythonPath
print "NIM Preset Path: %s" % nimFlamePresetPath

# If relocating these scripts uncomment the line below and enter the fixed path
# to the NIM Connector Root directory
#
# nimScriptPath = [NIM_CONNECTOR_ROOT]
#

sys.path.append(nimScriptPath)

import nimFlameExport

debug = True

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
   print "preCustomExport - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print info
      print userData

   #Test what 'exportType' was select in the UI, by the user
   if userData['nim_export_type'] == 'NimExportSequence' :
      #Set the proper 'presetPath' in the info dictionary
      #This defines which preset is used for the custom encode job
      #info['presetPath'] = '/path/to/export/presets/uncompressed_qt.xml'

      print "NIM - Exporting to NIM"
      userData['nim_export_sequence'] = True

      exportDlg = nimFlameExport.NimExportDialog()
      exportDlg.show()
      if exportDlg.exec_() :
         print "NIM - serverOSPath: %s" % exportDlg.nim_serverOSPath
         nim_serverOSPath = exportDlg.nim_serverOSPath
         userData['nim_serverOSPath'] = nim_serverOSPath

         print "NIM - jobID: %s" % exportDlg.nim_jobID
         nim_jobID = exportDlg.nim_jobID
         userData['nim_jobID'] = nim_jobID

         print "NIM - showID: %s" % exportDlg.nim_showID
         nim_showID = exportDlg.nim_showID
         userData['nim_showID'] = nim_showID
         
         # Create empty dictionary for shot data
         userData['shotData'] = {}
         
         # TODO: Add dropdown to dialog to select preset option
         #  Optional - read xml and resolve all NIM keywords and write to temp XML
         #           - set to temp XML
         #           This will work for custom but still won't resolve keys used in standard export
         
         #  DO INSTEAD OF OPTIONAL :
         #          To resolve all keywords in standard export modify the .export_node file in the batch
         #              retrieve & resolve batchSetup location from XML - batchSetup / namePattern

         info['presetPath'] = nimFlamePresetPath + '/sequence_publish/NimExportSequence.xml'

         # Set destination path to NIM server path
         info['destinationPath'] = nim_serverOSPath
         print "Destination Path: %s" % info['destinationPath']
         
         # Process in Background
         info['isBackground'] = False

      else:
         print "NIM - Canceled Export to NIM"
         userData['nim_export_sequence'] = False
         info['abort'] = True

      #Set the 'destinationPath' in the info dictionary
      #info['destinationPath'] = '/PRJ/NIM_PROJECTS/FlameFiles/' + CURRENT_PROJECT + '/'
      
   print "preCustomExport - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
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
   print "postCustomExport - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print info
      print userData
   print "postCustomExport - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
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
   print "preExport - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print info
      print userData
   print "preExport - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
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
   print "postExport - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print info
      print userData
   print "postExport - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
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
   print "preExportSequence - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print info
      print userData

   # Check if Custom NIM export or Standard Export
   # If standard export then ask for NIM association
   nimShowDialog = False

   if 'nim_export_type' in userData :
      if userData['nim_export_type'] != 'NimExportSequence' :
         nimShowDialog = True
   else :
      nimShowDialog = True

   if nimShowDialog :
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
            userData['shotData'] = {}
      else:
         print "NIM - Skipping Export to NIM"
         userData['nim_export_sequence'] = False

   print "preExportSequence - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
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
   print "postExportSequence - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print info
      print userData

   if userData['nim_export_sequence'] == True :
      shotData = userData['shotData']

      for shotName in shotData :
         print "shotName: %s" % shotName
         for assetType in shotData[shotName] :
            
            # Update Icons
            if assetType == 'video' :
               print "Updating Shot Icon"
               itemData = shotData[shotName]['video']
               nim_shotID = itemData['nim_shotID']
               nim_iconPath = itemData['nim_iconPath']
               print "shotID: %s" % nim_shotID
               print "iconPath: %s" % nim_iconPath
               result = nimFlameExport.updateShotIcon(nim_shotID=nim_shotID, image_path=nim_iconPath)

            # Resolve keywords in Batch export_node files
            if assetType == 'batch' :
               print "Resolving Keywords in Batch Export Node"
               itemData = shotData[shotName]['batch']
               nim_shotID = itemData['nim_shotID']
               resolvedPath = itemData['resolvedPath']
               destinationPath = info['destinationPath']
               batchPath = os.path.join(destinationPath,resolvedPath)
               result = nimFlameExport.resolveBatchKeywords(nim_shotID=nim_shotID, batch_path=batchPath)

   print "postExportSequence - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
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
   print "preExportAsset - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print info
      print userData

   if 'nim_export_sequence' in userData :
      if userData['nim_export_sequence'] == True :
         result = nimFlameExport.nimCreateShot(nim_showID=userData['nim_showID'], info=info)

   info['resolvedPath'] = result['resolvedPath']

   if info['shotName'] not in userData['shotData'] :
      userData['shotData'][info['shotName']] = {}

   userData['shotData'][info['shotName']][info['assetType']] = result 
   userData['currentShotID'] = result['nim_shotID']

   if debug :
      print "destinationPath: %s" % info['destinationPath']
      print "resolvedPath: %s" % info['resolvedPath']
      print "shotName: %s" % info['shotName']

   print "preExportAsset - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
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

   print "postExportAsset - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print info
      print userData

   if 'nim_export_sequence' in userData :
      if userData['nim_export_sequence'] == True :
         result = nimFlameExport.nimExportElement(nim_shotID=userData['currentShotID'], info=info)
   
   if debug :
      print "destinationPath: %s" % info['destinationPath']
      print "resolvedPath: %s" % info['resolvedPath']
      print "shotName: %s" % info['shotName']
      print "shotID: %s" % userData['currentShotID']

   print "postExportAsset - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" 
   
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
   print "getCustomExportProfiles - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   profiles['NIM Export Sequence']= {'nim_export_type':'NimExportSequence'} #Adds an entry to the 'userData' dictionary
   print "getCustomExportProfiles - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
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