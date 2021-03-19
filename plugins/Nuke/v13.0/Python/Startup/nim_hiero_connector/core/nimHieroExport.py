#!/usr/bin/env python
#******************************************************************************
#
# Filename: Nuke/Python/Startup/nim_hiero_connector/nimHieroExport.py
# Version:  v4.0.67.200318
#
# Copyright (c) 2014-2021 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

print ("Loading: nimHieroExport")

from hiero.core import *
import hiero.ui

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import os.path
import sys
import base64
import platform
import ntpath

import nim_core.UI as nimUI
import nim_core.nim_api as nimAPI
import nim_core.nim_prefs as nimPrefs
import nim_core.nim_file as nimFile
import nim_core.nim as nim

from . import nimHieroConnector

''' TODO: Need to check for trackItem as sequence ... 
			if sequence get all trackItems and dump into selected
'''

class NimHieroExport(QAction):
	'''Timeline Menu'''
	def __init__(self):
		QAction.__init__(self, "NIM", None)
		self.triggered.connect(self.nimMenu)
		hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)

		# Instantiate the action
		NimExportSelectedShotAction = NimHieroExport.NimExportSelectedShotAction()
		NimBuildTrackAction = NimHieroExport.NimBuildTrackAction()
		NimClearTagsAction = NimHieroExport.NimClearTagsAction()

	def nimMenu(self):
		'''No Action'''

	def eventHandler(self,event):
		nimMenu = event.menu.addMenu('NIM')
		hiero.nimMenu = nimMenu


	class NimExportDialog(QDialog):
		def __init__(self,  selection, selectedPresets, parent=None):
			super(NimHieroExport.NimExportDialog, self).__init__(parent)
			
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
			if not self.nim_userID :
				nimUI.GUI().update_user()
				userInfo=nim.NIM().userInfo()
				self.user = userInfo['name']
				self.nim_userID = userInfo['ID']

			print("NIM: user=%s" % self.user)
			print("NIM: userID=%s" % self.nim_userID)
			print("NIM: default job=%s" % self.pref_job)

			

			self.nim_jobPaths = {}
			self.nim_showPaths = {}
			self.nim_shotPaths = {}
			self.nim_showFolder = ''
			self.nim_servers = {}
			self.nim_serverID = None
			self.nim_serverOSPath = ''

			#Get NIM Jobs
			self.nim_jobID = None
			self.nim_jobs = nimAPI.get_jobs(self.nim_userID)
			if not self.nim_jobs :
				print("No Jobs Found")
				self.nim_jobs["None"]="0"
			
			self.nim_shows = []
			self.nim_showDict = {}
			self.nim_showID = None
			
			self.setWindowTitle("NIM Update Selected Shots")
			self.setSizeGripEnabled(True)

			self._exportTemplate = None

			tag_jobID = None
			tag_showID = None

			nimConnect = nimHieroConnector.NimHieroConnector()
			
			# Check Sequence for existing showID
			for trackItem in selection:
				sequence = trackItem.parentSequence()
				nim_sequence_tag = nimConnect.getNimTag(sequence)
				if(nim_sequence_tag != False):
					tag_showID = nim_sequence_tag.metadata().value("tag.showID")
					print("NIM: Sequence showID=%s" % tag_showID)
					if(tag_showID != ''):
						showInfo = nimAPI.get_showInfo(tag_showID)
						if len(showInfo)>0:
							for showInfoDetails in showInfo:
								tag_jobID = showInfoDetails['jobID']
								print("NIM: Sequence jobID=%s" % tag_jobID)
				break


			layout = QVBoxLayout()
			formLayout = QFormLayout()
			groupBox = QGroupBox()
			groupLayout = QFormLayout()
			groupBox.setLayout(groupLayout)

			# JOBS: List box for job selection
			horizontalLayout = QHBoxLayout()
			horizontalLayout.setSpacing(-1)
			horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
			horizontalLayout.setObjectName("HorizontalLayout")
			self.nimJobLabel = QLabel()
			self.nimJobLabel.setFixedWidth(40)
			self.nimJobLabel.setText("Job:")
			horizontalLayout.addWidget(self.nimJobLabel)
			self.nim_jobChooser = QComboBox()
			self.nim_jobChooser.setToolTip("Choose the job you wish to export shots to.")
			horizontalLayout.addWidget(self.nim_jobChooser)
			horizontalLayout.setStretch(1, 40)
			groupLayout.setLayout(0, QFormLayout.SpanningRole, horizontalLayout)

			# JOBS: Add dictionary in ordered list
			jobIndex = 0
			jobIter = 0
			if len(self.nim_jobs)>0:
				for key, value in sorted(list(self.nim_jobs.items()), reverse=True):
					self.nim_jobChooser.addItem(key)
					if nimHieroConnector.g_nim_jobID:
						if nimHieroConnector.g_nim_jobID == value:
							print("Found matching jobID, job=", key)
							self.pref_job = key
							jobIndex = jobIter
					else:
						if self.pref_job == key:
							print("Found matching Job Name, job=", key)
							jobIndex = jobIter
					jobIter += 1

				if self.pref_job != '':
					self.nim_jobChooser.setCurrentIndex(jobIndex)

			self.nim_jobChooser.currentIndexChanged.connect(self.nim_jobChanged)
			#self.nim_jobChanged() #trigger job changed to load choosers

			'''
			# SERVERS: List box for server selection
			horizontalLayout2 = QHBoxLayout()
			horizontalLayout2.setSpacing(-1)
			horizontalLayout2.setSizeConstraint(QLayout.SetDefaultConstraint)
			horizontalLayout2.setObjectName("HorizontalLayout2")
			self.nimServerLabel = QLabel()
			self.nimServerLabel.setFixedWidth(40)
			self.nimServerLabel.setText("Server:")
			horizontalLayout2.addWidget(self.nimServerLabel)
			self.nim_serverChooser = QComboBox()
			self.nim_serverChooser.setToolTip("Choose the server you wish to export shots to.")
			horizontalLayout2.addWidget(self.nim_serverChooser)
			horizontalLayout2.setStretch(1, 40)
			groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout2)

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
			'''

			# SHOWS: List box for show selection
			horizontalLayout3 = QHBoxLayout()
			horizontalLayout3.setSpacing(-1)
			horizontalLayout3.setSizeConstraint(QLayout.SetDefaultConstraint)
			horizontalLayout3.setObjectName("HorizontalLayout3")
			self.nimShowLabel = QLabel()
			self.nimShowLabel.setFixedWidth(40)
			self.nimShowLabel.setText("Show:")
			horizontalLayout3.addWidget(self.nimShowLabel)
			self.nim_showChooser = QComboBox()
			self.nim_showChooser.setToolTip("Choose the show you wish to export shots to.")
			horizontalLayout3.addWidget(self.nim_showChooser)
			horizontalLayout3.setStretch(1, 40)
			groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout3)
			self.nim_showChooser.currentIndexChanged.connect(self.nim_showChanged)
		

			# Add the standard ok/cancel buttons, default to ok.
			self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
			self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("Update")
			self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
			self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Executes exports on selection for each selected preset")
			self._buttonbox.accepted.connect(self.acceptTest)
			self._buttonbox.rejected.connect(self.reject)
			horizontalLayout4 = QHBoxLayout()
			horizontalLayout4.setSpacing(-1)
			horizontalLayout4.setSizeConstraint(QLayout.SetDefaultConstraint)
			horizontalLayout4.setObjectName("HorizontalLayout4")
			spacerItem4 = QSpacerItem(175, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
			horizontalLayout4.addItem(spacerItem4)
			horizontalLayout4.addWidget(self._buttonbox)
			horizontalLayout4.setStretch(1, 40)
			groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout4)

			self.setLayout(groupLayout)
			layout.addWidget(groupBox)

			self.nim_jobChanged() #trigger job changed to load choosers


		def nim_jobChanged(self):
			'''Action when job is selected'''
			#print "JOB CHANGED"
			job = self.nim_jobChooser.currentText()
			self.nim_jobID = self.nim_jobs[job]
			self.nim_jobPaths = nimAPI.get_paths('job', self.nim_jobID)

			#self.nim_updateServer()
			self.nim_updateShow()
			

		def nim_updateServer(self):
			self.nim_servers = {}
			self.nim_servers = nimAPI.get_jobServers(self.nim_jobID)
			self.nim_serverID = ''
			self.nim_serverOSPath = ''
			self.nim_serverDict = {}
			try:
				self.nim_serverChooser.clear()
				if self.nim_serverChooser:
					if len(self.nim_servers)>0:  
						for server in self.nim_servers:
							self.nim_serverDict[server['server']] = server['ID']
						for key, value in sorted(list(self.nim_serverDict.items()), reverse=False):
							self.nim_serverChooser.addItem(key)
			except:
				pass


		def nim_serverChanged(self):
			'''Action when job is selected'''
			#print "SERVER CHANGED"
			serverName = self.nim_serverChooser.currentText()
			if serverName:
				print("NIM: server=%s" % serverName)
				serverID = self.nim_serverDict[serverName]
				self.nim_serverID = serverID

				serverInfo = nimAPI.get_serverOSPath(serverID, self.nim_OS)
				if serverInfo:
					if len(serverInfo)>0:
						self.nim_serverOSPath = serverInfo[0]['serverOSPath']
						print("NIM: serverOSPath=%s" % self.nim_serverOSPath)
					else:
						print("NIM: No Server Found")
				else:
					print("NIM: No Data Returned")


		def nim_updateShow(self):
			self.nim_shows = {}
			self.nim_shows = nimAPI.get_shows(self.nim_jobID)
			#print self.nim_shows

			showIndex = 0
			showIter = 0
			self.nim_showDict = {}
			try:
				self.nim_showChooser.clear()
				if self.nim_showChooser:
					if len(self.nim_shows)>0:  
						for show in self.nim_shows:
							self.nim_showDict[show['showname']] = show['ID']
						for key, value in sorted(list(self.nim_showDict.items()), reverse=False):
							self.nim_showChooser.addItem(key)
							if nimHieroConnector.g_nim_showID:
								if nimHieroConnector.g_nim_showID == value:
									print("Found matching showID, show=", key)
									self.pref_show == key
									showIndex = showIter
							else:
								if self.pref_show == key:
									print("Found matching Show Name, show=", key)
									showIndex = showIter
							showIter += 1

						if self.pref_show != '':
							self.nim_showChooser.setCurrentIndex(showIndex)
			except:
				pass


		def nim_showChanged(self):
			'''Action when job is selected'''
			#print "SHOW CHANGED"
			showname = self.nim_showChooser.currentText()
			if showname:
				print("NIM: show=%s" % showname)

				showID = self.nim_showDict[showname]

				##set showID
				self.nim_showID = showID

				self.nim_showPaths = nimAPI.get_paths('show', showID)
				if self.nim_showPaths:
					if len(self.nim_showPaths)>0:
						#print "NIM: showPaths=", self.nim_showPaths
						self.nim_showFolder = self.nim_showPaths['root']
					else:
						print("NIM: No Show Paths Found")
				else:
					print("NIM: No Data Returned")
				

		def acceptTest(self):
			self.accept()


	class NimExportSelectedShotAction(QAction):
		'''Export Selected Shots to NIM'''
		'''		Add shots if no matching shots in NIM'''
		'''		If matching shots or trackItem is linked to NIM update info'''
		def __init__(self):
			QAction.__init__(self, "Update Selected Shots in NIM", None)
			#self.triggered.connect(self.exportShotSelection)
			self.triggered.connect(self.loadDialog)
			hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
			self._selectedPresets = []
			self.nim_showID = None

		def loadDialog(self):
			# Prepare list of selected items for export
			selection = self._selection

			# Create dialog
			dialog = NimHieroExport.NimExportDialog(selection, self._selectedPresets)
			# If dialog returns true
			if dialog.exec_():
				self.exportShotSelection(dialog)


		def exportShotSelection(self, dialog):
			"""Get the shot selection"""
			selection = self._selection
			updateThumbnail = True
			
			#global g_nim_showID
			nim_showID = dialog.nim_showID

			#Update Globals
			nimHieroConnector.g_nim_jobID = dialog.nim_jobID
			nimHieroConnector.g_nim_showID = dialog.nim_showID
			nimHieroConnector.g_nim_showFolder = dialog.nim_showFolder
			#nimHieroConnector.g_nim_serverID = dialog.nim_serverID
			#nimHieroConnector.g_nim_serverOSPath = dialog.nim_serverOSPath

			#Saving Preferences
			nimPrefs.update( 'Job', 'Nuke', dialog.nim_jobChooser.currentText() )
			nimPrefs.update( 'Show', 'Nuke', dialog.nim_showChooser.currentText() )


			nimConnect = nimHieroConnector.NimHieroConnector()

			if nim_showID != None:
				for trackItem in selection:
					#check for existing NIM data on trackItem
					name = trackItem.name()
					nim_tag = nimConnect.getNimTag(trackItem)

					if nim_tag != False:
						#update existing shot in NIM
						success = nimConnect.updateTrackItem(nim_showID, trackItem)
						if success:
							print("NIM: Successfully updated trackItem %s in NIM" % name)
							if updateThumbnail:
								success = nimConnect.updateShotIcon(trackItem)
								if success == False:
									print('NIM: Failed to upload icon')
						else:
							print("NIM: Failed to update trackItem %s in NIM" % name)
							continue
					else:
						#no tag found so create new shot in NIM... if shot exists with same name in NIM, link to this trackItem
						shotID = nimConnect.exportTrackItem(nim_showID, trackItem)
						if shotID == False:
							continue
						else:
							if updateThumbnail:
								success = nimConnect.updateShotIcon(trackItem)
								if success == False:
									print('NIM: Failed to upload icon')
				msgBox = QMessageBox()
				msgBox.setTextFormat(Qt.RichText)
				result = msgBox.information(None, "Update Shots", "The selected shots have been updated in NIM.", QMessageBox.Ok)
			else:
				print("NIM: No shows found")
				msgBox = QMessageBox()
				msgBox.setTextFormat(Qt.RichText)
				result = msgBox.information(None, "Warning", "No shows found. Nothing to update.", QMessageBox.Ok)
				

		def eventHandler(self, event):
			self._selection = None
			if hasattr(event.sender, 'getSelection') and event.sender.getSelection() is not None and len( event.sender.getSelection() ) != 0:
				selection = event.sender.getSelection() # Here, you could also use: hiero.ui.activeView().selection()

				self._selection = [shot for shot in selection if isinstance(shot,hiero.core.TrackItem)] # Filter out just TrackItems

				# Add the Menu to the right-click menu with an appropriate title
				if len(selection)>0:
					title = "Update Selected Shot in NIM" if len(self._selection)==1 else "Update Selected Shots in NIM"
					self.setText(title)
					hiero.nimMenu.addAction( self )


	class NimBuildTrackDialog(QDialog):
		def __init__(self,  selection, selectedPresets, parent=None):
			super(NimHieroExport.NimBuildTrackDialog, self).__init__(parent)
			
			self.pref_elementType = ''
			self.element = ''
			self.elementID = None
			self.nim_elementTypes = []
			self.nim_elementTypesDict = {}

			#Get NIM Element Types
			self.nim_elementTypes = nimAPI.get_elementTypes()
			#print self.nim_elementTypes

			self.setWindowTitle("NIM Build Track from Elements")
			self.setSizeGripEnabled(True)

			self._exportTemplate = None

			layout = QVBoxLayout()
			formLayout = QFormLayout()

			# Element Types: List box for element type selection
			self.nimElementTypeLabel = QLabel()
			self.nimElementTypeLabel.setText("Element Types:")
			layout.addWidget(self.nimElementTypeLabel)
			self.nim_elementTypeChooser = QComboBox()
			self.nim_elementTypeChooser.setToolTip("Choose the elementType you wish to create a track from.")
			self.nim_elementTypeChooser.currentIndexChanged.connect(self.nim_elementTypeChanged)
			layout.addWidget(self.nim_elementTypeChooser)

			#Add dictionary in ordered list
			if len(self.nim_elementTypes)>0:
				for element in self.nim_elementTypes:
					self.nim_elementTypesDict[element['name']] = element['ID']
				
				for key, value in sorted(list(self.nim_elementTypesDict.items()), reverse=False):
					self.nim_elementTypeChooser.addItem(key)
				if self.pref_elementType != '':
					self.nim_elementTypeChooser.setCurrentIndex(list(self.nim_elementTypesDict.keys()).index(self.pref_elementType))


			# Add the standard ok/cancel buttons, default to ok.
			self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
			self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("Build Track")
			self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
			self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Builds a new track based on the published NIM elements.")
			self._buttonbox.accepted.connect(self.acceptTest)
			self._buttonbox.rejected.connect(self.reject)
			layout.addWidget(self._buttonbox)

			self.setLayout(layout)

		def nim_elementTypeChanged(self):
			'''Action when element type is selected'''
			self.element = self.nim_elementTypeChooser.currentText()
			self.elementID = self.nim_elementTypesDict[self.element]
				
		def acceptTest(self):
			self.accept()


	class NimBuildTrackAction(QAction):
		'''Build a new track from shot render paths'''
		def __init__(self):
			QAction.__init__(self, "Build Track From Element", None)
			self.triggered.connect(self.loadDialog)
			hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
			self._selectedPresets = []
			self.nim_elementID = None

		def loadDialog(self):
			# Prepare list of selected items for export
			selection = self._selection

			# Create dialog
			dialog = NimHieroExport.NimBuildTrackDialog(selection, self._selectedPresets)
			# If dialog returns true
			if dialog.exec_():
				self.buildTrackFromElement(dialog)

		def eventHandler(self, event):
			self._selection = None
			if hasattr(event.sender, 'getSelection') and event.sender.getSelection() is not None and len( event.sender.getSelection() ) != 0:
				selection = event.sender.getSelection() # Here, you could also use: hiero.ui.activeView().selection()

				self._selection = [shot for shot in selection if isinstance(shot,hiero.core.TrackItem)] # Filter out just TrackItems

				# Add the Menu to the right-click menu with an appropriate title
				if len(selection)>0:
					title = "Build Track From Element" if len(self._selection)==1 else "Build Track From Elements"
					self.setText(title)
					hiero.nimMenu.addAction( self )

		def buildTrackFromElement(self, dialog):
			'''Create a new track from selected items render path'''
			print("NIM: Build Track From Element - %s" % dialog.element)

			#trackType = 'render'
			trackItems = self._selection
			if len(trackItems)>0:
				sequence = trackItems[0].parentSequence()

				nimConnect = nimHieroConnector.NimHieroConnector()
				nimConnect.createElementTrack(sequence, dialog.elementID, dialog.element, trackItems)
			else:
				print("NIM: No Track Items Found")
			return


	class NimClearTagsDialog(QDialog):
		def __init__(self,  selection, selectedPresets, parent=None):
			super(NimHieroExport.NimClearTagsDialog, self).__init__(parent)

			self.setWindowTitle("NIM: Tags")
			self.setSizeGripEnabled(True)

			self._exportTemplate = None

			layout = QVBoxLayout()
			formLayout = QFormLayout()

			# Element Types: List box for element type selection
			self.nimElementTypeLabel = QLabel()
			self.nimElementTypeLabel.setText("Clear All NIM Tags:")
			layout.addWidget(self.nimElementTypeLabel)

			# Add the standard ok/cancel buttons, default to ok.
			self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
			self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("OK")
			self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
			self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Clears all NIM Tags from selected trackItems.")
			self._buttonbox.accepted.connect(self.acceptTest)
			self._buttonbox.rejected.connect(self.reject)
			layout.addWidget(self._buttonbox)

			self.setLayout(layout)
				
		def acceptTest(self):
			self.accept()


	class NimClearTagsAction(QAction):
		'''Build a new track from shot render paths'''
		def __init__(self):
			QAction.__init__(self, "Clear All NIM Tags", None)
			self.triggered.connect(self.loadDialog)
			hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
			self._selectedPresets = []

		def loadDialog(self):
			# Prepare list of selected items for export
			selection = self._selection

			# Create dialog
			dialog = NimHieroExport.NimClearTagsDialog(selection, self._selectedPresets)
			# If dialog returns true
			if dialog.exec_():
				self.clearAllNimTags(dialog)

		def eventHandler(self, event):
			self._selection = None
			if hasattr(event.sender, 'getSelection') and event.sender.getSelection() is not None and len( event.sender.getSelection() ) != 0:
				selection = event.sender.getSelection() # Here, you could also use: hiero.ui.activeView().selection()

				self._selection = [shot for shot in selection if isinstance(shot,hiero.core.TrackItem)] # Filter out just TrackItems

				# Add the Menu to the right-click menu with an appropriate title
				if len(selection)>0:
					title = "Clear NIM Tag from Selected Shot" if len(self._selection)==1 else "Clear NIM Tags from Selected Shots"
					self.setText(title)
					hiero.nimMenu.addAction( self )

		def clearAllNimTags(self, dialog):
			'''Clears All NIM Tags from selected trackItems'''
			print("NIM: Clear NIM Tags")

			trackItems = self._selection
			if len(trackItems)>0:
				sequence = trackItems[0].parentSequence()

				for trackItem in trackItems:
					nimConnect = nimHieroConnector.NimHieroConnector()
					nim_tag = nimConnect.getNimTag(trackItem)
					if nim_tag != False:
						trackItem.removeTag(nim_tag)
						print("NIM: Removing Tag from ",trackItem.name())

			else:
				print("NIM: No Track Items Found")
			return



# Instantiate the action to get it to register itself.
NimHieroExport = NimHieroExport()
