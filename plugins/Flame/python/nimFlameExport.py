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

import os,sys,re,string,traceback
import base64
import platform
import ntpath
import json
import xml.dom.minidom as minidom
import shutil


try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET


# Relative path to append for NIM Scripts
nimFlamePythonPath = os.path.dirname(os.path.realpath(__file__))
nimFlamePythonPath = nimFlamePythonPath.replace('\\','/')
nimScriptPath = re.sub(r"\/plugins/Flame/python$", "", nimFlamePythonPath)
nimFlamePresetPath = os.path.join(re.sub(r"\/python$", "", nimFlamePythonPath),'presets')
nimFlameImgPath = os.path.join(re.sub(r"\/python$", "", nimFlamePythonPath),'img')

print "NIM Script Path: %s" % nimScriptPath
print "NIM Python Path: %s" % nimFlamePythonPath
print "NIM Preset Path: %s" % nimFlamePresetPath
print "NIM Image Path: %s" % nimFlameImgPath



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


#  Make prefs:
import nim_core.nim_prefs as menuPrefs
menuPrefs.mk_default( notify_success=True )


try :
	# from libwiretapPythonClientAPI import *
	nimExport_app = os.environ.get('NIM_APP', '-1')
	print "NIM - Current Application: %s" % nimExport_app
except :
	print "NIM - failed to load Wiretap API"


