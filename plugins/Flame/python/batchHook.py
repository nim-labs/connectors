#!/bin/env python
#******************************************************************************
#
# Filename: batchHook.py
# Version:  v4.0.56.201006
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

# Hook called when a batch setup is loaded
#
# setupPath: File path of the setup being loaded.
#
def batchSetupLoaded( setupPath ):
   print "batchSetupLoaded - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print setupPath
   print "batchSetupLoaded - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   pass


# Hook called when a batch setup is saved
#
# setupPath: File path of the setup being saved.
#
def batchSetupSaved( setupPath ):
   print "batchSetupSaved - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print setupPath
   print "batchSetupSaved - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   pass


# Hook called before an export begins.  Note that for stereo export this
# function will be called twice (for left then right channel)
#
# info [Dictionary] [Modifiable]
#    Information about the export,
#
#    Keys:
#
#    nodeName:   [String]
#       Name of the export node.
#
#    exportPath: [String] [Modifiable]
#       Export path as entered in the application UI.
#       Can be modified by the hook to change where the file are written.
#
#    namePattern: [String]
#       List of optional naming tokens as entered in the application UI.
#
#    resolvedPath: [String]
#       Full file pattern that will be exported with all the tokens resolved.
#
#    firstFrame: [Integer]
#       Frame number of the first frame that will be exported.
#
#    lastFrame: [Integer]
#       Frame number of the last frame that will be exported.
#
#    versionName: [String]
#       Current version name of export (Empty if unversioned).
#
#    versionNumber: [Integer]
#       Current version number of export (0 if unversioned).
#
#    openClipNamePattern: [String]
#       List of optional naming tokens pointing to the open clip created if any
#       as entered in the application UI. This is only available if versioning
#       is enabled.
#
#    openClipResolvedPath: [String]
#       Full path to the open clip created if any with all the tokens resolved.
#       This is only available if versioning is enabled.
#
#    setupNamePattern: [String]
#       List of optional naming tokens pointing to the setup created if any
#       as entered in the application UI. This is only available if versioning
#       is enabled.
#
#    setupResolvedPath: [String]
#       Full path to the setup created if any with all the tokens resolved.
#       This is only available if versioning is enabled.
#
#    width: [Long]
#       Frame width of the exported media.
#
#    height: [Long]
#       Frame height of the exported media.
#
#    aspectRatio: [Double]
#       Frame aspect ratio of the exported media.
#
#    depth: [String]
#       Frame depth of the exported media.
#       ( '8-bits', '10-bits', '12-bits', '16 fp' )
#
#    scanFormat: [String]
#       Scan format of the exported media.
#       ( 'FIELD_1', 'FIELD_2', 'PROGRESSIVE' )
#
#    fps: [Double]
#       Frame rate of exported asset.
#
# userData [Dictionary] [Modifiable]
#   Empty Dictionary that will be carried over into the batchExportEnd hook.
#   This can be used by the hook to pass black box data around.
#
def batchExportBegin( info, userData ):
   print "batchExportBegin - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print info
      print userData

   # Check if Custom NIM export or Standard Export
   # If standard export then ask for NIM association
   nimShowDialog = True

   batchExportDlg = nimFlameExport.NimBatchExportDialog()
   batchExportDlg.show()
   if batchExportDlg.exec_() :
      nim_comment = batchExportDlg.nim_comment
      nimFlameExport.nimAddBatchExport(info=info, comment=nim_comment)

   print "batchExportBegin - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   pass


