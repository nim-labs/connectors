#!/usr/bin/env python
#******************************************************************************
#
# Filename: Nuke/Python/Startup/nim_hiero_connector/nimShotProcessorUI.py
# Version:  v2.0.0.160502
#
# *****************************************************************************

import itertools
import hiero.core
import hiero.ui
from PySide import QtCore, QtGui

from hiero.ui.FnTagFilterWidget import TagFilterWidget
from nimShotProcessor import NimShotProcessorPreset, NimShotProcessor, findTrackItemExportTag, buildTagsData
from hiero.exporters.FnTrackSelectionWidget import TrackSelectionWidget

#NIM
import nim_core.nim_api as nimAPI
import nim_core.nim_prefs as nimPrefs
import nim_core.nim_file as nimFile
import nim_core.nim as nim

import nimHieroConnector

from nimProcessorUI import *
#END NIM

class NimShotProcessorUI(NimProcessorUIBase, QtCore.QObject):

  def __init__(self, preset):
    QtCore.QObject.__init__(self)
    NimProcessorUIBase.__init__(self, preset, itemTypes=hiero.core.TaskPresetBase.kTrackItem)


  def displayName(self):
    return "NIM: Process as Shots"


  def toolTip(self):
   return "NIM: Process as Shots generates output according to the NIM project structure on a per shot basis."


  def validate(self, exportItems):
    """Validate settings in UI. Return False for failure in order to abort export."""
    if not NimProcessorUIBase.validate(self, exportItems):
      return False

    invalidItems = []
    # Look for selected items which arent of the correct type
    for item in exportItems:
      if not item.sequence() and not item.trackItem():
        invalidItems.append(item.item().name() + " <span style='color: #CC0000'>(Not a Sequence)</span>")
    # Found invalid items
    if invalidItems:
      # Show warning
      msgBox = QtGui.QMessageBox()
      msgBox.setTextFormat(QtCore.Qt.RichText)
      result = msgBox.information(None, "Export", "The following items will be ignored by this export:<br/>%s" % str("<br/>".join(invalidItems)), QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
      # Continue if user clicks OK
      return result == QtGui.QMessageBox.Ok

    # Check existing versions for any of the selected items.
    if not self._checkExistingVersions(exportItems):
      return False

    return True


  def validateSelection(self, exportItems):
    """Validate if any items in the selection are suitable for processing by this processor"""

    invalidItems = []
    # Look for selected items which arent of the correct type
    for item in exportItems:
      if not item.sequence() and not item.trackItem():
        invalidItems.append(item)

    return len(invalidItems) < len(exportItems)


  def findTagsForItems(self, exportItems):
    return buildTagsData(exportItems)


  def createRangeWidgets(self):
    rangeWidget = QtGui.QWidget()
    rangeLayout = QtGui.QVBoxLayout()

    rangeLayout.setContentsMargins(0,0,0,0)
    rangeWidget.setLayout(rangeLayout)

    rangeLabel = QtGui.QLabel("HANDLES")
    rangeLayout.addWidget(rangeLabel)


    clipLengthToolTip = "Select this to export all available frames of the Clip, as displayed on the Clip's BinItem."
    cutLengthToolTip = """Select this to export frames from the cut length of the shot on the timeline.\nNote: Selecting Cut Length allows you to add handles to each clip, up to the\nmaximum available source clip length."""
    handlesToolTip = "The number of frame handles to export at the head and tail of a shot."
    retimeToolTip = "Selecting this will apply frame retiming to any shots that have been retimed, and include any TimeWarp effects in the exported Nuke script."
    startFrameToolTip = "Set how clip Start Frames are derived using the dropdown menu:\n-Source : use the source clip's start frame.\n-Custom : specify a start frame for all clips"

    radioLayout = QtGui.QVBoxLayout()

    # Clip Length Radio Button
    radioClip = QtGui.QRadioButton("Clip Length")
    radioClip.setToolTip(clipLengthToolTip)
    rangeLayout.addWidget(radioClip)

    # Cut Length Radio Button
    radioCut =  QtGui.QRadioButton("Cut Length")
    radioCut.setToolTip(cutLengthToolTip)
    radioCut.toggled.connect(self.cutLengthToggled)
    rangeLayout.addWidget(radioCut)

    # Handles Checkbox and layout
    cutLayout = QtGui.QHBoxLayout()
    cutLayout.addSpacing(20)
    self._cutCheckBox = QtGui.QCheckBox("Include")
    self._cutCheckBox.setToolTip(handlesToolTip)
    self._cutCheckBox.stateChanged.connect(self.cutUseHandlesChanged)
    cutLayout.addWidget(self._cutCheckBox)

    # Handles Spinbox
    self._cutHandles = QtGui.QSpinBox()
    self._cutHandles.setMaximum(10000)
    self._cutHandles.setMaximumWidth(60)
    self._cutHandles.setToolTip(handlesToolTip)
    cutLayout.addWidget(self._cutHandles)
    cutLayout.addWidget(QtGui.QLabel("frames"))
    self._cutHandles.setMinimum(0)

    self._cutHandles.valueChanged.connect(self.cutHandlesChanged)

    cutLayout.addStretch(1)
    rangeLayout.addLayout(cutLayout)

     # Options for applying (or ignoring) retimes
    retimeLayout = QtGui.QHBoxLayout()
    self._retimeCheckBox = QtGui.QCheckBox("Apply Retimes")
    self._retimeCheckBox.stateChanged.connect(self.retimesChanged)
    self._retimeCheckBox.setToolTip(retimeToolTip)
    retimeLayout.addSpacing(20)
    retimeLayout.addWidget(self._retimeCheckBox)
    retimeLayout.addStretch(1)
    rangeLayout.addLayout(retimeLayout)

    # Startframe layout
    startFrameLayout = QtGui.QHBoxLayout()
    self._startFrameSource = QtGui.QComboBox()
    self._startFrameSource.setToolTip(startFrameToolTip)

    startFrameSourceItems = (NimShotProcessor.kStartFrameSource, NimShotProcessor.kStartFrameCustom)
    for index, item in zip(range(0,len(startFrameSourceItems)), startFrameSourceItems):
      self._startFrameSource.addItem(item)
      if item == str(self._preset.properties()["startFrameSource"]):
        self._startFrameSource.setCurrentIndex(index)

    # Custom Startframe line edit, enabled only if 'Custom' start frame source selected
    self._startFrameIndex = QtGui.QLineEdit()
    self._startFrameIndex.setValidator(QtGui.QIntValidator())
    self._startFrameIndex.setText(str(self._preset.properties()["startFrameIndex"]))

    startFrameLayout.addWidget(QtGui.QLabel("Start Frame"))
    startFrameLayout.addWidget(self._startFrameSource)
    startFrameLayout.addWidget(self._startFrameIndex)
    startFrameLayout.addStretch(1)

    self._startFrameSource.currentIndexChanged.connect(self.onStartFrameSourceChanged)
    self._startFrameIndex.textChanged.connect(self.onStartFrameIndexChanged)
    self.onStartFrameSourceChanged(0)
    rangeLayout.addLayout(startFrameLayout)

    # Restore State - Cut / Clip length
    if self._preset.properties()["cutLength"]:
      radioCut.setChecked(True)
      self.cutLengthToggled(True)
    else:
      radioClip.setChecked(True)
      self.cutLengthToggled(False)

    # Restore State - Handles
    if self._preset.properties()["cutUseHandles"]:
      self._cutCheckBox.setCheckState(QtCore.Qt.Checked)
    self._cutHandles.setValue(int(self._preset.properties()["cutHandles"]))

    # Restore State - include retimes
    if self._preset.properties()["includeRetimes"]:
      self._retimeCheckBox.setCheckState(QtCore.Qt.Checked)

    rangeLayout.addStretch()

    return rangeWidget


  def createProcessorSettingsWidget(self, exportItems):
    widget = QtGui.QWidget()

    mainLayout = QtGui.QVBoxLayout()
    widget.setLayout(mainLayout)

    # Horizontal layout to stack group boxes side by side
    hLayout = QtGui.QHBoxLayout()
    mainLayout.addLayout(hLayout)


    sequences = []
    for item in exportItems:
      if not item.trackItem() and item.sequence():
        sequence = item.sequence()
      elif item.trackItem():
        sequence = item.trackItem().parentSequence()
      if not sequence in sequences:
        sequences.append(sequence)

    trackWidget = TrackSelectionWidget(sequences,
                                           self._preset.nonPersistentProperties()["excludedTracks"],
                                           excludedTrackIDs = self._preset._excludedTrackIDs)
    hLayout.addWidget(trackWidget)

    tagsLayout = QtGui.QVBoxLayout()

    tagsLabel = QtGui.QLabel("FILTER BY TAG")
    tagsLayout.addWidget(tagsLabel)

    include_tags = [tag for tag, objecttype in self._tags if tag.name() in self._preset.properties()["includeTags"]]
    exclude_tags = [tag for tag, objecttype in self._tags if tag.name() in self._preset.properties()["excludeTags"]]

    tagsWidget = TagFilterWidget([tag for tag, objecttype in self._tags if objecttype in (hiero.core.TrackItem, )], include_tags, exclude_tags)
    tagsWidget.setToolTip("Filter shot selection based on Shot Tags.\n+ Only include shots with these tags.\n- Exclude any shots with these tags.")
    tagsWidget.tagSelectionChanged.connect(self._tagsSelectionChanged)

    tagsLayout.addWidget(tagsWidget)
    hLayout.addLayout(tagsLayout)


    rangeWidget = self.createRangeWidgets()
    hLayout.addWidget(rangeWidget)

    versionWidget = self.createVersionWidget()
    mainLayout.addWidget(versionWidget)

    return widget


  def processorSettingsLabel(self):
    return "Tracks && Handles"


  def cutLengthToggled (self, checked):
    self._preset.properties()["cutLength"] = checked
    self._cutCheckBox.setEnabled(checked)
    self._cutHandles.setEnabled(checked)
    self._retimeCheckBox.setEnabled(checked)


  def cutHandlesChanged (self, value):
    self._preset.properties()["cutHandles"] = value


  def cutUseHandlesChanged (self, checked):
    self._preset.properties()["cutUseHandles"] = checked == QtCore.Qt.Checked


  def retimesChanged(self, checked):
    self._preset.properties()["includeRetimes"] = checked == QtCore.Qt.Checked


  def onStartFrameSourceChanged(self, index):
    value = self._startFrameSource.currentText()
    if str(value) in (NimShotProcessor.kStartFrameSource):
      self._startFrameIndex.setEnabled(False)
    elif str(value) == NimShotProcessor.kStartFrameCustom:
      self._startFrameIndex.setEnabled(True)
    self._preset.properties()["startFrameSource"] = str(value)


  def onStartFrameIndexChanged(self, value):
    self._preset.properties()["startFrameIndex"] = int(value)


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

    if item.checkState() == QtCore.Qt.Checked:
      if selectedtrack in excludedTracks:
        excludedTracks.remove(selectedtrack)
        excludedTrackNames.remove(selectedtrack.name())
      if selectedtrack.guid() in excludedTrackIDs:
        excludedTrackIDs.remove(selectedtrack.guid())

    elif item.checkState() == QtCore.Qt.Unchecked:
      if selectedtrack not in excludedTracks:
        excludedTracks.append(selectedtrack)
        excludedTrackNames.append(selectedtrack.name())
      if selectedtrack.guid() not in excludedTrackIDs:
        excludedTrackIDs.append(selectedtrack.guid())


  def toggleAllTracks(self):
    for row in range(self.trackListModel.rowCount()):
      if self.trackListModel.item(row).checkState() == QtCore.Qt.Checked:
        anySelected = True
        break
      else:
        anySelected = False

    if anySelected:
      for row in range(self.trackListModel.rowCount()):
        self.trackListModel.itemFromIndex(self.trackListModel.index(row, 0)).setCheckState(QtCore.Qt.Unchecked)
    else:
      for row in range(self.trackListModel.rowCount()):
        # Get the current track object by grabbing the data (track guid) stored on the checkbox
        for sequence in self._sequences:
          currentTrack = [track for track in sequence if track.guid() in [self.trackListModel.itemFromIndex(self.trackListModel.index(row, 0)).data()]][0]
          if currentTrack.isEnabled() and self._trackHasTrackOrSubTrackItems(track):
            self.trackListModel.itemFromIndex(self.trackListModel.index(row, 0)).setCheckState(QtCore.Qt.Checked)


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
        trackIcon = QtGui.QIcon("icons:AudioOnly.png")
    elif isinstance(track,hiero.core.VideoTrack):
        trackIcon = QtGui.QIcon("icons:VideoOnly.png")
    return trackIcon


  def _trackHasTrackOrSubTrackItems(self, track):
    """ Test if a track has any items or sub-track items. """
    if (
      len(track.items()) > 0 or
      (isinstance(track, hiero.core.VideoTrack) and len( [ item for item in itertools.chain(*track.subTrackItems()) ] ) > 0)
      ):
      return True
    else:
      return False


  def _tagsSelectionChanged(self, include_subset, exclude_subset):
    self._preset.properties()["includeTags"] = [ tag.name() for tag in include_subset ]
    self._preset.properties()["excludeTags"] = [ tag.name() for tag in exclude_subset ]


  def _checkExistingVersions(self, exportItems):
    """ Iterate over all the track items which are set to be exported, and check if they have previously
        been exported with the same version as the setting in the current preset.  If yes, show a message box
        asking the user if they would like to increment the version, or overwrite it. """

    existingExportVersionsFound = False
    unversionedExportsFound = False
    trackItems = self._trackItemsToExport(exportItems)
    for item in trackItems:
      tag = findTrackItemExportTag(self._preset, item)
      if tag:
        try:
          existingExportVersionsFound = self._checkTrackItemExportExistingVersion(item, self._preset.properties()["versionIndex"], tag)
        except:
          unversionedExportsFound = True

    title = "Export"
    result = True
    if existingExportVersionsFound:
      text = "Previous export(s) found.  Do you want to create a new version or overwrite the existing files?"
      msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Question, title, text)
      overwriteButton = msgBox.addButton("Overwrite", QtGui.QMessageBox.AcceptRole)
      newVersionButton = msgBox.addButton("New Version", QtGui.QMessageBox.AcceptRole)
      msgBox.setDefaultButton(newVersionButton)
      msgBox.addButton(QtGui.QMessageBox.Cancel)
      msgBox.exec_()
      if msgBox.clickedButton() == newVersionButton:
        NimShotProcessorUI._versionUpPreviousExports = True
      elif msgBox.clickedButton() == overwriteButton:
        NimShotProcessorUI._versionUpPreviousExports = False
      else:
        result = False
    elif unversionedExportsFound:
      text = "Previous unversioned export(s) found.  Do you want to overwrite them?"
      response = QtGui.QMessageBox.question(hiero.ui.mainWindow(), title, text, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
      result = (response == QtGui.QMessageBox.Yes)

    return result



  def _tracksToExport(self, sequence):
    """ Get the tracks on the given sequence which will be included in the export. """
    for track in itertools.chain(sequence.videoTracks(), sequence.audioTracks()):
      if track.isEnabled() and not track.guid() in self._preset._excludedTrackIDs:
        yield track


  def _trackItemsToExport(self, exportItems):
    """ Get a list of the track items which will be included in the export. """
    trackItems = []
    if exportItems[0].trackItem():
      trackItems = [ item.trackItem() for item in exportItems if isinstance(item.trackItem(), hiero.core.TrackItem) and not item.ignore() ]
    else:
      sequences = [ item.sequence() for item in exportItems ]
      for sequence in sequences:
        for track in self._tracksToExport(sequence):
          trackItems.extend( [ item for item in track if (item.isMediaPresent() or not self.skipOffline()) ] )

    return trackItems


hiero.ui.taskUIRegistry.registerProcessorUI(NimShotProcessorPreset, NimShotProcessorUI)
