#!/usr/bin/env python
#******************************************************************************
#
# Filename: Flame/python/nimFlameExport.py
# Version:  v2.6.01.170417
#
# Copyright (c) 2017 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

import os,sys,re,string
import os.path
import base64
import platform
import ntpath

# Relative path to append for NIM Scripts
nimFlameScriptPath = os.path.dirname(os.path.realpath(__file__))
nimFlameScriptPath = nimFlameScriptPath.replace('\\','/')
nimScriptPath = re.sub(r"\/plugins/Flame/python$", "", nimFlameScriptPath)
print "NIM - Script Path: %s" % nimScriptPath

# If relocating these scripts uncomment the line below and enter the fixed path
# to the NIM Connector Root directory
#
# nimScriptPath = [NIM_CONNECTOR_ROOT]
#

sys.path.append(nimScriptPath)

try:
	import nim_core.UI as nimUI
	import nim_core.nim_api as nimAPI
	import nim_core.nim_prefs as nimPrefs
	import nim_core.nim_file as nimFile
	import nim_core.nim as nim
except:
	print "NIM - Failed to load modules"

from PySide.QtGui import *
from PySide.QtCore import *

print "NIM - Loading nimFlameExport"


class NimExportDialog(QDialog):
	def __init__(self, parent=None):
		super(NimExportDialog, self).__init__(parent)

		self.result = ""

		try:
			#TODO: update prefs with Flame awareness
			self.app=nimFile.get_app()
			self.prefs=nimPrefs.read()
			self.user=self.prefs['NIM_User']
			self.pref_job=self.prefs[self.app+'_Job']
			self.pref_show=self.prefs[self.app+'_Show']
			self.pref_server=self.prefs[self.app+'_ServerPath']
		except:
			print "NIM - Failed to read NIM prefs"
			self.app='flame'
			self.prefs=''
			self.user='andrew'
			self.pref_job=0
			self.pref_show=0
			self.pref_server=''
			pass

		self.nim_OS = platform.system()
		
		try:
			self.nim_userID = nimAPI.get_userID(self.user)
			if not self.nim_userID :
				nimUI.GUI().update_user()
				userInfo=nim.NIM().userInfo()
				self.user = userInfo['name']
				self.nim_userID = userInfo['ID']
		except:
			# failing on user
			print "NIM - Failed to get userID"
			self.nim_userID = 1

		print "NIM - user=%s" % self.user
		print "NIM - userID=%s" % self.nim_userID
		print "NIM - default job=%s" % self.pref_job

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
			print "No Jobs Found"
			self.nim_jobs["None"]="0"
		
		self.nim_shows = []
		self.nim_showDict = {}
		self.nim_showID = None
		
		self.setWindowTitle("NIM Update Selected Shots")
		self.setSizeGripEnabled(True)

		self._exportTemplate = None

		tag_jobID = None
		tag_showID = None

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
			for key, value in sorted(self.nim_jobs.items(), reverse=True):
				self.nim_jobChooser.addItem(key)
				if self.nim_jobID:
					if self.nim_jobID == value:
						print "Found matching jobID, job=", key
						self.pref_job = key
						jobIndex = jobIter
				else:
					if self.pref_job == key:
						print "Found matching Job Name, job=", key
						jobIndex = jobIter
				jobIter += 1

			if self.pref_job != '':
				self.nim_jobChooser.setCurrentIndex(jobIndex)

		self.nim_jobChooser.currentIndexChanged.connect(self.nim_jobChanged)

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

		self.nim_updateShow()
		


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
					for key, value in sorted(self.nim_showDict.items(), reverse=False):
						self.nim_showChooser.addItem(key)
						'''
						if self.g_nim_showID:
							if self.g_nim_showID == value:
								print "Found matching showID, show=", key
								self.pref_show == key
								showIndex = showIter
						else:
							if self.pref_show == key:
								print "Found matching Show Name, show=", key
								showIndex = showIter
						'''
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
			print "NIM: show=%s" % showname

			showID = self.nim_showDict[showname]

			##set showID
			self.nim_showID = showID

			self.nim_showPaths = nimAPI.get_paths('show', showID)
			if self.nim_showPaths:
				if len(self.nim_showPaths)>0:
					#print "NIM: showPaths=", self.nim_showPaths
					self.nim_showFolder = self.nim_showPaths['root']
				else:
					print "NIM: No Show Paths Found"
			else:
				print "NIM: No Data Returned"
			
	def acceptTest(self):
		self.accept()


def nimExportShots(nim_showID=None, info=None) :
	'''Export Shots to NIM'''

	success = False

	if nim_showID != None:

		nim_shotID = False
		nim_shotName = info['shotName']
		nim_sourceIn = info['sourceIn']
		nim_sourceOut = info['sourceOut']
		nim_handleIn = info['handleIn']
		nim_handleOut = info['handleOut']
		nim_duration = nim_sourceOut - nim_sourceIn
		nim_assetType = info['assetType']
		nim_destinationPath = info['destinationPath']
		nim_resolvedPath = info['resolvedPath']
		nim_fullPath = os.path.join(nim_destinationPath, nim_resolvedPath)

		print "NIM - Creating New Shot"
		shotInfo = nimAPI.add_shot( nim_showID, nim_shotName, nim_duration )
		#print shotInfo

		if shotInfo['success'] == 'true':
			nim_shotID = shotInfo['ID']
			print "NIM - nim_shotID: %s" % nim_shotID
			if 'error' in shotInfo:
				print "NIM - WARNING: %s" % shotInfo['error']
		else:
			if shotInfo['error']:
				#error exists
				print "NIM - ERROR: %s" % shotInfo['error']
			nim_shotID = False

		if nim_shotID == False:
			pass
		else:
			if nim_assetType == 'video' :
				icon_success = False

				mediaExt = nim_fullPath.rpartition('.')[2]
				pathPartition = nim_fullPath.rpartition('[')
				pathRoot = pathPartition[0]
				iconFrame = pathPartition[2].rpartition('-')[0]

				iconPath = string.join([pathRoot, iconFrame,'.',mediaExt],'')
				print "NIM - iconPath: %s" % iconPath

				print "NIM - Updating Thumbnail"
				icon_success = updateShotIcon(nim_shotID, iconPath)
				if icon_success :
					print 'NIM - Shot Icon uploaded'
				else :
					print 'NIM - Failed to upload icon'
			else :
				print 'NIM - Skipping icon upload for non-video assetType'

			
			# Add Media Item as Element
			element_result = nimAPI.add_element( parent='shot', parentID=nim_shotID, path=nim_fullPath, name=nim_resolvedPath, \
										startFrame=nim_sourceIn, endFrame=nim_sourceOut, handles=nim_handleIn, isPublished=False )


		print "NIM - %s has been updated in NIM." % nim_shotName
		success = True
	else:
		print "NIM - No shows found"

	return success


def updateShotIcon(nim_shotID=None, image_path='') :
	success = False

	if(nim_shotID) :

		apiInfo = nimAPI.upload_shotIcon( nim_shotID, image_path )

		#print apiInfo
		if apiInfo == True:
			status_msg = "NIM - Successfully uploaded icon for shotID: %s" % nim_shotID
			print status_msg
			success = True
		else:
			status_msg = "NIM - Failed to upload icon for shotID: %s" % nim_shotID
			print status_msg

	return success



