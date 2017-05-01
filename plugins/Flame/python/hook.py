#!/bin/env python
#******************************************************************************
#
# Filename: hook.py
#
# Copyright (c) 2008 Autodesk Canada Co.
# All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

from PySide import QtGui, QtCore

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
   #return ()
   action1 = {}
   action1[ "name" ] = "nimExportEdit"
   action1[ "caption" ] = "Export to Edits"

   action2 = {}
   action2[ "name" ] = "nimExportDailies"
   action2[ "caption" ] = "Export to Dailies"

   action3 = {}
   action3[ "name" ] = "nimScanForVersions"
   action3[ "caption" ] = "Scan for Versions"

   action4 = {}
   action4[ "name" ] = "nimBuildOpenClipFromElements"
   action4[ "caption" ] = "Build OpenClip from Elements"

   action5 = {}
   action5[ "name" ] = "nimChangeUser"
   action5[ "caption" ] = "Change User"

   group1 = {}
   group1[ "name" ] = "NIM"
   group1[ "actions" ] = ( action1, action2, action3, action4, action5, )

   # action2 = {}
   # action2[ "name" ] = "action2"
   # action2[ "caption" ] = "Action Number 2"

   # group2 = {}
   # group2[ "name" ] = "Custom Group 2"
   # group2[ "actions" ] = ( action2, )

   #return ( group1, group2 )
   return ( group1, )

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
   if info[ "name" ] == "nimExportEdit" :
      print "nimExportDaily triggered"
      print info["selection"]

      utf8 = QtCore.QTextCodec.codecForName("utf-8")
      QtCore.QTextCodec.setCodecForCStrings(utf8)


      import sys, traceback
      '''
      try:
         import xml.etree.cElementTree as ET
      except ImportError:
         import xml.etree.ElementTree as ET
      try:
         print "XML loaded"
         nimFlamePresetPath = '/Users/andrew/Documents/NIM Labs/Repository/nim_connectors/plugins/Flame/presets/sequence_publish/NimExportSequence.xml'
         preset_xml = ET.parse(nimFlamePresetPath)
         preset_root = preset_xml.getroot()
         for elem in preset_root.iterfind('createOpenClip/batchSetup/namePattern'):
            print elem.text
         print "XML done"
      except Exception, e :
         print 'XML Failed'
         print '    %s' % traceback.print_exc()
      '''

      version = "Version: %s.%s" % (sys.version_info[0], sys.version_info[0])

      title = "Export to Edits"
      msg = "Export to Edits: "+version
      dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
      if dialog==QtGui.QMessageBox.Ok :
         userInput='OK'

   if info[ "name" ] == "nimExportDailies" :
      print "nimExportDaily triggered"
      print info["selection"]

      utf8 = QtCore.QTextCodec.codecForName("utf-8")
      QtCore.QTextCodec.setCodecForCStrings(utf8)

      title = "Export to Dailies"
      msg = "Export to Dailies"
      dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
      if dialog==QtGui.QMessageBox.Ok :
         userInput='OK'

   if info[ "name" ] == "nimScanForVersions" :
      print "nimScanForVersions triggered"
      print info["selection"]

      utf8 = QtCore.QTextCodec.codecForName("utf-8")
      QtCore.QTextCodec.setCodecForCStrings(utf8)

      title = "Scan for Versions"
      msg = "Scan for Versions"
      dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
      if dialog==QtGui.QMessageBox.Ok :
         userInput='OK'

   if info[ "name" ] == "nimBuildOpenClipFromElements" :
      print "nimBuildOpenClipFromElements triggered"
      print info["selection"]

      utf8 = QtCore.QTextCodec.codecForName("utf-8")
      QtCore.QTextCodec.setCodecForCStrings(utf8)

      title = "Build OpenClip from Elements"
      msg = "Build OpenClip from Elements"
      dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
      if dialog==QtGui.QMessageBox.Ok :
         userInput='OK'

   if info[ "name" ] == "nimChangeUser" :
      print "nimChangeUser triggered"
      print info["selection"]

      utf8 = QtCore.QTextCodec.codecForName("utf-8")
      QtCore.QTextCodec.setCodecForCStrings(utf8)

      title = "Change User"
      msg = "Change User"
      dialog=QtGui.QMessageBox.information( None, title, msg, QtGui.QMessageBox.Ok)
      if dialog==QtGui.QMessageBox.Ok :
         userInput='OK'
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
