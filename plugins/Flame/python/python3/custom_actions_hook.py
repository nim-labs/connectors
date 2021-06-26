#!/bin/env python
#******************************************************************************
#
# Filename:    custom_actions_hook.py
# Version:     v5.0.2.210624
# Compatible:  Python 3.x
#
# Copyright (c) 2014-2021 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

#  Import Python GUI packages :
try : 
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtCore
except ImportError :
    try : 
        from PySide import QtCore, QtGui
    except ImportError : 
        print("NIM: Failed to load UI Modules")

import os,sys,re
import flame

nim_app = 'Flame'
os.environ['NIM_APP'] = str(nim_app)
os.environ['NIM_EXPORT'] = ''

# Relative path to append for NIM Scripts
nimFlamePythonPath = os.path.dirname(os.path.realpath(__file__))
nimFlamePythonPath = nimFlamePythonPath.replace('\\','/')
nimScriptPath = re.sub(r"\/plugins/Flame/python$", "", nimFlamePythonPath)
nimFlamePresetPath = os.path.join(re.sub(r"\/python$", "", nimFlamePythonPath),'presets')

try :
    if int(flame.get_version_major()) >= 2022 :
        nimFlamePresetPath = os.path.join(nimFlamePresetPath,'Flame_2022')
    else :
        nimFlamePresetPath = os.path.join(nimFlamePresetPath,'Flame_2020')
except :
    nimFlamePresetPath = os.path.join(nimFlamePresetPath,'Flame_2020')


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


# Hook returning the custom ui actions to display to the user in the
# contextual menu.
#
#   Returns a tuple of group dictionaries.
#
#   A group dictionary defines a custom menu group where keys defines
#   the group.
#
#   Keys:
#
#       name: [String]
#           Name of the action group that will be created in the menu.
#
#       actions: [Tuple]
#           Tuple of action dictionary which menu items will be created
#           in the group.
#
#   An action dictionary of where the keys defines the action attributes
#
#   Keys:
#
#       name: [String]
#           Name of the action. Will also be used as the caption
#           if no caption is defined.
#
#       caption: [String] [Optional]
#           Caption of the menu item. Defaults to name if not defined.
#
#       isEnabled: [Boolean/Callable] [Optional]
#           Boolean or callable object that can be used to enable/disable an
#           action. True is assumed if not defined. The callback object takes
#           one parameter which is a tuple of selected Flame objects.
#
#       isVisible: [Boolean/Callable] [Optional]
#           Boolean or callable object that can be used to show/hide an action.
#           True is assumed if not defined. The callback object takes one
#           parameter which is a tuple of selected Flame objects.
#
#       execute: [Callable] [Optional]
#           Action to execute upon selection. The callback object takes one
#           parameter which is a tuple of selected Flame objects.
#
#   For example: 2 menu groups: one with 1 custom action, the other with 2
#                custom actions.
#
#   def get_media_panel_custom_ui_actions():
#       def execute_action_1(selection):
#           pass
#
#       def execute_action_2(selection):
#           pass
#
#       def execute_action_3(selection):
#           pass
#
#       action_1 = {}
#       action_1["name"] = "Action Number 1"
#       action_1["execute"] = execute_action_1
#
#       group_1 = {}
#       group_1["name"] = "Custom Group 1"
#       group_1["actions"] = [action_1]
#
#       action_2 = {}
#       action_2["name"] = "Action Number 2"
#       action_2["execute"] = execute_action_2
#
#       action_3 = {}
#       action_3["name"] = "Action Number 3"
#       action_3["execute"] = execute_action_3
#
#       group_2 = {}
#       group_2["name"] = "Custom Group 2"
#       group_2["actions"] = [action_2, action_3]
#
#       return [group_1, group_2]
#
#   This could also be written as the following
#
#   def get_media_panel_custom_ui_actions():
#       def action_1(selection):
#           pass
#
#       def action_2(selection):
#           pass
#
#       def action_3(selection):
#           pass
#
#       return [
#            {
#               "name": "Custom Group 1",
#               "actions": [
#                   {
#                       "name": "Action Number 1",
#                       "execute": action_1
#                   }
#               ]
#           },
#           {
#               "name": "Custom Group 2",
#               "actions": [
#                   {
#                       "name": "Action Number 2",
#                       "execute": action_2
#                   },
#                   {
#                       "name": "Action Number 3",
#                       "execute": action_3
#                   }
#               ]
#           }
#       ]
#
def get_media_panel_custom_ui_actions():

    def scanForVersions(selection):
        print("Scan for Versions")
        #print info["selection"]
        
        nimScanDlg = nimFlameExport.NimScanForVersionsDialog()
        nimScanDlg.show()
        if nimScanDlg.exec_() :
            nim_showID = nimScanDlg.nim_showID
            clipCount = nimScanDlg.clipCount
            clipFail = nimScanDlg.clipFail
        
            utf8 = QtCore.QTextCodec.codecForName("utf-8")
            
            # QtCore.QTextCodec.setCodecForCStrings(utf8) deprecated in QT5
            # Left in for backwards compatiblity with older versions of QT
            try :
                QtCore.QTextCodec.setCodecForCStrings(utf8)
            except :
                pass
        
            title = "New Versions Found"
            msg = "New Versions Found: "+str(clipCount)
            if clipFail > 0 :
                msg += "\nFailed to Read Versions: "+str(clipFail)
                msg += "\nPlease try again"
        
            dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
            if dialog==QtGui.QMessageBox.Ok :
                userInput='OK'
        pass

    def buildOpenClipFromElements(selection):
        print("Build OpenClip from Elements")
        #print info["selection"]
        title = "Build OpenClip from Elements"
        
        nimScanDlg = nimFlameExport.NimBuildOpenClipsFromElementDialog()
        nimScanDlg.show()
        if nimScanDlg.exec_() :
            nim_showID = nimScanDlg.nim_showID
            nim_serverID = nimScanDlg.nim_serverID
            clipCount = nimScanDlg.clipCount
            clipFail = nimScanDlg.clipFail
            
            utf8 = QtCore.QTextCodec.codecForName("utf-8")
            
            # QtCore.QTextCodec.setCodecForCStrings(utf8) deprecated in QT5
            # Left in for backwards compatiblity with older versions of QT
            try :
                QtCore.QTextCodec.setCodecForCStrings(utf8)
            except :
                pass
            
            title = "New Versions Found"
            msg = "New Versions Found: "+str(clipCount)
            if clipFail > 0 :
                msg += "\nFailed to Read Versions: "+str(clipFail)
                msg += "\nPlease try again"
            dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
            if dialog==QtGui.QMessageBox.Ok :
                userInput='OK'
        pass
    
    def buildOpenClipFromProject(selection):
        print("Build OpenClip from Project")
        #print info["selection"]
        title = "Build OpenClip from Project Structure"
        
        nimScanDlg = nimFlameExport.NimBuildOpenClipsFromProjectDialog()
        nimScanDlg.show()
        if nimScanDlg.exec_() :
            nim_showID = nimScanDlg.nim_showID
            nim_serverID = nimScanDlg.nim_serverID
            clipCount = nimScanDlg.clipCount
            clipFail = nimScanDlg.clipFail
            
            utf8 = QtCore.QTextCodec.codecForName("utf-8")
            
            # QtCore.QTextCodec.setCodecForCStrings(utf8) deprecated in QT5
            # Left in for backwards compatiblity with older versions of QT
            try :
                QtCore.QTextCodec.setCodecForCStrings(utf8)
            except :
                pass
            
            title = "New Versions Found"
            msg = "New Versions Found: "+str(clipCount)
            if clipFail > 0 :
                msg += "\nFailed to Read Versions: "+str(clipFail)
                msg += "\nPlease try again"
            dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
            if dialog==QtGui.QMessageBox.Ok :
                userInput='OK'
        pass

    def changeUser(selection):
        print("Change User triggered")
        #print info["selection"]

        import nim_core.nim_win as Win;
        Win.userInfo()
        pass

    action1 = {}
    action1[ "name" ] = "Scan for Versions"
    action1[ "caption" ] = "Scan for Versions"
    action1["execute"] = scanForVersions

    action2 = {}
    action2[ "name" ] = "Build OpenClip from Elements"
    action2[ "caption" ] = "Build OpenClip from Elements"
    action2["execute"] = buildOpenClipFromElements

    action3 = {}
    action3[ "name" ] = "Build OpenClip from Project"
    action3[ "caption" ] = "Build OpenClip from Project"
    action3["execute"] = buildOpenClipFromProject

    action4 = {}
    action4[ "name" ] = "Change User"
    action4[ "caption" ] = "Change User"
    action4[ "execute" ] = changeUser

    group1 = {}
    group1[ "name" ] = "NIM Update OpenClips"
    group1[ "actions" ] = ( action1, action2, action3, )

    group2 = {}
    group2[ "name" ] = "NIM Settings"
    group2[ "actions" ] = ( action4, )

    return [ group1, group2, ]

    pass