class NimScanForVersionsDialog(QDialog):
	def __init__(self, parent=None):
		super(NimScanForVersionsDialog, self).__init__(parent)

		self.result = ""

		try:
			#self.app=nimFile.get_app()
			self.app = 'Flame'
			self.prefs=nimPrefs.read()
			print "NIM - Prefs: "
			print self.prefs

			if 'NIM_User' in self.prefs :
				self.user=self.prefs['NIM_User']
			else :
				self.user = ''

			if self.app+'_Job' in self.prefs:
				self.pref_job=self.prefs[self.app+'_Job']
			else :
				self.pref_job = ''

			if self.app+'_Show' in self.prefs:
				self.pref_show=self.prefs[self.app+'_Show']
			else :
				self.pref_show= ''

			if self.app+'_ServerPath' in self.prefs:
				self.pref_server=self.prefs[self.app+'_ServerPath']
			else :
				self.pref_server= ''

			if self.app+'_ServerID' in self.prefs:
				self.pref_serverID=self.prefs[self.app+'_ServerID']
			else :
				self.pref_serverID= ''

			print "NIM - Prefs successfully read"

		except:
			print "NIM - Failed to read NIM prefs"
			print 'NIM - ERROR: %s' % traceback.print_exc()
			self.app='Flame'
			self.prefs=''
			self.user=''
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
			self.nim_userID = 0

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
		
		self.setWindowTitle("NIM: Scan For Versions")
		self.setStyleSheet("QLabel {font: 14pt}")
		self.setSizeGripEnabled(True)

		tag_jobID = None
		tag_showID = None

		layout = QVBoxLayout()
		formLayout = QFormLayout()
		groupBox = QGroupBox()
		groupLayout = QFormLayout()
		groupBox.setLayout(groupLayout)

		pixmap = QPixmap(1, 24)
		pixmap.fill(Qt.transparent)
		self.clearPix = QIcon(pixmap)
		

		# Header
		horizontalLayout_header = QHBoxLayout()
		horizontalLayout_header.setSpacing(-1)
		horizontalLayout_header.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_header.setObjectName("horizontalLayout_header")
		connectorImage = QPixmap(nimFlameImgPath+"/nim2flm.png")
		self.nimConnectorHeader = QLabel()
		self.nimConnectorHeader.setPixmap(connectorImage)
		horizontalLayout_header.addWidget(self.nimConnectorHeader)

		# Comment Label
		horizontalLayout_commentDesc = QHBoxLayout()
		horizontalLayout_commentDesc.setSpacing(-1)
		horizontalLayout_commentDesc.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_commentDesc.setObjectName("horizontalLayout_commentDesc")
		self.nimCommentLabel = QLabel()
		self.nimCommentLabel.setText("Select the show to scan for versions:")
		horizontalLayout_commentDesc.addWidget(self.nimCommentLabel)
		horizontalLayout_commentDesc.setStretch(1, 40)

		# JOBS: List box for job selection
		horizontalLayout_job = QHBoxLayout()
		horizontalLayout_job.setSpacing(-1)
		horizontalLayout_job.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_job.setObjectName("horizontalLayout_job")
		self.nimJobLabel = QLabel()
		self.nimJobLabel.setFixedWidth(120)
		self.nimJobLabel.setText("Job:")
		horizontalLayout_job.addWidget(self.nimJobLabel)
		self.nim_jobChooser = QComboBox()
		self.nim_jobChooser.setToolTip("Choose the job you wish to export shots to.")
		self.nim_jobChooser.setMinimumHeight(28)
		self.nim_jobChooser.setIconSize(QSize(1, 24))
		horizontalLayout_job.addWidget(self.nim_jobChooser)
		horizontalLayout_job.setStretch(1, 40)
		

		# JOBS: Add dictionary in ordered list
		jobIndex = 0
		jobIter = 0
		if len(self.nim_jobs)>0:
			for key, value in sorted(self.nim_jobs.items(), reverse=True):
				self.nim_jobChooser.addItem(self.clearPix, key)
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
		horizontalLayout_show = QHBoxLayout()
		horizontalLayout_show.setSpacing(-1)
		horizontalLayout_show.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_show.setObjectName("horizontalLayout_show")
		self.nimShowLabel = QLabel()
		self.nimShowLabel.setFixedWidth(120)
		self.nimShowLabel.setText("Show:")
		horizontalLayout_show.addWidget(self.nimShowLabel)
		self.nim_showChooser = QComboBox()
		self.nim_showChooser.setToolTip("Choose the show you wish to export shots to.")
		self.nim_showChooser.setMinimumHeight(28)
		self.nim_showChooser.setIconSize(QSize(1, 24))
		horizontalLayout_show.addWidget(self.nim_showChooser)
		horizontalLayout_show.setStretch(1, 40)
		self.nim_showChooser.currentIndexChanged.connect(self.nim_showChanged)
	

		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText(" Scan for Versions ")
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Scans the selected show for element types that match the batchOpenClip and adds them to the batchOpenClip.")
		self._buttonbox.accepted.connect(self.acceptTest)
		self._buttonbox.rejected.connect(self.reject)
		horizontalLayout_OkCancel = QHBoxLayout()
		horizontalLayout_OkCancel.setSpacing(-1)
		horizontalLayout_OkCancel.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_OkCancel.setObjectName("horizontalLayout_OkCancel")
		spacerItem4 = QSpacerItem(175, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
		horizontalLayout_OkCancel.addItem(spacerItem4)
		horizontalLayout_OkCancel.addWidget(self._buttonbox)
		horizontalLayout_OkCancel.setStretch(1, 40)

		groupLayout.setLayout(0, QFormLayout.SpanningRole, horizontalLayout_header)
		groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout_commentDesc)
		groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout_job)
		groupLayout.setLayout(3, QFormLayout.SpanningRole, horizontalLayout_show)
		groupLayout.setLayout(4, QFormLayout.SpanningRole, horizontalLayout_OkCancel)

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
						self.nim_showChooser.addItem(self.clearPix, key)
						'''
						if self.nim_showID:
							if self.nim_showID == value:
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
		# Saving Preferences
		nimPrefs.update( 'Job', 'Flame', self.nim_jobID )
		nimPrefs.update( 'Show', 'Flame', self.nim_showID )

		self.accept()


class NimBatchExportDialog(QDialog):
	def __init__(self, parent=None):
		super(NimBatchExportDialog, self).__init__(parent)

		self.result = ""
		self.nim_comment = ""

		layout = QVBoxLayout()
		formLayout = QFormLayout()
		groupBox = QGroupBox()
		groupLayout = QFormLayout()
		groupBox.setLayout(groupLayout)

		pixmap = QPixmap(1, 24)
		pixmap.fill(Qt.transparent)
		self.clearPix = QIcon(pixmap)
		
		# Header Image
		horizontalLayout_header = QHBoxLayout()
		horizontalLayout_header.setSpacing(-1)
		horizontalLayout_header.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_header.setObjectName("horizontalLayout_header")
		connectorImage = QPixmap(nimFlameImgPath+"/flm2nim.png")
		self.nimConnectorHeader = QLabel()
		self.nimConnectorHeader.setPixmap(connectorImage)
		horizontalLayout_header.addWidget(self.nimConnectorHeader)

		# Comment Label
		horizontalLayout_commentDesc = QHBoxLayout()
		horizontalLayout_commentDesc.setSpacing(-1)
		horizontalLayout_commentDesc.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_commentDesc.setObjectName("horizontalLayout_commentDesc")
		self.nimCommentLabel = QLabel()
		self.nimCommentLabel.setText("Enter the comment to use for logged batch files.")
		horizontalLayout_commentDesc.addWidget(self.nimCommentLabel)
		horizontalLayout_commentDesc.setStretch(1, 40)

		# Create textbox
		horizontalLayout_comment = QHBoxLayout()
		horizontalLayout_comment.setSpacing(-1)
		horizontalLayout_comment.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_comment.setObjectName("horizontalLayout_comment")
		self.commentBox = QLineEdit()
		self.commentBox.move(20, 20)
		self.commentBox.resize(280,40)
		horizontalLayout_comment.addWidget(self.commentBox)
		horizontalLayout_comment.setStretch(1, 40)

		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText(" Log to NIM ")
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Log render and batch files to NIM")
		self._buttonbox.accepted.connect(self.acceptTest)
		self._buttonbox.rejected.connect(self.reject)
		horizontalLayout_OkCancel = QHBoxLayout()
		horizontalLayout_OkCancel.setSpacing(-1)
		horizontalLayout_OkCancel.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_OkCancel.setObjectName("horizontalLayout_OkCancel")
		spacerItem4 = QSpacerItem(175, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
		horizontalLayout_OkCancel.addItem(spacerItem4)
		horizontalLayout_OkCancel.addWidget(self._buttonbox)
		horizontalLayout_OkCancel.setStretch(1, 40)


		groupLayout.setLayout(0, QFormLayout.SpanningRole, horizontalLayout_header)
		groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout_commentDesc)
		groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout_comment)
		groupLayout.setLayout(3, QFormLayout.SpanningRole, horizontalLayout_OkCancel)

		self.setLayout(groupLayout)
		layout.addWidget(groupBox)


	def acceptTest(self):
		# Get Current Values For Static Objects
		self.nim_comment = self.commentBox.text()
		self.accept()


class NimExportDialog(QDialog):
	def __init__(self, parent=None):
		super(NimExportDialog, self).__init__(parent)

		self.result = ""

		try:
			#self.app=nimFile.get_app()
			self.app = 'Flame'
			self.prefs=nimPrefs.read()
			print "NIM - Prefs: "
			print self.prefs

			if 'NIM_User' in self.prefs :
				self.user=self.prefs['NIM_User']
			else :
				self.user = ''

			if self.app+'_Job' in self.prefs:
				self.pref_job=self.prefs[self.app+'_Job']
			else :
				self.pref_job = ''

			if self.app+'_Show' in self.prefs:
				self.pref_show=self.prefs[self.app+'_Show']
			else :
				self.pref_show= ''

			if self.app+'_ServerPath' in self.prefs:
				self.pref_server=self.prefs[self.app+'_ServerPath']
			else :
				self.pref_server= ''

			if self.app+'_ServerID' in self.prefs:
				self.pref_serverID=self.prefs[self.app+'_ServerID']
			else :
				self.pref_serverID= ''

			print "NIM - Prefs successfully read"

		except:
			print "NIM - Failed to read NIM prefs"
			print 'NIM - ERROR: %s' % traceback.print_exc()
			self.app='Flame'
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
			self.nim_userID = 0

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

		
		#Get NIM Element Types
		self.nim_elementTypes = []
		self.nim_elementTypesDict = {}
		self.nim_elementTypes = nimAPI.get_elementTypes()
		if len(self.nim_elementTypes)>0:
			for element in self.nim_elementTypes:
				self.nim_elementTypesDict[element['name']] = element['ID']

		self.videoElement = ''
		self.videoElementID = 0
		self.audioElement = ''
		self.audioElementID = 0
		self.openClipElement = ''
		self.openClipElementID = 0
		self.batchOpenClipElement = ''
		self.batchOpenClipElementID = 0


		#Get NIM Task Types
		self.nim_taskTypes = []
		self.nim_taskTypesDict = {}
		self.nim_taskFolderDict = {}
		self.nim_taskTypes = nimAPI.get_tasks(app='NUKE', userType='all')
		if len(self.nim_taskTypes)>0:
			for task in self.nim_taskTypes:
				self.nim_taskTypesDict[task['name']] = task['ID']
				self.nim_taskFolderDict[task['ID']] = task['folder']

		self.batchTaskType = ''
		self.batchTaskTypeID = 0
		self.batchTaskTypeFolder = ''


		#Get NIM Jobs
		self.nim_jobID = None
		self.nim_jobs = nimAPI.get_jobs(self.nim_userID)
		if not self.nim_jobs :
			print "No Jobs Found"
			self.nim_jobs["None"]="0"
		
		self.nim_shows = []
		self.nim_showDict = {}
		self.nim_showID = None
		
		self.setWindowTitle("NIM: Export Sequence")
		self.setStyleSheet("QLabel {font: 14pt}")
		self.setSizeGripEnabled(True)

		self._exportTemplate = None

		tag_jobID = None
		tag_showID = None

		

		layout = QVBoxLayout()
		formLayout = QFormLayout()
		groupBox = QGroupBox()
		groupLayout = QFormLayout()
		groupBox.setLayout(groupLayout)

		pixmap = QPixmap(1, 24)
		pixmap.fill(Qt.transparent)
		self.clearPix = QIcon(pixmap)
		

		# Flame 2 NIM image
		# 400x88
		# PRESETS: List box for preset selection
		horizontalLayout_header = QHBoxLayout()
		horizontalLayout_header.setSpacing(-1)
		horizontalLayout_header.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_header.setObjectName("horizontalLayout_header")
		connectorImage = QPixmap(nimFlameImgPath+"/flm2nim.png")
		self.nimConnectorHeader = QLabel()
		self.nimConnectorHeader.setPixmap(connectorImage)
		horizontalLayout_header.addWidget(self.nimConnectorHeader)


		# PRESETS: List box for preset selection
		horizontalLayout_preset = QHBoxLayout()
		horizontalLayout_preset.setSpacing(-1)
		horizontalLayout_preset.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_preset.setObjectName("horizontalLayout_preset")
		self.nimPresetLabel = QLabel()
		self.nimPresetLabel.setFixedWidth(120)
		self.nimPresetLabel.setText("Export Preset:")
		horizontalLayout_preset.addWidget(self.nimPresetLabel)
		self.nim_presetChooser = QComboBox()
		self.nim_presetChooser.setToolTip("Choose the NIM preset to use for this export.")
		self.nim_presetChooser.setMinimumHeight(28)
		self.nim_presetChooser.setIconSize(QSize(1, 24))
		horizontalLayout_preset.addWidget(self.nim_presetChooser)
		horizontalLayout_preset.setStretch(1, 40)

		presetList = self.nim_getPresets()
		if len(presetList) > 0:
			for preset in presetList :
				 self.nim_presetChooser.addItem(self.clearPix, preset)

		self.nim_presetChooser.currentIndexChanged.connect(self.nim_presetChanged)

		# JOBS: List box for job selection
		horizontalLayout_job = QHBoxLayout()
		horizontalLayout_job.setSpacing(-1)
		horizontalLayout_job.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_job.setObjectName("horizontalLayout_job")
		self.nimJobLabel = QLabel()
		self.nimJobLabel.setFixedWidth(120)
		self.nimJobLabel.setText("Job:")
		horizontalLayout_job.addWidget(self.nimJobLabel)
		self.nim_jobChooser = QComboBox()
		self.nim_jobChooser.setToolTip("Choose the job you wish to export shots to.")
		self.nim_jobChooser.setMinimumHeight(28)
		self.nim_jobChooser.setIconSize(QSize(1, 24))
		horizontalLayout_job.addWidget(self.nim_jobChooser)
		horizontalLayout_job.setStretch(1, 40)
		

		# JOBS: Add dictionary in ordered list
		jobIndex = 0
		jobIter = 0
		if len(self.nim_jobs)>0:
			for key, value in sorted(self.nim_jobs.items(), reverse=True):
				self.nim_jobChooser.addItem(self.clearPix, key)
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


		# SERVERS: List box for server selection
		horizontalLayout_server = QHBoxLayout()
		horizontalLayout_server.setSpacing(-1)
		horizontalLayout_server.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_server.setObjectName("horizontalLayout_server")
		self.nimServerLabel = QLabel()
		self.nimServerLabel.setFixedWidth(120)
		self.nimServerLabel.setText("Server:")
		horizontalLayout_server.addWidget(self.nimServerLabel)
		self.nim_serverChooser = QComboBox()
		self.nim_serverChooser.setToolTip("Choose the server you wish to export shots to.")
		self.nim_serverChooser.setMinimumHeight(28)
		self.nim_serverChooser.setIconSize(QSize(1, 24))
		horizontalLayout_server.addWidget(self.nim_serverChooser)
		horizontalLayout_server.setStretch(1, 40)
		self.nim_serverChooser.currentIndexChanged.connect(self.nim_serverChanged)
		

		# SHOWS: List box for show selection
		horizontalLayout_show = QHBoxLayout()
		horizontalLayout_show.setSpacing(-1)
		horizontalLayout_show.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_show.setObjectName("horizontalLayout_show")
		self.nimShowLabel = QLabel()
		self.nimShowLabel.setFixedWidth(120)
		self.nimShowLabel.setText("Show:")
		horizontalLayout_show.addWidget(self.nimShowLabel)
		self.nim_showChooser = QComboBox()
		self.nim_showChooser.setToolTip("Choose the show you wish to export shots to.")
		self.nim_showChooser.setMinimumHeight(28)
		self.nim_showChooser.setIconSize(QSize(1, 24))
		horizontalLayout_show.addWidget(self.nim_showChooser)
		horizontalLayout_show.setStretch(1, 40)
		self.nim_showChooser.currentIndexChanged.connect(self.nim_showChanged)
	


		# -- ELEMENT TYPES -- #

		horizontalLayout_elementSpacer = QHBoxLayout()
		horizontalLayout_elementSpacer.setSpacing(-1)
		horizontalLayout_elementSpacer.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_elementSpacer.setObjectName("horizontalLayout_elementSpacer")
		elementSpacer = QLabel()
		elementSpacer.setText("")
		horizontalLayout_elementSpacer.addWidget(elementSpacer)
		horizontalLayout_elementSpacer.setStretch(1, 40)


		# Elements Label
		horizontalLayout_elementDesc = QHBoxLayout()
		horizontalLayout_elementDesc.setSpacing(-1)
		horizontalLayout_elementDesc.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_elementDesc.setObjectName("horizontalLayout_elementDesc")
		self.nimElementSectionLabel = QLabel()
		self.nimElementSectionLabel.setText("Select NIM element type to assign to export media:")
		horizontalLayout_elementDesc.addWidget(self.nimElementSectionLabel)
		horizontalLayout_elementDesc.setStretch(1, 40)



		# video - exported media
		horizontalLayout_video = QHBoxLayout()
		horizontalLayout_video.setSpacing(-1)
		horizontalLayout_video.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_video.setObjectName("horizontalLayout_video")
		self.nimVideoLabel = QLabel()
		self.nimVideoLabel.setFixedWidth(120)
		self.nimVideoLabel.setText("Video:")
		horizontalLayout_video.addWidget(self.nimVideoLabel)
		self.nim_videoChooser = QComboBox()
		self.nim_videoChooser.setToolTip("Choose the NIM element type for video media.")
		self.nim_videoChooser.setMinimumHeight(28)
		self.nim_videoChooser.setIconSize(QSize(1, 24))
		horizontalLayout_video.addWidget(self.nim_videoChooser)
		horizontalLayout_video.setStretch(1, 40)

		for key, value in sorted(self.nim_elementTypesDict.items(), reverse=False):
			self.nim_videoChooser.addItem(self.clearPix, key)

		self.nim_videoChooser.currentIndexChanged.connect(self.nim_videoElementChanged)


		# audio - exported media
		horizontalLayout_audio = QHBoxLayout()
		horizontalLayout_audio.setSpacing(-1)
		horizontalLayout_audio.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_audio.setObjectName("horizontalLayout_audio")
		self.nimAudioLabel = QLabel()
		self.nimAudioLabel.setFixedWidth(120)
		self.nimAudioLabel.setText("Audio:")
		horizontalLayout_audio.addWidget(self.nimAudioLabel)
		self.nim_audioChooser = QComboBox()
		self.nim_audioChooser.setToolTip("Choose the NIM element type for audio media.")
		self.nim_audioChooser.setMinimumHeight(28)
		self.nim_audioChooser.setIconSize(QSize(1, 24))
		horizontalLayout_audio.addWidget(self.nim_audioChooser)
		horizontalLayout_audio.setStretch(1, 40)

		for key, value in sorted(self.nim_elementTypesDict.items(), reverse=False):
			self.nim_audioChooser.addItem(self.clearPix, key)
		
		self.nim_audioChooser.currentIndexChanged.connect(self.nim_audioElementChanged)

		# openClip - Source Clip
		horizontalLayout_openClip = QHBoxLayout()
		horizontalLayout_openClip.setSpacing(-1)
		horizontalLayout_openClip.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_openClip.setObjectName("horizontalLayout_openClip")
		self.nimOpenClipLabel = QLabel()
		self.nimOpenClipLabel.setFixedWidth(120)
		self.nimOpenClipLabel.setText("Source OpenClip:")
		horizontalLayout_openClip.addWidget(self.nimOpenClipLabel)
		self.nim_openClipChooser = QComboBox()
		self.nim_openClipChooser.setToolTip("Choose the NIM element type for openClip media.")
		self.nim_openClipChooser.setMinimumHeight(28)
		self.nim_openClipChooser.setIconSize(QSize(1, 24))
		horizontalLayout_openClip.addWidget(self.nim_openClipChooser)
		horizontalLayout_openClip.setStretch(1, 40)
		
		for key, value in sorted(self.nim_elementTypesDict.items(), reverse=False):
			self.nim_openClipChooser.addItem(self.clearPix, key)
		
		self.nim_openClipChooser.currentIndexChanged.connect(self.nim_openClipElementChanged)

		# video - exported media
		horizontalLayout_batchOpenClip = QHBoxLayout()
		horizontalLayout_batchOpenClip.setSpacing(-1)
		horizontalLayout_batchOpenClip.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_batchOpenClip.setObjectName("horizontalLayout_batchOpenClip")
		self.nimBatchOpenClipLabel = QLabel()
		self.nimBatchOpenClipLabel.setFixedWidth(120)
		self.nimBatchOpenClipLabel.setText("Batch OpenClip:")
		horizontalLayout_batchOpenClip.addWidget(self.nimBatchOpenClipLabel)
		self.nim_batchOpenClipChooser = QComboBox()
		self.nim_batchOpenClipChooser.setToolTip("Choose the NIM element type for batchOpenClip media.")
		self.nim_batchOpenClipChooser.setMinimumHeight(28)
		self.nim_batchOpenClipChooser.setIconSize(QSize(1, 24))
		horizontalLayout_batchOpenClip.addWidget(self.nim_batchOpenClipChooser)
		horizontalLayout_batchOpenClip.setStretch(1, 40)
		
		for key, value in sorted(self.nim_elementTypesDict.items(), reverse=False):
			self.nim_batchOpenClipChooser.addItem(self.clearPix, key)
		
		self.nim_batchOpenClipChooser.currentIndexChanged.connect(self.nim_batchOpenClipElementChanged)


		# -- TASK TYPES -- #

		horizontalLayout_taskSpacer = QHBoxLayout()
		horizontalLayout_taskSpacer.setSpacing(-1)
		horizontalLayout_taskSpacer.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_taskSpacer.setObjectName("horizontalLayout_taskSpacer")
		taskSpacer = QLabel()
		taskSpacer.setText("")
		horizontalLayout_taskSpacer.addWidget(taskSpacer)
		horizontalLayout_taskSpacer.setStretch(1, 40)


		# Task Label
		horizontalLayout_taskDesc = QHBoxLayout()
		horizontalLayout_taskDesc.setSpacing(-1)
		horizontalLayout_taskDesc.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_taskDesc.setObjectName("horizontalLayout_taskDesc")
		self.nimElementSectionLabel = QLabel()
		self.nimElementSectionLabel.setText("Select NIM task type to assign to batch files:")
		horizontalLayout_taskDesc.addWidget(self.nimElementSectionLabel)
		horizontalLayout_taskDesc.setStretch(1, 40)


		# batch - versioned comps
		horizontalLayout_batch = QHBoxLayout()
		horizontalLayout_batch.setSpacing(-1)
		horizontalLayout_batch.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_batch.setObjectName("horizontalLayout_batch")
		self.nimBatchLabel = QLabel()
		self.nimBatchLabel.setFixedWidth(120)
		self.nimBatchLabel.setText("Batch:")
		horizontalLayout_batch.addWidget(self.nimBatchLabel)
		self.nim_batchChooser = QComboBox()
		self.nim_batchChooser.setToolTip("Choose the NIM task type to assign to batch files.")
		self.nim_batchChooser.setMinimumHeight(28)
		self.nim_batchChooser.setIconSize(QSize(1, 24))
		horizontalLayout_batch.addWidget(self.nim_batchChooser)
		horizontalLayout_batch.setStretch(1, 40)

		for key, value in sorted(self.nim_taskTypesDict.items(), reverse=False):
			self.nim_batchChooser.addItem(self.clearPix, key)

		self.nim_batchChooser.currentIndexChanged.connect(self.nim_batchTaskChanged)


		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("Export")
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Executes exports on selection for each selected preset")
		self._buttonbox.accepted.connect(self.acceptTest)
		self._buttonbox.rejected.connect(self.reject)
		horizontalLayout_OkCancel = QHBoxLayout()
		horizontalLayout_OkCancel.setSpacing(-1)
		horizontalLayout_OkCancel.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_OkCancel.setObjectName("horizontalLayout_OkCancel")
		spacerItem4 = QSpacerItem(175, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
		horizontalLayout_OkCancel.addItem(spacerItem4)
		horizontalLayout_OkCancel.addWidget(self._buttonbox)
		horizontalLayout_OkCancel.setStretch(1, 40)


		groupLayout.setLayout(0, QFormLayout.SpanningRole, horizontalLayout_header)

		groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout_preset)
		groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout_job)
		groupLayout.setLayout(3, QFormLayout.SpanningRole, horizontalLayout_server)
		groupLayout.setLayout(4, QFormLayout.SpanningRole, horizontalLayout_show)

		groupLayout.setLayout(5, QFormLayout.SpanningRole, horizontalLayout_elementSpacer)
		groupLayout.setLayout(6, QFormLayout.SpanningRole, horizontalLayout_elementDesc)
		groupLayout.setLayout(7, QFormLayout.SpanningRole, horizontalLayout_video)
		groupLayout.setLayout(8, QFormLayout.SpanningRole, horizontalLayout_audio)
		groupLayout.setLayout(9, QFormLayout.SpanningRole, horizontalLayout_openClip)
		groupLayout.setLayout(10, QFormLayout.SpanningRole, horizontalLayout_batchOpenClip)

		groupLayout.setLayout(11, QFormLayout.SpanningRole, horizontalLayout_taskSpacer)
		groupLayout.setLayout(12, QFormLayout.SpanningRole, horizontalLayout_taskDesc)
		groupLayout.setLayout(13, QFormLayout.SpanningRole, horizontalLayout_batch)

		groupLayout.setLayout(14, QFormLayout.SpanningRole, horizontalLayout_OkCancel)

		self.setLayout(groupLayout)
		layout.addWidget(groupBox)

		self.nim_jobChanged() #trigger job changed to load choosers


	def nim_getPresets(self):
		presetList = []
		for preset in os.listdir(nimFlamePresetPath+'/sequence_publish'):
			print "PRESET: %s" % preset
			if preset.endswith(".xml"):
				presetName = preset.rpartition('.')[0]
				presetList.append(presetName)
				
		return presetList


	def nim_presetChanged(self):
		'''Action when task type is selected'''
		self.nim_preset = self.nim_presetChooser.currentText()


	def nim_jobChanged(self):
		'''Action when job is selected'''
		#print "JOB CHANGED"
		job = self.nim_jobChooser.currentText()
		self.nim_jobID = self.nim_jobs[job]
		self.nim_jobPaths = nimAPI.get_paths('job', self.nim_jobID)

		self.nim_updateServer()
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
					for key, value in sorted(self.nim_serverDict.items(), reverse=False):
						self.nim_serverChooser.addItem(self.clearPix, key)
		except:
			pass


	def nim_serverChanged(self):
		'''Action when job is selected'''
		#print "SERVER CHANGED"
		serverName = self.nim_serverChooser.currentText()
		if serverName:
			print "NIM: server=%s" % serverName
			serverID = self.nim_serverDict[serverName]
			self.nim_serverID = serverID

			serverInfo = nimAPI.get_serverOSPath(serverID, self.nim_OS)
			if serverInfo:
				if len(serverInfo)>0:
					self.nim_serverOSPath = serverInfo[0]['serverOSPath']
					print "NIM: serverOSPath=%s" % self.nim_serverOSPath
				else:
					print "NIM: No Server Found"
			else:
				print "NIM: No Data Returned"


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
						self.nim_showChooser.addItem(self.clearPix, key)
						'''
						if self.nim_showID:
							if self.nim_showID == value:
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
	

	def nim_videoElementChanged(self):
		'''Action when video type is selected'''
		self.videoElement = self.nim_videoChooser.currentText()
		self.videoElementID = self.nim_elementTypesDict[self.videoElement]


	def nim_audioElementChanged(self):
		'''Action when video type is selected'''
		self.audioElement = self.nim_audioChooser.currentText()
		self.audioElementID = self.nim_elementTypesDict[self.audioElement]


	def nim_openClipElementChanged(self):
		'''Action when video type is selected'''
		self.openClipElement = self.nim_openClipChooser.currentText()
		self.openClipElementID = self.nim_elementTypesDict[self.openClipElement]


	def nim_batchOpenClipElementChanged(self):
		'''Action when video type is selected'''
		self.batchOpenClipElement = self.nim_batchOpenClipChooser.currentText()
		self.batchOpenClipElementID = self.nim_elementTypesDict[self.batchOpenClipElement]


	def nim_batchTaskChanged(self):
		'''Action when task type is selected'''
		self.batchTaskType = self.nim_batchChooser.currentText()
		self.batchTaskTypeID = self.nim_taskTypesDict[self.batchTaskType]
		self.batchTaskTypeFolder = self.nim_taskFolderDict[self.batchTaskTypeID]


	def acceptTest(self):
		# Get Current Values For Static Objects
		self.nim_preset = self.nim_presetChooser.currentText()
		self.videoElement = self.nim_videoChooser.currentText()
		self.videoElementID = self.nim_elementTypesDict[self.videoElement]
		self.audioElement = self.nim_audioChooser.currentText()
		self.audioElementID = self.nim_elementTypesDict[self.audioElement]
		self.openClipElement = self.nim_openClipChooser.currentText()
		self.openClipElementID = self.nim_elementTypesDict[self.openClipElement]
		self.batchOpenClipElement = self.nim_batchOpenClipChooser.currentText()
		self.batchOpenClipElementID = self.nim_elementTypesDict[self.batchOpenClipElement]
		self.batchTaskType = self.nim_batchChooser.currentText()
		self.batchTaskTypeID = self.nim_taskTypesDict[self.batchTaskType]
		self.batchTaskTypeFolder = self.nim_taskFolderDict[self.batchTaskTypeID]

		# Saving Preferences
		nimPrefs.update( 'Job', 'Flame', self.nim_jobID )
		nimPrefs.update( 'Show', 'Flame', self.nim_showID )

		# TODO: Save custom Flame-NIM preferences for element associations

		self.accept()


