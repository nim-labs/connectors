#!/bin/env python
#******************************************************************************
#
# Filename:    batchHook.py
# Version:     v6.0.4.230905
# Compatible:  Python 3.x
#
# Copyright (c) 2014-2023 NIM Labs LLC
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
        print("NIM: Failed to load UI Modules")

import os,sys,re
import flame

nim_app = 'Flame'
os.environ['NIM_APP'] = str(nim_app)

# Relative path to append for NIM Scripts
nimFlamePythonPath = os.path.dirname(os.path.realpath(__file__))
nimFlamePythonPath = nimFlamePythonPath.replace('\\','/')
nimScriptPath = re.sub(r"\/plugins/Flame/python/py3$", "", nimFlamePythonPath)
nimFlamePresetPathBase = os.path.join(re.sub(r"\/python/py3$", "", nimFlamePythonPath),'presets')

try :
    flame_major_version = flame.get_version_major()
    nimFlamePresetPath = os.path.join(nimFlamePresetPathBase, flame_major_version)

    if os.path.isdir(nimFlamePresetPath) == False :
        nimFlamePresetPath = os.path.join(nimFlamePresetPathBase,'_default')
except :
    nimFlamePresetPath = os.path.join(nimFlamePresetPathBase,'_default')


# print ("NIM Script Path: %s" % nimScriptPath)
# print ("NIM Python Path: %s" % nimFlamePythonPath)
# print ("NIM Preset Path: %s" % nimFlamePresetPath)


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
def batch_setup_loaded(setupPath, *args, **kwargs):
    print("batch_setup_loaded - START")
    if debug :
        print(setupPath)
    print("batch_setup_loaded - END")
    pass


# Hook called when a batch setup is saved
#
# setupPath: File path of the setup being saved.
#
def batch_setup_saved(setupPath, *args, **kwargs):
    print("batch_setup_saved - START")
    if debug :
        print(setupPath)
    print("batch_setup_saved - END")
    pass



# Hook called before a batch iteration is created
#
# info [Dictionary] [Modifiable]
#    Information about the batch iteration,
#
#    Keys:
#
#    savePath:     [String] [Modifiable]
#       The path to which a corresponding batch setup file is saved on disk.
#
#    setupName:    [String] [Modifiable]
#       The name of the corresponding batch setup file saved on disk.
#
#    abort:        [Boolean] [Modifiable]
#       Set this variable to True if you want to abort the backup process.
#       If you do so, batchSetupIteratedPost will not be called.
#       False if undefined.
#
#    abortMessage: [String] [Modifiable]
#       Error message to describe why the abort happened.
#       A generic one will be used if left blank.
#
# userData [Dictionary] [Modifiable]
#   Object that will be carried over into the batchSetupIteratedPost hook.
#   This can be used by the hook to pass black box data around.
#
def batch_setup_iterated_pre(info, userData, *args, **kwargs):
    print("batch_setup_iterated_pre - START")
    if debug :
        print(info)
        print(userData)
    print("batch_setup_iterated_pre - END")
    pass


# Hook called after a batch iteration is created
#
# info [Dictionary]
#    Information about the batch iteration,
#
#    Keys:
#
#    savePath:       [String]
#       The path to which a corresponding batch setup file is saved on disk.
#
#    setupName:      [String]
#       The name of the corresponding batch setup file saved on disk.
#
#    abort:          [Boolean]
#       Will be True if the save failed, it won<t be defined otherwise.
#       Note: if the save was manually aborted, this hook will not be called.
#             so this variable only expresses actual errors.
#
#    abortMessage:   [String]
#       Error message to describe why the abort happened.
#
# userData [Dictionary]
#   Object that can be set from the batchSetupIteratedPre hook.
#   This can be used by the hook to pass black box data around.
#
def batch_setup_iterated_post(info, userData, *args, **kwargs):
    print("batch_setup_iterated_post - START")
    if debug :
        print(info)
        print(userData)
    print("batch_setup_iterated_post - END")
    pass


