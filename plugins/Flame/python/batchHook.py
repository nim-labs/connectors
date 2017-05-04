#!/bin/env python
#******************************************************************************
#
# Filename: batchHook.py
#
# Copyright (c) 2014 Autodesk Inc.
# All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

# Hook called when a batch setup is loaded
#
# setupPath: File path of the setup being loaded.
#
def batchSetupLoaded( setupPath ):
   pass


# Hook called when a batch setup is saved
#
# setupPath: File path of the setup being saved.
#
def batchSetupSaved( setupPath ):
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
   return ""