def nimCreateShot(nim_showID=None, info=None) :
	'''Create Shot in NIM on preAssetExport'''

	# TODO: Needs to be Variable Project Structure Aware
	#		Check if project is online

	result = {}

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

		#TODO: If shotName is '' then set to assetName

		print "NIM - Exporting Shot Info"
		shotInfo = nimAPI.add_shot( nim_showID, nim_shotName, nim_duration )

		if shotInfo['success'] == 'true':
			result['success'] = True
			nim_shotID = shotInfo['ID']
			print "NIM - nim_shotID: %s" % nim_shotID
			if 'error' in shotInfo:
				print "NIM - WARNING: %s" % shotInfo['error']
		else:
			result['success'] = False
			nim_shotID = False
			if shotInfo['error']:
				#error exists
				print "NIM - ERROR: %s" % shotInfo['error']

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
				
				# Append iconPath to result
				result['nim_iconPath'] = nimResolvePath(nim_shotID=nim_shotID, keyword_string=iconPath)
				print "NIM - iconPath: %s" % result['nim_iconPath']

			else :
				print 'NIM - Skipping icon upload for non-video assetType'
		
		result['nim_shotID'] = nim_shotID
		result['resolvedPath'] = nimResolvePath(nim_shotID=nim_shotID, keyword_string=nim_resolvedPath)

	return result