# Hook called before a render begins.
#
# info [Dictionary] [Modifiable]
#    Information about the render,
#
#    Keys:
#
#    backgroundJobName: [String] [Modifiable]
#       Job name as shown in Backburner. Can be modified by the hook
#       before the job is actually sent.
#
#    aborted: [Boolean] [Modifiable]
#       Set this variable to True if you want to abort the process.
#
#    abortMessage: [String] [Modifiable]
#       Error message to describe why the abort happened.
#       A generic one will be used if left blank.
#
# userData [Dictionary] [Modifiable]
#   Object that will be carried over into the batchRenderEnd hook.
#   This can be used by the hook to pass black box data around.
#
def batch_render_begin(info, userData, *args, **kwargs):
    print("batch_render_begin - START")
    if debug :
        print(info)
        print(userData)
    print("batch_render_begin - END")
    pass



# Hook called when a render ends.
#
# This function complements the above batchRenderBegin function.
#
# info [Dictionary]
#    Information about the render,
#
#    Keys:
#
#    backgroundJobName: [String]
#       Job name as shown in Backburner.
#
#    backgroundJobId: [String]
#       Id of the background job given by the backburner Manager upon
#       submission.
#
#    aborted: [Boolean]
#       Indicate if the render has been aborted by the user or by a render
#       error.
#
#    abortMessage: [String]
#       Error message to describe why the abort happened.
#
# userData [Dictionary] [Modifiable]
#   Object that will be carried over into the batchExportEnd hook.
#   This can be used by the hook to pass black box data around.
#
def batch_render_end(info, userData, *args, **kwargs):
    print("batch_render_end - START")
    if debug :
        print(info)
        print(userData)
    print("batch_render_end - END")
    pass


# Hook called before a job is sent to Burn or Background Reactor.
#
# info [Dictionary] [Modifiable]
#    Information about the job,
#
#    Keys:
#
#    aborted: [Boolean] [Modifiable]
#       Set this variable to True if you want to abort the process.
#
#    abortMessage: [String] [Modifiable]
#       Error message to describe why the abort happened.
#       A generic one will be used if left blank.
#
# userData [Dictionary] [Modifiable]
#   Object that will be carried over into the batchRenderEnd hook.
#   This can be used by the hook to pass black box data around.
#
def batch_burn_begin(info, userData, *args, **kwargs):
    print("batch_burn_begin - START")
    if debug :
        print(info)
        print(userData)
    print("batch_burn_begin - END")
    pass


# Hook called after a job is sent to Burn or Background Reactor.
#
# This function complements the above batch_burn_begin function.
#
# info [Dictionary]
#    Information about the job,
#
#    Keys:
#
#    aborted: [Boolean]
#       Indicate if the process has been aborted by the user or by an
#       error.
#
#    abortMessage: [String]
#       Error message to describe why the abort happened.
#
#    backgroundJobId: [String]
#       Id of the background job given by the backburner Manager upon
#       submission.
#
# userData [Dictionary] [Modifiable]
#   Object that will be carried over into the batchExportEnd hook.
#   This can be used by the hook to pass black box data around.
#
def batch_burn_end(info, userData, *args, **kwargs):
    print("batch_burn_end - START")
    if debug :
        print(info)
        print(userData)
    print("batch_burn_end - END")
    pass

            
# Hook called before a write file node starts to export.  Note that for stereo
# exports this function is called twice, once for each channel
# (left first, right second).
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
#    shotName: [String]
#       Current shot name of export.
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
#       ('8-bits', '10-bits', '12-bits', '16 fp')
#
#    scanFormat: [String]
#       Scan format of the exported media.
#       ('FIELD_1', 'FIELD_2', 'PROGRESSIVE')
#
#    colourSpace: [String]
#       Colour space of the exported media.
#
#    fps: [Double]
#       Frame rate of exported asset.
#
#    aborted: [Boolean] [Modifiable]
#       Set this variable to True if you want to abort the process.
#
#    abortMessage: [String] [Modifiable]
#       Error message to describe why the abort happened.
#       A generic one will be used if left blank.
#
# userData [Object] [Modifiable]
#   Object that will be carried over into the batchExportEnd hook.
#   This can be used by the hook to pass black box data around.
#
def batch_export_begin(info, userData, *args, **kwargs):
    print("batch_export_begin - START")
    if debug :
        print(info)
        print(userData)

    # Check if Custom NIM export or Standard Export
    # If standard export then ask for NIM association
    nimShowDialog = True
 
    batchExportDlg = nimFlameExport.NimBatchExportDialog()
    batchExportDlg.show()
    if batchExportDlg.exec_() :
        nim_comment = batchExportDlg.nim_comment
        nimFlameExport.nimAddBatchExport(info=info, comment=nim_comment)

    print("batch_export_begin - END")
    pass


