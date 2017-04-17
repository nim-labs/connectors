#!/usr/bin/env python
#******************************************************************************
#
# Filename: Nuke/Python/Startup/nim_hiero_connector/nimShotProcessor.py
# Version:  v2.6.01.170417
#
# Nuke 10.5v2
#
# *****************************************************************************

import time
import hiero.core
import hiero.core.FnExporterBase as FnExporterBase
import itertools

from hiero.core.VersionScanner import VersionScanner
from hiero.exporters.FnExportKeywords import kFileBaseKeyword, kFileHeadKeyword, kFilePathKeyword, KeywordTooltips
from hiero.exporters.FnEffectHelpers import ensureEffectsNodesCreated

#NIM
import os.path
import sys,re
import base64
import platform
import ntpath

import nim_core.UI as nimUI
import nim_core.nim_api as nimAPI
import nim_core.nim_prefs as nimPrefs
import nim_core.nim_file as nimFile
import nim_core.nim_win as nimWin
import nim_core.nim as nim

import nimHieroConnector
#END NIM

def getShotNameIndex(trackItem):
  """ Get the name index string for a track item.  This counts other items on the sequence
      with the same name and returns a string in the form '_{index}'.
      If this is the first item, or there are no others with the same name, returns an empty string. """
      
  indexStr = ''
  sequence = trackItem.sequence()
  name = trackItem.name()
  index = 1

  # Iterate over all video track items and check if their names match, incrementing the index.
  # When we hit the test track item, break.
  for videoTrack in sequence.videoTracks():
    matchFound = False
    for otherItem in videoTrack.items():
      if otherItem.name() == name:
        if otherItem == trackItem:
          matchFound = True
          break
        else:
          index = index + 1
    if matchFound:
      break
  if index > 1:
    indexStr = '_%s' % index
  return indexStr



def findTrackItemExportTag(preset, item):
  """ Find a tag from a previous export. """
  presetId = hiero.core.taskRegistry.getPresetId(preset)
  foundTag = None
  for tag in item.tags():
    if tag.metadata().hasKey("tag.presetid") and tag.metadata()["tag.presetid"] == presetId:
      foundTag = tag
      break
  return foundTag



def buildTagsData(exportItems):
  # Collect tags from selection
  tags = FnExporterBase.tagsFromSelection(exportItems, includeChildren=True)

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

  tags = [(tag, objecttype) for tag, objecttype in tags if tag.visible() and reverse_contains(tag.name(), filters) and uniquetest(tag,objecttype)]
  return tags