def nimExportElement(nim_shotID=None, info=None, typeID='', nim_userID=None) :
	# Export Elements in NIM on postAssetExport

	print "Exporting NIM Element"
	success = False

	if nim_shotID != None and info != None :
		nim_shotName = info['shotName']
		nim_sourceIn = info['sourceIn']
		nim_sourceOut = info['sourceOut']
		nim_handleIn = info['handleIn']
		nim_handleOut = info['handleOut']
		nim_duration = nim_sourceOut - nim_sourceIn
		nim_assetType = info['assetType']
		nim_sequenceName = info['sequenceName']
		nim_destinationPath = info['destinationPath']
		nim_resolvedPath = info['resolvedPath']
		if 'nim_fullPath' in info :
			nim_fullPath = info['nim_fullPath']
		else :
			nim_fullPath = os.path.join(nim_destinationPath, nim_resolvedPath)

		nim_tapeName = ''
		if 'tapeName' in info :
			nim_tapeName = info['tapeName']
		
		nim_element_path = nim_fullPath.rpartition('/')
		nim_path = nim_element_path[0]
		nim_name = nim_element_path[2]
		
		# Build metadata
		metadata = {}
		if nim_assetType :
			metadata['flameAssetType'] = nim_assetType
		if nim_tapeName :
			metadata['flameTapeName'] = nim_tapeName
		if nim_sequenceName :
			metadata['flameSequenceName'] = nim_sequenceName
		metadata = json.dumps(metadata)

		# Add Media Item as Element
		element_result = nimAPI.add_element( parent='shot', parentID=nim_shotID, userID=nim_userID, typeID=typeID, path=nim_path, name=nim_name, \
										startFrame=nim_sourceIn, endFrame=nim_sourceOut, handles=nim_handleIn, isPublished=False, metadata=metadata )

		print "NIM - %s has been added in NIM." % (nim_assetType)
		success = True
	else:
		print "NIM - shotID missing found"

	return success