# Hook called when a write file node ends the export. Note that for stereo
# exports this function is called twice, once for each channel
# (left first, right second).
#
# This function complements the above batch_export_begin function.
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
#    shotName: [String]
#       Current shot name of export.
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
#       ('8-bits', '10-bits', '12-bits', '16 fp')
#
#    scanFormat: [String]
#       Scan format of the exported media.
#       ('FIELD_1', 'FIELD_2', 'PROGRESSIVE')
#
#    fps: [Double]
#       Frame rate of exported asset.
#
#    backgroundJobId: [String]
#       Id of the background job given by the backburner Manager upon
#       submission. Empty if job is done in foreground.
#
#    aborted: [Boolean]
#       Indicate if the export has been aborted by the user or by a render
#       error.
#
#    abortMessage: [String]
#       Error message to describe why the abort happened.
#
# userData [Dictionary]
#   Object optionally filled by the batchExportBegin hook.
#   This can be used by the hook to pass black box data around.
#
def batch_export_end(info, userData, *args, **kwargs):
    print("batch_export_end - START")
    if debug :
        print(info)
        print(userData)
    print("batch_export_end - END")
    pass


# Hook called when starting the application and when switching project
# This default name will be used at batch creation.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    batch iteration name for this project will be returned.
#
# Ex: if project == "project_name":
#         return "<batch name>_<iteration###>_project"
#     return "<batch name>_<iteration###>_global"
#
# The returned string should contains the following mandatory tokens:
# <batch name> and <iteration>
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def batch_default_iteration_name(project, *args, **kwargs):
    print("batch_default_iteration_name - START")
    if debug :
        print(project)
    print("batch_default_iteration_name - END")
    return ""


# Hook called when starting the application and when switching project
# This default name will be used at render node creation.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    render node name for this project will be returned.
#
# Ex: if project == "project_name":
#         return "<batch name>_render_project"
#     return "<batch name>_render_global"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def batch_default_render_node_name(project, *args, **kwargs):
    print("batch_default_render_node_name - START")
    if debug :
        print(project)
    print("batch_default_render_node_name - END")
    return ""


# Hook called when starting the application and when switching project
# This default name will be used at write file node creation.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    write file node name for this project will be returned.
#
# Ex: if project == "project_name":
#         return "<batch name>_writefile_project"
#     return "<batch name>_writefile_global"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def batch_default_write_file_node_name(project, *args, **kwargs):
    print("batch_default_write_file_node_name - START")
    if debug :
        print(project)
    print("batch_default_write_file_node_name - END")
    return ""


# Hook called when starting the application and when switching project
# This default batch group path will be used to save setups.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    Batch group path for this project will be returned.
#
# Ex: if project == "project_name":
#         return "~/specialPathForthatProject/batch/<batch name>"
#     return "~/batch/<batch name>"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def batch_default_group_path(project, *args, **kwargs):
    print("batch_default_group_path - START")
    if debug :
        print(project)
    print("batch_default_group_path - END")
    return ""


# Hook called when starting the application and when switching project
# This default batch iteration path will be used to save setups.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    Batch iteration path for this project will be returned.
#
# Ex: if project == "project_name":
#         return "~/specialPathForthatProject/batch/<batch name>/iterations"
#     return "~/batch/<batch name>/iterations"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def batch_default_iteration_path(project, *args, **kwargs):
    print("batch_default_iteration_path - START")
    if debug :
        print(project)
    print("batch_default_iteration_path - END")
    return ""


# Hook called when starting the application and when switching project
# This default atcion geometry path will be used to import geometry.
#
# project: [String]
#    Usually called with current project.  If specified, the default
#    Action geometry path for this project will be returned.
#
# Ex: if project == "project_name":
#         return "~/specialPathForthatProject/batch/<batch name>/fileformats"
#     return "~/batch/<batch name>/fileformats"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def action_default_geometry_path(project, *args, **kwargs):
    print("action_default_geometry_path - START")
    if debug :
        print(project)
    print("action_default_geometry_path - END")
    return ""

