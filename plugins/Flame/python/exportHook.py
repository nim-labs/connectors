#!/bin/env python
#******************************************************************************
#
# Filename: exportHook.py
# Version:  v4.0.49.200410
#
# Copyright (c) 2014-2020 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

#  Import Python GUI packages :
try : 
   from PySide2.QtWidgets import *
   from PySide2.QtGui import *
   from PySide2.QtCore import *
except ImportError :
   try : 
      from PySide.QtGui import *
      from PySide.QtCore import *
   except ImportError : 
      print "NIM: Failed to load UI Modules"

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

   #NimExportSequence
   if userData['nim_export_type'] == 'NimExportSequence' :
      #Set the proper 'presetPath' in the info dictionary
      #This defines which preset is used for the custom encode job
      #info['presetPath'] = '/path/to/export/presets/uncompressed_qt.xml'

      print "NIM - Exporting Sequence"
      userData['nim_export_sequence'] = True

      exportDlg = nimFlameExport.NimExportSequenceDialog()
      exportDlg.show()
      if exportDlg.exec_() :
         print "NIM - nim_userID: %s" % exportDlg.nim_userID
         userData['nim_userID'] = exportDlg.nim_userID

         print "NIM - serverID: %s" % exportDlg.nim_serverID
         userData['nim_serverID'] = exportDlg.nim_serverID

         print "NIM - serverOSPath: %s" % exportDlg.nim_serverOSPath
         nim_serverOSPath = exportDlg.nim_serverOSPath
         userData['nim_serverOSPath'] = nim_serverOSPath

         # Set destination path to NIM server path
         info['destinationPath'] = nim_serverOSPath
         print "Destination Path: %s" % info['destinationPath']


         print "NIM - jobID: %s" % exportDlg.nim_jobID
         userData['nim_jobID'] = exportDlg.nim_jobID

         print "NIM - showID: %s" % exportDlg.nim_showID
         userData['nim_showID'] = exportDlg.nim_showID

         print "NIM - videoElementID: %s" % exportDlg.videoElementID
         userData['videoElementID'] = exportDlg.videoElementID

         print "NIM - audioElementID: %s" % exportDlg.audioElementID
         userData['audioElementID'] = exportDlg.audioElementID

         print "NIM - openClipElementID: %s" % exportDlg.openClipElementID
         userData['openClipElementID'] = exportDlg.openClipElementID

         print "NIM - batchOpenClipElementID: %s" % exportDlg.batchOpenClipElementID
         userData['batchOpenClipElementID'] = exportDlg.batchOpenClipElementID

         print "NIM - batchTaskTypeID: %s" % exportDlg.batchTaskTypeID
         userData['batchTaskTypeID'] = exportDlg.batchTaskTypeID
         userData['batchTaskTypeFolder'] = exportDlg.batchTaskTypeFolder
         
         # Create empty dictionary for shot data
         userData['shotData'] = {}
         
         # Set NIM Preset
         nim_preset = exportDlg.nim_preset
         info['presetPath'] = nimFlamePresetPath + '/sequence/'+nim_preset+'.xml'         
         
         # Process in Background
         info['isBackground'] = False

      else:
         print "NIM - Canceled Export to NIM"
         userData['nim_export_sequence'] = False
         info['abort'] = True


   #NimExportEdit
   if userData['nim_export_type'] == 'NimExportEdit' :
      #Set the proper 'presetPath' in the info dictionary
      #This defines which preset is used for the custom encode job
      #info['presetPath'] = '/path/to/export/presets/uncompressed_qt.xml'

      print "NIM - Exporting Edit"
      userData['nim_export_edit'] = True

      exportDlg = nimFlameExport.NimExportEditDialog()
      exportDlg.show()
      if exportDlg.exec_() :
         print "NIM - nim_userID: %s" % exportDlg.nim_userID
         userData['nim_userID'] = exportDlg.nim_userID

         print "NIM - serverID: %s" % exportDlg.nim_serverID
         userData['nim_serverID'] = exportDlg.nim_serverID

         print "NIM - serverOSPath: %s" % exportDlg.nim_serverOSPath
         nim_serverOSPath = exportDlg.nim_serverOSPath
         userData['nim_serverOSPath'] = nim_serverOSPath

         # Set destination path to NIM server path
         info['destinationPath'] = nim_serverOSPath
         print "Destination Path: %s" % info['destinationPath']


         print "NIM - jobID: %s" % exportDlg.nim_jobID
         userData['nim_jobID'] = exportDlg.nim_jobID

         print "NIM - showID: %s" % exportDlg.nim_showID
         userData['nim_showID'] = exportDlg.nim_showID
         
         # Create empty dictionary for shot data
         userData['shotData'] = {}
         
         # Set NIM Preset
         nim_preset = exportDlg.nim_preset
         info['presetPath'] = nimFlamePresetPath + '/edit/'+nim_preset+'.xml'         
         
         # Process in Background
         info['isBackground'] = False
         #nim_bg_export = exportDlg.nim_bg_export
         #info['isBackground'] = nim_bg_export
         
      else:
         print "NIM - Canceled Export to NIM"
         userData['nim_export_edit'] = False
         info['abort'] = True
   

   #NimExportEdit
   if userData['nim_export_type'] == 'NimExportDaily' :
      #Set the proper 'presetPath' in the info dictionary
      #This defines which preset is used for the custom encode job
      #info['presetPath'] = '/path/to/export/presets/uncompressed_qt.xml'

      print "NIM - Exporting Daily"
      userData['nim_export_daily'] = True

      exportDlg = nimFlameExport.NimExportDailyDialog()
      exportDlg.show()
      if exportDlg.exec_() :
         print "NIM - nim_userID: %s" % exportDlg.nim_userID
         userData['nim_userID'] = exportDlg.nim_userID

         print "NIM - serverID: %s" % exportDlg.nim_serverID
         userData['nim_serverID'] = exportDlg.nim_serverID

         print "NIM - serverOSPath: %s" % exportDlg.nim_serverOSPath
         nim_serverOSPath = exportDlg.nim_serverOSPath
         userData['nim_serverOSPath'] = nim_serverOSPath

         # Set destination path to NIM server path
         info['destinationPath'] = nim_serverOSPath
         print "Destination Path: %s" % info['destinationPath']


         print "NIM - jobID: %s" % exportDlg.nim_jobID
         userData['nim_jobID'] = exportDlg.nim_jobID

         print "NIM - showID: %s" % exportDlg.nim_showID
         userData['nim_showID'] = exportDlg.nim_showID

         print "NIM - shotID: %s" % exportDlg.nim_shotID
         userData['nim_shotID'] = exportDlg.nim_shotID

         print "NIM - taskID: %s" % exportDlg.nim_taskID
         userData['nim_taskID'] = exportDlg.nim_taskID
         
         # Create empty dictionary for shot data
         userData['shotData'] = {}
         
         # Set NIM Preset
         nim_preset = exportDlg.nim_preset
         info['presetPath'] = nimFlamePresetPath + '/daily/'+nim_preset+'.xml'         
         
         # Process in Background
         info['isBackground'] = False

      else:
         print "NIM - Canceled Export to NIM"
         userData['nim_export_edit'] = False
         info['abort'] = True


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

   if 'nim_export_sequence' in userData :
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


   if 'nim_export_edit' in userData :
      if userData['nim_export_edit'] == True :
         print "postExportSequence - Edit"
         # Upload Edit
         nim_showID = None
         if 'nim_showID' in userData :
            nim_showID = userData['nim_showID']
      
         if 'editData' in userData :
            mov_path = userData['editData']['path']
            result = nimFlameExport.uploadEdit(nim_showID=nim_showID, mov_path=mov_path)
         

   if 'nim_export_daily' in userData :
      if userData['nim_export_daily'] == True :
         print "postExportSequence - Daily"
         # Upload Daily

         nim_taskID = None
         if 'nim_taskID' in userData :
            nim_taskID = userData['nim_taskID']
      
         if 'dailyData' in userData :
            mov_path = userData['dailyData']['path']
            result = nimFlameExport.uploadDaily(nim_taskID=nim_taskID, mov_path=mov_path)

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

         # Build Shot Array
         if info['shotName'] not in userData['shotData'] :
            userData['shotData'][info['shotName']] = {}

         userData['shotData'][info['shotName']][info['assetType']] = result 
         userData['currentShotID'] = result['nim_shotID']


   if 'nim_export_edit' in userData :
      if userData['nim_export_edit'] == True :
         info['resolvedPath'] = nimFlameExport.nimResolvePath(nim_showID=userData['nim_showID'], keyword_string=info['resolvedPath'])


   if 'nim_export_daily' in userData :
      if userData['nim_export_daily'] == True :
         info['resolvedPath'] = nimFlameExport.nimResolvePath(nim_shotID=userData['nim_shotID'], keyword_string=info['resolvedPath'])


   if debug :
      print "destinationPath: %s" % info['destinationPath']
      print "resolvedPath: %s" % info['resolvedPath']
      #print "shotName: %s" % info['shotName']

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

         nim_userID = userData['nim_userID']
         
         nim_tapeName = ''
         # Check if tapeName is in info
         # if exists set userData 
         #  - should happen first on batchOpenClip before batch
         if 'tapeName' in info :
            userData['tapeName'] = info['tapeName']

         # If tapeName has been sent in userData set var for exportFile
         if 'tapeName' in userData :
            nim_tapeName = userData['tapeName']

         assetTypeID = 0
         exportFile = False
         if info['assetType'] == 'video' :
            assetTypeID = userData['videoElementID']
         if info['assetType'] == 'audio' :
            assetTypeID = userData['audioElementID']
         if info['assetType'] == 'openClip' :
            assetTypeID = userData['openClipElementID']
         if info['assetType'] == 'batchOpenClip' :
            assetTypeID = userData['batchOpenClipElementID']
         if info['assetType'] == 'batch' :
            assetTypeID = userData['batchTaskTypeID']
            exportFile = True

         comment = 'Batch File exported from Flame'

         if exportFile :
            # export batch to NIM files
            result = nimFlameExport.nimExportFile(nim_shotID=userData['currentShotID'], info=info, taskTypeID=assetTypeID, \
                                    taskFolder=userData['batchTaskTypeFolder'], serverID=userData['nim_serverID'], \
                                    nim_userID=nim_userID, tapeName=nim_tapeName, comment=comment)
         else :
            # export asset to NIM element
            result = nimFlameExport.nimExportElement(nim_shotID=userData['currentShotID'], info=info, typeID=assetTypeID, nim_userID=nim_userID)

   
   if 'nim_export_edit' in userData :
      if userData['nim_export_edit'] == True :
         print "postExportEdit"
         editPath = os.path.join(info['destinationPath'], info['resolvedPath'])
         userData['editData'] = {}
         userData['editData']['path'] = editPath


   if 'nim_export_daily' in userData :
      if userData['nim_export_daily'] == True :
         print "postExportDaily"
         dailyPath = os.path.join(info['destinationPath'], info['resolvedPath'])
         userData['dailyData'] = {}
         userData['dailyData']['path'] = dailyPath


   if debug :
      print "destinationPath: %s" % info['destinationPath']
      print "resolvedPath: %s" % info['resolvedPath']
      #print "shotName: %s" % info['shotName']
      #print "shotID: %s" % userData['currentShotID']

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
   profiles['NIM Publish Sequence']        = {'nim_export_type':'NimExportSequence'} #Adds an entry to the 'userData' dictionary
   profiles['NIM Export Clip to Daily']        = {'nim_export_type':'NimExportDaily'}    #Adds an entry to the 'userData' dictionary
   profiles['NIM Export Clip to Edit']        = {'nim_export_type':'NimExportEdit'}     #Adds an entry to the 'userData' dictionary
   
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