def nimExportFile(nim_shotID=None, info=None, taskTypeID='', taskFolder='', serverID=None, nim_userID=None, tapeName='', comment='') :
	# Export File in NIM on postAssetExport

	print "Exporting NIM File"
	success = False

	if nim_shotID != None and info != None :
		nim_shotName = info['shotName']
		nim_sourceIn = info['sourceIn']
		nim_sourceOut = info['sourceOut']
		nim_handleIn = info['handleIn']
		nim_handleOut = info['handleOut']
		nim_duration = nim_sourceOut - nim_sourceIn
		nim_assetType = info['assetType']
		nim_sequenceName = info['sequenceName']
		nim_destinationPath = info['destinationPath']
		nim_resolvedPath = info['resolvedPath']
		nim_versionName = info['versionName']

		if 'nim_fullPath' in info :
			nim_fullPath = info['nim_fullPath']
		else :
			nim_fullPath = os.path.join(nim_destinationPath, nim_resolvedPath)

		nim_element_path = nim_fullPath.rpartition('/')
		element_filePath = nim_element_path[0]
		element_fileName = nim_element_path[2]

		#Derive basename from file ( TODO: give option to use shot_task_tag_ver.batch method )
		#Using filename entered in Export window
		#ext = '.batch'
		nim_doSave = True
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
			print "Version information was either not found in batch export name or has incorrect placement to be NIM compatible.\n \
					Please include the version in the comp name at the end of the name by using the <version name> keyword \
					or manually adding 'v#' to the batch file name.\n \
					Example: <shot name>_comp_<version name>.batch\n \
					The batch file will be created but not logged into NIM."
			nim_doSave = False
		
		filename = element_fileName
		filepath = element_filePath
		
		print "basename: %s" % basename
		print "filename: %s" % filename
		print "version: %s" % version

		# Verify entry is not duplicate of existing version
		nim_doUpdate = False

		# Get versions for basename
		nim_versions = {}
		nim_versionID = 0
		nim_versions = nimAPI.get_vers(shotID=nim_shotID, basename=basename)
		print "Versions Returned: %s" % nim_versions

		# If file matching class / basename / filename / version
		try:
			if len(nim_versions)>0:
				print "Versions found" 
				for versionItem in nim_versions:
					if versionItem['filename'] == filename:
						print "Existing Version Found"
						nim_versionID = versionItem['fileID']
						print "versionID: %s" % nim_versionID
						nim_doUpdate = True

					# Match previous taskTypeID, taskFolder, and serverID if not set
					if taskTypeID == '' :
						taskTypeID = versionItem['task_type_ID']
						print "taskTypeID: %s" % taskTypeID
					if taskFolder == '' :
						taskFolder = versionItem['task_type_folder']
						print "taskFolder: %s" % taskFolder
					if not serverID :
						serverID = versionItem['serverID']
						print "serverID: %s" % serverID
			else:
				print "No existing versions found"
		except:
			print "Failed to load existing versions from NIM"
			pass
				  
		if not serverID :
			print "NIM Sever information is missing.\n \
					Please select a NIM Project Server from the Server dropdown list.\n \
					The batch file will be created but not logged into NIM."
			nim_doSave = False

		pub = False
		forceLink = 0 	# lazy symlink as files wont exist yet
		work = True 	# set comp as working file
		metadata = {}

		# Build Metadata		
		# Resolve setupNamePattern to match against batchExport setupNamePattern
		if 'namePattern' in info :
			namePattern = nimResolvePath(nim_shotID=nim_shotID, keyword_string=info['namePattern'])
			setupNamePattern = resolveBatchSetupNamePattern(namePattern=namePattern, sequenceName=nim_sequenceName, tapeName=tapeName)
			metadata['setupNamePattern'] = setupNamePattern

		if nim_sequenceName :
			metadata['flameSequenceName'] = nim_sequenceName
		if nim_versionName :
			metadata['flameVersionName'] = nim_versionName
		metadata = json.dumps(metadata)

		if nim_doSave is True:
			if nim_doUpdate is True:
				print "Updating file data in NIM"
				file_apiResult = nimAPI.update_file( ID=nim_versionID, task_type_ID=taskTypeID, task_folder=taskFolder, userID=nim_userID, \
														basename=basename, filename=filename, path=filepath, ext=ext, version=version, \
														comment=comment, serverID=serverID, pub=pub, forceLink=forceLink, work=work, metadata=metadata )
				print file_apiResult
			else:
				print "Saving file data to NIM"
				file_apiResult = nimAPI.save_file( parent='shot', parentID=nim_shotID, task_type_ID=taskTypeID, task_folder=taskFolder, userID=nim_userID, \
													basename=basename, filename=filename, path=filepath, ext=ext, version=version, \
													comment=comment, serverID=serverID, pub=pub, forceLink=forceLink, work=work, metadata=metadata )
				print file_apiResult

	return success


