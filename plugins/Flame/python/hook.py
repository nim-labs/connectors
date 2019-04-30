#!/bin/env python
#******************************************************************************
#
# Filename: hook.py
# Version:  v4.0.27.190418
#
# Copyright (c) 2014-2019 NIM Labs LLC
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
      print "NIM: Failed to load UI Modules"

import os,sys,re

nim_app = 'Flame'
os.environ['NIM_APP'] = str(nim_app)
os.environ['NIM_EXPORT'] = ''

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



# Hook called when a sequence finishes rendering (even if unsuccessful).
# moduleName : Name of the rendering module -- String.
# sequenceName : Name of the rendered sequence -- String.
# elapsedTimeInSeconds : number of seconds used to render -- Float
def renderEnded(moduleName, sequenceName, elapsedTimeInSeconds):
   print "renderEnded - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   print "renderEnded - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
   pass


# Hook called when a sequence finishes playback (even if unsuccessful).
# sequenceName : Name of the rendered sequence -- String.
# fps : FPS -- Float
# debugInfo: Debugging Playback Information -- Dict
def  playbackEnded(sequenceName, fps, debugInfo):
    pass


# Hook called when the user changes the video preview device. The following
# values are read from the init.cfg VideoPreviewDevice keyword.
# description : Description of the video preview device -- String
#               (ex : "1920x1080@5994i_free")
# width : Width of the preview device -- Integer.
# height : Height of the preview device -- Integer.
# bitDepth : Bit depth of the preview device -- Integer.
# rateString : Rate of the preview device -- String.
#              (ex : "6000i")
# syncString : Sync source of the preview device -- String.
#              (ex : "freesync")
def previewWindowConfigChanged(description,width,height,bitDepth,
      rateString,syncString):
   pass


# Hook returning the custom ui actions to display to the user in the
# contextual menu.
#
#    Returns a tuple of group dictionaries.
#
#    A group dictionary defines a custom menu group where keys defines
#    the group.
#
#    Keys:
#
#    name: [String] 
#       Name of the action group that will be created in the menu.
#
#    actions: [String]
#       Tuple of action dictionary which menu items will be created
#       in the group.
#
#    An action dictionary of userData where the keys defines
#    the action
#
#    Keys:
#
#    name: [String] 
#       Name of the action that will be passed on customUIAction
#       callback.
#
#    caption: [String]
#       Caption of the menu item.
#
#    For example: 2 menu groups containing 1 custom action
#
#    def getCustomUIActions():
#
#        action1 = {}
#        action1[ "name" ] = "action1"
#        action1[ "caption" ] = "Action Number 1"
#
#        group1 = {}
#        group1[ "name" ] = "Custom Group 1"
#        group1[ "actions" ] = ( action1, )
#
#        action2 = {}
#        action2[ "name" ] = "action2"
#        action2[ "caption" ] = "Action Number 2"
#
#        group2 = {}
#        group2[ "name" ] = "Custom Group 2"
#        group2[ "actions" ] = ( action2, )
#
#        return ( group1, group2 )
#
#
def getCustomUIActions( ):

   action1 = {}
   action1[ "name" ] = "nimScanForVersions"
   action1[ "caption" ] = "Scan for Versions"

   action2 = {}
   action2[ "name" ] = "nimBuildOpenClipFromElements"
   action2[ "caption" ] = "Build OpenClip from Elements"

   action3 = {}
   action3[ "name" ] = "nimBuildOpenClipFromProject"
   action3[ "caption" ] = "Build OpenClip from Project"

   action4 = {}
   action4[ "name" ] = "nimChangeUser"
   action4[ "caption" ] = "Change User"

   group1 = {}
   group1[ "name" ] = "NIM Update OpenClips"
   group1[ "actions" ] = ( action1, action2, action3, )

   group2 = {}
   group2[ "name" ] = "NIM Settings"
   group2[ "actions" ] = ( action4, )

   return ( group1, group2, )

# Hook called when a custom action is triggered in the menu
#
# info [Dictionary] [Modifiable]
#    Information about the custom action,
#
#    Keys:
#
#    name: [String] 
#       Name of the action being triggered.
#
#    selection: [Tuple]
#       Tuple of wiretap ids.
#
# userData [Dictionary] [Modifiable]
#   Dictionary that is passed to getCustomUIActions.
#
def customUIAction( info, userData ):
   

   if info[ "name" ] == "nimScanForVersions" :
      print "nimScanForVersions"
      #print info["selection"]

      nimScanDlg = nimFlameExport.NimScanForVersionsDialog()
      nimScanDlg.show()
      if nimScanDlg.exec_() :
         nim_showID = nimScanDlg.nim_showID
         clipCount = nimScanDlg.clipCount
         clipFail = nimScanDlg.clipFail
 
         utf8 = QtCore.QTextCodec.codecForName("utf-8")
         QtCore.QTextCodec.setCodecForCStrings(utf8)
         title = "New Versions Found"
         msg = "New Versions Found: "+str(clipCount)
         if clipFail > 0 :
            msg += "\nFailed to Read Versions: "+str(clipFail)
            msg += "\nPlease try again"

         dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
         if dialog==QtGui.QMessageBox.Ok :
            userInput='OK'


   if info[ "name" ] == "nimBuildOpenClipFromElements" :
      print "nimBuildOpenClipFromElements"
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
         QtCore.QTextCodec.setCodecForCStrings(utf8)
         title = "New Versions Found"
         msg = "New Versions Found: "+str(clipCount)
         if clipFail > 0 :
            msg += "\nFailed to Read Versions: "+str(clipFail)
            msg += "\nPlease try again"
         dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
         if dialog==QtGui.QMessageBox.Ok :
            userInput='OK'


   if info[ "name" ] == "nimBuildOpenClipFromProject" :
      print "nimBuildOpenClipFromProject"
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
         QtCore.QTextCodec.setCodecForCStrings(utf8)
         title = "New Versions Found"
         msg = "New Versions Found: "+str(clipCount)
         if clipFail > 0 :
            msg += "\nFailed to Read Versions: "+str(clipFail)
            msg += "\nPlease try again"
         dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
         if dialog==QtGui.QMessageBox.Ok :
            userInput='OK'
      

   if info[ "name" ] == "nimChangeUser" :
      print "nimChangeUser triggered"
      #print info["selection"]

      import nim_core.nim_win as Win;
      Win.userInfo()
   pass


# Hook called when starting the application and when switching project
# This value will be used as default for the rename shotname dialog
#
# project: [String]
#    Usually called with current project.
#
# Ex: if project == "project_name":
#        return "<track>_<segment>_project"
#     return "<track>_<segment>_global"

def timelineDefaultShotName( project ):
   return ""
