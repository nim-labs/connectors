#!/usr/bin/env python
#******************************************************************************
#
# Filename: Nuke/Python/Startup/nim_hiero_connector/nimHieroConnector.py
# Version:  v2.0.0.160510
#
# Copyright (c) 2016 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

from hiero.core import *
import hiero.ui
from hiero.core import log

from PySide.QtGui import *
from PySide.QtCore import *

import sys,os
import base64

import nim_core.nim_api as nimAPI
import nim_core.nim_prefs as nimPrefs
import nim_core.nim_file as nimFile
import nim_core.nim as nim

def statusBar():
	"""Returns an instance of the MainWindow's status bar, displayed at the bottom of the main window()"""
	return hiero.ui.mainWindow().statusBar()

hiero.ui.statusBar = statusBar

g_nim_jobID = None
g_nim_showID = None
g_nim_showFolder = ''
g_nim_element = ''
g_nim_elementTypeID = None
g_nim_publishElement = False
g_nim_publishComp = False
g_nim_serverID = None
g_nim_serverOSPath = ''
g_nim_taskID = None
g_nim_taskFolder = ''
g_nim_basename = ''
g_nim_versionID = None
g_nim_expTask = ''
g_nim_expTaskTypeID = None
g_nim_expTaskFolder = ''

class NimHieroConnector():
	def __init__(self):
		'''NIM Connector'''
		#print "NIM: Connector Loaded"
		return

	def getNimTag(self, trackItem):
		'''Find NIM tag on trackItem and return'''
		nim_tagFound = False
		nim_tag = hiero.core.Tag("NIM")
		trackItem_tags = trackItem.tags()
		for tag in trackItem_tags:
			if tag.name() == "NIM":
				#print "NIM: Tag Found"
				nim_tagFound = True
				nim_tag = tag
				break
		if nim_tagFound:
			return nim_tag
		else:
			return False


	def exportTrackItem(self, showID, trackItem):
		'''Add video trackItem as shot in NIM and add NIM tag to trackItem'''
		shotID = False
		trackItem_mediaType = trackItem.mediaType()

		exportTrackItem = False
		if trackItem_mediaType == hiero.core.TrackItem.MediaType.kVideo:
			print "Processing Video TrackItem"
			exportTrackItem = True

		if exportTrackItem:
			#iterate though shots and get trackItem details
			print "NIM: Adding Shot %s" % (trackItem)
			print "     name %s" % trackItem.name()
			'''
			print "     duration %s" % trackItem.duration()
			print "     handleInLength %s" % trackItem.handleInLength()
			print "     handleInTime %s" % trackItem.handleInTime()
			print "     handleOutLength %s" % trackItem.handleOutLength()
			print "     handleOutTime %s" % trackItem.handleOutTime()
			print "     playbackSpeed %s" % trackItem.playbackSpeed()
			print "     timelineIn %s" % trackItem.timelineIn()
			print "     timelineOut %s" % trackItem.timelineOut()
			print "     sourceIn %s" % trackItem.sourceIn()
			print "     sourceOut %s" % trackItem.sourceOut()
			'''

			#Check for NIM tag on sequence and set showID
			sequence = trackItem.parentSequence()
			nim_sequence_tag = self.getNimTag(sequence)
			if nim_sequence_tag != False:
				print "NIM: Updating sequence tag"
				nim_sequence_tag.metadata().setValue("tag.showID" , showID)
			else:
				print "NIM: Adding sequence tag"
				nim_sequence_tag = hiero.core.Tag("NIM")
				nim_sequence_tag.metadata().setValue("tag.showID" , showID)
				nim_script_path = os.path.dirname(__file__)
				nim_icon_path = os.path.join(nim_script_path,'NIM.png')
				nim_sequence_tag.setIcon(nim_icon_path)
				sequence.addTag(nim_sequence_tag)
				

			shotInfo = nimAPI.add_shot( showID=showID, name=trackItem.name(), frames=trackItem.duration() )
			#print shotInfo
			if shotInfo['success'] == 'true':
				shotID = shotInfo['ID']
				print "		NIM shotID: %s" % shotID
				
				if 'error' in shotInfo:
					print "		WARNING: %s" % shotInfo['error']

				''' IF SHOT IS ONLINE GET PATHS '''
				nim_shotPath = trackItem.name()
				nim_platesPath = 'PLATES'
				nim_compPath = 'COMP'
				nim_renderPath = 'RENDER'
				nim_shotPaths = nimAPI.get_paths('shot', shotID)
				if nim_shotPaths:
					if len(nim_shotPaths)>0:
						#print "NIM: Shot Paths"
						#print nim_shotPaths
						nim_shotPath = nim_shotPaths['root']
						nim_platesPath = nim_shotPaths['plates']
						nim_renderPath = nim_shotPaths['renders']
						nim_compPath = nim_shotPaths['comps']
						
				print '		Adding NIM Tag to shot %s' % trackItem.name()
				nim_tag = hiero.core.Tag("NIM")
				nim_tag.metadata().setValue("tag.showID" , showID)
				nim_tag.metadata().setValue("tag.shotID" , shotID)
				nim_tag.metadata().setValue("tag.shotPath" , nim_shotPath)
				nim_tag.metadata().setValue("tag.platesPath" , nim_platesPath)
				nim_tag.metadata().setValue("tag.renderPath" , nim_renderPath)
				nim_tag.metadata().setValue("tag.compPath" , nim_compPath)
				
				nim_script_path = os.path.dirname(__file__)
				nim_icon_path = os.path.join(nim_script_path,'NIM.png')
				#print '		Icon Path: %s' % nim_icon_path
				#nim_tag.setIcon('./NIM.png')
				nim_tag.setIcon(nim_icon_path)

				tmp_tag = trackItem.addTag(nim_tag)
				#print tmp_tag

			else:
				if shotInfo['error']:
					#error exists
					print "		ERROR: %s" % shotInfo['error']
				shotID = False
		else:
			print "NIM: Skipping MediaType"
			print trackItem_mediaType
			shotID =  False

		return shotID


	def updateTrackItem(self, showID, trackItem):
		'''Update trackItem linked to shot in NIM'''

		trackItem_mediaType = trackItem.mediaType()

		exportTrackItem = False
		if trackItem_mediaType == hiero.core.TrackItem.MediaType.kVideo:
			print "Processing Video TrackItem"
			exportTrackItem = True

		if exportTrackItem:
			#iterate though shots and get trackItem details
			print "NIM: Adding Shot ", trackItem.name()
			'''
			print "NIM: Adding Shot %s" % (trackItem)
			print "     name %s" % trackItem.name()
			print "     duration %s" % trackItem.duration()
			print "     eventNumber %s" % trackItem.eventNumber()
			print "     handleInLength %s" % trackItem.handleInLength()
			print "     handleInTime %s" % trackItem.handleInTime()
			print "     handleOutLength %s" % trackItem.handleOutLength()
			print "     handleOutTime %s" % trackItem.handleOutTime()
			print "     playbackSpeed %s" % trackItem.playbackSpeed()
			print "     timelineIn %s" % trackItem.timelineIn()
			print "     timelineOut %s" % trackItem.timelineOut()
			print "     sourceIn %s" % trackItem.sourceIn()
			print "     sourceOut %s" % trackItem.sourceOut()
			'''

			#get NIM tag for shot
			nim_tag = self.getNimTag(trackItem)

			if nim_tag != False:
				# UPDATE trackItem details in NIM
				
				#showID = nim_tag.metadata().value("tag.showID")
				#Check for NIM tag on sequence and set showID
				sequence = trackItem.parentSequence()
				nim_sequence_tag = self.getNimTag(sequence)
				if nim_sequence_tag != False:
					print "NIM: Updating sequence tag"
					nim_sequence_tag.metadata().setValue("tag.showID" , showID)
				else:
					print "NIM: Adding sequence tag"
					nim_sequence_tag = hiero.core.Tag("NIM")
					nim_sequence_tag.metadata().setValue("tag.showID" , showID)
					nim_script_path = os.path.dirname(__file__)
					nim_icon_path = os.path.join(nim_script_path,'NIM.png')
					nim_sequence_tag.setIcon(nim_icon_path)
					sequence.addTag(nim_sequence_tag)
				

				nim_shotID = nim_tag.metadata().value("tag.shotID")
				'''
				trackItem.timelineIn
				trackItem.timelineOut
				trackItem.playbackSpeed
				'''
				shotInfo = nimAPI.update_shot( nim_shotID, trackItem.duration() )

				if shotInfo['success']:
					print "NIM: Updated corresponding shot in NIM"

					''' GET UPDATED PATHS '''
					nim_shotPath = nim_tag.metadata().value("tag.shotPath")
					nim_platesPath = nim_tag.metadata().value("tag.platesPath")
					nim_renderPath = nim_tag.metadata().value("tag.renderPath")
					nim_compPath = nim_tag.metadata().value("tag.compPath")
					
					nim_shotPaths = nimAPI.get_paths('shot', nim_shotID)
					if nim_shotPaths:
						if len(nim_shotPaths)>0:
							print "NIM: Shot Paths"
							print nim_shotPaths
							nim_shotPath = nim_shotPaths['root']
							nim_platesPath = nim_shotPaths['plates']
							nim_renderPath = nim_shotPaths['renders']
							nim_compPath = nim_shotPaths['comps']
							
							print '		Updating NIM Paths for shot %s' % trackItem.name()
							nim_tag.metadata().setValue("tag.shotPath" , nim_shotPath)
							nim_tag.metadata().setValue("tag.platesPath" , nim_platesPath)
							nim_tag.metadata().setValue("tag.renderPath" , nim_renderPath)
							nim_tag.metadata().setValue("tag.compPath" , nim_compPath)
					return True
				else:
					print "NIM: Failed to update shot details"
					return False
			else:
				print 'NIM: Failed to get Nim Tag'
				return False

		else:
			print "NIM: Skipping MediaType"
			print trackItem_mediaType
			return False


	def updateShotIcon(self, trackItem):
		'''Create thumbnail from trackItem and upload to NIM'''
		
		nim_shotID = None
		nim_tagFound = False
		nim_tag = None

		nim_tag = self.getNimTag(trackItem)

		if nim_tag != False:
			nim_shotID = nim_tag.metadata().value("tag.shotID")
		else:
			print "NIM: ERROR - trackItem Missing NIM Tag"
			return False

		'''
		# Get middle frame for thumbnail
		trackItem_sourceIn = trackItem.sourceIn()
		trackItem_sourceOut = trackItem.sourceOut()
		middleFrame = (trackItem_sourceOut - trackItem_sourceIn) // 2
		trackItem_thumbnail = trackItem.thumbnail(middleFrame)
		'''
		
		# Get first track frame for thumbnail
		trackItem_sourceIn = trackItem.sourceIn()
		trackItem_thumbnail = trackItem.thumbnail(trackItem_sourceIn)
		 
		nim_hiero_home = os.path.normpath( os.path.join( nimPrefs.get_home(), 'apps', 'Hiero' ) )

		#img_name = trackItem.name()+".png"
		img_name = "shoticon.png"

		image_path = os.path.normpath( os.path.join(nim_hiero_home,img_name) )

		trackItem_thumbnail.save( image_path, "PNG",-1)

		apiInfo = nimAPI.upload_shotIcon( nim_shotID, image_path )

		#print apiInfo
		if apiInfo == True:
			status_msg = "NIM: Successfully uploaded icon for %s" % trackItem.name()
			print status_msg
			self.setStatusMessage(status_msg,0,True)
		else:
			status_msg = "NIM: Failed to upload icon for %s" % trackItem.name()
			print status_msg
			self.setStatusMessage(status_msg,0,True)

			'''
			if apiInfo['file_success'] == 'true':
				if 'error' in apiInfo:
					print "		WARNING: %s" % apiInfo['error']
			else:
				if 'error' in apiInfo:
					print "		ERROR: %s" % apiInfo['error']
			'''
		return True
		
	
	def createElementTrack(self, sequence, elementTypeID, element, trackItems):
		'''Create a new track from selected sequence items and a NIM element type'''

		print "NIM: createElementTrack"

		trackName = "NIM: "+ element

		# create a bin for new elements
		elementBin = Bin("NIM: "+ element)

		# get current project and add bin to it
		currentProject = sequence.project()
		clipsBin = currentProject.clipsBin()
		clipsBin.addItem(elementBin)

		# create a track to add items/clips to
		track = VideoTrack(trackName)

		# add the track to the sequence now
		sequence.addTrack(track)
		sequence_framerate = sequence.framerate()
		print "NIM: Sequence Framerate=%s" % sequence_framerate.toString()

		for trackItem in trackItems:
			trackItem_mediaType = trackItem.mediaType()
			if trackItem_mediaType == hiero.core.TrackItem.MediaType.kVideo:
				print "NIM: Processing Video TrackItem:"
				
				nim_tag = self.getNimTag(trackItem)
				if nim_tag != False:

					nim_shotID = nim_tag.metadata().value("tag.shotID")
					
					nim_elements = nimAPI.get_elements('shot', nim_shotID , elementTypeID, True, True)
					#print nim_elements
					
					nim_element_path = None
					if len(nim_elements)>0:
						'''Get the full path of the first item found - should be latest element from API'''
						nim_element_path = nim_elements[0]['full_path']
					else:
						'''Skip this element as none found'''
						continue

					''' TODO:
						Search path and see if file exists
						if not found, get servers and look for matching server prefix
						when found check against os type and repath if needed
					'''

					# set it's source
					trackItem_name = trackItem.name()
					
					trackClip = trackItem.source()							#original clip
					elementClip = Clip(MediaSource(nim_element_path))		#new clip
					newTrackItem = track.createTrackItem(trackItem_name)	#new trackItem

					# set its timeline values
					newTrackItem.setTimelineIn(trackItem.timelineIn())
					newTrackItem.setTimelineOut(trackItem.timelineOut())
					
					# add clip to NIM Bin
					elementBin.addItem(BinItem(elementClip))

					# add it to the track
					track.addTrackItem(newTrackItem)

					# setSource
					newTrackItem.setSourceIn( trackItem.sourceIn() - ( elementClip.sourceIn() - trackClip.sourceIn() ) )
					newTrackItem.setPlaybackSpeed(trackItem.playbackSpeed())
					newTrackItem.setSource(elementClip)

					'''
					print "		elementClip.sourceIn=%s" % elementClip.sourceIn()
					print "		trackItem.sourceIn=%s" % trackItem.sourceIn()
					print " 	trackClip.sourceIn=%s" % trackClip.sourceIn()
					print "		trackItem.handleInLength=%s" % trackItem.handleInLength()
					print "		trackItem.handleOutLength=%s" % trackItem.handleOutLength()
					print "		newTrackItem.sourceIn=%s" % newTrackItem.sourceIn()
					print " 	playbackSpeed=%s" % trackItem.playbackSpeed()
					'''
					
				else:
					print "NIM: Skipping trackItem without NIM Tag"

		return

	
	def clearStatusMessage(self):
		"""
		clearStatusMessage() -> Removes any message being shown in the Mainwindow's statusbar.
		"""
		hiero.ui.statusBar().clearMessage()

	def statusMessage(self):
		"""
		statusMessage() -> returns the current status message displayed in the Hiero statusbar.
		"""
		return unicode(hiero.ui.statusBar().currentMessage())

	def setStatusMessage(self, message, time = 0, showBarIfHidden = True):
		"""
		setStatusMessage(message, time = 0) -> Shows a message in the Mainwindow's statusbar.
		Displays the given message for the specified number of milliseconds, specified by time keyword argument.
		If time is 0 (default), the message remains displayed until hiero.ui.clearStatusMessage() is called or until setStatusMesssage() is called again to change the message.

		@param message: string to display in the Mainwindow statusbar
		@param time: (optional) - a duration value in milliseconds, after which which the status message will be hidden.
		@param showBarIfHidden (optional) - If 'True' and the statusbar is hidden, this will force the statusbar to be shown. 'False' will keep it hidden.
		@return: None 
		"""
		mBar = hiero.ui.statusBar()
		if showBarIfHidden:
			if not mBar.isVisible():
				mBar.show()
		mBar.showMessage(message, timeout = time)

	def toggleStatusBar(self):
		"""Toggles the visibility of the Mainwindow StatusBar"""
		mBar = hiero.ui.statusBar()
		mBar.setHidden( mBar.isVisible() )