def nimAddBatchExport(info=None, comment='') :
	'''Determine NIM shot from associated openClip, then log elements and files'''

	# exportPath - path prefix
	# openClipResolvedPath - path to the output openClip
	# setupResolvedPath - path to the new batch file
	# resolvedPath - path to the image sequence / output
	
	success = False

	nimPrefs = getNimPrefs()
	nim_userID = nimPrefs['NIM_userID']

	exportPath = info['exportPath']
	openClipResolvedPath = info['openClipResolvedPath']
	setupResolvedPath = info['setupResolvedPath']
	resolvedPath = info['resolvedPath']
	firstFrame = info['firstFrame']
	lastFrame = info['lastFrame']

	clipPartition = openClipResolvedPath.rpartition('/')
	clipPath = clipPartition[0]
	clipName = clipPartition[2]

	print "ClipPath: %s" % clipPath
	print "ClipName: %s" % clipName

	# Resolve shot by assocaited openClipResolvedPath
	elements = nimAPI.find_elements(name=clipName, path=clipPath)
	print "Matching Clip Element Found: "
	print elements 

	if len(elements) > 1 :
		print "Found more than one result..."
	else :
		# Get Element metadata to read sequenceName

		nim_shotID = elements[0]['shotID']
		print "NIM shotID: %s" % nim_shotID
		elementTypeID = elements[0]['elementTypeID']
		print "NIM elementTypeID: %s" % elementTypeID

		elementData = {}
		elementData['shotName'] = ''
		elementData['sourceIn'] = firstFrame
		elementData['sourceOut'] = lastFrame
		elementData['handleIn'] = 0
		elementData['handleOut'] = 0
		elementData['assetType'] = 'video'
		elementData['sequenceName'] = ''
		elementData['destinationPath'] = exportPath
		elementData['resolvedPath'] = resolvedPath
		elementData['nim_fullPath'] = resolvedPath
		elementData['versionName'] = info['versionName']

		nimExportElement(nim_shotID=nim_shotID, info=elementData, typeID=elementTypeID, nim_userID=nim_userID)


		fileData = {}
		fileData['shotName'] =''
		fileData['sourceIn'] = firstFrame
		fileData['sourceOut'] = lastFrame
		fileData['handleIn'] = 0
		fileData['handleOut'] = 0
		fileData['assetType'] = 'batch'
		fileData['sequenceName'] = ''
		fileData['destinationPath'] = exportPath
		fileData['resolvedPath'] = setupResolvedPath
		fileData['versionName'] = info['versionName']

		nimExportFile(nim_shotID=nim_shotID, info=fileData, taskTypeID='', taskFolder='', nim_userID=nim_userID, comment=comment)
	
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


