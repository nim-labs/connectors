#!/usr/bin/env python
#******************************************************************************
#
# Filename: Nuke/Python/Startup/nim_hiero_connector/nimProcessorUI.py
# Version:  v0.7.3.150625
#
# Copyright (c) 2015 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

import itertools
import ui
import os
import hiero.core
import hiero.core.FnExporterBase as FnExporterBase

from PySide import QtGui, QtCore
from ui import IProcessorUI
from hiero.core.FnExporterBase import CompSourceInfo

#NIM
import os.path
import sys
import base64
import platform
import ntpath

import nim_core.nim_api as nimAPI
import nim_core.nim_prefs as nimPrefs
import nim_core.nim_file as nimFile
import nim_core.nim as nim

import nimHieroConnector
#END NIM

def isCompItemMissingRenders(compItem):
  """ Check if renders for a comp item are missing. """
  try:
    # Get the render info for the comp
    info = CompSourceInfo(compItem)
    startFrame = info.firstFrame
    endFrame = info.lastFrame

    # If the item is a TrackItem, search for missing files in its source range
    if isinstance(compItem, hiero.core.TrackItem):
      startFrame = int(compItem.sourceIn() + info.firstFrame)
      endFrame = int(compItem.sourceOut() + info.firstFrame)

    # Iterate over the frame range and check if any files are missing
    for frame in xrange(startFrame, endFrame):
      framePath = info.writePath % frame
      if not os.path.exists(framePath):
        return True
  except:
    pass

  return False


