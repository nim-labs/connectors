#******************************************************************************
#
# Filename: Hiero/nim_hiero_connector/nimShotProcessor.py
# Version:  v0.7.3.150625
#
# Copyright (c) 2015 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


# Copyright (c) 2011 The Foundry Visionmongers Ltd.  All Rights Reserved.

import os.path
import sys
import base64
import platform
import ntpath

import PySide.QtCore
import PySide.QtGui
import time
import hiero.core
import hiero.ui
import hiero.core.FnExporterBase as FnExporterBase
import itertools

from hiero.ui.FnTagFilterWidget import TagFilterWidget

import nim_core.nim_api as nimAPI
import nim_core.nim_prefs as nimPrefs
import nim_core.nim_file as nimFile
import nim_core.nim as nim

import nimHieroConnector



class NimShotProcessor(hiero.core.ProcessorBase, hiero.ui.ProcessorUIBase, PySide.QtCore.QObject):

  def __init__(self, preset, submission=None, synchronous=False):
    """Initialize"""
    hiero.core.ProcessorBase.__init__(self, preset, submission, synchronous)
    hiero.ui.ProcessorUIBase.__init__(self)

    self._contentBox = None
    self._contentui = None
    self._contentElement = None
    self._contentlayout = None
    self._exportStructureViewer = None
    self._exportTemplate = None
    self._editMode = NimShotProcessor.ReadOnly

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

    self.nim_userID = nimAPI.get_userID()
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
    self.nim_showChooser = PySide.QtGui.QComboBox()
    self.nim_serverChooser = PySide.QtGui.QComboBox()

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

    self.nim_publishElementCheckbox = PySide.QtGui.QCheckBox()
    self.nim_publishElement = False

    self.loadingNimUI = False
    '''
    # END NIM VARS
    #######################################################
    '''

  def preset (self):
    return self._preset

  def setPreset ( self, preset ):
    self._preset = preset
    oldTemplate = self._exportTemplate
    self._exportTemplate = hiero.core.ExportStructure2()
    self._exportTemplate.restore(self._preset.properties()["exportTemplate"])
    if self._preset.properties()["exportRoot"] != "None":
      self._exportTemplate.setExportRootPath(self._preset.properties()["exportRoot"])

    # Must replace the Export Structure viewer structure object before old template is destroyed
    if self._exportStructureViewer is not None:
      self._exportStructureViewer.setExportStructure(self._exportTemplate)

    for (exportPath, preset) in self._exportTemplate.flatten():
      taskUI = hiero.ui.taskUIRegistry.getTaskUIForPreset(preset)
      # Initialise each taskUI with preset
      # This is where callbacks are registered with the exportTemplate
      if taskUI is not None:
        taskUI.initialise(preset, self._exportTemplate)

  def displayName(self):
    return "NIM: Process as Shots"
  def toolTip(self):
    return "NIM: Process as Shots generates output according to the NIM project structure on a per shot basis."
  
  def _tagsSelectionChanged(self, include_subset, exclude_subset):
  
    self._preset.properties()["includeTags"] = [ tag.name() for tag in include_subset ]    
    self._preset.properties()["excludeTags"] = [ tag.name() for tag in exclude_subset ]
        
  def trackSelectionChanged(self, item):
    selectedtrack = None
    excludedTrackNames = self._preset.nonPersistentProperties()["excludedTracks"]
    excludedTracks = []
    for sequence in self._sequences:
      excludedTracks.extend( [track for track in sequence if track.name() in excludedTrackNames] )
      if not selectedtrack:
        for track in sequence:
          if track.guid() == item.data():
            selectedtrack = track
            break

    excludedTrackIDs = self._preset._excludedTrackIDs

    if item.checkState() == PySide.QtCore.Qt.Checked:
      if selectedtrack in excludedTracks:
        excludedTracks.remove(selectedtrack)
        excludedTrackNames.remove(selectedtrack.name())
      if selectedtrack.guid() in excludedTrackIDs:
        excludedTrackIDs.remove(selectedtrack.guid())

    elif item.checkState() == PySide.QtCore.Qt.Unchecked:
      if selectedtrack not in excludedTracks:
        excludedTracks.append(selectedtrack)
        excludedTrackNames.append(selectedtrack.name())
      if selectedtrack.guid() not in excludedTrackIDs:
        excludedTrackIDs.append(selectedtrack.guid())

  def toggleAllTracks(self):
    for row in range(self.trackListModel.rowCount()):
      if self.trackListModel.item(row).checkState() == PySide.QtCore.Qt.Checked:
        anySelected = True
        break
      else:
        anySelected = False

    if anySelected:
      for row in range(self.trackListModel.rowCount()):
        self.trackListModel.itemFromIndex(self.trackListModel.index(row, 0)).setCheckState(PySide.QtCore.Qt.Unchecked)
    else:
      for row in range(self.trackListModel.rowCount()):
        # Get the current track object by grabbing the data (track guid) stored on the checkbox
        for sequence in self._sequences:
          currentTrack = [track for track in sequence if track.guid() in [self.trackListModel.itemFromIndex(self.trackListModel.index(row, 0)).data()]][0]
          if currentTrack.isEnabled() and len(currentTrack.items()) > 0:
            self.trackListModel.itemFromIndex(self.trackListModel.index(row, 0)).setCheckState(PySide.QtCore.Qt.Checked)

  def offlineTrackItems(self, track):
    offlineMedia = []
    for trackitem in track:
      if not trackitem.isMediaPresent():
        try:
            sourcepath = trackitem.source().mediaSource().fileinfos()[0].filename()
        except:
            sourcepath = "Unknown Source"
        offlineMedia.append(' : '.join([trackitem.name(), sourcepath]))
    return offlineMedia

  def getIconForTrack(self, track):
    trackIcon = None
    if isinstance(track,hiero.core.AudioTrack):
        trackIcon = PySide.QtGui.QIcon("icons:AudioOnly.png")
    elif isinstance(track,hiero.core.VideoTrack):
        trackIcon = PySide.QtGui.QIcon("icons:VideoOnly.png")
    return trackIcon

  def versionIndexChanged(self, value):
    self._preset.properties()["versionIndex"] = int(value)

  def versionPaddingChanged(self, value):
    self._preset.properties()["versionPadding"] = int(value)

  def cutLengthToggled (self, checked):
    self._preset.properties()["cutLength"] = checked
    self._cutCheckBox.setEnabled(checked)
    self._cutHandles.setEnabled(checked)
    self._retimeCheckBox.setEnabled(checked)

  def cutHandlesChanged (self, value):
    self._preset.properties()["cutHandles"] = value

  def cutUseHandlesChanged (self, checked):
    self._preset.properties()["cutUseHandles"] = checked == PySide.QtCore.Qt.Checked

  def retimesChanged(self, checked):
    self._preset.properties()["includeRetimes"] = checked == PySide.QtCore.Qt.Checked

  def startFrameSourceChanged(self, index):
    value = self._startFrameSource.currentText()
    if str(value) == "Source":
      self._startFrameIndex.setEnabled(False)
    if str(value) == "Custom":
      self._startFrameIndex.setEnabled(True)
    self._preset.properties()["startFrameSource"] = str(value)

  def startFrameIndexChanged(self, value):
    self._preset.properties()["startFrameIndex"] = int(value)


  def exportStructureModified(self):
    self._preset.properties()["exportTemplate"] = self._exportTemplate.flatten()
    self._preset.properties()["exportRoot"] = self._exportTemplate.exportRootPath()
    if self._exportStructureViewer and self._contentElement is not None:
      self._exportStructureViewer.refreshContentField(self._contentElement)
    #self.exportStructureSelectionChanged()

  def selectRenderTaskContent(self):
    for (exportPath, preset) in self._exportTemplate.flatten():
      if isinstance(preset, hiero.core.RenderTaskPreset):
        self.setTaskContent(preset)

  def exportStructureSelectionChanged(self):
    # Grab current selection
    element = self._exportStructureViewer.selection()
    if element is not None:
      self._contentElement = element
      self.setTaskContent(element.preset())

  def setTaskContent(self, preset):

    # if selection is valid, grab preset
    if preset is not None:
      taskUI = hiero.ui.taskUIRegistry.getTaskUIForPreset(preset)
      # if UI is valid, set preset and add to 'contentlayout'
      if taskUI:
        taskUI.setPreset(preset)
        taskUI.setTags(self._tags)

        self._contentWidget = PySide.QtGui.QWidget()
        self._contentScrollArea.setWidget(self._contentWidget)

        # Populate UI
        taskUI.populateUI(self._contentWidget, self._exportTemplate)
        
        self._contentui = taskUI
        self._contentBox.setTitle(taskUI.displayName())
        if self._editMode == NimShotProcessor.ReadOnly:
          self._contentWidget.setEnabled(False)
        if self._editMode != NimShotProcessor.Limited:
          # In limited mode the visibility is controlled by a disclosure button.
          self._contentBox.setVisible(True)
          
        try:
          taskUI.propertiesChanged.connect(self.exportStructureModified, type=PySide.QtCore.Qt.UniqueConnection)
        except:
          # Signal already connected.
          pass

        return

    self._contentBox.setVisible(False)

  def _buildTagsData (self, exportItems):
    # Collect tags from selection
    self._tags = []
    self._tags = FnExporterBase.tagsFromSelection(exportItems, includeChildren=True)
    
    filters = ["Transcode", "Nuke Project File"]
    # Filter Transcode/NukeProjectFile tags out
    
    def reverse_contains(item, filters):
      for filter in filters:
        if filter in item:
          return False
      return True
  
    uniquelist = set()
    def uniquetest(tag, type):
      uniquestr = str(tag.name()) + str(type)
      if uniquestr in uniquelist:
        return False
      uniquelist.add(uniquestr)
      return True
    
    self._tags = [(tag, objecttype) for tag, objecttype in self._tags if tag.visible() and reverse_contains(tag.name(), filters) and uniquetest(tag,objecttype)]

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

  def nim_publishElementChanged(self, state):
    '''Action when publish element checkbox is selected'''
    #global g_nim_publishElement
    if state == PySide.QtCore.Qt.Checked:
      nimHieroConnector.g_nim_publishElement = True
    else:
      nimHieroConnector.g_nim_publishElement = False

  '''
  # END NIM FUNCTIONS
  #######################################################
  '''

  def populateUI(self, widget, exportItems, editMode=None):
    layout = PySide.QtGui.QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)

    # Optional parameter cannot reference Class members
    if editMode == None:
      self._editMode = NimShotProcessor.Full
    else:
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

    nim_groupBox = PySide.QtGui.QGroupBox("NIM")
    nim_groupLayout = PySide.QtGui.QFormLayout()
    #nim_groupBox.setLayout(nim_groupLayout)

    # JOBS: List box for job selection
    nim_horizontalLayout1 = PySide.QtGui.QHBoxLayout()
    nim_horizontalLayout1.setSpacing(-1)
    nim_horizontalLayout1.setSizeConstraint(PySide.QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout1.setObjectName("nim_HorizontalLayout1")
    self.nimJobLabel = PySide.QtGui.QLabel()
    self.nimJobLabel.setFixedWidth(40)
    self.nimJobLabel.setText("Job:")
    nim_horizontalLayout1.addWidget(self.nimJobLabel)
    self.nim_jobChooser = PySide.QtGui.QComboBox()
    self.nim_jobChooser.setToolTip("Choose the job you wish to export shots to.")
    nim_horizontalLayout1.addWidget(self.nim_jobChooser)
    nim_horizontalLayout1.setStretch(1, 40)
    nim_groupLayout.setLayout(1, PySide.QtGui.QFormLayout.SpanningRole, nim_horizontalLayout1)

    # JOBS: List box for job selection
    '''
    self.nimJobLabel = PySide.QtGui.QLabel()
    self.nimJobLabel.setText("Job:")
    layout.addWidget(self.nimJobLabel)
    self.nim_jobChooser = PySide.QtGui.QComboBox()
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
    nim_horizontalLayout2 = PySide.QtGui.QHBoxLayout()
    nim_horizontalLayout2.setSpacing(-1)
    nim_horizontalLayout2.setSizeConstraint(PySide.QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout2.setObjectName("nim_HorizontalLayout2")
    self.nimServerLabel = PySide.QtGui.QLabel()
    self.nimServerLabel.setFixedWidth(40)
    self.nimServerLabel.setText("Server:")
    nim_horizontalLayout2.addWidget(self.nimServerLabel)
    self.nim_serverChooser = PySide.QtGui.QComboBox()
    self.nim_serverChooser.setToolTip("Choose the server you wish to export shots to.")
    nim_horizontalLayout2.addWidget(self.nim_serverChooser)
    nim_horizontalLayout2.setStretch(1, 40)
    nim_groupLayout.setLayout(2, PySide.QtGui.QFormLayout.SpanningRole, nim_horizontalLayout2)
    '''
    self.nimServerLabel = PySide.QtGui.QLabel()
    self.nimServerLabel.setText("Server:")
    layout.addWidget(self.nimServerLabel)
    self.nim_serverChooser = PySide.QtGui.QComboBox()
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
    nim_horizontalLayout3 = PySide.QtGui.QHBoxLayout()
    nim_horizontalLayout3.setSpacing(-1)
    nim_horizontalLayout3.setSizeConstraint(PySide.QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout3.setObjectName("nim_HorizontalLayout3")
    self.nimShowLabel = PySide.QtGui.QLabel()
    self.nimShowLabel.setFixedWidth(40)
    self.nimShowLabel.setText("Show:")
    nim_horizontalLayout3.addWidget(self.nimShowLabel)
    self.nim_showChooser = PySide.QtGui.QComboBox()
    self.nim_showChooser.setToolTip("Choose the show you wish to export shots to.")
    nim_horizontalLayout3.addWidget(self.nim_showChooser)
    nim_horizontalLayout3.setStretch(1, 40)
    nim_groupLayout.setLayout(3, PySide.QtGui.QFormLayout.SpanningRole, nim_horizontalLayout3)
    '''
    self.nimShowLabel = PySide.QtGui.QLabel()
    self.nimShowLabel.setText("Show:")
    layout.addWidget(self.nimShowLabel)
    self.nim_showChooser = PySide.QtGui.QComboBox()
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

    nim_horizontalLayout6 = PySide.QtGui.QHBoxLayout()
    nim_horizontalLayout6.setSpacing(-1)
    nim_horizontalLayout6.setSizeConstraint(PySide.QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout6.setObjectName("nim_HorizontalLayout6")
    nim_dividerline1 = PySide.QtGui.QFrame()
    nim_dividerline1.setFrameShape(PySide.QtGui.QFrame.HLine)
    nim_dividerline1.setFrameShadow(PySide.QtGui.QFrame.Sunken)
    nim_horizontalLayout6.addWidget(nim_dividerline1)
    nim_horizontalLayout6.setStretch(1, 40)
    nim_groupLayout.setLayout(4, PySide.QtGui.QFormLayout.SpanningRole, nim_horizontalLayout6)

    # Publish NIM Elements Checkbox
    nim_horizontalLayout4 = PySide.QtGui.QHBoxLayout()
    nim_horizontalLayout4.setSpacing(-1)
    nim_horizontalLayout4.setSizeConstraint(PySide.QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout4.setObjectName("nim_HorizontalLayout4")
    self.nimPublishElementLabel = PySide.QtGui.QLabel()
    self.nimPublishElementLabel.setFixedWidth(110)
    self.nimPublishElementLabel.setText("Publish NIM Elements:")
    nim_horizontalLayout4.addWidget(self.nimPublishElementLabel)
    self.nim_publishElementCheckbox = PySide.QtGui.QCheckBox()
    self.nim_publishElementCheckbox.setToolTip("Choose to publish the elements to the associated NIM shots.")
    self.nim_publishElementCheckbox.stateChanged.connect(self.nim_publishElementChanged)
    nim_horizontalLayout4.addWidget(self.nim_publishElementCheckbox)
    nim_horizontalLayout4.setStretch(1, 40)
    nim_groupLayout.setLayout(5, PySide.QtGui.QFormLayout.SpanningRole, nim_horizontalLayout4)
    '''
    self.nimPublishElementLabel = PySide.QtGui.QLabel()
    self.nimPublishElementLabel.setText("Publish NIM Elements:")
    layout.addWidget(self.nimPublishElementLabel)
    self.nim_publishElementCheckbox = PySide.QtGui.QCheckBox()
    self.nim_publishElementCheckbox.stateChanged.connect(self.nim_publishElementChanged)
    layout.addWidget(self.nim_publishElementCheckbox)
    '''
    if nimHieroConnector.g_nim_publishElement == True:
      self.nim_publishElementCheckbox.toggle()

    # Element Types: List box for element type selection
    '''
    self.nimElementTypeLabel = PySide.QtGui.QLabel()
    self.nimElementTypeLabel.setText("Element Types:")
    layout.addWidget(self.nimElementTypeLabel)
    self.nim_elementTypeChooser = PySide.QtGui.QComboBox()
    self.nim_elementTypeChooser.setToolTip("Choose the elementType you wish to create a track from.")
    layout.addWidget(self.nim_elementTypeChooser)
    '''
    nim_horizontalLayout5 = PySide.QtGui.QHBoxLayout()
    nim_horizontalLayout5.setSpacing(-1)
    nim_horizontalLayout5.setSizeConstraint(PySide.QtGui.QLayout.SetDefaultConstraint)
    nim_horizontalLayout5.setObjectName("nim_HorizontalLayout5")
    self.nimElementTypeLabel = PySide.QtGui.QLabel()
    self.nimElementTypeLabel.setFixedWidth(110)
    self.nimElementTypeLabel.setText("Element Types:")
    nim_horizontalLayout5.addWidget(self.nimElementTypeLabel)
    self.nim_elementTypeChooser = PySide.QtGui.QComboBox()
    self.nim_elementTypeChooser.setToolTip("Choose the elementType you wish to create a track from.")
    nim_horizontalLayout5.addWidget(self.nim_elementTypeChooser)
    nim_horizontalLayout5.setStretch(1, 40)
    nim_groupLayout.setLayout(6, PySide.QtGui.QFormLayout.SpanningRole, nim_horizontalLayout5)

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


    nim_groupBox.setLayout(nim_groupLayout)
    layout.addWidget(nim_groupBox)
    layout.addSpacing(5)
    
    self.loadingNimUI = False
    '''
    # END NIM CONTROLS
    #######################################################
    '''

    # Build Tags data from selection
    self._buildTagsData(exportItems)

    structureViewerMode = hiero.ui.ExportStructureViewer.Full
    if self._editMode == NimShotProcessor.Limited:
      structureViewerMode = hiero.ui.ExportStructureViewer.Limited
    elif self._preset.readOnly():
      self._editMode = NimShotProcessor.ReadOnly
      structureViewerMode = hiero.ui.ExportStructureViewer.ReadOnly

    exportStructureViewer = hiero.ui.ExportStructureViewer(self._exportTemplate, structureViewerMode)
    project = self.projectFromSelection(exportItems)
    if project is not None:
      exportStructureViewer.setProject(project)

    self._preset.createResolver().addEntriesToExportStructureViewer(exportStructureViewer)
    exportStructureViewer.structureModified.connect(self.exportStructureModified)
    self._exportStructureViewer = exportStructureViewer

    if self._editMode != NimShotProcessor.Limited:
      exportStructureViewer.selectionChanged.connect(self.exportStructureSelectionChanged)

    if self._editMode == NimShotProcessor.Limited:
      layout.addWidget(PySide.QtGui.QLabel("Project Root:"))
      layout.addWidget(self._exportStructureViewer.filenameField())

      groupBox = PySide.QtGui.QGroupBox("Local Nuke Roundtrip")
      layout.addWidget( groupBox )
      layout = PySide.QtGui.QVBoxLayout( groupBox )

      self._structureDisclosureButton = hiero.ui.DisclosureButton()
      self._structureDisclosureButton.setText("Shot Structure")
      self._structureDisclosureButton.stateChanged.connect(self._structureDisclosureButton.showOrHideWidgets)
      self._structureDisclosureButton.addWidget(self._exportStructureViewer)
      layout.addWidget(self._structureDisclosureButton)

    exportStructureViewer.setItemTypes(hiero.core.TaskPresetBase.kTrackItem)
    layout.addWidget(exportStructureViewer)
    layout.setStretchFactor( exportStructureViewer, 20 )

    layout.addSpacing(5)

    self._contentBox = PySide.QtGui.QGroupBox("Preset Properties")
    self._contentBox.setLayout(PySide.QtGui.QVBoxLayout())
    self._contentScrollArea = PySide.QtGui.QScrollArea()
    self._contentScrollArea.setFrameStyle( PySide.QtGui.QScrollArea.NoFrame )
    self._contentScrollArea.setWidgetResizable(True)
    self._contentWidget = PySide.QtGui.QWidget()
    self._contentScrollArea.setWidget(self._contentWidget)
    self._contentBox.layout().addWidget(self._contentScrollArea)


    if self._editMode == NimShotProcessor.Limited:
      self._codecDisclosureButton = hiero.ui.DisclosureButton()
      self._codecDisclosureButton.setText("Write Node Settings")
      self._codecDisclosureButton.stateChanged.connect(self._codecDisclosureButton.showOrHideWidgets)
      self._codecDisclosureButton.addWidget(self._contentBox)
      layout.addWidget(self._codecDisclosureButton)

      self.selectRenderTaskContent()
    elif self._editMode == NimShotProcessor.ReadOnly:
      self._contentWidget.setEnabled(False)

    self._contentBox.setVisible(False)
    layout.addWidget(self._contentBox)

    # Horizontal layout for bottom half of dialog
    hLayout = PySide.QtGui.QHBoxLayout()
    layout.addLayout(hLayout)

    radioBox = PySide.QtGui.QGroupBox("Handles")

    # In readonly mode disable the contents of this group box
    if self._editMode == NimShotProcessor.ReadOnly:
      radioBox.setEnabled(False)
  
    clipLengthToolTip = "Select this to export all available frames of the Clip, as displayed on the Clip's BinItem."
    cutLengthToolTip = """Select this to export frames from the cut length of the shot on the timeline.\nNote: Selecting Cut Length allows you to add handles to each clip, up to the\nmaximum available source clip length."""
    handlesToolTip = "The number of frame handles to export at the head and tail of a shot."
    retimeToolTip = "Selecting this will apply frame retiming to any shots that have been retimed."
    startFrameToolTip = "Set how clip Start Frames are derived using the dropdown menu:\n-Source : use the source clip's start frame.\n-Custom : specify a start frame for all clips"
    

    radioBox.setMinimumHeight(150)
    radioBox.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Preferred)
    radioLayout = PySide.QtGui.QVBoxLayout()
        
    # Clip Length Radio Button
    radioClip = PySide.QtGui.QRadioButton("Clip Length")
    radioClip.setToolTip(clipLengthToolTip)
    radioLayout.addWidget(radioClip)
        
    # Cut Length Radio Button
    radioCut =  PySide.QtGui.QRadioButton("Cut Length")
    radioCut.setToolTip(cutLengthToolTip)
    radioCut.toggled.connect(self.cutLengthToggled)
    radioLayout.addWidget(radioCut)

    # Handles Checkbox and layout
    cutLayout = PySide.QtGui.QHBoxLayout()
    cutLayout.addSpacing(20)
    self._cutCheckBox = PySide.QtGui.QCheckBox("Include")
    self._cutCheckBox.setToolTip(handlesToolTip)
    self._cutCheckBox.stateChanged.connect(self.cutUseHandlesChanged)
    cutLayout.addWidget(self._cutCheckBox)
        
    # Handles Spinbox
    self._cutHandles = PySide.QtGui.QSpinBox()
    self._cutHandles.setMaximum(10000)
    self._cutHandles.setMaximumWidth(60)
    self._cutHandles.setToolTip(handlesToolTip)
    cutLayout.addWidget(self._cutHandles)
    cutLayout.addWidget(PySide.QtGui.QLabel("frames"))
    self._cutHandles.setMinimum(0)

    self._cutHandles.valueChanged.connect(self.cutHandlesChanged)

    cutLayout.addStretch(1)
    radioLayout.addLayout(cutLayout)

     # Options for applying (or ignoring) retimes
    retimeLayout = PySide.QtGui.QHBoxLayout()
    self._retimeCheckBox = PySide.QtGui.QCheckBox("Apply Retimes")
    self._retimeCheckBox.stateChanged.connect(self.retimesChanged)
    self._retimeCheckBox.setToolTip(retimeToolTip)
    retimeLayout.addSpacing(20)
    retimeLayout.addWidget(self._retimeCheckBox)
    retimeLayout.addStretch(1)
    radioLayout.addLayout(retimeLayout)

    # Startframe layout
    startFrameLayout = PySide.QtGui.QHBoxLayout()
    self._startFrameSource = PySide.QtGui.QComboBox()
    self._startFrameSource.setToolTip(startFrameToolTip)
        
    startFrameSourceItems = ("Source", "Custom")
    for index, item in zip(range(0,len(startFrameSourceItems)), startFrameSourceItems):
      self._startFrameSource.addItem(item)
      if item == str(self._preset.properties()["startFrameSource"]):
        self._startFrameSource.setCurrentIndex(index)

    # Custom Startframe line edit, enabled only if 'Custom' start frame source selected
    self._startFrameIndex = PySide.QtGui.QLineEdit()
    self._startFrameIndex.setValidator(PySide.QtGui.QIntValidator())
    self._startFrameIndex.setText(str(self._preset.properties()["startFrameIndex"]))

    startFrameLayout.addWidget(PySide.QtGui.QLabel("Start Frame"))
    startFrameLayout.addWidget(self._startFrameSource)
    startFrameLayout.addWidget(self._startFrameIndex)
    startFrameLayout.addStretch(1)

    self._startFrameSource.currentIndexChanged.connect(self.startFrameSourceChanged)
    self._startFrameIndex.textChanged.connect(self.startFrameIndexChanged)
    self.startFrameSourceChanged(0)
    radioLayout.addLayout(startFrameLayout)

    radioLayout.addStretch(1)
    radioBox.setLayout(radioLayout)
    hLayout.addWidget(radioBox)

    # Restore State - Cut / Clip length
    if self._preset.properties()["cutLength"]:
      radioCut.setChecked(True)
      self.cutLengthToggled(True)
    else:
      radioClip.setChecked(True)
      self.cutLengthToggled(False)

    # Restore State - Handles
    if self._preset.properties()["cutUseHandles"]:
      self._cutCheckBox.setCheckState(PySide.QtCore.Qt.Checked)
    self._cutHandles.setValue(int(self._preset.properties()["cutHandles"]))

    # Restore State - include retimes
    if self._preset.properties()["includeRetimes"]:
      self._retimeCheckBox.setCheckState(PySide.QtCore.Qt.Checked)

    # Track Selection only visible in Full ui mode.
    if self._editMode != NimShotProcessor.Limited:
      
      groupBox = PySide.QtGui.QGroupBox("Tracks")
      groupBox.setMinimumHeight(150)
      groupBox.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Preferred)
      groupLayout = PySide.QtGui.QFormLayout()
      groupBox.setLayout(groupLayout)
      
      versionToolTip = "Set the version number for files/scripts which include the {version} token in the path.\nThis box sets the version number string (#) in the form: v#, e.g. 01 > v01.\nUse the +/- to control padding e.g. v01 / v0001."

      # Version custom spinbox widget - allows user to specify padding
      spinbox = hiero.ui.VersionWidget()
      spinbox.setToolTip(versionToolTip)
      spinbox.setValue(self._preset.properties()["versionIndex"])
      spinbox.setPadding(self._preset.properties()["versionPadding"])
      spinbox.valueChanged.connect(self.versionIndexChanged)
      spinbox.paddingChanged.connect(self.versionPaddingChanged)
      groupLayout.addRow("Version:", spinbox)

      class KeyPressRedirect(PySide.QtCore.QObject):
        def eventFilter(self, obj, event):
          # Grab the space key event and use it to toggle multiple selections
          if event.type() == PySide.QtCore.QEvent.KeyPress and event.key() == PySide.QtCore.Qt.Key(PySide.QtCore.Qt.Key_Space):
            current = obj.currentIndex().model().itemFromIndex(obj.currentIndex())
            if current.checkState() == PySide.QtCore.Qt.Checked:
              current.setCheckState(PySide.QtCore.Qt.Unchecked)
            else:
              current.setCheckState(PySide.QtCore.Qt.Checked)
            for index in obj.selectedIndexes():
              selectedItem = index.model().itemFromIndex(index)
              if selectedItem.checkState() == PySide.QtCore.Qt.Checked:
                selectedItem.setCheckState(PySide.QtCore.Qt.Unchecked)
              else:
                selectedItem.setCheckState(PySide.QtCore.Qt.Checked)
            return PySide.QtCore.QObject.eventFilter(self, obj, event)
          else:
            # If not the space key then back to standard event processing
            return PySide.QtCore.QObject.eventFilter(self, obj, event)

      # Build list of tracks
      tracks = []
      self._sequences = set()
      for item in exportItems:
        if item.sequence():
          self._sequences.add( item.sequence() )
          for track in reversed(item.sequence().videoTracks()):
            if track not in tracks:
              tracks.append(track)
          for track in reversed(item.sequence().audioTracks()):
            if track not in tracks:
              tracks.append(track)
      
      trackListToolTip = "Enabled/Disable tracks you wish to export from the Sequence"

      # List box for track selection
      self.trackListModel = PySide.QtGui.QStandardItemModel()
      trackListView = PySide.QtGui.QListView()
      trackListView.setToolTip(trackListToolTip)
      keyPressRedirect = KeyPressRedirect(self)
      trackListView.installEventFilter(keyPressRedirect)
      trackListView.setSelectionBehavior(PySide.QtGui.QAbstractItemView.SelectItems)
      trackListView.setSelectionMode(PySide.QtGui.QAbstractItemView.ExtendedSelection)
      trackListView.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Maximum)
      trackListView.setModel(self.trackListModel)

      # We build the excluded tracks list from the track names saved in the preset
      # Then build a GUID list that will deal with duplicate track names
      excludedTrackNames = self._preset.nonPersistentProperties()["excludedTracks"]
      excludedTracks = []
      for sequence in self._sequences:
        excludedTracks.extend( [track for track in itertools.chain(sequence.videoTracks(), sequence.audioTracks()) if track.name() in excludedTrackNames ] )
      excludedTrackIDs = self._preset._excludedTrackIDs
      excludedTrackIDs = self._preset._excludedTrackIDs

      for track in tracks:
        item = PySide.QtGui.QStandardItem(track.name())
        item.setData(track.guid())
        item.setIcon(self.getIconForTrack(track))

        # If a track contains offline items we change the track icon to show a warning
        # and then change the tooltip to show a quick list of offline items
        offlineItems = self.offlineTrackItems(track)
        if offlineItems:
          if isinstance(track, hiero.core.AudioTrack):
            item.setIcon(PySide.QtGui.QIcon("icons:AudioOnlyWarning.png"))
          if isinstance(track, hiero.core.VideoTrack):
            item.setIcon(PySide.QtGui.QIcon("icons:VideoOnlyWarning.png"))
          item.setText(item.text() + "  ( Media Offline )")
          item.setToolTip("Offline Items will be ignored:\n" + '\n'.join(offlineItems))

        # If tracks are disabled or empty we disable the checkbox and change
        # the tooltip to inform the user why they are disabled
        if not track.isEnabled():
          item.setToolTip("Track is Disabled")
          if track not in excludedTracks:
            excludedTracks.append(track)
            excludedTrackNames.append(track.name())
          if track.guid() not in excludedTrackIDs:
            excludedTrackIDs.append(track.guid())

        if len(track.items()) == 0:
          item.setToolTip("Track is Empty")
          if track not in excludedTracks:
            excludedTracks.append(track)
            excludedTrackNames.append(track.name())
          if track.guid() not in excludedTrackIDs:
            excludedTrackIDs.append(track.guid())

        if track in excludedTracks:
          item.setCheckState(PySide.QtCore.Qt.Unchecked)
          if not track.isEnabled() or len(track.items()) == 0:
            item.setEnabled(False)
          else:
            item.setEnabled(True)
        else:
          item.setCheckState(PySide.QtCore.Qt.Checked)
          item.setEnabled(True)


        item.setCheckable(True)
        item.setEditable(False)
        self.trackListModel.appendRow(item)
        self.trackSelectionChanged(item)

      if self._editMode == NimShotProcessor.ReadOnly:
        trackListView.setEnabled(False)

      self.trackListModel.itemChanged.connect(self.trackSelectionChanged)

      groupLayout.addRow("Tracks For Export:", trackListView)
      self.toggleAll = PySide.QtGui.QPushButton("Select/Deselect All Tracks")
      self.toggleAll.setToolTip("Selects or Deselects All Tracks")
      groupLayout.addRow("", self.toggleAll)
      self.toggleAll.clicked.connect(self.toggleAllTracks)
      
      include_tags = [tag for tag, objecttype in self._tags if tag.name() in self._preset.properties()["includeTags"]]
      exclude_tags = [tag for tag, objecttype in self._tags if tag.name() in self._preset.properties()["excludeTags"]]
      
      tagsWidget = TagFilterWidget([tag for tag, objecttype in self._tags if objecttype in (hiero.core.TrackItem, )], include_tags, exclude_tags)
      tagsWidget.setToolTip("Filter shot selection based on Shot Tags.\n+ Only include shots with these tags.\n- Exclude any shots with these tags.")
      tagsWidget.tagSelectionChanged.connect(self._tagsSelectionChanged)

      groupLayout.addRow("Tag Filter:", tagsWidget)

      hLayout.addWidget(groupBox)
  

  def savePreset ( self ):
    self._preset.properties()["exportTemplate"] = self._exportTemplate.flatten()
    self._preset.properties()["exportRoot"] = self._exportTemplate.exportRootPath()


  def validateSelection(self,exportItems):
    """Validate if any items in the selection are suitable for processing by this processor"""

    invalidItems = []
    # Look for selected items which arent of the correct type
    for item in exportItems:
      if not item.sequence() and not item.trackItem():
        invalidItems.append(item)

    return len(invalidItems) < len(exportItems)


  def validate ( self, exportItems ):
    """Validate settings in UI. Return False for failure in order to abort export."""
    if not hiero.ui.ProcessorUIBase.validate(self, exportItems):
      return False

    invalidItems = []
    # Look for selected items which arent of the correct type
    for item in exportItems:
      if not item.sequence() and not item.trackItem():
        invalidItems.append(item.item().name() + " <span style='color: #CC0000'>(Not a Sequence)</span>")
    # Found invalid items
    if invalidItems:
      # Show warning
      msgBox = PySide.QtGui.QMessageBox()
      msgBox.setTextFormat(PySide.QtCore.Qt.RichText)
      result = msgBox.information(None, "Export", "The following items will be ignored by this export:<br/>%s" % str("<br/>".join(invalidItems)), PySide.QtGui.QMessageBox.Ok | PySide.QtGui.QMessageBox.Cancel)
      # Continue if user clicks OK
      return result == PySide.QtGui.QMessageBox.Ok

    # Do any NimShotProcessor-specific validation here...
    return True


  def startProcessing(self, exportItems):
    hiero.core.log.debug( "NimShotProcessor::startProcessing(" + str(exportItems) + ")" )

    sequences = []
    selectedTrackItems = set()
    ignoredTrackItems = set()
    excludedTracks = []
    
    # Build Tags data from selection
    self._buildTagsData(exportItems)
    
    # Filter the include/exclude tags incase the previous tag selection is not included in the current selection
    included_tag_names = [ tag.name() for tag, objectType in self._tags if tag.name() in self._preset.properties()["includeTags"] ]
    excluded_tag_names = [ tag.name() for tag, objectType in self._tags if tag.name() in self._preset.properties()["excludeTags"] ]

    # This flag controls whether items which havent been explicitly included in the export, 
    # should be removed from the cloned sequence. This primarily affects the collate functionality in nuke script generation.
    exclusiveClone = False


    if exportItems[0].trackItem():
      sequences.append( exportItems[0].trackItem().parent().parent() )
      for item in exportItems:
        trackItem = item.trackItem()
        selectedTrackItems.add( trackItem )
        if item.ignore():
          ignoredTrackItems.add( trackItem )
    else:
      sequences = [ item.sequence() for item in exportItems ]
      
    if ignoredTrackItems:
      # A set of track items have been explicitly marked as ignored. 
      # This track items are to be included in the clone, but not exported.
      # Thus any shot which isnt in the selected list, should be excluded from the clone.
      exclusiveClone = True

    for sequence in sequences:
      excludedTracks.extend( [track for track in sequence if track.guid() in self._preset._excludedTrackIDs] )
      
    localtime = time.localtime(time.time())

    path = self._exportTemplate.exportRootPath()
    versionIndex = self._preset.properties()["versionIndex"]
    versionPadding = self._preset.properties()["versionPadding"]
    retime = self._preset.properties()["includeRetimes"]

    version = "v%s" % format(versionIndex, "0%id" % int(versionPadding))

    cutHandles = None
    startFrame = None

    if self._preset.properties()["startFrameSource"] == "Custom":
      startFrame = self._preset.properties()["startFrameIndex"]

    # If we are exporting the shot using the cut length (rather than the (shared) clip length)
    if self._preset.properties()["cutLength"]:
      # Either use the specified number of handles or zero
      if self._preset.properties()["cutUseHandles"]:
        cutHandles = int(self._preset.properties()["cutHandles"])
      else:
        cutHandles = 0


    # Create a resolver from the preset (specific to this type of processor)
    resolver = self._preset.createResolver()

    self._submission.setFormatDescription( self._preset.name() )

    exportTrackItems = []

    clonedSequences = []

    project = None

    for sequence in sequences:
      sequenceClone = sequence.clone()
      clonedSequences.append( sequenceClone )
      self._tagClonedSequence(sequence, sequenceClone)

      # The export items should all come from the same project
      if not project:
        project = sequence.project()

      # For each video track
      for track, trackClone in zip(sequence.videoTracks(), sequenceClone.videoTracks()) + zip(sequence.audioTracks(), sequenceClone.audioTracks()):

        # Unlock cloned track so that items may be removed
        trackClone.setLocked(False)

        if track in excludedTracks or not track.isEnabled():
          # remove unselected track from cloned sequence
          sequenceClone.removeTrack(trackClone)
          continue

        # For each track item on track
        for trackitem, trackitemClone in zip(track, trackClone):

          # If we're processing the whole sequence, or this shot has been selected
          if not selectedTrackItems or trackitem in selectedTrackItems:

            if trackitem in ignoredTrackItems:
              hiero.core.log.debug( "%s marked as ignore, skipping. Selection : %s" % (str(trackitemClone), str(exportTrackItems)) )
              continue
              
            # Check tags for excluded tags
            excludedTags = [tag for tag in trackitem.tags() if tag.name() in excluded_tag_names]
            includedTags = [tag for tag in trackitem.tags() if tag.name() in included_tag_names]

            if included_tag_names:
              # If not included, or explictly excluded
              if not includedTags or excludedTags:
                hiero.core.log.debug( "%s does not contain include tag %s, skipping." % (str(trackitemClone), str(included_tag_names)) )
                ignoredTrackItems.add(trackitem)
                continue
              else:
                hiero.core.log.debug( "%s has include tag %s." % (str(trackitemClone), str(included_tag_names)) )
              
            elif excludedTags:
              hiero.core.log.debug( "%s contains excluded tag %s, skipping." % (str(trackitemClone), str(excluded_tag_names)) )
              ignoredTrackItems.add(trackitem)
              continue  

            if trackitem.isMediaPresent() or not self.skipOffline():

              exportTrackItems.append((trackitem, trackitemClone))  

            else:
              hiero.core.log.debug( "%s is offline. Removing." % str(trackitem) )
              trackClone.removeItem(trackitemClone)
          else:
            # Either remove the track item entirely, or mark it as ignored, so that no tasks are spawned to export it.
            if exclusiveClone:
              hiero.core.log.debug( "%s is not selected. Removing." % str(trackitem) )
              trackClone.removeItem(trackitemClone)
            else:
              hiero.core.log.debug( "%s is not selected. Ignoring." % str(trackitem) )
              ignoredTrackItems.add(trackitem)

    for trackitem, trackitemClone in exportTrackItems:
      
      if trackitem in ignoredTrackItems:
       continue
      
      taskGroup = hiero.core.TaskGroup()
      taskGroup.setTaskDescription( trackitem.name() )

      ''' ****************** NIM START UPDATE TRACKITEM ****************** '''
      # TODO: Need to check if job is online... if not raise warning before exporting plates *********
      #       *If forcing to be online in NIM before exporting plates then paths will always resolve

      print "exporting trackItem: %s" % trackitem.name()

      #Test for video track
      exportTrackItem = False
      trackItem_mediaType = trackitem.mediaType()
      if trackItem_mediaType == hiero.core.TrackItem.MediaType.kVideo:
        print "Processing Video TrackItem"
        exportTrackItem = True

      #SKIP IF NOT VIDEO TRACK ITEM
      if exportTrackItem:
        nim_shotID = None
        nim_shotPaths = {}
        nim_platesPath = 'PLATES'
        updateThumbnail = True

        #global g_nim_showID
        nim_showID = nimHieroConnector.g_nim_showID
        print 'NIM: showID=%s' % nim_showID

        name = trackitem.name()

        nimConnect = nimHieroConnector.NimHieroConnector()
        nim_tag = nimConnect.getNimTag(trackitem)

        if nim_tag != False:
          #print "NIM: Tag Found"
          #print         nim_tag

          #update existing shot in NIM
          nim_shotID = nim_tag.metadata().value("tag.shotID")
          print 'NIM: shotID=%s' % nim_shotID

          success = nimConnect.updateTrackItem(nim_showID, trackitem)
          if success:
            print "NIM: Successfully updated trackitem %s in NIM" % name
            if updateThumbnail:
              success = nimConnect.updateShotIcon(trackitem)
              if success == False:
                print 'NIM: Failed to upload icon'
          else:
            print "NIM: Failed to update trackitem %s in NIM" % name

        else:
          #NO TAG found so create new shot in NIM... if shot exists with same name in NIM, link to this trackitem
          print 'NIM: Tag Not Found  Exporting as new trackitem'
          nim_shotID = nimConnect.exportTrackItem(nim_showID, trackitem)
          if nim_shotID == False:
            print 'NIM: Failed to export trackitem %s' % name
          else:
            if updateThumbnail:
              success = nimConnect.updateShotIcon(trackitem)
              if success == False:
                print 'NIM: Failed to upload icon for trackitem %s' % name

        ''' GET UPDATED NIM TAG AND COPY TO CLONE '''
        nim_tag = nimConnect.getNimTag(trackitem)
        if nim_tag != False:
          print 'NIM: Copying nim_tag to clone'
          trackitemClone.addTag(nim_tag)
        else:
          print 'NIM: Could not copy nim_tag to clone.. tag not found'


        ''' ****************** NIM END UPDATE TRACKITEM ****************** '''

      # If processor is flagged as Synchronous, flag tasks too
      if self._synchronous:
        self._submission.setSynchronous()

      # For each entry in the shot template
      for (exportPath, preset) in self._exportTemplate.flatten():
        # Build TaskData seed
        taskData = hiero.core.TaskData(preset, trackitemClone, path, exportPath, version, self._exportTemplate,
          project=project, cutHandles=cutHandles, retime=retime, startFrame=startFrame, resolver=resolver, submission=self._submission, skipOffline=self.skipOffline())

        # Spawn task
        task = hiero.core.taskRegistry.createTaskFromPreset(preset, taskData)

        # Add task to export queue
        if task and task.hasValidItem():

          # Give the task an opportunity to modify the original (not the clone) track item
          if not task.error():
            task.updateItem(trackitem, localtime)

          taskGroup.addChild(task)
          hiero.core.log.debug( "Added to Queue " + trackitem.name() )

          ''' ****************** NIM START PUBLISH ELEMENT ****************** '''
          resolvedFullPath = os.path.join(resolver.resolve(task, path),resolver.resolve(task, exportPath))
          trackitem_clip = trackitem.source()

          '''
          print "NIM:   resolved fulPath=", resolvedFullPath
          print "NIM:   path=",path
          print "NIM:   exportPath=",exportPath
          print "NIM:   version=",version
          print "NIM:   cutHandles=",cutHandles
          print "NIM:   retime=",retime
          print "NIM:   startFrame=",startFrame
          print "       trackItem:"
          print "       trackitem.name=", trackitem.name()
          print "       trackitem.duration=", trackitem.duration()
          print "       trackitem.eventNumber=", trackitem.eventNumber()
          print "       trackitem.handleInLength=", trackitem.handleInLength()
          print "       trackitem.handleInTime=", trackitem.handleInTime()
          print "       trackitem.handleOutLength=", trackitem.handleOutLength()
          print "       trackitem.handleOutTime=", trackitem.handleOutTime()
          print "       trackitem.playbackSpeed=", trackitem.playbackSpeed()
          print "       trackitem.timelineIn=", trackitem.timelineIn()
          print "       trackitem.timelineOut=", trackitem.timelineOut()
          print "       trackitem.sourceIn=", trackitem.sourceIn()
          print "       trackitem.sourceOut=", trackitem.sourceOut()
          print "       clip:"
          print "       clip.sourceIn=", trackitem_clip.sourceIn()
          print "       clip.sourceOut=", trackitem_clip.sourceOut()
          '''

          element_startFrame = trackitem_clip.sourceIn() + (trackitem.sourceIn() - cutHandles)
          element_endFrame =  trackitem_clip.sourceIn() + (trackitem.sourceOut() + cutHandles)
          element_filePath = ntpath.dirname(resolvedFullPath)
          element_fileName = ntpath.basename(resolvedFullPath)

          #global g_nim_publishElement
          #global g_nim_element
          #global g_nim_elementTypeID

          print "nimHieroConnector.g_nim_publishElement=",nimHieroConnector.g_nim_publishElement
          print "nimHieroConnector.g_nim_element=",nimHieroConnector.g_nim_element
          print "nimHieroConnector.g_nim_elementTypeID=",nimHieroConnector.g_nim_elementTypeID

          if nimHieroConnector.g_nim_publishElement == True:
            print "NIM: Publish Element"
            print "     name=", trackitem.name()
            print "     type=", nimHieroConnector.g_nim_element
            print "     filePath=", element_filePath
            print "     fileName=", element_fileName
            print "     startFrame=", element_startFrame 
            print "     endFrame=", element_endFrame
            print "     cutHandles=", cutHandles
            
            element_result = nimAPI.add_element( parent='shot', parentID=nim_shotID, typeID=nimHieroConnector.g_nim_elementTypeID, \
                                                  path=element_filePath, name=element_fileName, startFrame=element_startFrame, endFrame=element_endFrame, \
                                                  handles=cutHandles, isPublished=nimHieroConnector.g_nim_publishElement )

          ''' ****************** NIM END PUBLISH ELEMENT ****************** '''
      
      # Dont add empty groups
      if len(taskGroup.children()) > 0:
        self._submission.addChild( taskGroup )
            
    # If processor is flagged as Synchronous, flag tasks too
    if self._synchronous:
      self._submission.setSynchronous()

    if self._submission.children():
    
      # Detect any duplicates
      self.processTaskPreQueue()

      self._submission.addToQueue()
      
      
class NimShotProcessorPreset(hiero.core.ProcessorPreset):
  def __init__(self, name, properties):
    hiero.core.ProcessorPreset.__init__(self, NimShotProcessor, name)

    # setup defaults
    self._excludedTrackIDs = [ ]
    self.nonPersistentProperties()["excludedTracks"] = []
    self.properties()["excludeTags"] = []
    self.properties()["includeTags"] = []
    self.properties()["versionIndex"] = 1
    self.properties()["versionPadding"] = 2
    self.properties()["exportTemplate"] = ( )
    self.properties()["exportRoot"] = "{projectroot}"
    self.properties()["cutHandles"] = 12
    self.properties()["cutUseHandles"] = False
    self.properties()["cutLength"] = False
    self.properties()["includeRetimes"] = False
    self.properties()["startFrameIndex"] = 1001
    self.properties()["startFrameSource"] = "Source"

    self.properties().update(properties)

    # This remaps the project root if os path remapping has been set up in the preferences
    self.properties()["exportRoot"] = hiero.core.remapPath (self.properties()["exportRoot"])


  def addCustomResolveEntries(self, resolver):
    """addDefaultResolveEntries(self, resolver)
    Create resolve entries for default resolve tokens shared by all task types.
    @param resolver : ResolveTable object"""

    resolver.addResolver("{filename}", "Filename of the media being processed", lambda keyword, task: task.fileName())
    resolver.addResolver("{filebase}", "Filename base part of the media being processed", lambda keyword, task: task.filebase())
    resolver.addResolver("{filehead}", "Source Filename not including frame padding or extension", lambda keyword, task: task.filehead())
    resolver.addResolver("{filepadding}", "Source Filename padding for formatting frame indices", lambda keyword, task: task.filepadding())
    resolver.addResolver("{fileext}", "Filename extension part of the media being processed", lambda keyword, task: task.fileext())
    resolver.addResolver("{clip}", "Name of the clip used in the shot being processed", lambda keyword, task: task.clipName())
    resolver.addResolver("{shot}", "Name of the shot being processed", lambda keyword, task: task.shotName())
    resolver.addResolver("{track}", "Name of the track being processed", lambda keyword, task: task.trackName())
    resolver.addResolver("{sequence}", "Name of the sequence being processed", lambda keyword, task: task.sequenceName())
    resolver.addResolver("{event}", "EDL event of the track item being processed", lambda keyword, task: task.editId())
    
    #NIM Keywords
    resolver.addResolver("{nim_server_path}", "NIM Job Server Path", lambda keyword, task: serverOSPath(task))
    #resolver.addResolver("{nim_job_root}", "NIM Job Root Directory", lambda keyword: self.nim_getJobRootPath())
    resolver.addResolver("{nim_show_root}", "NIM Show Root Directory", lambda keyword, task: showRootPath(task))
    #resolver.addResolver("{nim_shot_root}", "NIM Shot Root Directory", lambda keyword, task: task.editId())
    resolver.addResolver("{nim_shot_plates}", "NIM Shot Plates Directory", lambda keyword, task: shotPlatesPath(task))
    #resolver.addResolver("{nim_shot_render}", "NIM Shot Render Output Directory", lambda keyword, task: task.editId())
    #resolver.addResolver("{nim_shot_comp}", "NIM Shot Comp Output Directory", lambda keyword, task: task.editId())

    def serverOSPath(task):
      '''
      global g_nim_serverOSPath
      return g_nim_serverOSPath
      '''
      return nimHieroConnector.g_nim_serverOSPath

    def showRootPath(task):
      '''
      global g_nim_showFolder
      return g_nim_showFolder
      '''
      return nimHieroConnector.g_nim_showFolder

    def shotPlatesPath(task):
      
      nim_hiero_debug = False
      if nim_hiero_debug:
        print "************* NIM: START RESOLVING PLATES PATH ***************"
      nim_shotID = None
      nim_shotPaths = {}
      nim_platesPath = 'PLATES'
      updateThumbnail = True

      trackItem = task._item
      name = trackItem.name()

      #Test for video track
      exportTrackItem = False
      trackItem_mediaType = trackItem.mediaType()
      if trackItem_mediaType == hiero.core.TrackItem.MediaType.kVideo:
        if nim_hiero_debug:
          print "Processing Video TrackItem"
        exportTrackItem = True

      #SKIP IF NOT VIDEO TRACK ITEM
      if exportTrackItem:
        #global g_nim_showID
        nim_showID = nimHieroConnector.g_nim_showID
        if nim_hiero_debug:
          print 'NIM: showID=%s' % nim_showID

        nimConnect = nimHieroConnector.NimHieroConnector()
        nim_tag = nimConnect.getNimTag(trackItem)

        if nim_tag != False:
          if nim_hiero_debug:
            print "NIM: Tag Found"
            print         nim_tag

          #update existing shot in NIM
          nim_shotID = nim_tag.metadata().value("tag.shotID")
          if nim_hiero_debug:
            print 'NIM: shotID=%s' % nim_shotID

          nim_platesPath = nim_tag.metadata().value("tag.platesPath")
          if nim_hiero_debug:
            print 'NIM: platesPath=%s' % nim_platesPath

        else:
          if nim_hiero_debug:
            print 'NIM: Tag Not Found'
            print 'NIM: Using default path'

      if nim_hiero_debug:
        print "************* NIM: END RESOLVING PLATES PATH ***************"
  
      return nim_platesPath


hiero.core.taskRegistry.registerProcessor(NimShotProcessorPreset, NimShotProcessor)
hiero.ui.taskUIRegistry.registerProcessorUI(NimShotProcessorPreset, NimShotProcessor)