def nimScanForVersions(nim_showID=None, nim_shotID=None) :
	# find_elements in show with metadata flameAssetType : batchOpenClip
	# get element type
	# find all elements of type in shot
	# add elements to batchOpenClip
	metadata = {}
	metadata['flameAssetType'] = 'batchOpenClip'
	metadata = json.dumps(metadata)
	openClipElements = nimAPI.find_elements(showID=nim_showID, metadata=metadata)
	print openClipElements

	for openClipElement in openClipElements :
		clipID = openClipElement['ID']
		shotID = openClipElement['shotID']
		clipPath = openClipElement['path'].encode('utf-8')
		clipName = openClipElement['name'].encode('utf-8')
		clipFile = os.path.join(clipPath,clipName)

		elementTypeID = openClipElement['elementTypeID']
		elements = nimAPI.find_elements(shotID=shotID, elementTypeID=elementTypeID)
		print "matching elements found"
		print elements

		elementFolders = []
		for element in elements :
			if element['ID'] != clipID :
				print "Element found for shotID %s" % shotID
				elementPath = element['path'].encode('utf-8')
				elementName = element['name'].encode('utf-8')
				print os.path.join(elementPath,elementName)
				elementFolders.append(elementPath)

		getMediaScript = "/usr/discreet/mio/current/dl_get_media_info"
		
		if not os.path.isfile(getMediaScript) :
			print "The get media info script is not installed: file %s missing" % getMediaScript
			return
		else :
			#tmpfile = os.path.abspath("tmpfile")
			tmpfile = "tmp.clip"
			
			for folder in elementFolders:
				apath = os.path.abspath(folder)
				print " Adding folder %s" % apath
				#output a temp file 
				tmpfile = apath+"/"+tmpfile
				if os.path.isfile(tmpfile):
					os.remove(tmpfile)
				print "Temp File: %s" % tmpfile
				res = os.popen4("%s -r %s" % ( getMediaScript, apath ) )[1].readlines()
				
				with open(tmpfile,"w+") as f:
					#f = open(tmpfile, "w")
					for line in res:
						f.write( line )
					#f.close()
				splice(clipFile,tmpfile)

			'''
			if os.path.isfile(tmpfile):
				os.remove(tmpfile)
			'''

	return
	

def nimResolvePath(nim_jobID=None, nim_showID=None, nim_shotID=None, keyword_string='', tokenL='<', tokenR='>') :

	nimPaths = {}
	
	# Get shotInfo
	if nim_shotID :	
		nim_shotInfo = nimAPI.get_shotInfo(nim_shotID)
		if nim_shotInfo:
			if len(nim_shotInfo)>0:
				nim_showID = nim_shotInfo[0]['showID']

		nim_shotPaths = nimAPI.get_paths('shot', nim_shotID)
		if nim_shotPaths:
			if len(nim_shotPaths)>0:
				nimPaths['nim_shot_root'] = nim_shotPaths['root']
				nimPaths['nim_shot_plates'] = nim_shotPaths['plates']
				nimPaths['nim_shot_render'] = nim_shotPaths['renders']
				nimPaths['nim_shot_comp'] = nim_shotPaths['comps']

	# Get showInfo
	if nim_showID :	
		nim_showInfo = nimAPI.get_showInfo(nim_showID)
		if nim_showInfo:
			if len(nim_showInfo)>0:
				nim_jobID = nim_showInfo[0]['jobID']
				nimPaths['nim_show_name'] = nim_showInfo[0]['showname']

		nim_showPaths = nimAPI.get_paths('show', nim_showID)
		if nim_showPaths:
			if len(nim_showPaths)>0:
				nimPaths['nim_show_root'] = nim_showPaths['root']

		
	# Get jobInfo
	if nim_jobID :	
		nim_jobInfo = nimAPI.get_jobInfo(nim_jobID)
		if nim_jobInfo:
			if len(nim_jobInfo)>0:
				nimPaths['nim_job_name'] = nim_jobInfo[0]['jobname']
				nimPaths['nim_job_number'] = nim_jobInfo[0]['number']

		nim_jobPaths = nimAPI.get_paths('job', nim_jobID)
		if nim_jobPaths:
			if len(nim_jobPaths)>0:
				nimPaths['nim_job_root'] = nim_jobPaths['root']


	#keyword_string = keyword_string.format(**nimPaths)
	if 'nim_job_root' in nimPaths :
		keyword_string = keyword_string.replace(tokenL+'nim_job_root'+tokenR, nimPaths['nim_job_root'])

	if 'nim_job_number' in nimPaths :
		keyword_string = keyword_string.replace(tokenL+'nim_job_number'+tokenR, nimPaths['nim_job_number'])

	if 'nim_job_name' in nimPaths :
		keyword_string = keyword_string.replace(tokenL+'nim_job_name'+tokenR, nimPaths['nim_job_name'])

	if 'nim_show_root' in nimPaths :
		keyword_string = keyword_string.replace(tokenL+'nim_show_root'+tokenR, nimPaths['nim_show_root'])

	if 'nim_show_name' in nimPaths :
		keyword_string = keyword_string.replace(tokenL+'nim_show_name'+tokenR, nimPaths['nim_show_name'])

	if 'nim_shot_root' in nimPaths :
		keyword_string = keyword_string.replace(tokenL+'nim_shot_root'+tokenR, nimPaths['nim_shot_root'])

	if 'nim_shot_plates' in nimPaths :
		keyword_string = keyword_string.replace(tokenL+'nim_shot_plates'+tokenR, nimPaths['nim_shot_plates'])

	if 'nim_shot_render' in nimPaths :
		keyword_string = keyword_string.replace(tokenL+'nim_shot_render'+tokenR, nimPaths['nim_shot_render'])

	if 'nim_shot_comp' in nimPaths :
		keyword_string = keyword_string.replace(tokenL+'nim_shot_comp'+tokenR, nimPaths['nim_shot_comp'])

	return keyword_string.encode('utf-8')