class NimProcessorUIBase(IProcessorUI):
  """NimProcessorUIBase is the base class from which all Processor UI components must derive.  Defines the UI structure followed
     by the specialised processor UIs. """

  def __init__(self, preset, itemTypes):
    IProcessorUI.__init__(self)

    self._preset = None
    self._exportTemplate = None
    self._exportStructureViewer = None
    self._contentElement = None
    self._contentScrollArea = None
    self._contentUI = None
    self._contentTabIndex = -1
    self._tabWidget = None
    self._editMode = IProcessorUI.ReadOnly
    self._itemTypes = itemTypes
    self._tags = []

    self.setPreset(preset)

    '''
    #######################################################
    # NIM VARS
    '''
    self.app=nimFile.get_app()
    self.prefs=nimPrefs.read()
    try:
      self.user=self.prefs['NIM_User']
      self.pref_job=self.prefs[self.app+'_Job']
      self.pref_show=self.prefs[self.app+'_Show']
      self.pref_server=self.prefs[self.app+'_ServerPath']
    except:
      #return False
      pass

    self.nim_OS = platform.system()

    self.nim_userID = nimAPI.get_userID(self.user)
    print "NIM: user=%s" % self.user
    print "NIM: userID=%s" % self.nim_userID
    print "NIM: default job=%s" % self.pref_job

    #Get NIM Jobs
    self.nim_jobID = None
    self.nim_jobs = nimAPI.get_jobs(self.nim_userID)
    if not self.nim_jobs :
      print "No Jobs Found"
      self.nim_jobs["None"]="0"
      
    #self.nim_shows = []
    self.nim_servers = {}
    
    self.nim_shows = {}
    self.nim_showDict = {}
    self.nim_showChooser = QtGui.QComboBox()
    self.nim_serverChooser = QtGui.QComboBox()

    self.nim_jobPaths = {}
    self.nim_showPaths = {}
    self.nim_showFolder = ''
    self.nim_serverOSPath = ''

    #Get NIM Element Types
    self.pref_elementType = ''
    self.element = ''
    self.elementID = None
    self.nim_elementTypes = []
    self.nim_elementTypesDict = {}
    self.nim_elementTypes = nimAPI.get_elementTypes()

    #Get NIM Task Types
    self.pref_taskType = ''
    self.task = ''
    self.taskID = None
    self.nim_taskTypes = []
    self.nim_taskTypesDict = {}
    self.nim_taskFolderDict = {}
    self.nim_taskTypes = nimAPI.get_tasks(app='NUKE', userType='all')

    self.nim_publishElementCheckbox = QtGui.QCheckBox()
    self.nim_publishElement = False

    self.nim_publishCompCheckbox = QtGui.QCheckBox()
    self.nim_publishComp = False

    self.loadingNimUI = False
    '''
    # END NIM VARS
    #######################################################
    '''


  def validate ( self, exportItems ):
    """Validate settings in UI. Return False for failure in order to abort export."""
    exportRoot = self._exportTemplate.exportRootPath()
    if exportRoot is None or len(exportRoot)<1:
      msgBox = QtGui.QMessageBox()
      msgBox.setText("The export path root is not set, please set a valid path.")
      msgBox.exec_()
      return False
    elif "{projectroot}" in exportRoot:
      project = self.projectFromSelection(exportItems)

      from hiero.ui import getProjectRootInteractive
      projectRoot = getProjectRootInteractive(project)
      if not projectRoot:
        return False

    # Check for offline track items
    if not self.checkOfflineMedia(exportItems):
      return False

    if not self.checkUnrenderedComps(exportItems):
      return False

    return True


  def isTranscodeExport(self):
    """ Check if there are transcode tasks in this export. """

    # To avoid importing the hiero.exporters module here, just check
    # for 'Transcode' in the preset class name.
    for (exportPath, preset) in self._exportTemplate.flatten():
      if "Transcode" in FnExporterBase.classBasename(type(preset)):
        return True
    return False


  def findCompItems(self, items):
    """ Search for comp clips and track items in a list of ItemWrappers. """
    for item in items:
      if item.clip():
        if CompSourceInfo(item.clip()).nkPath:
          yield item.clip()
      else:
        for trackItem in self.toTrackItems([item]):
          try:
            if CompSourceInfo(trackItem).nkPath:
              yield trackItem
          except:
            pass


  def checkUnrenderedComps(self, exportItems):
    """ Check for unrendered comps selected for export and ask the user what to do. """

    # Only do this check for transcodes
    if not self.isTranscodeExport():
      return True

    # Scan the items and find comps which haven't been rendered
    unrenderedNkSources = []
    for compItem in self.findCompItems(exportItems):
      if isCompItemMissingRenders(compItem):
        if isinstance(compItem, hiero.core.TrackItem):
          unrenderedNkSources.append( compItem.source().mediaSource() )
        elif isinstance(compItem, hiero.core.Clip):
          unrenderedNkSources.append( compItem.mediaSource() )

    continueExport = True
    renderComps = False

    # Show a message box and give the user the option to either render the comps or skip them
    if unrenderedNkSources:
      messageText = "Some Comp items have not been rendered.  Do you want to render them now, or skip them?"
      messageBox = QtGui.QMessageBox( QtGui.QMessageBox.Question, "Export", messageText, QtGui.QMessageBox.NoButton, hiero.ui.mainWindow() )
      cancelButton = messageBox.addButton( "Cancel export", QtGui.QMessageBox.RejectRole )
      messageBox.setDefaultButton( cancelButton )
      renderButton = messageBox.addButton("Render", QtGui.QMessageBox.YesRole)
      skipButton = messageBox.addButton("Skip", QtGui.QMessageBox.YesRole)
      messageBox.exec_()

      clickedButton = messageBox.clickedButton()
      if clickedButton == cancelButton:
        continueExport = False
      else:
        renderComps = (clickedButton == renderButton)

      if renderComps:
        self._preset.setCompsToRender(unrenderedNkSources)
      else:
        self._preset.setCompsToSkip(unrenderedNkSources)

    # Otherwise make sure the comps to render list is cleared
    else:
      self._preset.setCompsToRender([])

    return continueExport


  def projectFromSelection(self, items):
    # Return the project of the first item in the selection

    for item in items:
      if item.trackItem():
        return item.trackItem().project()
      elif item.sequence():
        return item.sequence().project()
      elif item.clip():
        return item.clip().project()

    return None


  def toTrackItems(self, items):
    # Filter out tracks which have been excluded in the preset.  This isn't a great solution
    # (we shouldn't really be doing the validation in this class at all), but it works for now.
    excludedTracksGUIDs = []
    if hasattr(self._preset, "_excludedTrackIDs"):
      excludedTracksGUIDs = self._preset._excludedTrackIDs

    for item in items:
      if item.trackItem():
        yield item.trackItem()
      elif item.sequence():
        for track in itertools.chain(item.sequence().videoTracks(), item.sequence().audioTracks()):
          if track.guid() not in excludedTracksGUIDs and track.isEnabled():
            for trackItem in track:
              yield trackItem


  def findOfflineMedia(self, exportItems):
    # Return a tuple containing a list of offline track items, and a list of online ones
    offline = []
    online = []
    for trackItem in self.toTrackItems(exportItems):
      if (not isinstance(trackItem, hiero.core.TrackItem)) or trackItem.source().mediaSource().isMediaPresent():
        online.append(trackItem)
      else:
        offline.append(trackItem)
    return (offline, online)


  def offlineMediaPrompt(self, messageText, messageDetails, hasOnline):
    # Ask the user how they want to proceed when trying to export offline media.
    # They will be given the option to skip or include offline media, or to cancel.
    # Return True if the export should proceed.
    messageBox = QtGui.QMessageBox( QtGui.QMessageBox.Question, "Export", messageText, QtGui.QMessageBox.NoButton, hiero.ui.mainWindow() )
    if messageDetails:
      messageBox.setDetailedText( messageDetails )
    noButton = messageBox.addButton( "Cancel export", QtGui.QMessageBox.RejectRole )
    messageBox.setDefaultButton( noButton )
    skipButton = None
    if hasOnline:
      skipButton = messageBox.addButton( "Skip offline", QtGui.QMessageBox.YesRole )
    includeButton = messageBox.addButton( "Export offline", QtGui.QMessageBox.YesRole )
    messageBox.exec_()
    if messageBox.clickedButton() == skipButton:
      self._preset.setSkipOffline( True )
      return True
    elif messageBox.clickedButton() == includeButton:
      self._preset.setSkipOffline( False )
      return True
    else:
      return False


  def checkOfflineMedia(self, exportItems):
    # Check for track items which has offline media and prompt the user if any are found
    offline, online = self.findOfflineMedia(exportItems)
    if offline:
      messageText = "Some items are offline.  Do you want to continue?"
      messageDetails = "\n".join( [offlineItem.name() + " (MediaOffline)" for offlineItem in offline ] )
      return self.offlineMediaPrompt(messageText, messageDetails, online)
    else:
      return True


  def findTagsForItems(self, exportItems):
    """ Find tags for the export items. """
    return FnExporterBase.tagsFromSelection(exportItems, includeChildren=True)


  def populateUI(self, widget, exportItems, editMode):
    """ Build the processor UI and add it to widget. """

    self._tags = self.findTagsForItems(exportItems)

    layout = QtGui.QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)

    if self._preset.readOnly():
      editMode = IProcessorUI.ReadOnly

    self._editMode = editMode


    '''
    #######################################################
    # NIM CONTROLS
    '''
    print "NIM: Loading UI"
    self.loadingNimUI = True

    print "NimHieroConnector.g_nim_jobID=",nimHieroConnector.g_nim_jobID
    print "NimHieroConnector.g_nim_serverID=",nimHieroConnector.g_nim_serverID
    print "NimHieroConnector.g_nim_showID=",nimHieroConnector.g_nim_showID
    print "NimHieroConnector.g_nim_elementTypeID=",nimHieroConnector.g_nim_elementTypeID

    nim_groupBox = QtGui.QGroupBox("NIM")
    nim_groupLayout = QtGui.QFormLayout()
    #nim_groupBox.setLayout(nim_groupLayout)

    # JOBS: List box for job selection
    nim_horizontalLayout1 = QtGui.QHBoxLayout()
    nim_horizontalLayout1.setSpacing(-1)
    nim_horizontalLayout1.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout1.setObjectName("nim_HorizontalLayout1")
    self.nimJobLabel = QtGui.QLabel()
    self.nimJobLabel.setFixedWidth(40)
    self.nimJobLabel.setText("Job:")
    nim_horizontalLayout1.addWidget(self.nimJobLabel)
    self.nim_jobChooser = QtGui.QComboBox()
    self.nim_jobChooser.setToolTip("Choose the job you wish to export shots to.")
    nim_horizontalLayout1.addWidget(self.nim_jobChooser)
    nim_horizontalLayout1.setStretch(1, 40)
    nim_groupLayout.setLayout(1, QtGui.QFormLayout.SpanningRole, nim_horizontalLayout1)

    # JOBS: List box for job selection
    '''
    self.nimJobLabel = QtGui.QLabel()
    self.nimJobLabel.setText("Job:")
    layout.addWidget(self.nimJobLabel)
    self.nim_jobChooser = QtGui.QComboBox()
    self.nim_jobChooser.setToolTip("Choose the job you wish to export shots to.")
    '''

    # JOBS: Add dictionary in ordered list
    jobIndex = 0
    jobIter = 0
    if len(self.nim_jobs)>0:
      for key, value in sorted(self.nim_jobs.items(), reverse=True):
        self.nim_jobChooser.addItem(key)
        if nimHieroConnector.g_nim_jobID == value:
          #print "Found matching jobID, job=", key
          self.pref_job = key
          jobIndex = jobIter
        jobIter += 1

      if self.pref_job != '':
        self.nim_jobChooser.setCurrentIndex(jobIndex)
    
    self.nim_jobChooser.currentIndexChanged.connect(self.nim_jobChanged)
    layout.addWidget(self.nim_jobChooser)
    self.nim_jobChanged() #trigger job changed to load choosers

    # SERVERS: List box for server selection
    nim_horizontalLayout2 = QtGui.QHBoxLayout()
    nim_horizontalLayout2.setSpacing(-1)
    nim_horizontalLayout2.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout2.setObjectName("nim_HorizontalLayout2")
    self.nimServerLabel = QtGui.QLabel()
    self.nimServerLabel.setFixedWidth(40)
    self.nimServerLabel.setText("Server:")
    nim_horizontalLayout2.addWidget(self.nimServerLabel)
    self.nim_serverChooser = QtGui.QComboBox()
    self.nim_serverChooser.setToolTip("Choose the server you wish to export shots to.")
    nim_horizontalLayout2.addWidget(self.nim_serverChooser)
    nim_horizontalLayout2.setStretch(1, 40)
    nim_groupLayout.setLayout(2, QtGui.QFormLayout.SpanningRole, nim_horizontalLayout2)
    '''
    self.nimServerLabel = QtGui.QLabel()
    self.nimServerLabel.setText("Server:")
    layout.addWidget(self.nimServerLabel)
    self.nim_serverChooser = QtGui.QComboBox()
    self.nim_serverChooser.setToolTip("Choose the server you wish to export shots to.")
    layout.addWidget(self.nim_serverChooser)
    '''

    # SERVERS: Add dictionary in ordered list
    serverIndex = 0
    serverIter=0
    if len(self.nim_servers)>0:
      for server in self.nim_servers:
        self.nim_serverDict[server['server']] = server['ID']
      
      for key, value in sorted(self.nim_serverDict.items(), reverse=False):
        self.nim_serverChooser.addItem(key)
        if nimHieroConnector.g_nim_serverID == value:
          self.pref_server = key
          serverIndex = serverIter
          #print "Found matching serverID, server=", key
          #print "serverIndex=",serverIndex

        serverIter +=1

      if self.pref_server != '':
        #print "self.pref_server=",self.pref_server
        self.nim_serverChooser.setCurrentIndex(serverIndex)

    self.nim_serverChooser.currentIndexChanged.connect(self.nim_serverChanged)
    self.nim_serverChanged()

    # SHOWS: List box for show selection
    nim_horizontalLayout3 = QtGui.QHBoxLayout()
    nim_horizontalLayout3.setSpacing(-1)
    nim_horizontalLayout3.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout3.setObjectName("nim_HorizontalLayout3")
    self.nimShowLabel = QtGui.QLabel()
    self.nimShowLabel.setFixedWidth(40)
    self.nimShowLabel.setText("Show:")
    nim_horizontalLayout3.addWidget(self.nimShowLabel)
    self.nim_showChooser = QtGui.QComboBox()
    self.nim_showChooser.setToolTip("Choose the show you wish to export shots to.")
    nim_horizontalLayout3.addWidget(self.nim_showChooser)
    nim_horizontalLayout3.setStretch(1, 40)
    nim_groupLayout.setLayout(3, QtGui.QFormLayout.SpanningRole, nim_horizontalLayout3)
    '''
    self.nimShowLabel = QtGui.QLabel()
    self.nimShowLabel.setText("Show:")
    layout.addWidget(self.nimShowLabel)
    self.nim_showChooser = QtGui.QComboBox()
    self.nim_showChooser.setToolTip("Choose the show you wish to export shots to.")
    layout.addWidget(self.nim_showChooser)
    '''

    # SHOWS: Add dictionary in ordered list
    showIndex = 0
    showIter = 0
    if len(self.nim_shows)>0:
      for show in self.nim_shows:
        self.nim_showDict[show['showname']] = show['ID']
      
      for key, value in sorted(self.nim_showDict.items(), reverse=False):
        self.nim_showChooser.addItem(key)
        if nimHieroConnector.g_nim_showID == value:
          #print "Found matching showID, show=", key
          self.pref_show == key
          showIndex = showIter
        showIter += 1

      if self.pref_show != '':
        self.nim_showChooser.setCurrentIndex(showIndex)

    self.nim_showChooser.currentIndexChanged.connect(self.nim_showChanged)
    self.nim_showChanged()

    nim_horizontalLayout6 = QtGui.QHBoxLayout()
    nim_horizontalLayout6.setSpacing(-1)
    nim_horizontalLayout6.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout6.setObjectName("nim_HorizontalLayout6")
    nim_dividerline1 = QtGui.QFrame()
    nim_dividerline1.setFrameShape(QtGui.QFrame.HLine)
    nim_dividerline1.setFrameShadow(QtGui.QFrame.Sunken)
    nim_horizontalLayout6.addWidget(nim_dividerline1)
    nim_horizontalLayout6.setStretch(1, 40)
    nim_groupLayout.setLayout(4, QtGui.QFormLayout.SpanningRole, nim_horizontalLayout6)

    # Publish NIM Elements Checkbox
    nim_horizontalLayout4 = QtGui.QHBoxLayout()
    nim_horizontalLayout4.setSpacing(-1)
    nim_horizontalLayout4.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout4.setObjectName("nim_HorizontalLayout4")
    
    self.nimPublishElementLabel = QtGui.QLabel()
    self.nimPublishElementLabel.setFixedWidth(260)
    self.nimPublishElementLabel.setText("Publish Transcoded Images as NIM Elements:")
    nim_horizontalLayout4.addWidget(self.nimPublishElementLabel)
    self.nim_publishElementCheckbox = QtGui.QCheckBox()
    self.nim_publishElementCheckbox.setToolTip("Choose to publish the elements to the associated NIM shots.")
    self.nim_publishElementCheckbox.stateChanged.connect(self.nim_publishElementChanged)
    nim_horizontalLayout4.addWidget(self.nim_publishElementCheckbox)

    if nimHieroConnector.g_nim_publishElement == True:
      self.nim_publishElementCheckbox.toggle()

    # Element Types: List box for element type selection
    self.nimElementTypeLabel = QtGui.QLabel()
    self.nimElementTypeLabel.setFixedWidth(90)
    self.nimElementTypeLabel.setText("Element Type:")
    nim_horizontalLayout4.addWidget(self.nimElementTypeLabel)
    self.nim_elementTypeChooser = QtGui.QComboBox()
    self.nim_elementTypeChooser.setToolTip("Choose the element type you wish to publish.")
    self.nim_elementTypeChooser.setFixedWidth(160)
    nim_horizontalLayout4.addWidget(self.nim_elementTypeChooser)
    nim_horizontalLayout4.setStretch(1, 40)
    nim_groupLayout.setLayout(6, QtGui.QFormLayout.SpanningRole, nim_horizontalLayout4)

    #Add dictionary in ordered list
    elemIndex = 0
    elemIter = 0
    if len(self.nim_elementTypes)>0:
      for element in self.nim_elementTypes:
        self.nim_elementTypesDict[element['name']] = element['ID']
      
      for key, value in sorted(self.nim_elementTypesDict.items(), reverse=False):
        self.nim_elementTypeChooser.addItem(key)
        if nimHieroConnector.g_nim_elementTypeID == value:
          #print "Found matching elementTypeID, elementType=", key
          self.pref_elementType = key
          elemIndex = elemIter
        elemIter += 1

      if self.pref_elementType != '':
        self.nim_elementTypeChooser.setCurrentIndex(elemIndex)

    self.nim_elementTypeChooser.currentIndexChanged.connect(self.nim_elementTypeChanged)
    self.nim_elementTypeChanged()


    # Publish NIM Comp Checkbox
    nim_horizontalLayout7 = QtGui.QHBoxLayout()
    nim_horizontalLayout7.setSpacing(-1)
    nim_horizontalLayout7.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout7.setObjectName("nim_HorizontalLayout7")
    self.nimPublishCompLabel = QtGui.QLabel()
    self.nimPublishCompLabel.setFixedWidth(260)
    self.nimPublishCompLabel.setText("Publish Nuke Project Files as NIM Files:")
    nim_horizontalLayout7.addWidget(self.nimPublishCompLabel)
    self.nim_publishCompCheckbox = QtGui.QCheckBox()
    self.nim_publishCompCheckbox.setToolTip("Choose to publish the nuke projects to the associated NIM shots.")
    self.nim_publishCompCheckbox.stateChanged.connect(self.nim_publishCompChanged)
    nim_horizontalLayout7.addWidget(self.nim_publishCompCheckbox)
    #nim_horizontalLayout7.setStretch(1, 40)
    #nim_groupLayout.setLayout(7, QtGui.QFormLayout.SpanningRole, nim_horizontalLayout7)

    if nimHieroConnector.g_nim_publishComp == True:
      self.nim_publishCompCheckbox.toggle()

    # Task Types: List box for element type selection
    self.nimTaskTypeLabel = QtGui.QLabel()
    self.nimTaskTypeLabel.setFixedWidth(90)
    self.nimTaskTypeLabel.setText("Task:")
    nim_horizontalLayout7.addWidget(self.nimTaskTypeLabel)
    self.nim_taskTypeChooser = QtGui.QComboBox()
    self.nim_taskTypeChooser.setToolTip("Choose the task you wish to assign to the exported nuke project files.")
    self.nim_taskTypeChooser.setFixedWidth(160)
    nim_horizontalLayout7.addWidget(self.nim_taskTypeChooser)
    
    nim_horizontalLayout7.setStretch(1, 40)
    nim_groupLayout.setLayout(7, QtGui.QFormLayout.SpanningRole, nim_horizontalLayout7)

    #Add dictionary in ordered list
    taskIndex = 0
    taskIter = 0
    if len(self.nim_taskTypes)>0:
      for task in self.nim_taskTypes:
        self.nim_taskTypesDict[task['name']] = task['ID']
        self.nim_taskFolderDict[task['ID']] = task['folder']
      for key, value in sorted(self.nim_taskTypesDict.items(), reverse=False):
        self.nim_taskTypeChooser.addItem(key)
        if nimHieroConnector.g_nim_expTaskTypeID == value:
          self.pref_taskType = key
          taskIndex = taskIter
        taskIter += 1

      if self.pref_taskType != '':
        self.nim_taskTypeChooser.setCurrentIndex(taskIndex)

    self.nim_taskTypeChooser.currentIndexChanged.connect(self.nim_taskTypeChanged)
    self.nim_taskTypeChanged()



    nim_groupBox.setLayout(nim_groupLayout)
    layout.addWidget(nim_groupBox)
    layout.addSpacing(5)
    
    self.loadingNimUI = False
    '''
    # END NIM CONTROLS
    #######################################################
    '''

    # The same enums are declared in 2 classes.  They should have the same values but to be sure, map between them
    editModeMap = { IProcessorUI.ReadOnly : ui.ExportStructureViewer.ReadOnly,
                    IProcessorUI.Limited : ui.ExportStructureViewer.Limited,
                    IProcessorUI.Full : ui.ExportStructureViewer.Full }

    structureViewerMode = editModeMap[editMode]

    self._exportStructureViewer = ui.ExportStructureViewer(self._exportTemplate, structureViewerMode)
    self._exportStructureViewer.destroyed.connect(self.onExportStructureViewerDestroyed)
    layout.addWidget(self._exportStructureViewer)

    self._exportStructureViewer.setItemTypes(self._itemTypes)
    self._preset.createResolver().addEntriesToExportStructureViewer(self._exportStructureViewer)
    self._exportStructureViewer.structureModified.connect(self.onExportStructureModified)
    self._exportStructureViewer.selectionChanged.connect(self.onExportStructureSelectionChanged)


    self._tabWidget = QtGui.QTabWidget()
    layout.addWidget(self._tabWidget)
    self._tabWidget.currentChanged.connect(self.onCurrentTabChanged)

    self._processorSettingsWidget = self.createProcessorSettingsWidget(exportItems)
    self._tabWidget.addTab(self._processorSettingsWidget, self.processorSettingsLabel())

    self._contentScrollArea = QtGui.QScrollArea()
    self._contentScrollArea.setFrameStyle( QtGui.QScrollArea.NoFrame )
    self._contentScrollArea.setWidgetResizable(True)
    self._contentTabIndex = self._tabWidget.addTab(self._contentScrollArea, "Content")


  def setPreset(self, preset):
    """ Set the export preset. """
    self._preset = preset
    oldTemplate = self._exportTemplate

    self._exportTemplate = hiero.core.ExportStructure2()
    self._exportTemplate.restore(self._preset.properties()["exportTemplate"])
    if self._preset.properties()["exportRoot"] != "None":
      self._exportTemplate.setExportRootPath(self._preset.properties()["exportRoot"])

    # Must replace the Export Structure viewer structure object before old template is destroyed
    if self._exportStructureViewer is not None:
      self._exportStructureViewer.setExportStructure(self._exportTemplate)

    for (exportPath, taskPreset) in self._exportTemplate.flatten():
      taskUI = hiero.ui.taskUIRegistry.getTaskUIForPreset(taskPreset)
      # Initialise each taskUI with preset
      # This is where callbacks are registered with the exportTemplate
      if taskUI is not None:
        # Bug 46032 - Make sure that the task preset shares the same project as its parent.
        # Since the taskUI might require information from the project.
        taskPreset.setProject(preset.project())
        taskUI.initialise(taskPreset, self._exportTemplate)


  def preset(self):
    """ Get the export preset. """
    return self._preset


  def setTaskContent(self, preset):
    """ Get the UI for a task preset and add it in the 'Content' tab. """

    # if selection is valid, grab preset
    if preset is not None:
      taskUI = hiero.ui.taskUIRegistry.getTaskUIForPreset(preset)
      # if UI is valid, set preset and add to 'contentlayout'
      if taskUI:
        taskUI.setPreset(preset)
        taskUI.setTags(self._tags)

        widget = QtGui.QGroupBox()
        widget.setTitle(taskUI.displayName())
        self._contentScrollArea.setWidget(widget)

        # Populate UI
        taskUI.populateUI(widget, self._exportTemplate)

        self._contentUI = taskUI

        if self._editMode == IProcessorUI.ReadOnly:
          widget.setEnabled(False)

        try:
          taskUI.propertiesChanged.connect(self.onExportStructureModified, type=QtCore.Qt.UniqueConnection)
        except:
          # Signal already connected.
          pass

        return

    self._contentScrollArea.setWidget( QtGui.QWidget() )


  def onExportStructureModified(self):
    """ Callback when the export structure is modified by the user. """

    self._preset.properties()["exportTemplate"] = self._exportTemplate.flatten()
    self._preset.properties()["exportRoot"] = self._exportTemplate.exportRootPath()
    if self._exportStructureViewer and self._contentElement is not None:
      self._exportStructureViewer.refreshContentField(self._contentElement)


  def onExportStructureSelectionChanged(self):
    """ Callback when the selection in the export structure viewer changes. """
    # Grab current selection
    element = self._exportStructureViewer.selection()
    if element is not None:
      self._contentElement = element
      self.setTaskContent(element.preset())

      # Block signals to prevent onCurrentTabChanged being called
      self._tabWidget.blockSignals(True)
      self._tabWidget.setCurrentIndex(self._contentTabIndex)
      self._tabWidget.blockSignals(False)


  def onExportStructureViewerDestroyed(self):
    """ Callback when the export structure viewer is destroyed.  Qt will delete it while we still
        have a reference, so reset to None when the destroyed() signal is emitted. """
    self._exportStructureViewer = None


  def createProcessorSettingsWidget(self, exportItems):
    """ Create the UI for processor-specific settings.  To be reimplemented by subclasses. """
    raise NotImplementedError()


  def processorSettingsLabel(self):
    """ Get the label which is put on the tab for processor-specific settings.  To be reimplemented by subclasses. """
    raise NotImplementedError()


  def savePreset( self ):
    """ Save the export template to the preset. """
    self._preset.properties()["exportTemplate"] = self._exportTemplate.flatten()
    self._preset.properties()["exportRoot"] = self._exportTemplate.exportRootPath()


  def onCurrentTabChanged(self, index):
    """ Callback when the tab selection changes. """
    # If the user selects the 'Content' tab, select the first task in the export structure viewer
    # if there wasn't already a selection.
    currentSelection = self._exportStructureViewer.selection()
    if (index == self._contentTabIndex) and (currentSelection is None):
      self._exportStructureViewer.selectFirstFile()


  def createVersionWidget(self):
    """ Create a widget for selecting the version number for export. """
    widget = QtGui.QWidget()
    layout = QtGui.QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    widget.setLayout(layout)

    # Version custom versionSpinBox widget - allows user to specify padding
    versionToolTip = "Set the version number for files/scripts which include the {version} token in the path.\nThis box sets the version number string (#) in the form: v#, e.g. 01 > v01.\nUse the +/- to control padding e.g. v01 / v0001."

    versionLayout = QtGui.QHBoxLayout()

    versionLabel = QtGui.QLabel("Version token number")
    layout.addWidget(versionLabel)

    versionSpinBox = hiero.ui.VersionWidget()
    versionSpinBox.setToolTip(versionToolTip)
    versionSpinBox.setValue(self._preset.properties()["versionIndex"])
    versionSpinBox.setPadding(self._preset.properties()["versionPadding"])
    versionSpinBox.valueChanged.connect(self.onVersionIndexChanged)
    versionSpinBox.paddingChanged.connect(self.onVersionPaddingChanged)
    layout.addWidget(versionSpinBox)
    layout.addStretch()

    return widget


  def onVersionIndexChanged(self, value):
    """ Callback when the version index changes. """
    self._preset.properties()["versionIndex"] = int(value)


  def onVersionPaddingChanged(self, padding):
    """ Callback when the version padding changes. """
    self._preset.properties()["versionPadding"] = int(padding)


  def skipOffline(self):
    return self._preset.skipOffline()


  '''
  #######################################################
  # NIM FUNCTIONS
  '''

  def nim_getServerOSPath(self):
    return self.nim_serverOSPath


  def nim_getJobRootPath(self):
    if len(self.nim_jobPaths)>0:
      return self.nim_jobPaths[0]['root']
    else:
      return


  def nim_getShowRootPath(self):
    if len(self.nim_showPaths)>0:
      return self.nim_showPaths[0]['root']
    else:
      return


  def nim_getShotRootPath(self, ID=None):
    return


  def nim_getShotPlatesPath(self, ID=None):
    return


  def nim_getShotRenderPath(self, ID=None):
    return


  def nim_getShotCompPath(self, ID=None):
    return


  def nim_jobChanged(self):
    '''Action when job is selected'''
    #print "JOB CHANGED"
    job = self.nim_jobChooser.currentText()
    self.nim_jobID = self.nim_jobs[job]
    self.nim_jobPaths = nimAPI.get_paths('job', self.nim_jobID)
    
    ##set jobID global
    nimHieroConnector.g_nim_jobID = self.nim_jobID

    #print "NIM: jobPaths"
    #print self.nim_jobPaths
    self.nim_updateServer()
    self.nim_updateShow()

    
  def nim_updateServer(self):
    self.nim_servers = {}
    self.nim_servers = nimAPI.get_jobServers(self.nim_jobID)
    #print self.nim_servers

    self.nim_serverDict = {}
    try:
      self.nim_serverChooser.clear()
      if self.nim_serverChooser:
        if len(self.nim_servers)>0:  
          for server in self.nim_servers:
            self.nim_serverDict[server['server']] = server['ID']
          for key, value in sorted(self.nim_serverDict.items(), reverse=False):
            self.nim_serverChooser.addItem(key)
    except:
      pass


  def nim_serverChanged(self):
    '''Action when job is selected'''
    #print "SERVER CHANGED"
    serverName = self.nim_serverChooser.currentText()
    if serverName:
      print "NIM: server=%s" % serverName
      
      serverID = self.nim_serverDict[serverName]
      nimHieroConnector.g_nim_serverID = serverID
      #print "Setting serverID=",serverID

      serverInfo = nimAPI.get_serverOSPath(serverID, self.nim_OS)
      if serverInfo:
        if len(serverInfo)>0:
          self.nim_serverOSPath = serverInfo[0]['serverOSPath']
          print "NIM: serverOSPath=%s" % self.nim_serverOSPath
          #set nim global
          nimHieroConnector.g_nim_serverOSPath = self.nim_serverOSPath
        else:
          print "NIM: No Server Found"
      else:
        print "NIM: No Data Returned"


  def nim_updateShow(self):
    self.nim_shows = {}
    self.nim_shows = nimAPI.get_shows(self.nim_jobID)
    #print self.nim_shows

    self.nim_showDict = {}
    try:
      self.nim_showChooser.clear()
      if self.nim_showChooser:
        if len(self.nim_shows)>0:  
          for show in self.nim_shows:
            self.nim_showDict[show['showname']] = show['ID']
          for key, value in sorted(self.nim_showDict.items(), reverse=False):
            self.nim_showChooser.addItem(key)
    except:
      pass


  def nim_showChanged(self):
    '''Action when job is selected'''
    #print "SHOW CHANGED"
    showname = self.nim_showChooser.currentText()
    if showname:
      print "NIM: show=%s" % showname
      
      showID = self.nim_showDict[showname]
      
      ##set showID global
      #global g_nim_showID
      nimHieroConnector.g_nim_showID = showID

      self.nim_showPaths = nimAPI.get_paths('show', showID)
      if self.nim_showPaths:
        if len(self.nim_showPaths)>0:
          #print "NIM: showPaths=", self.nim_showPaths
          self.nim_showFolder = self.nim_showPaths['root']
          #global g_nim_showFolder
          nimHieroConnector.g_nim_showFolder = self.nim_showFolder
        else:
          print "NIM: No Show Paths Found"
      else:
        print "NIM: No Data Returned"


  def nim_elementTypeChanged(self):
    '''Action when element type is selected'''
    self.element = self.nim_elementTypeChooser.currentText()
    self.elementID = self.nim_elementTypesDict[self.element]
    nimHieroConnector.g_nim_element = self.nim_elementTypeChooser.currentText()
    nimHieroConnector.g_nim_elementTypeID = self.nim_elementTypesDict[self.element]

  def nim_taskTypeChanged(self):
    '''Action when task type is selected'''
    self.task = self.nim_taskTypeChooser.currentText()
    self.taskID = self.nim_taskTypesDict[self.task]
    taskFolder = self.nim_taskFolderDict[self.taskID]
    nimHieroConnector.g_nim_expTask = self.nim_taskTypeChooser.currentText()
    nimHieroConnector.g_nim_expTaskTypeID = self.nim_taskTypesDict[self.task]
    nimHieroConnector.g_nim_expTaskFolder = taskFolder


  def nim_publishElementChanged(self, state):
    '''Action when publish element checkbox is selected'''
    #global g_nim_publishElement
    if state == QtCore.Qt.Checked:
      nimHieroConnector.g_nim_publishElement = True
    else:
      nimHieroConnector.g_nim_publishElement = False


  def nim_publishCompChanged(self, state):
    '''Action when publish element checkbox is selected'''
    #global g_nim_publishComp
    if state == QtCore.Qt.Checked:
      nimHieroConnector.g_nim_publishComp = True
    else:
      nimHieroConnector.g_nim_publishComp = False


  '''
  # END NIM FUNCTIONS
  #######################################################
  '''