# Hook returning the custom ui actions to display to the user in the
# flame main menu.
#
#   Returns a tuple of group dictionaries.
#
#   A group dictionary defines a custom menu group where keys defines
#   the group.
#
# Same Documentation as get_media_panel_custom_ui_actions() above
#
def get_main_menu_custom_ui_actions():
    pass


# Hook returning the custom ui actions to display to the user in the
# MediaHub Files menu.
#
#   Returns a tuple of group dictionaries.
#
#   A group dictionary defines a custom menu group where keys defines
#   the group.
#
# Same Documentation as get_media_panel_custom_ui_actions() above
#
def get_mediahub_files_custom_ui_actions():
    pass


# Hook returning the custom ui actions to display to the user in the
# MediaHub Projects menu.
#
#   Returns a tuple of group dictionaries.
#
#   A group dictionary defines a custom menu group where keys defines
#   the group.
#
# Same Documentation as get_media_panel_custom_ui_actions() above
#
def get_mediahub_projects_custom_ui_actions():
    pass


# Hook returning the custom ui actions to display to the user in the
# MediaHub Archives.
#
#   Returns a tuple of group dictionaries.
#
#   A group dictionary defines a custom menu group where keys defines
#   the group.
#
# Same Documentation as get_media_panel_custom_ui_actions() above
#
def get_mediahub_archives_custom_ui_actions():
    pass


# Hook returning the custom ui actions to display to the user in the
# Timeline contextual menus.
#
#   Returns a tuple of group dictionaries.
#
#   A group dictionary defines a custom menu group where keys defines
#   the group.
#
# Same Documentation as get_media_panel_custom_ui_actions() above
#
def get_timeline_custom_ui_actions():
    pass


# Hook returning the custom ui actions to display to the user in the
# Batch Menu.
#
#   Returns a tuple of group dictionaries.
#
#   A group dictionary defines a custom menu group where keys defines
#   the group.
#
# Same Documentation as get_media_panel_custom_ui_actions() above
#
def get_batch_custom_ui_actions():
    pass


# Hook returning the custom ui actions to display to the user in the
# Action Menu.
#
#   Returns a tuple of group dictionaries.
#
#   A group dictionary defines a custom menu group where keys defines
#   the group.
#
# Same Documentation as get_media_panel_custom_ui_actions() above
#
def get_action_custom_ui_actions():
    pass