def resolveBatchKeywords(nim_shotID=None, batch_path=None) :
	'''Scrubs batch files for NIM keywords and resolves path'''
	success = False
	if batch_path :
		#	/PRJ/NIM_PROJECTS/NIM_1/17022_FLAME/FLM/SHOTS/SH_011/FLAME/batch/SH_011_v00.batch
		if batch_path.endswith('.batch') :
			batch_path = batch_path[:-6]
			print "Bath Path: %s" % batch_path

		for file in os.listdir(batch_path) :
			if file.endswith(".export_node") :
				export_node_file = os.path.join(batch_path, file)
				print "Export Node Found: %s" % export_node_file
				try:
					with open(export_node_file) as f :
						export_node_contents=f.read()
						print "Export Node Loaded"
						export_node_contents = nimResolvePath(nim_shotID=nim_shotID, keyword_string=export_node_contents, tokenL='&lt;', tokenR='&gt;')
					with open(export_node_file, "w") as f :
						f.write(export_node_contents)
					print 'Export Node Updated'
					success = True
				except Exception, e :
					print 'Export Node Keyword Resolution Failed'
					print '    %s' % traceback.print_exc()

	return success


def resolveBatchSetupNamePattern(namePattern=None, sequenceName='', tapeName='') :
	# Update namePattern to match value saved on batchExportBegin
	#	Used When saving metatag to match back new batch versions
	#		Resolve <nim_shot_root> 
	#		Replace <name> (sequence name) and <tape> (tape name) as they are already resolved in batchExportBegin
	#	 	Convert <shot name> to <name> to match setupNamePattern
	namePattern = namePattern.replace('<name>', sequenceName)
	namePattern = namePattern.replace('<tape>', tapeName)
	return namePattern


def getNimPrefs() :
	try:
		#self.app=nimFile.get_app()
		app = 'Flame'
		prefs=nimPrefs.read()
		print "NIM - Prefs: "
		print prefs

		if 'NIM_User' in prefs :
			user=prefs['NIM_User']
		else :
			user = ''

		print "NIM - Prefs successfully read"

	except:
		print "NIM - Failed to read NIM prefs"
		print 'NIM - ERROR: %s' % traceback.print_exc()
		app='Flame'
		prefs=''
		user=''

	nim_OS = platform.system()
	prefs['OS'] = nim_OS
	
	try:
		nim_userID = nimAPI.get_userID(user)
		if not nim_userID :
			nimUI.GUI().update_user()
			userInfo=nim.NIM().userInfo()
			user = userInfo['name']
			nim_userID = userInfo['ID']
	except:
		# failing on user
		print "NIM - Failed to get userID"
		nim_userID = 0

	prefs['NIM_userID'] = nim_userID

	print "NIM - user=%s" % user
	print "NIM - userID=%s" % nim_userID

	return prefs


def addFeed(feed,vuid,targetMIO,trackUID):

	tracks = targetMIO.getElementsByTagName('track')
	newID  = vuid

	#Iterate through the tracks, looking for perfect matches for the incoming feed
	for i in range(len(tracks)):
		if tracks[i].attributes["uid"].value == trackUID:
			if ( len(vuid) == 0 ):
				#Get the version of the last feed
				allfeeds = tracks[i].getElementsByTagName('feed')
				for j in range(len(allfeeds)):
					feedID = allfeeds[j].attributes["uid"].value
					if feedID == "v0":
						newID = "002"
					else:
						match = re.search( "([\d]+)", feedID)
						if match:				   				
							number = int(match.group(1))
							number = number + 1					
							newID = "%03d" % number 
						else:
							print "Invalid feed uid in masterfile: %s" % feedID
							return False

			feed.attributes['vuid'].value = newID
			feed.attributes['uid'].value = newID		

			#When the feed's track matches the one in the clip, add the feed to this track
			tracks[i].getElementsByTagName('feeds')[0].appendChild(feed)

	return newID


def splice( masterFile, newFile ):

	print "MasterFile: 	%s" % masterFile
	print "newFile: 	%s" % newFile

	#Read the Gateway Clip XML files for the existing and new versions
	sourceGWXML	= minidom.parse(masterFile)
	newGWXML	= minidom.parse(newFile)

	#Get all of the tracks from the new
	allTracks	= newGWXML.getElementsByTagName('track') 


	#--> Start ET Implementation
	sourceXML 	= ET.parse(masterFile)
	newXML 		= ET.parse(newFile)
	
	for track in newXML.iter('track'):
		theTrackID = track.get('uid')
		theFeed = track.find('feeds/feed')
		print theTrackID
		print theFeed
		#newVersionID = addFeed(theFeed,newVersionID,sourceGWXML,theTrackID)

	#--> END ET Implementation


	newVersionID = ''

	for i in range(len(allTracks)):
		theTrackID	= allTracks[i].attributes["uid"].value
		theTrack	= allTracks[i]
		theFeed	= theTrack.getElementsByTagName('feed')[0]
		newVersionID = addFeed(theFeed,newVersionID,sourceGWXML,theTrackID)

	if newVersionID :
		print "newVersionID: %s" % newVersionID
		#Add a version description at the end of the file, for this new version
		doc		= minidom.Document()
		newVersion	= sourceGWXML.getElementsByTagName('versions')[0].appendChild(doc.createElement('version'))
		newVersion.setAttribute('type', 'version')
		newVersion.setAttribute('uid', newVersionID)

		resultXML	= sourceGWXML.toxml()


		# Create a backup of the original file
		bakfile = "%s.bak" % masterFile
		if not os.path.isfile(bakfile):
			shutil.copy2(masterFile,bakfile)
		else:
			created = False
			for i in range ( 1, 99 ):
				bakfile = "%s.bak.%02d" % ( masterFile, i )
				if not os.path.isfile(bakfile):
					shutil.copy2(masterFile,bakfile)
					created = True
					break
			if not created:
				bakfile = "%s.bak.last" % masterFile
				shutil.copy2(masterFile,bakfile)
				
		outFile = masterFile

		print " Adding feed version %s" % newVersionID
		f = open(outFile, "w")	
		f.write( resultXML )
		f.close()
	else :
		print "No VersionID Found"