class NimShotProcessor(hiero.core.ProcessorBase):

  # Settings for determining the start frame of an export.  Note that 'Sequence' is currently disabled.
  kStartFrameSource = "Source"
  kStartFrameCustom = "Custom"
  #kStartFrameSequence = "Sequence"

  # Flag to determine if we should auto-increment the version number if the one selected in the
  # export preset already exists for a track item.  This is a class variable because the check is done
  # in a different instance than the one used for the export.
  _versionUpPreviousExports = False

  def __init__(self, preset, submission=None, synchronous=False):
    """Initialize"""
    hiero.core.ProcessorBase.__init__(self, preset, submission, synchronous)

    self._exportTemplate = None

    self._tags = []

    self.setPreset(preset)

  def preset (self):
    return self._preset

  def setPreset ( self, preset ):
    self._preset = preset
    oldTemplate = self._exportTemplate
    self._exportTemplate = hiero.core.ExportStructure2()
    self._exportTemplate.restore(self._preset.properties()["exportTemplate"])
    if self._preset.properties()["exportRoot"] != "None":
      self._exportTemplate.setExportRootPath(self._preset.properties()["exportRoot"])


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


  def _trackHasTrackOrSubTrackItems(self, track):
    """ Test if a track has any items or sub-track items. """
    if (
      len(track.items()) > 0 or
      (isinstance(track, hiero.core.VideoTrack) and len( [ item for item in itertools.chain(*track.subTrackItems()) ] ) > 0)
      ):
      return True
    else:
      return False



  def _getTrackItemExistingExportVersionIndices(self, item, tag):
    """ Get the indices of all the existing versions which were exported with the
        current preset from the given track item . """
    tagScriptPath = tag.metadata().value("tag.script")
    scanner = VersionScanner()
    versionIndices = scanner.getVersionIndicesForPath(tagScriptPath) # Get all the existing version indices
    return versionIndices


  def _getTrackItemExportVersionIndex(self, item, version, tag):
    """ Get the version index with which the track item should be exported.  The input is the version which is
        selected in the preset.  If the option was selected, we scan for existing versions, and if that version
        already exists, return a new one. """
    newVersion = version
    if NimShotProcessor._versionUpPreviousExports and tag:
      versionIndices = self._getTrackItemExistingExportVersionIndices(item, tag)
      if version in versionIndices:
        newVersion = versionIndices[-1] + 1
    return newVersion


  def _checkTrackItemExportExistingVersion(self, item, version, tag):
    """ Check if a track item has already been exported with a given version. """
    versionIndices = self._getTrackItemExistingExportVersionIndices(item, tag)
    if not versionIndices:
      raise RuntimeError("No version indices found")
    if version in versionIndices:
      return True
    else:
      return False


  def startProcessing(self, exportItems, preview=False):
    hiero.core.log.debug( "NimShotProcessor::startProcessing(" + str(exportItems) + ")" )

    sequences = []
    selectedTrackItems = set()
    selectedSubTrackItems = set()
    ignoredTrackItems = set()
    excludedTracks = []
    
    # Build Tags data from selection
    self._tags = buildTagsData(exportItems)
    
    # Filter the include/exclude tags incase the previous tag selection is not included in the current selection
    included_tag_names = [ tag.name() for tag, objectType in self._tags if tag.name() in self._preset.properties()["includeTags"] ]
    excluded_tag_names = [ tag.name() for tag, objectType in self._tags if tag.name() in self._preset.properties()["excludeTags"] ]

    # This flag controls whether items which havent been explicitly included in the export, 
    # should be removed from the copied sequence. This primarily affects the collate functionality in nuke script generation.
    exclusiveCopy = False


    if exportItems[0].trackItem():
      sequences.append( exportItems[0].trackItem().parent().parent() )
      for item in exportItems:
        trackItem = item.trackItem()
        if isinstance(trackItem, hiero.core.TrackItem):
          selectedTrackItems.add( trackItem )
          if item.ignore():
            ignoredTrackItems.add( trackItem )
        elif isinstance(trackItem, hiero.core.SubTrackItem):
          selectedSubTrackItems.add( trackItem )
    else:
      sequences = [ item.sequence() for item in exportItems ]
      
    if ignoredTrackItems:
      # A set of track items have been explicitly marked as ignored. 
      # This track items are to be included in the copy, but not exported.
      # Thus any shot which isnt in the selected list, should be excluded from the copy.
      exclusiveCopy = True

    for sequence in sequences:
      excludedTracks.extend( [track for track in sequence if track.guid() in self._preset._excludedTrackIDs] )
      
    localtime = time.localtime(time.time())

    path = self._exportTemplate.exportRootPath()
    versionIndex = self._preset.properties()["versionIndex"]
    versionPadding = self._preset.properties()["versionPadding"]
    retime = self._preset.properties()["includeRetimes"]

    cutHandles = None
    startFrame = None

    if self._preset.properties()["startFrameSource"] == NimShotProcessor.kStartFrameCustom:
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

    copiedSequences = []

    project = None

    for sequence in sequences:
      sequenceCopy = sequence.copy()
      copiedSequences.append( sequenceCopy )
      self._tagCopiedSequence(sequence, sequenceCopy)

      # Copied effect items create their nodes lazily, but this has to happen on
      # the main thread, force it to be done here.
      ensureEffectsNodesCreated(sequenceCopy)

      # The export items should all come from the same project
      if not project:
        project = sequence.project()

      if not preview:
        presetId = hiero.core.taskRegistry.addPresetToProjectExportHistory(project, self._preset)
      else:
        presetId = None

      # For each video track
      for track, trackCopy in zip(sequence.videoTracks(), sequenceCopy.videoTracks()) + zip(sequence.audioTracks(), sequenceCopy.audioTracks()):

        # Unlock copied track so that items may be removed
        trackCopy.setLocked(False)

        if track in excludedTracks or not track.isEnabled():
          # remove unselected track from copied sequence
          sequenceCopy.removeTrack(trackCopy)
          continue

        # Used to store the track items to be removed from trackCopy, this is to
        # avoid removing items whilst we are iterating over them.
        trackItemsToRemove = []

        # For each track item on track
        for trackitem, trackitemCopy in zip(track.items(), trackCopy.items()):

          trackitemCopy.unlinkAll() # Unlink to prevent accidental removal of items we want to keep

          # If we're processing the whole sequence, or this shot has been selected
          if not selectedTrackItems or trackitem in selectedTrackItems:

            if trackitem in ignoredTrackItems:
              hiero.core.log.debug( "%s marked as ignore, skipping. Selection : %s" % (str(trackitemCopy), str(exportTrackItems)) )
              continue
              
            # Check tags for excluded tags
            excludedTags = [tag for tag in trackitem.tags() if tag.name() in excluded_tag_names]
            includedTags = [tag for tag in trackitem.tags() if tag.name() in included_tag_names]

            if included_tag_names:
              # If not included, or explictly excluded
              if not includedTags or excludedTags:
                hiero.core.log.debug( "%s does not contain include tag %s, skipping." % (str(trackitemCopy), str(included_tag_names)) )
                ignoredTrackItems.add(trackitem)
                continue
              else:
                hiero.core.log.debug( "%s has include tag %s." % (str(trackitemCopy), str(included_tag_names)) )
              
            elif excludedTags:
              hiero.core.log.debug( "%s contains excluded tag %s, skipping." % (str(trackitemCopy), str(excluded_tag_names)) )
              ignoredTrackItems.add(trackitem)
              continue

            if trackitem.isMediaPresent() or not self.skipOffline():

              exportTrackItems.append((trackitem, trackitemCopy))  

            else:
              hiero.core.log.debug( "%s is offline. Removing." % str(trackitem) )
              trackItemsToRemove.append(trackitemCopy)
          else:
            # Either remove the track item entirely, or mark it as ignored, so that no tasks are spawned to export it.
            if exclusiveCopy:
              hiero.core.log.debug( "%s is not selected. Removing." % str(trackitem) )
              trackItemsToRemove.append(trackitemCopy)
            else:
              hiero.core.log.debug( "%s is not selected. Ignoring." % str(trackitem) )
              ignoredTrackItems.add(trackitem)


        for item in trackItemsToRemove:
          trackCopy.removeItem(item)

    ''' ****************** NIM START CHECK ONLINE STATUS AND VBPS ****************** '''
    # Iterate through track items and find NIM associations
    # Check for any shots that can not be brought online due to a variable based project structure

    print 'NIM: Checking for variable based project structure items'
    is_vbps = 0
    is_vbps = nimAPI.can_bringOnline(item='shot',showID=nimHieroConnector.g_nim_showID)
    if is_vbps == 0 :
      # The show uses project variables so check the shots  
      for trackitem, trackitemCopy in exportTrackItems:
        if trackitem in ignoredTrackItems:
         continue

        #Test for video track
        exportTrackItem = False
        trackItem_mediaType = trackitem.mediaType()
        if trackItem_mediaType == hiero.core.TrackItem.MediaType.kVideo:
          exportTrackItem = True

        #Skip if not video track item
        if exportTrackItem:
          nim_shotID = None

          nimConnect = nimHieroConnector.NimHieroConnector()
          nim_tag = nimConnect.getNimTag(trackitem)
          if nim_tag != False:
            #NIM Tag Found
            nim_shotID = nim_tag.metadata().value("tag.shotID")
            is_vbps = nimAPI.can_bringOnline(item='shot',shotID=nim_shotID)
            if is_vbps == 0 :
              # If any shot requires variable break
              break


    if is_vbps == 0 :
      message = 'NIM Warning:\n\n'
      message += 'The NIM job selected uses a variable based project structure which requires '
      message += 'specific fields on each shot to be set prior to being brought online. \n\n'
      message += 'Shots can be made using the "Update Selected Shots in NIM" context menu in the timeline. '
      message += 'After making shots go to the NIM Job\'s Production/Config/Offline tab to resolve any required fields.'
      nimWin.popup( title='NIM Error', msg=message)
      return False

    ''' ****************** NIM END CHECK ONLINE STATUS AND VBPS ****************** '''


    allTasks = []

    for trackitem, trackitemCopy in exportTrackItems:
      
      if trackitem in ignoredTrackItems:
       continue

      # Check if a task is already exporting this item and if so, skip it.
      # This is primarily to handle the case of collating shots by name, where we only 
      # want one script containing all the items with that name.
      createTasks = True
      for existingTask in allTasks:

        if existingTask.isExportingItem(trackitemCopy):
          createTasks = False
          break

      if not createTasks:
        continue
      
      taskGroup = hiero.core.TaskGroup()
      taskGroup.setTaskDescription( trackitem.name() )

      # Track items may end up with different versions if they're being re-exported.  Determine
      # the version for each item.
      trackItemVersionIndex = self._getTrackItemExportVersionIndex(trackitem, versionIndex, findTrackItemExportTag(self._preset, trackitem))
      trackItemVersion = "v%s" % format(int(trackItemVersionIndex), "0%id" % int(versionPadding))

      ''' ****************** NIM START UPDATE TRACKITEM ****************** '''
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

        #BRING SHOT ONLINE AND CREATE PROJECT STRUCTURE FOLDERS
        bringOnline_result = nimAPI.bring_online( item='shot', shotID=nim_shotID )
        if bringOnline_result['success'] == 'false':
          print 'NIM: Failed to bring shot online'
          print 'NIM: %s' % bringOnline_result['error']
        elif bringOnline_result['success'] == 'true':
          print 'NIM: Shot brought online %s' % name
        else :
          print 'NIM: bringOnline returned and invalid status'

        #GET UPDATED NIM TAG AND COPY TO CLONE
        nim_tag = nimConnect.getNimTag(trackitem)
        if nim_tag != False:
          print 'NIM: Copying nim_tag to clone'
          trackitemCopy.addTag(nim_tag)
        else:
          print 'NIM: Could not copy nim_tag to copy.. tag not found'


      ''' ****************** NIM END UPDATE TRACKITEM ****************** '''

      # If processor is flagged as Synchronous, flag tasks too
      if self._synchronous:
        self._submission.setSynchronous()

      # For each entry in the shot template
      for (exportPath, preset) in self._exportTemplate.flatten():

        # Build TaskData seed
        taskData = hiero.core.TaskData( preset,
                                        trackitemCopy,
                                        path,
                                        exportPath,
                                        trackItemVersion,
                                        self._exportTemplate,
                                        project=project,
                                        cutHandles=cutHandles,
                                        retime=retime,
                                        startFrame=startFrame,
                                        startFrameSource = self._preset.properties()["startFrameSource"],
                                        resolver=resolver,
                                        submission=self._submission,
                                        skipOffline=self.skipOffline(),
                                        presetId=presetId,
                                        shotNameIndex = getShotNameIndex(trackitem) )

        # Spawn task
        task = hiero.core.taskRegistry.createTaskFromPreset(preset, taskData)

        # Add task to export queue
        if task and task.hasValidItem():

          # Give the task an opportunity to modify the original (not the copy) track item
          if not task.error() and not preview:
            task.updateItem(trackitem, localtime)

          taskGroup.addChild(task)
          allTasks.append(task)
          hiero.core.log.debug( "Added to Queue " + trackitem.name() )


          ''' ****************** NIM START PUBLISH ELEMENT ****************** '''

          #resolvedFullPath = os.path.join(resolver.resolve(task, path),resolver.resolve(task, exportPath))
          resolvedFullPath = "/".join([resolver.resolve(task, path),resolver.resolve(task, exportPath)])
          trackitem_clip = trackitem.source()

          ''''''
          #print "NIM:   2.0"
          print "NIM:   resolved fulPath=", resolvedFullPath
          print "NIM:   path=",path
          print "NIM:   exportPath=",exportPath
          #print "NIM:   version=",version
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
          
          if cutHandles == None:
            cutHandles = 0

          element_startFrame = trackitem_clip.sourceIn() + (trackitem.sourceIn() - cutHandles)
          element_endFrame =  trackitem_clip.sourceIn() + (trackitem.sourceOut() + cutHandles)
          element_filePath = ntpath.dirname(resolvedFullPath)
          element_fileName = ntpath.basename(resolvedFullPath)

          print "nimHieroConnector.g_nim_publishElement=",nimHieroConnector.g_nim_publishElement
          print "nimHieroConnector.g_nim_element=",nimHieroConnector.g_nim_element
          print "nimHieroConnector.g_nim_elementTypeID=",nimHieroConnector.g_nim_elementTypeID

          #Determine Export Preset
          presetName = preset.name()
          presetExportName = type(preset).__name__
          print "preset name: %s" % presetName
          #print "export name: %s" % presetExportName

          if presetName == 'hiero.exporters.FnTranscodeExporter.TranscodeExporter':
            if nimHieroConnector.g_nim_publishElement == True:
              print "NIM: Publish Element"
              print "     shotID=", nim_shotID
              print "     name=", trackitem.name()
              print "     type=", nimHieroConnector.g_nim_element
              print "     filePath=", element_filePath
              print "     fileName=", element_fileName
              print "     startFrame=", element_startFrame 
              print "     endFrame=", element_endFrame
              print "     cutHandles=", cutHandles
            
              element_result = nimAPI.add_element( 'shot', nim_shotID, nimHieroConnector.g_nim_elementTypeID, element_filePath, element_fileName, element_startFrame, element_endFrame, cutHandles, nimHieroConnector.g_nim_publishElement )

          elif presetName == 'hiero.exporters.FnNukeShotExporter.NukeShotExporter':
            if nimHieroConnector.g_nim_publishComp == True:
              print "NIM: Publish Comp"
              print "     shotID=", nim_shotID
              print "     name=", trackitem.name()
              print "     filePath=", element_filePath
              print "     fileName=", element_fileName
            
              nim_doSave = True
              #check to ensure valid task is selected
              print "nimHieroConnector.g_nim_expTaskTypeID=",nimHieroConnector.g_nim_expTaskTypeID
              print "nimHieroConnector.g_nim_expTaskFolder=",nimHieroConnector.g_nim_expTaskFolder
              task_type_ID = nimHieroConnector.g_nim_expTaskTypeID
              task_folder = nimHieroConnector.g_nim_expTaskFolder
              if task_type_ID == 0:
                print "No Task selected for Nuke Comp Export.\n \
                       The Nuke comp will be created but not logged into NIM."
                nim_doSave = False
              

              nim_prefInfo = nimPrefs.read()
              user = nim_prefInfo['NIM_User']
              userID = nimAPI.get_userID(user)
              if not userID :
                nimUI.GUI().update_user()
                userInfo=nim.NIM().userInfo()
                user = userInfo['name']
                userID = userInfo['ID']
              print "NIM: user=%s" % user
              print "NIM: userID: %s" % userID

              #Derive basename from file ( TODO: give option to use shot_task_tag_ver.nk method )
              #Using filename entered in Export window
              #ext = '.nk'
              basename = element_fileName
              version = 0

              basenameFull, ext = os.path.splitext(element_fileName)
              basenameMatch = re.search(r'v[0-9]+$', basenameFull, re.I)
              if basenameMatch:
                matchIndex = basenameMatch.start(0)
                basename = basenameFull[:matchIndex]    #returns basename without v#: shot_comp_ (test for trailing _ and remove to be NIM compliant)
                lastCharMatch = re.search(r'_+$', basename)
                if lastCharMatch:
                  basename = basename[:lastCharMatch.start(0)]

                version = basenameFull[matchIndex:][1:].lstrip('0') #returns version without v and leading 0s: '1'
              else:
                print "Version information was either not found in Nuke Project export name or has incorrect placement to be NIM compatible.\n \
                       Please include the version in the comp name at the end of the name by using the {version} keyword or manually adding 'v#' to the Nuke Project File name.\n \
                       example: {shot}_comp_{version}.nk\n \
                       The Nuke comp will be created but not logged into NIM."
                nim_doSave = False
              
              filename = element_fileName
              filepath = element_filePath
              
              print "basename: %s" % basename
              print "filename: %s" % filename
              print "version: %s" % version

              #TODO: verify entry is not duplicate of existing version
              nim_doUpdate = False

              # Get versions for basename
              nim_versions = {}
              nim_versionID = 0
              nim_versions = nimAPI.get_vers(shotID=nim_shotID, basename=basename)
              print "Versions Returned: %s" % nim_versions

              # if file matching class / basename / filename / version
              try:
                if len(nim_versions)>0:
                  print "Existing versions found" 
                  for versionItem in nim_versions:
                    if versionItem['filename'] == filename:
                      print "Existing Version Found"
                      nim_versionID = versionItem['fileID']
                      print "versionID: %s" % nim_versionID
                      nim_doUpdate = True
                else:
                  print "No existing versions found"
              except:
                print "Failed to load existing versions from NIM"
                pass
              
              comment = 'Nuke Project File exported from NukeStudio'
              
              serverID = nimHieroConnector.g_nim_serverID
              if not serverID:
                print "NIM Sever information is missing.\n \
                       Please select a NIM Project Server from the Server dropdown list.\n \
                       The Nuke comp will be created but not logged into NIM."
                nim_doSave = False

              pub = nimHieroConnector.g_nim_publishComp
              forceLink = 0 # lazy symlink as files wont exist yet
              work = True # set comp as working file

              if nim_doSave is True:
                if nim_doUpdate is True:
                  print "Updating file data in NIM"
                  file_apiResult = nimAPI.update_file( ID=nim_versionID, task_type_ID=task_type_ID, task_folder=task_folder, userID=userID, basename=basename, filename=filename, path=filepath, ext=ext, version=version, comment=comment, serverID=serverID, pub=pub, forceLink=forceLink, work=work )
                else:
                  print "Saving file data to NIM"
                  file_apiResult = nimAPI.save_file( parent='shot', parentID=nim_shotID, task_type_ID=task_type_ID, task_folder=task_folder, userID=userID, basename=basename, filename=filename, path=filepath, ext=ext, version=version, comment=comment, serverID=serverID, pub=pub, forceLink=forceLink, work=work )

          elif presetName == 'hiero.exporters.FnExternalRender.NukeRenderTask':
            #Skip - user to publish element at comp render time
            pass

          else:
            pass
          
          ''' ****************** NIM END PUBLISH ELEMENT ****************** '''
      
      if preview:
        # If previewing only generate tasks for the first item, otherwise it
        # can slow down the UI
        if allTasks:
          break
      else:
        # Dont add empty groups
        if len(taskGroup.children()) > 0:
          self._submission.addChild( taskGroup )

    if not preview:
      # If processor is flagged as Synchronous, flag tasks too
      if self._synchronous:
        self._submission.setSynchronous()

      if self._submission.children():

        # Detect any duplicates
        self.processTaskPreQueue()

        self._submission.addToQueue()

      NimShotProcessor._versionUpPreviousExports = False # Reset this after export
    return allTasks
      
      
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
    self.properties()["startFrameSource"] = NimShotProcessor.kStartFrameSource

    self.properties().update(properties)

    # This remaps the project root if os path remapping has been set up in the preferences
    self.properties()["exportRoot"] = hiero.core.remapPath (self.properties()["exportRoot"])

  def addCustomResolveEntries(self, resolver):
    """addDefaultResolveEntries(self, resolver)
    Create resolve entries for default resolve tokens shared by all task types.
    @param resolver : ResolveTable object"""

    resolver.addResolver("{filename}", "Filename of the media being processed", lambda keyword, task: task.fileName())
    resolver.addResolver(kFileBaseKeyword, KeywordTooltips[kFileBaseKeyword], lambda keyword, task: task.filebase())
    resolver.addResolver(kFileHeadKeyword, KeywordTooltips[kFileHeadKeyword], lambda keyword, task: task.filehead())
    resolver.addResolver(kFilePathKeyword, KeywordTooltips[kFilePathKeyword], lambda keyword, task: task.filepath())
    resolver.addResolver("{filepadding}", "Source Filename padding for formatting frame indices", lambda keyword, task: task.filepadding())
    resolver.addResolver("{fileext}", "Filename extension part of the media being processed", lambda keyword, task: task.fileext())
    resolver.addResolver("{clip}", "Name of the clip used in the shot being processed", lambda keyword, task: task.clipName())
    resolver.addResolver("{shot}", "Name of the shot being processed", lambda keyword, task: task.shotName())
    resolver.addResolver("{track}", "Name of the track being processed", lambda keyword, task: task.trackName())
    resolver.addResolver("{sequence}", "Name of the sequence being processed", lambda keyword, task: task.sequenceName())
    resolver.addResolver("{event}", "EDL event of the track item being processed", lambda keyword, task: task.editId())
    resolver.addResolver("{_nameindex}", "Index of the shot name in the sequence preceded by an _, for avoiding clashes with shots of the same name", lambda keyword, task: task.shotNameIndex())

    #NIM Keywords
    resolver.addResolver("{nim_job_name}", "NIM Job Name", lambda keyword, task: nimJobName(task))
    resolver.addResolver("{nim_job_number}", "NIM Job Number", lambda keyword, task: nimJobNumber(task))
    resolver.addResolver("{nim_show_name}", "NIM Show Name", lambda keyword, task: nimShowName(task))
    resolver.addResolver("{nim_server_path}", "NIM Job Server Path", lambda keyword, task: serverOSPath(task))
    #resolver.addResolver("{nim_job_root}", "NIM Job Root Directory", lambda keyword: nim_getJobRootPath())
    resolver.addResolver("{nim_show_root}", "NIM Show Root Directory", lambda keyword, task: showRootPath(task))
    resolver.addResolver("{nim_shot_root}", "NIM Shot Root Directory", lambda keyword, task: shotRootPath(task))
    resolver.addResolver("{nim_shot_plates}", "NIM Shot Plates Directory", lambda keyword, task: shotPlatesPath(task))
    resolver.addResolver("{nim_shot_render}", "NIM Shot Render Output Directory", lambda keyword, task: shotRenderPath(task))
    resolver.addResolver("{nim_shot_comp}", "NIM Shot Comp Output Directory", lambda keyword, task: shotCompPath(task))

    #NOTE: Use encode('ascii') on return value to avoid PyZMQ errors

    def nimJobName(task):
      nim_hiero_debug = False
      nim_jobName = ''
      jobID = nimHieroConnector.g_nim_jobID
      nim_jobInfo = nimAPI.get_jobInfo(jobID)
      if nim_jobInfo:
        if len(nim_jobInfo)>0:
          nim_jobName = nim_jobInfo[0]['jobname']
          if nim_hiero_debug:
            print nim_jobInfo
      return nim_jobName.encode('ascii')

    def nimJobNumber(task):
      nim_hiero_debug = False
      nim_jobNumber = ''
      jobID = nimHieroConnector.g_nim_jobID
      nim_jobInfo = nimAPI.get_jobInfo(jobID)
      if nim_jobInfo:
        if len(nim_jobInfo)>0:
          nim_jobNumber = nim_jobInfo[0]['number']
          if nim_hiero_debug:
            print nim_jobInfo
      return nim_jobNumber.encode('ascii')

    def nimShowName(task):
      nim_hiero_debug = False
      nim_showName = ''
      showID = nimHieroConnector.g_nim_showID
      nim_showInfo = nimAPI.get_showInfo(showID)
      if nim_showInfo:
        if len(nim_showInfo)>0:
          nim_showName = nim_showInfo[0]['showname']
          if nim_hiero_debug:
            print nim_showInfo
      return nim_showName.encode('ascii')

    def serverOSPath(task):
      return nimHieroConnector.g_nim_serverOSPath.encode('ascii')

    def showRootPath(task):
      nim_hiero_debug = False
      if nim_hiero_debug:
        print "nim_show_root: %s" % nimHieroConnector.g_nim_showFolder.encode('ascii')
      return nimHieroConnector.g_nim_showFolder.encode('ascii')

    def shotRootPath(task):
      nim_hiero_debug = False
      if nim_hiero_debug:
        print "************* NIM: START RESOLVING PLATES PATH ***************"
      nim_shotID = None
      nim_shotPaths = {}
      nim_shotPath = 'SHOT'
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

          nim_shotPath = nim_tag.metadata().value("tag.shotPath")
          if nim_hiero_debug:
            print 'NIM: shotPath=%s' % nim_shotPath

        else:
          if nim_hiero_debug:
            print 'NIM: Tag Not Found'
            print 'NIM: Using default path'

      if nim_hiero_debug:
        print "************* NIM: END RESOLVING PLATES PATH ***************"
  
      nim_shotPath = nim_shotPath.encode('ascii')
      return nim_shotPath

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
  
      nim_platesPath = nim_platesPath.encode('ascii')
      return nim_platesPath

    def shotRenderPath(task):
      nim_hiero_debug = False
      if nim_hiero_debug:
        print "************* NIM: START RESOLVING PLATES PATH ***************"
      nim_shotID = None
      nim_shotPaths = {}
      nim_renderPath = 'RENDER'
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

          nim_renderPath = nim_tag.metadata().value("tag.renderPath")
          if nim_hiero_debug:
            print 'NIM: renderPath=%s' % nim_renderPath

        else:
          if nim_hiero_debug:
            print 'NIM: Tag Not Found'
            print 'NIM: Using default path'

      if nim_hiero_debug:
        print "************* NIM: END RESOLVING PLATES PATH ***************"
  
      nim_renderPath = nim_renderPath.encode('ascii')
      return nim_renderPath

    def shotCompPath(task):
      nim_hiero_debug = False
      if nim_hiero_debug:
        print "************* NIM: START RESOLVING PLATES PATH ***************"
      nim_shotID = None
      nim_shotPaths = {}
      nim_compPath = 'COMP'
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

          nim_compPath = nim_tag.metadata().value("tag.compPath")
          if nim_hiero_debug:
            print 'NIM: compPath=%s' % nim_compPath

        else:
          if nim_hiero_debug:
            print 'NIM: Tag Not Found'
            print 'NIM: Using default path'

      if nim_hiero_debug:
        print "************* NIM: END RESOLVING PLATES PATH ***************"
  
      nim_compPath = nim_compPath.encode('ascii')
      return nim_compPath

      
  #check that all nuke shot exporters have at least one write node
  def isValid(self):
    allNukeShotsHaveWriteNodes = True
    for itemPath, itemPreset in self.properties()["exportTemplate"]:
      isNukeShot = isinstance(itemPreset, hiero.exporters.FnNukeShotExporter.NukeShotPreset)
      if isNukeShot and not itemPreset.properties()["writePaths"]:
        allNukeShotsHaveWriteNodes = False
        return (False,"Your Export Structure has no Write Nodes defined.")
    return (True,"")

hiero.core.taskRegistry.registerProcessor(NimShotProcessorPreset, NimShotProcessor)