# Hook called when an export ends. Note that for stereo export this
# function will be called twice (for left then right channel)
#
# This function complements the above batchExportBegin function.
#
# info [Dictionary]
#    Information about the export,
#
#    Keys:
#
#    nodeName:   [String]
#       Name of the export node.
#
#    exportPath: [String]
#       Export path as entered in the application UI.
#
#    namePattern: [String]
#       List of optional naming tokens as entered in the application UI.
#
#    resolvedPath: [String]
#       Full file pattern that will be exported with all the tokens resolved.
#
#    firstFrame: [Integer]
#       Frame number of the first frame that will be exported.
#
#    lastFrame: [Integer]
#       Frame number of the last frame that will be exported.
#
#    versionName: [String]
#       Current version name of export (Empty if unversioned).
#
#    versionNumber: [Integer]
#       Current version number of export (0 if unversioned).
#
#    openClipNamePattern: [String]
#       List of optional naming tokens pointing to the open clip created if any
#       as entered in the application UI. This is only available if versioning
#       is enabled.
#
#    openClipResolvedPath: [String]
#       Full path to the open clip created if any with all the tokens resolved.
#       This is only available if versioning is enabled.
#
#    setupNamePattern: [String]
#       List of optional naming tokens pointing to the setup created if any
#       as entered in the application UI. This is only available if versioning
#       is enabled.
#
#    setupResolvedPath: [String]
#       Full path to the setup created if any with all the tokens resolved.
#       This is only available if versioning is enabled.
#
#    width: [Long]
#       Frame width of the exported media.
#
#    height: [Long]
#       Frame height of the exported media.
#
#    aspectRatio: [Double]
#       Frame aspect ratio of the exported media.
#
#    depth: [String]
#       Frame depth of the exported media.
#       ( '8-bits', '10-bits', '12-bits', '16 fp' )
#
#    scanFormat: [String]
#       Scan format of the exported media.
#       ( 'FIELD_1', 'FIELD_2', 'PROGRESSIVE' )
#
#    fps: [Double]
#       Frame rate of exported asset.
#
#    aborted: [Boolean]
#       Indicate if the export has been aborted by the user.
#
# userData [Dictionary]
#   Dictionary optionally filled by the batchExportBegin hook.
#   This can be used by the hook to pass black box data around.
#
def batchExportEnd( info, userData ):
   print "batchExportEnd - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print info
      print userData
   print "batchExportEnd - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   pass

# Hook called when starting the application and when switching project
# This default name will be used at batch creation.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    batch iteration name for this project will be returned.
#
# Ex: if project == "project_name":
#        return "<batch name>_<iteration###>_project"
#     return "<batch name>_<iteration###>_global"
#
# The returned string should contains the following mandatory tokens:
# <batch name> and <iteration>

def batchDefaultIterationName( project ):
   print "batchDefaultIterationName - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print project
   print "batchDefaultIterationName - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   return ""

# Hook called when starting the application and when switching project
# This default name will be used at render node creation.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    render node name for this project will be returned.
#
# Ex: if project == "project_name":
#        return "<batch name>_render_project"
#     return "<batch name>_render_global"
#

def batchDefaultRenderNodeName( project ):
   print "batchDefaultRenderNodeName - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print project
   print "batchDefaultRenderNodeName - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   return ""

# Hook called when starting the application and when switching project
# This default name will be used at write file node creation.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    write file node name for this project will be returned.
#
# Ex: if project == "project_name":
#        return "<batch name>_writefile_project"
#     return "<batch name>_writefile_global"

def batchDefaultWriteFileNodeName( project ):
   print "batchDefaultWriteFileNodeName - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print project
   print "batchDefaultWriteFileNodeName - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   return ""

# Hook called when starting the application and when switching project
# This default batch group path will be used to save setups.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    Batch group path for this project will be returned.
#
# Ex: if project == "project_name":
#        return "~/specialPathForthatProject/batch/<batch name>"
#     return "~/batch/<batch name>"
#

def batchDefaultGroupPath( project ):
   print "batchDefaultGroupPath - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print project
   print "batchDefaultGroupPath - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   return ""

# Hook called when starting the application and when switching project
# This default batch iteration path will be used to save setups.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    Batch iteration path for this project will be returned.
#
# Ex: if project == "project_name":
#        return "~/specialPathForthatProject/batch/<batch name>/iterations"
#     return "~/batch/<batch name>/iterations"
#

def batchDefaultIterationPath( project ):
   print "batchDefaultIterationPath - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print project
   print "batchDefaultIterationPath - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   return ""

# Hook called when starting the application and when switching project
# This default atcion geometry path will be used to import geometry.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    Action geometry path for this project will be returned.
#
# Ex: if project == "project_name":
#        return "~/specialPathForthatProject/batch/<batch name>/fileformats"
#     return "~/batch/<batch name>/fileformats"
#

def actionDefaultGeometryPath( project ):
   print "actionDefaultGeometryPath - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   if debug :
      print project
   print "actionDefaultGeometryPath - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   return ""

