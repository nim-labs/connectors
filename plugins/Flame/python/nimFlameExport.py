#!/usr/bin/env python
#******************************************************************************
#
# Filename: Flame/python/nimFlameExport.py
# Version:  v4.0.27.190418
#
# Copyright (c) 2014-2019 NIM Labs LLC
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
import subprocess

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


#  Import Python GUI packages :
try : 
	from PySide2.QtWidgets import *
	from PySide2.QtGui import *
	from PySide2.QtCore import *
except ImportError :
	try :
		from PySide.QtGui import *
		from PySide.QtCore import *
	except ImportError : 
		print "NIM: Failed to load UI Modules"

			
print "NIM - Loading nimFlameExport"


#  Make NIM prefs:
nimPrefs.mk_default( notify_success=True )

# Set Flame prefs location:
flamePrefFile = os.path.normpath( os.path.join( nimPrefs.get_home(), "apps","Flame","flame.nim" ) )
print "Flame Prefs: %s" % flamePrefFile

try :
	# from libwiretapPythonClientAPI import *
	nimExport_app = os.environ.get('NIM_APP', '-1')
	print "NIM - Current Application: %s" % nimExport_app
except :
	print "NIM - failed to load Wiretap API"


class NimScanForVersionsDialog(QDialog):
	# Reads NIM for openClips with elementTypes 
	#	and updates with logged elements of matching types

	def __init__(self, parent=None):
		super(NimScanForVersionsDialog, self).__init__(parent)

		self.result = ""
		QApplication.setOverrideCursor(Qt.ArrowCursor)
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

			# Using Flame Specific Prefs file


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
		self.nimCommentLabel.setText("Scan for Versions updates openClip files logged \nas elements in NIM with matching element types.")
		horizontalLayout_commentDesc.addWidget(self.nimCommentLabel)
		horizontalLayout_commentDesc.setStretch(1, 40)

		# Progress Bar
		horizontalLayout_progress = QHBoxLayout()
		horizontalLayout_progress.setSpacing(-1)
		horizontalLayout_progress.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_progress.setObjectName("horizontalLayout_progress")
		self.progressBar = QProgressBar(self)
		self.progressBar.setGeometry(200, 80, 250, 20)
		horizontalLayout_progress.addWidget(self.progressBar)
		horizontalLayout_progress.setStretch(1, 40)

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
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Scans the show for elements that match the\nOpen Clip element types selected during publish\nand updates the corresponding clips.")
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
		#groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout_commentDesc)
		groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout_progress)
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

		# Start Loop
		self.clipCount = 0
		self.clipFail = 0
		
		shots = nimAPI.get_shots(showID=self.nim_showID)
		numShots = len(shots)
		print "Shot count: %s" % numShots
		self.progressBar.setRange(0, numShots)

		self.nim_jobChooser.setDisabled(True)
		self.nim_showChooser.setDisabled(True)
		self._buttonbox.setDisabled(True)

		shotCount = 0
		for shot in shots :
			shotCount += 1
			self.nimCommentLabel.setText( "Scanning shot: "+shot['name'] )
			self.progressBar.setValue(shotCount)
			QApplication.processEvents()
			
			clipSucess = {}
			clipSucess = nimScanForVersions(nim_shotID=shot['ID'])

			self.clipCount += clipSucess['clipCount']
			self.clipFail += clipSucess['clipFail']

		self.accept()


class NimBuildOpenClipsFromElementDialog(QDialog):
	def __init__(self, parent=None):
		super(NimBuildOpenClipsFromElementDialog, self).__init__(parent)

		self.result = ""
		QApplication.setOverrideCursor(Qt.ArrowCursor)
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
		
		self.setWindowTitle("NIM: Build Open Clips from Elements")
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
		self.nimCommentLabel.setText("Build OpenClips from Elements creates new open clips with versions for each element type in NIM.\nExisting open clips will be updated with new elements.")
		horizontalLayout_commentDesc.addWidget(self.nimCommentLabel)
		horizontalLayout_commentDesc.setStretch(1, 40)


		# Progress Bar
		horizontalLayout_progress = QHBoxLayout()
		horizontalLayout_progress.setSpacing(-1)
		horizontalLayout_progress.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_progress.setObjectName("horizontalLayout_progress")
		self.progressBar = QProgressBar(self)
		self.progressBar.setGeometry(200, 80, 250, 20)
		horizontalLayout_progress.addWidget(self.progressBar)
		horizontalLayout_progress.setStretch(1, 40)


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
	

		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText(" Build Open Clips ")
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
		#groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout_commentDesc)
		groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout_progress)
		groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout_job)
		groupLayout.setLayout(3, QFormLayout.SpanningRole, horizontalLayout_server)
		groupLayout.setLayout(4, QFormLayout.SpanningRole, horizontalLayout_show)
		groupLayout.setLayout(5, QFormLayout.SpanningRole, horizontalLayout_OkCancel)

		self.setLayout(groupLayout)
		layout.addWidget(groupBox)

		self.nim_jobChanged() #trigger job changed to load choosers


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
	

	def acceptTest(self):
		# Saving Preferences
		nimPrefs.update( 'Job', 'Flame', self.nim_jobID )
		nimPrefs.update( 'Show', 'Flame', self.nim_showID )

		# Start Loop
		self.clipCount = 0
		self.clipFail = 0

		shots = nimAPI.get_shots(showID=self.nim_showID)
		numShots = len(shots)
		print "Shot count: %s" % numShots
		self.progressBar.setRange(0, numShots)

		self.nim_jobChooser.setDisabled(True)
		self.nim_serverChooser.setDisabled(True)
		self.nim_showChooser.setDisabled(True)
		self._buttonbox.setDisabled(True)

		shotCount = 0
		for shot in shots :
			shotCount += 1
			self.nimCommentLabel.setText( "Scanning shot: "+shot['name'] )
			self.progressBar.setValue(shotCount)
			QApplication.processEvents()
			
			clipSucess = {}
			clipSucess = nimBuildOpenClipFromElements(nim_shotID=shot['ID'], nim_serverID=self.nim_serverID)

			self.clipCount += clipSucess['clipCount']
			self.clipFail += clipSucess['clipFail']

		self.accept()


class NimBuildOpenClipsFromProjectDialog(QDialog):
	def __init__(self, parent=None):
		super(NimBuildOpenClipsFromProjectDialog, self).__init__(parent)

		self.result = ""
		QApplication.setOverrideCursor(Qt.ArrowCursor)
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
		
		self.setWindowTitle("NIM: Build Open Clips from Project Structure")
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
		self.nimCommentLabel.setText("Build OpenClips from Project scans the NIM project structure root files (plates, renders, comps)")
		horizontalLayout_commentDesc.addWidget(self.nimCommentLabel)
		horizontalLayout_commentDesc.setStretch(1, 40)

		# Comment Label
		horizontalLayout_comment2Desc = QHBoxLayout()
		horizontalLayout_comment2Desc.setSpacing(-1)
		horizontalLayout_comment2Desc.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_comment2Desc.setObjectName("horizontalLayout_comment2Desc")
		self.nimComment2Label = QLabel()
		self.nimComment2Label.setText("and creates new open clips for each folder with versions for each subfolder.")
		horizontalLayout_comment2Desc.addWidget(self.nimComment2Label)
		horizontalLayout_comment2Desc.setStretch(1, 40)

		# Comment Label
		horizontalLayout_comment3Desc = QHBoxLayout()
		horizontalLayout_comment3Desc.setSpacing(-1)
		horizontalLayout_comment3Desc.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_comment3Desc.setObjectName("horizontalLayout_comment3Desc")
		self.nimComment3Label = QLabel()
		self.nimComment3Label.setText("Existing clips will be updated with new media found.")
		horizontalLayout_comment3Desc.addWidget(self.nimComment3Label)
		horizontalLayout_comment3Desc.setStretch(1, 40)


		# Progress Bar
		horizontalLayout_progress = QHBoxLayout()
		horizontalLayout_progress.setSpacing(-1)
		horizontalLayout_progress.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_progress.setObjectName("horizontalLayout_progress")
		self.progressBar = QProgressBar(self)
		self.progressBar.setGeometry(200, 80, 250, 20)
		horizontalLayout_progress.addWidget(self.progressBar)
		horizontalLayout_progress.setStretch(1, 40)


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
	

		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText(" Build Open Clips ")
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
		#groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout_commentDesc)
		#groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout_comment2Desc)
		#groupLayout.setLayout(3, QFormLayout.SpanningRole, horizontalLayout_comment3Desc)
		groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout_progress)
		groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout_job)
		groupLayout.setLayout(3, QFormLayout.SpanningRole, horizontalLayout_server)
		groupLayout.setLayout(4, QFormLayout.SpanningRole, horizontalLayout_show)
		groupLayout.setLayout(5, QFormLayout.SpanningRole, horizontalLayout_OkCancel)

		self.setLayout(groupLayout)
		layout.addWidget(groupBox)

		self.nim_jobChanged() #trigger job changed to load choosers


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
	

	def acceptTest(self):
		# Saving Preferences
		nimPrefs.update( 'Job', 'Flame', self.nim_jobID )
		nimPrefs.update( 'Show', 'Flame', self.nim_showID )

		# Start Loop
		self.clipCount = 0
		self.clipFail = 0

		shots = nimAPI.get_shots(showID=self.nim_showID)
		numShots = len(shots)
		print "Shot count: %s" % numShots
		self.progressBar.setRange(0, numShots)

		self.nim_jobChooser.setDisabled(True)
		self.nim_serverChooser.setDisabled(True)
		self.nim_showChooser.setDisabled(True)
		self._buttonbox.setDisabled(True)

		usePlates = True
		useRenders = True
		useComps = True

		shotCount = 0
		for shot in shots :
			shotCount += 1
			self.nimCommentLabel.setText( "Scanning shot: "+shot['name'] )
			self.progressBar.setValue(shotCount)
			QApplication.processEvents()
			
			folders = []
			if usePlates :
				folders.append('<nim_shot_plates>')
			if useRenders :
				folders.append('<nim_shot_render>')
			if useComps :
				folders.append('<nim_shot_comp>')

			clipSucess = {}
			clipSucess = nimBuildOpenClipFromFolders(nim_shotID=shot['ID'], nim_serverID=self.nim_serverID, folders=folders)

			self.clipCount += clipSucess['clipCount']
			self.clipFail += clipSucess['clipFail']

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


class NimExportSequenceDialog(QDialog):
	def __init__(self, parent=None):
		super(NimExportSequenceDialog, self).__init__(parent)

		self.result = ""
		QApplication.setOverrideCursor(Qt.ArrowCursor)
		try:
			self.app = 'Flame'
			self.prefs=nimPrefs.read()
			print "NIM - Prefs: "
			print self.prefs

			if 'NIM_User' in self.prefs :
				self.user=self.prefs['NIM_User']
			else :
				self.user = ''

			# Read Flame specific prefs
			self.flamePrefs = readFlamePrefs()

			print "NIM - Prefs successfully read"

		except:
			print "NIM - Failed to read NIM prefs"
			print 'NIM - ERROR: %s' % traceback.print_exc()
			self.app='Flame'
			self.user=''
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
		self.nim_taskTypes = nimAPI.get_tasks(app='FLAME', userType='all')
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
		self.nimPresetLabel.setText("Preset:")
		horizontalLayout_preset.addWidget(self.nimPresetLabel)
		self.nim_presetChooser = QComboBox()
		self.nim_presetChooser.setToolTip("Choose the NIM preset to use for this export.")
		self.nim_presetChooser.setMinimumHeight(28)
		self.nim_presetChooser.setIconSize(QSize(1, 24))
		horizontalLayout_preset.addWidget(self.nim_presetChooser)
		horizontalLayout_preset.setStretch(1, 40)

		presetList = self.nim_getPresets()

		if len(presetList) > 0:
			presetIndex = 0
			presetIter = 0
			for preset in presetList :
				self.nim_presetChooser.addItem(self.clearPix, preset)
				# Set Preference
				if self.flamePrefs['sequencePreset'] == preset:
					presetIndex = presetIter
				presetIter += 1

			if self.flamePrefs['sequencePreset'] != '':
				self.nim_presetChooser.setCurrentIndex(presetIndex)

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
				if self.flamePrefs['jobID'] == value:
					print "Found matching Job Name, job=", key
					jobIndex = jobIter
			jobIter += 1

			if self.flamePrefs['jobID'] != '':
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
		self.nimElementSectionLabel.setText("Select the NIM element type to assign exported media:")
		horizontalLayout_elementDesc.addWidget(self.nimElementSectionLabel)
		horizontalLayout_elementDesc.setStretch(1, 40)



		# video - exported media
		horizontalLayout_video = QHBoxLayout()
		horizontalLayout_video.setSpacing(-1)
		horizontalLayout_video.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_video.setObjectName("horizontalLayout_video")
		self.nimVideoLabel = QLabel()
		self.nimVideoLabel.setFixedWidth(120)
		self.nimVideoLabel.setText("Video Out:")
		horizontalLayout_video.addWidget(self.nimVideoLabel)
		self.nim_videoChooser = QComboBox()
		self.nim_videoChooser.setToolTip("Choose the NIM element type to associate with exported video media.")
		self.nim_videoChooser.setMinimumHeight(28)
		self.nim_videoChooser.setIconSize(QSize(1, 24))
		horizontalLayout_video.addWidget(self.nim_videoChooser)
		horizontalLayout_video.setStretch(1, 40)

		if len(self.nim_elementTypesDict)>0:
			videoIndex = 0
			videoIter = 0
			for key, value in sorted(self.nim_elementTypesDict.items(), reverse=False):
				self.nim_videoChooser.addItem(self.clearPix, key)
				if self.flamePrefs['videoElementID'] == value:
					print "Found video element preference=", key
					videoIndex = videoIter
				videoIter += 1

			if self.flamePrefs['videoElementID'] != '':
				self.nim_videoChooser.setCurrentIndex(videoIndex)

		self.nim_videoChooser.currentIndexChanged.connect(self.nim_videoElementChanged)


		# audio - exported media
		horizontalLayout_audio = QHBoxLayout()
		horizontalLayout_audio.setSpacing(-1)
		horizontalLayout_audio.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_audio.setObjectName("horizontalLayout_audio")
		self.nimAudioLabel = QLabel()
		self.nimAudioLabel.setFixedWidth(120)
		self.nimAudioLabel.setText("Audio Out:")
		horizontalLayout_audio.addWidget(self.nimAudioLabel)
		self.nim_audioChooser = QComboBox()
		self.nim_audioChooser.setToolTip("Choose the NIM element type to associate with exported audio media.")
		self.nim_audioChooser.setMinimumHeight(28)
		self.nim_audioChooser.setIconSize(QSize(1, 24))
		horizontalLayout_audio.addWidget(self.nim_audioChooser)
		horizontalLayout_audio.setStretch(1, 40)

		if len(self.nim_elementTypesDict)>0:
			audioIndex = 0
			audioIter = 0
			for key, value in sorted(self.nim_elementTypesDict.items(), reverse=False):
				self.nim_audioChooser.addItem(self.clearPix, key)
				if self.flamePrefs['audioElementID'] == value:
					print "Found audio element preference=", key
					audioIndex = audioIter
				audioIter += 1

			if self.flamePrefs['audioElementID'] != '':
				self.nim_audioChooser.setCurrentIndex(audioIndex)
		
		self.nim_audioChooser.currentIndexChanged.connect(self.nim_audioElementChanged)

		# openClip - Source Clip
		horizontalLayout_openClip = QHBoxLayout()
		horizontalLayout_openClip.setSpacing(-1)
		horizontalLayout_openClip.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_openClip.setObjectName("horizontalLayout_openClip")
		self.nimOpenClipLabel = QLabel()
		self.nimOpenClipLabel.setFixedWidth(120)
		self.nimOpenClipLabel.setText("BatchFX In:")
		horizontalLayout_openClip.addWidget(self.nimOpenClipLabel)
		self.nim_openClipChooser = QComboBox()
		self.nim_openClipChooser.setToolTip("Choose the NIM element type to associate new elements with the BatchFX Open Clip.\nThe source open clip is the read node used when promoting a timeline clip to BatchFX.\nNew elements added to the Open Clip will appear as versions on the BatchFX read node.")
		self.nim_openClipChooser.setMinimumHeight(28)
		self.nim_openClipChooser.setIconSize(QSize(1, 24))
		horizontalLayout_openClip.addWidget(self.nim_openClipChooser)
		horizontalLayout_openClip.setStretch(1, 40)
		
		if len(self.nim_elementTypesDict)>0:
			sourceIndex = 0
			sourceIter = 0
			for key, value in sorted(self.nim_elementTypesDict.items(), reverse=False):
				self.nim_openClipChooser.addItem(self.clearPix, key)
				if self.flamePrefs['sourceElementID'] == value:
					print "Found source element preference=", key
					sourceIndex = sourceIter
				sourceIter += 1

			if self.flamePrefs['sourceElementID'] != '':
				self.nim_openClipChooser.setCurrentIndex(sourceIndex)
		
		self.nim_openClipChooser.currentIndexChanged.connect(self.nim_openClipElementChanged)

		# video - exported media
		horizontalLayout_batchOpenClip = QHBoxLayout()
		horizontalLayout_batchOpenClip.setSpacing(-1)
		horizontalLayout_batchOpenClip.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_batchOpenClip.setObjectName("horizontalLayout_batchOpenClip")
		self.nimBatchOpenClipLabel = QLabel()
		self.nimBatchOpenClipLabel.setFixedWidth(120)
		self.nimBatchOpenClipLabel.setText("Timeline In:")
		horizontalLayout_batchOpenClip.addWidget(self.nimBatchOpenClipLabel)
		self.nim_batchOpenClipChooser = QComboBox()
		self.nim_batchOpenClipChooser.setToolTip("Choose the NIM element type to associate new elements with the Timeline Open Clip.\nThe Timeline Open Clip is used directly on a published Timeline.\nNew elements added to the Open Clip will appear as clip versions on the Timeline.")
		self.nim_batchOpenClipChooser.setMinimumHeight(28)
		self.nim_batchOpenClipChooser.setIconSize(QSize(1, 24))
		horizontalLayout_batchOpenClip.addWidget(self.nim_batchOpenClipChooser)
		horizontalLayout_batchOpenClip.setStretch(1, 40)
		
		if len(self.nim_elementTypesDict)>0:
			batchIndex = 0
			batchIter = 0
			for key, value in sorted(self.nim_elementTypesDict.items(), reverse=False):
				self.nim_batchOpenClipChooser.addItem(self.clearPix, key)
				if self.flamePrefs['batchElementID'] == value:
					print "Found batch element preference=", key
					batchIndex = batchIter
				batchIter += 1

			if self.flamePrefs['batchElementID'] != '':
				self.nim_batchOpenClipChooser.setCurrentIndex(batchIndex)
		
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
		self.nimElementSectionLabel.setText("Select the NIM task type to assign exported batch files:")
		horizontalLayout_taskDesc.addWidget(self.nimElementSectionLabel)
		horizontalLayout_taskDesc.setStretch(1, 40)


		# batch - versioned comps
		horizontalLayout_batch = QHBoxLayout()
		horizontalLayout_batch.setSpacing(-1)
		horizontalLayout_batch.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_batch.setObjectName("horizontalLayout_batch")
		self.nimBatchLabel = QLabel()
		self.nimBatchLabel.setFixedWidth(120)
		self.nimBatchLabel.setText("Batch Files:")
		horizontalLayout_batch.addWidget(self.nimBatchLabel)
		self.nim_batchChooser = QComboBox()
		self.nim_batchChooser.setToolTip("Select the NIM task type to assign exported batch files.")
		self.nim_batchChooser.setMinimumHeight(28)
		self.nim_batchChooser.setIconSize(QSize(1, 24))
		horizontalLayout_batch.addWidget(self.nim_batchChooser)
		horizontalLayout_batch.setStretch(1, 40)

		if len(self.nim_taskTypesDict)>0:
			batchFileIndex = 0
			batchFileIter = 0
			for key, value in sorted(self.nim_taskTypesDict.items(), reverse=False):
				self.nim_batchChooser.addItem(self.clearPix, key)
				if self.flamePrefs['batchTaskTypeID'] == value:
					print "Found batchFile element preference=", key
					batchFileIndex = batchFileIter
				batchFileIter += 1

			if self.flamePrefs['batchTaskTypeID'] != '':
				self.nim_batchChooser.setCurrentIndex(batchFileIndex)

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
		for preset in os.listdir(nimFlamePresetPath+'/sequence'):
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
		serverIndex = 0
		serverIter = 0
		try:
			self.nim_serverChooser.clear()
			if self.nim_serverChooser:
				if len(self.nim_servers)>0:  
					for server in self.nim_servers:
						self.nim_serverDict[server['server']] = server['ID']
					for key, value in sorted(self.nim_serverDict.items(), reverse=False):
						self.nim_serverChooser.addItem(self.clearPix, key)

						if self.flamePrefs['serverID'] == value:
							print "Found server preference=", key
							serverIndex = serverIter
						
						serverIter += 1

					if self.flamePrefs['serverID'] != '':
						self.nim_serverChooser.setCurrentIndex(serverIndex)
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

						if self.flamePrefs['showID'] == value:
							print "Found show preference=", key
							showIndex = showIter
						
						showIter += 1

					if self.flamePrefs['showID'] != '':
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

		# Saving NIM Preferences
		nimPrefs.update( 'Job', 'Flame', self.nim_jobID )
		nimPrefs.update( 'ServerID', 'Flame', self.nim_serverID )
		nimPrefs.update( 'Show', 'Flame', self.nim_showID )

		# Save Flame-NIM preferences for element associations
		self.flamePrefs["sequencePreset"] = self.nim_preset
		self.flamePrefs["jobID"] = self.nim_jobID
		self.flamePrefs["serverID"] = self.nim_serverID
		self.flamePrefs["showID"] = self.nim_showID
		self.flamePrefs["videoElementID"] = self.videoElementID
		self.flamePrefs["audioElementID"] = self.audioElementID
		self.flamePrefs["sourceElementID"] = self.openClipElementID
		self.flamePrefs["batchElementID"] = self.batchOpenClipElementID
		self.flamePrefs["batchTaskTypeID"] = self.batchTaskTypeID
		writeFlamePrefs(self.flamePrefs)

		self.accept()


class NimExportEditDialog(QDialog):
	def __init__(self, parent=None):
		super(NimExportEditDialog, self).__init__(parent)

		self.result = ""
		QApplication.setOverrideCursor(Qt.ArrowCursor)
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

			# Read Flame specific prefs
			self.flamePrefs = readFlamePrefs()

			print "NIM - Prefs successfully read"

		except:
			print "NIM - Failed to read NIM prefs"
			print 'NIM - ERROR: %s' % traceback.print_exc()
			self.app='Flame'
			self.user=''
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
		
		self.setWindowTitle("NIM: Export Edit")
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
		self.nimPresetLabel.setText("Preset:")
		horizontalLayout_preset.addWidget(self.nimPresetLabel)
		self.nim_presetChooser = QComboBox()
		self.nim_presetChooser.setToolTip("Choose the NIM preset to use for this export.")
		self.nim_presetChooser.setMinimumHeight(28)
		self.nim_presetChooser.setIconSize(QSize(1, 24))
		horizontalLayout_preset.addWidget(self.nim_presetChooser)
		horizontalLayout_preset.setStretch(1, 40)

		presetList = self.nim_getPresets()

		if len(presetList) > 0:
			presetIndex = 0
			presetIter = 0
			for preset in presetList :
				self.nim_presetChooser.addItem(self.clearPix, preset)
				# Set Preference
				if self.flamePrefs['editPreset'] == preset:
					presetIndex = presetIter
				presetIter += 1

			if self.flamePrefs['editPreset'] != '':
				self.nim_presetChooser.setCurrentIndex(presetIndex)

		self.nim_presetChooser.currentIndexChanged.connect(self.nim_presetChanged)


		# USE BACKGROUND
		#horizontalLayout_BG = QHBoxLayout()
		#horizontalLayout_BG.setSpacing(-1)
		#horizontalLayout_BG.setSizeConstraint(QLayout.SetDefaultConstraint)
		#horizontalLayout_BG.setObjectName("horizontalLayout_BG")
		#self.nimBgLabel = QLabel()
		#self.nimBgLabel.setFixedWidth(120)
		#self.nimBgLabel.setText("Background Export:")
		#horizontalLayout_BG.addWidget(self.nimBgLabel)
		#self.nim_BgCheck = QCheckBox()
		#self.nim_BgCheck.setToolTip("Exports clip as background process.")
		#self.nim_BgCheck.setMinimumHeight(28)
		#self.nim_BgCheck.setIconSize(QSize(1, 24))
		#horizontalLayout_BG.addWidget(self.nim_BgCheck)
		#horizontalLayout_BG.setStretch(1, 40)


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
				if self.flamePrefs['jobID'] == value:
					print "Found Job Preferences"
					jobIndex = jobIter
			jobIter += 1

			if self.flamePrefs['jobID'] != '':
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
	

		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("Export")
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Executes exports on selection for the selected preset")
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
		#groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout_BG)

		groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout_job)
		groupLayout.setLayout(3, QFormLayout.SpanningRole, horizontalLayout_server)
		groupLayout.setLayout(4, QFormLayout.SpanningRole, horizontalLayout_show)

		groupLayout.setLayout(5, QFormLayout.SpanningRole, horizontalLayout_OkCancel)

		self.setLayout(groupLayout)
		layout.addWidget(groupBox)

		self.nim_jobChanged() #trigger job changed to load choosers


	def nim_getPresets(self):
		presetList = []
		for preset in os.listdir(nimFlamePresetPath+'/edit'):
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
		serverIndex = 0
		serverIter = 0
		try:
			self.nim_serverChooser.clear()
			if self.nim_serverChooser:
				if len(self.nim_servers)>0:  
					for server in self.nim_servers:
						self.nim_serverDict[server['server']] = server['ID']
					for key, value in sorted(self.nim_serverDict.items(), reverse=False):
						self.nim_serverChooser.addItem(self.clearPix, key)

						if self.flamePrefs['serverID'] == value:
							print "Found server preference=", key
							serverIndex = serverIter
						
						serverIter += 1

					if self.flamePrefs['serverID'] != '':
						self.nim_serverChooser.setCurrentIndex(serverIndex)
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

						if self.flamePrefs['showID'] == value:
							print "Found show preference=", key
							showIndex = showIter
						
						showIter += 1

					if self.flamePrefs['showID'] != '':
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
		# Get Current Values For Static Objects
		self.nim_preset = self.nim_presetChooser.currentText()
		
		#if self.nim_BgCheck.isChecked() :
		#	self.nim_bg_export = True
		#else :
		#	self.nim_bg_export = False

		# Saving Preferences
		nimPrefs.update( 'Job', 'Flame', self.nim_jobID )
		nimPrefs.update( 'ServerID', 'Flame', self.nim_serverID )
		nimPrefs.update( 'Show', 'Flame', self.nim_showID )

		# Save Flame-NIM preferences for element associations
		self.flamePrefs["editPreset"] = self.nim_preset
		self.flamePrefs["jobID"] = self.nim_jobID
		self.flamePrefs["serverID"] = self.nim_serverID
		self.flamePrefs["showID"] = self.nim_showID
		writeFlamePrefs(self.flamePrefs)

		self.accept()


class NimExportDailyDialog(QDialog):
	def __init__(self, parent=None):
		super(NimExportDailyDialog, self).__init__(parent)

		self.result = ""
		QApplication.setOverrideCursor(Qt.ArrowCursor)
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

			# Read Flame specific prefs
			self.flamePrefs = readFlamePrefs()

			print "NIM - Prefs successfully read"

		except:
			print "NIM - Failed to read NIM prefs"
			print 'NIM - ERROR: %s' % traceback.print_exc()
			self.app='Flame'
			self.user=''
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

		self.nim_shots = []
		self.nim_shotDict = {}
		self.nim_shotID = None

		self.nim_tasks = []
		self.nim_taskDict = {}
		self.nim_taskID = None
		
		self.setWindowTitle("NIM: Export Daily")
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
		self.nimPresetLabel.setText("Preset:")
		horizontalLayout_preset.addWidget(self.nimPresetLabel)
		self.nim_presetChooser = QComboBox()
		self.nim_presetChooser.setToolTip("Choose the NIM preset to use for this export.")
		self.nim_presetChooser.setMinimumHeight(28)
		self.nim_presetChooser.setIconSize(QSize(1, 24))
		horizontalLayout_preset.addWidget(self.nim_presetChooser)
		horizontalLayout_preset.setStretch(1, 40)

		presetList = self.nim_getPresets()
		if len(presetList) > 0:
			presetIndex = 0
			presetIter = 0
			for preset in presetList :
				self.nim_presetChooser.addItem(self.clearPix, preset)
				# Set Preference
				if self.flamePrefs['dailyPreset'] == preset:
					presetIndex = presetIter
				presetIter += 1

			if self.flamePrefs['dailyPreset'] != '':
				self.nim_presetChooser.setCurrentIndex(presetIndex)

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
		self.nim_jobChooser.setToolTip("Choose the job to filter shows.")
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
				if self.flamePrefs['jobID'] == value:
					print "Found Job Preferences"
					jobIndex = jobIter
			jobIter += 1

			if self.flamePrefs['jobID'] != '':
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
		self.nim_serverChooser.setToolTip("Choose the server you wish to export the daily to.")
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
		self.nim_showChooser.setToolTip("Choose the show to filter shots.")
		self.nim_showChooser.setMinimumHeight(28)
		self.nim_showChooser.setIconSize(QSize(1, 24))
		horizontalLayout_show.addWidget(self.nim_showChooser)
		horizontalLayout_show.setStretch(1, 40)
		self.nim_showChooser.currentIndexChanged.connect(self.nim_showChanged)


		# SHOTS: List box for shot selection
		horizontalLayout_shot = QHBoxLayout()
		horizontalLayout_shot.setSpacing(-1)
		horizontalLayout_shot.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_shot.setObjectName("horizontalLayout_shot")
		self.nimShotLabel = QLabel()
		self.nimShotLabel.setFixedWidth(120)
		self.nimShotLabel.setText("Shot:")
		horizontalLayout_shot.addWidget(self.nimShotLabel)
		self.nim_shotChooser = QComboBox()
		self.nim_shotChooser.setToolTip("Choose the shot to filter tasks.")
		self.nim_shotChooser.setMinimumHeight(28)
		self.nim_shotChooser.setIconSize(QSize(1, 24))
		horizontalLayout_shot.addWidget(self.nim_shotChooser)
		horizontalLayout_shot.setStretch(1, 40)
		self.nim_shotChooser.currentIndexChanged.connect(self.nim_shotChanged)


		# TASKS: List box for shot selection
		horizontalLayout_task = QHBoxLayout()
		horizontalLayout_task.setSpacing(-1)
		horizontalLayout_task.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout_task.setObjectName("horizontalLayout_task")
		self.nimTaskLabel = QLabel()
		self.nimTaskLabel.setFixedWidth(120)
		self.nimTaskLabel.setText("Task:")
		horizontalLayout_task.addWidget(self.nimTaskLabel)
		self.nim_taskChooser = QComboBox()
		self.nim_taskChooser.setToolTip("Choose the task you wish to upload the dialy to.")
		self.nim_taskChooser.setMinimumHeight(28)
		self.nim_taskChooser.setIconSize(QSize(1, 24))
		horizontalLayout_task.addWidget(self.nim_taskChooser)
		horizontalLayout_task.setStretch(1, 40)
		self.nim_taskChooser.currentIndexChanged.connect(self.nim_taskChanged)
	

		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("Export")
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Executes exports on selection for the selected preset")
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
		groupLayout.setLayout(5, QFormLayout.SpanningRole, horizontalLayout_shot)
		groupLayout.setLayout(6, QFormLayout.SpanningRole, horizontalLayout_task)

		groupLayout.setLayout(7, QFormLayout.SpanningRole, horizontalLayout_OkCancel)

		self.setLayout(groupLayout)
		layout.addWidget(groupBox)

		self.nim_jobChanged() #trigger job changed to load choosers


	def nim_getPresets(self):
		presetList = []
		for preset in os.listdir(nimFlamePresetPath+'/daily'):
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
		serverIndex = 0
		serverIter = 0
		try:
			self.nim_serverChooser.clear()
			if self.nim_serverChooser:
				if len(self.nim_servers)>0:  
					for server in self.nim_servers:
						self.nim_serverDict[server['server']] = server['ID']
					for key, value in sorted(self.nim_serverDict.items(), reverse=False):
						self.nim_serverChooser.addItem(self.clearPix, key)

						if self.flamePrefs['serverID'] == value:
							print "Found server preference=", key
							serverIndex = serverIter
						
						serverIter += 1

					if self.flamePrefs['serverID'] != '':
						self.nim_serverChooser.setCurrentIndex(serverIndex)
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
						
						if self.flamePrefs['showID'] == value:
							print "Found show preference=", key
							showIndex = showIter
						
						showIter += 1

					if self.flamePrefs['showID'] != '':
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

			self.nim_updateShot()


	def nim_updateShot(self):
		self.nim_shots = {}
		self.nim_shots = nimAPI.get_shots(self.nim_showID)
		#print self.nim_shots

		shotIndex = 0
		shotIter = 0
		self.nim_shotDict = {}
		try:
			self.nim_shotChooser.clear()
			if self.nim_shotChooser:
				if len(self.nim_shots)>0:  
					for shot in self.nim_shots:
						self.nim_shotDict[shot['name']] = shot['ID']
					for key, value in sorted(self.nim_shotDict.items(), reverse=False):
						self.nim_shotChooser.addItem(self.clearPix, key)
						
						if self.flamePrefs['shotID'] == value:
							print "Found shot preference=", key
							shotIndex = shotIter
						
						shotIter += 1

					if self.flamePrefs['shotID'] != '':
						self.nim_shotChooser.setCurrentIndex(shotIndex)
		except:
			pass


	def nim_shotChanged(self):
		'''Action when job is selected'''
		#print "SHOW CHANGED"
		shotname = self.nim_shotChooser.currentText()
		if shotname:
			print "NIM: show=%s" % shotname

			shotID = self.nim_shotDict[shotname]

			##set showID
			self.nim_shotID = shotID

			self.nim_updateTask()


	def nim_updateTask(self):
		self.nim_tasks = {}
		self.nim_tasks = nimAPI.get_taskInfo(itemClass='SHOT', itemID=self.nim_shotID)
		print self.nim_tasks

		taskIndex = 0
		taskIter = 0
		self.nim_taskDict = {}
		try:
			self.nim_taskChooser.clear()
			if self.nim_taskChooser:
				if len(self.nim_tasks)>0:  
					for task in self.nim_tasks:
						taskTitle = task['taskName']
						if task['username'] :
							taskTitle += " - "+task['username']
						if task['taskDesc'] :
							taskTitle += " - "+task['taskDesc']
						self.nim_taskDict[taskTitle] = task['taskID']

						print "taskTitle: %s" % taskTitle
					for key, value in sorted(self.nim_taskDict.items(), reverse=False):
						self.nim_taskChooser.addItem(self.clearPix, key)
						
						if self.flamePrefs['taskID'] == value:
							print "Found task preference=", key
							taskIndex = taskIter
						
						taskIter += 1

					if self.flamePrefs['taskID'] != '':
						self.nim_taskChooser.setCurrentIndex(taskIndex)
		except:
			pass


	def nim_taskChanged(self):
		'''Action when job is selected'''
		#print "TASK CHANGED"
		taskTitle = self.nim_taskChooser.currentText()
		if taskTitle:
			print "NIM: task=%s" % taskTitle
			taskID = self.nim_taskDict[taskTitle]
			##set taskID
			self.nim_taskID = taskID


	def acceptTest(self):
		# Get Current Values For Static Objects
		self.nim_preset = self.nim_presetChooser.currentText()
		
		# Saving Preferences
		nimPrefs.update( 'Job', 'Flame', self.nim_jobID )
		nimPrefs.update( 'ServerID', 'Flame', self.nim_serverID )
		nimPrefs.update( 'Show', 'Flame', self.nim_showID )

		# Save Flame-NIM preferences for element associations
		self.flamePrefs["dailyPreset"] = self.nim_preset
		self.flamePrefs["jobID"] = self.nim_jobID
		self.flamePrefs["serverID"] = self.nim_serverID
		self.flamePrefs["showID"] = self.nim_showID
		self.flamePrefs["shotID"] = self.nim_shotID
		self.flamePrefs["taskID"] = self.nim_taskID
		writeFlamePrefs(self.flamePrefs)

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
		shotInfo = nimAPI.add_shot( showID=nim_showID, name=nim_shotName, frames=nim_duration )

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
		# print "Versions Returned: %s" % nim_versions

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

	# Resolve shot by associated openClipResolvedPath
	elements = nimAPI.find_elements(name=clipName, path=clipPath)
	print "Matching Clip Element Found: "
	# print elements 

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

	if nim_shotID :

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


def uploadEdit(nim_showID=None, mov_path='') :
	# Upload mov to a show as an edit
	success = False

	if nim_showID :
		if mov_path :
			#result = nimAPI.upload_edit(showID=nim_showID, path=mov_path)
			result = nimAPI.upload_reviewItem( itemID=nim_showID, itemType='show', path=mov_path )
			print result
			success = True
		else :
			status_msg = "NIM - upload_reviewItem missing movie path"
	else :
		status_msg = "NIM - upload_reviewItem missing showID"

	return success


def uploadDaily(nim_taskID=None, mov_path='') :
	# Upload mov to a show as an edit
	success = False

	if nim_taskID :
		if mov_path :
			#result = nimAPI.upload_dailies(taskID=nim_taskID, path=mov_path)
			result = nimAPI.upload_reviewItem( itemID=nim_taskID, itemType='task', path=mov_path )
			print result
			success = True
		else :
			status_msg = "NIM - upload_reviewItem missing movie path"
	else :
		status_msg = "NIM - upload_reviewItem missing taskID"

	return success


def nimScanForVersions(nim_showID=None, nim_shotID=None) :
	# find_elements in show with metadata flameAssetType : batchOpenClip
	# get element type
	# find all elements of type in shot
	clipCount = 0
	clipFail = 0

	if nim_showID :
		shots = nimAPI.get_shots(showID=nim_showID)
	if nim_shotID :
		shotInfo = nimAPI.get_shotInfo(shotID=nim_shotID)
		shots = []
		if shotInfo :
			shots.append( {'ID':nim_shotID, 'name':shotInfo[0]['shotName'] } )

	# Iterate through shots in show
	for shot in shots :
		if 'ID' in shot :
			nim_shotID = shot['ID']

			# Get Elements By extension
			# openClipElements = nimAPI.find_elements(showID=nim_showID, ext='.clip')
			openClipElements = nimAPI.find_elements(shotID=nim_shotID, ext='.clip')
			# print openClipElements

			for openClipElement in openClipElements :
				clipID = openClipElement['ID']
				shotID = openClipElement['shotID']
				clipPath = openClipElement['path'].encode('utf-8')
				clipName = openClipElement['name'].encode('utf-8')
				clipFile = os.path.join(clipPath,clipName)

				elementTypeID = openClipElement['elementTypeID']
				elements = nimAPI.find_elements(shotID=shotID, elementTypeID=elementTypeID)
				# print "Elements found"
				# print elements

				for element in elements :
					if element['ID'] != clipID :
						print "Element found for shotID %s" % shotID
						elementPath = element['path'].encode('utf-8')
						elementName = element['name'].encode('utf-8')
						
						# Update elementPath using server os resolution
						# print "Raw Element Path: %s" % elementPath
						elementPath = resolveServerOsPath(path=elementPath)

						# print "OS Element Path: %s" % elementPath
						
						fullPath = os.path.join(elementPath,elementName)
						# print "Full Path: %s" % fullPath

						# If sequence with name.frame.ext format, replace frame with *
						# This will limit dl_get_media_info failure when finding subfolders
						elementExt = os.path.splitext(elementName)[1]
						elementBasename = elementName.rpartition('.')[0].rpartition('.')[0]
						elementWildcard = elementBasename+".*"+elementExt
						# print "elementWildcard: %s" % elementWildcard

						clipUpdated = updateOpenClip( masterFile=clipFile, elementPath=elementPath, \
														elementName=elementName, elementWildcard=elementWildcard, recursive=False )
						if clipUpdated :
							if clipUpdated == -1 :
								clipFail += 1
							else :
								clipCount += 1

	clipSucess = {}
	clipSucess['clipCount'] = clipCount
	clipSucess['clipFail'] = clipFail
	return clipSucess
	

def nimBuildOpenClipFromElements(nim_showID=None, nim_shotID=None, nim_serverID=None) :
	# Find all element types on shots in a show
	# Update existing openClips of matching elementType
	# Create newClip if no matching type
	# print("nimBuildOpenClipFromElements")
	clipCount = 0
	clipFail = 0

	serverOsPathInfo = nimAPI.get_serverOSPath( nim_serverID, platform.system() )
	serverOSPath = serverOsPathInfo[0]['serverOSPath']


	if nim_showID :
		shots = nimAPI.get_shots(showID=nim_showID)
	if nim_shotID :
		shotInfo = nimAPI.get_shotInfo(shotID=nim_shotID)
		shots = []
		if shotInfo :
			shots.append( {'ID':nim_shotID, 'name':shotInfo[0]['shotName'] } )

	#Get NIM Element Types
	elementTypes = []
	elementTypesDict = {}
	elementTypes = nimAPI.get_elementTypes()
	
	# Iterate through shots in show
	for shot in shots :
		if 'ID' in shot :
			nim_shotID = shot['ID']
			nim_shotName = shot['name']
			print "Looking for elements in shot %s" % nim_shotName
			# Iterate through elements types to find nim elements
			if len(elementTypes)>0:
				for elementType in elementTypes:
					elementTypeID = elementType['ID']
					elementTypeName = elementType['name']
					print "Looking for %s elements" % elementTypeName
					
					elements = nimAPI.find_elements(shotID=nim_shotID, elementTypeID=elementTypeID)
					openClipElements = nimAPI.find_elements( shotID=nim_shotID, ext='.clip', elementTypeID=elementTypeID )

					# Create new openClip from comp path and elementTypeName
					nim_comp_path = os.path.join(serverOSPath,"<nim_shot_comp>")
					nim_comp_path = nimResolvePath(nim_shotID=nim_shotID, keyword_string=nim_comp_path)
					# print "nim_comp_path: %s" % nim_comp_path

					clipPath = nim_comp_path.encode('utf-8')
					clipName = nim_shotName +"_nimElement_"+ elementTypeName +".clip"
					clipFile = os.path.join(clipPath,clipName)

					for element in elements :
						# Compare to make sure not recursively adding openClip elements
						isOpenClip = False
						for openClipElement in openClipElements :
							clipID = openClipElement['ID']
							if element['ID'] == clipID :
								isOpenClip = True

						if not isOpenClip :
							print "Element found for shotID %s" % nim_shotID
							elementPath = element['path'].encode('utf-8')
							elementName = element['name'].encode('utf-8')
							
							# Update elementPath using server os resolution
							# print "Raw ElementPath: %s" % elementPath
							elementPath = resolveServerOsPath(elementPath)
							# print "OS ElementPath: %s" % elementPath

							fullPath = os.path.join(elementPath,elementName)
							# print "Full Path: %s" % fullPath

							# If sequence with name.frame.ext format, replace frame with *
							# This will limit dl_get_media_info failure when finding subfolders
							elementExt = os.path.splitext(elementName)[1]
							elementBasename = elementName.rpartition('.')[0].rpartition('.')[0]
							elementWildcard = elementBasename+".*"+elementExt
							# print "elementWildcard: %s" % elementWildcard

							clipUpdated = updateOpenClip( masterFile=clipFile, elementPath=elementPath, \
														elementName=elementName, elementWildcard=elementWildcard, recursive=False )
							if clipUpdated :
								# TODO: Add newly created openClip to shot elements
								# 		found_clips = nimAPI.find_elements(name=clipName, shotID=nim_shotID)
								#		if len(found_clips) == 0 :
								#			nimAPI.add_elements()
								if clipUpdated :
									if clipUpdated == -1 :
										clipFail += 1
									else :
										clipCount += 1
	
	clipSucess = {}
	clipSucess['clipCount'] = clipCount
	clipSucess['clipFail'] = clipFail
	return clipSucess					


def nimBuildOpenClipFromFolders(nim_showID=None, nim_shotID=None, nim_serverID=None, folders=None) :
	# Find all root folders for given show (comp, render, plates)
	# Update existing openClips with contents of folders
	# Create newClip if no matching type
	clipCount = 0
	clipFail = 0

	serverOsPathInfo = nimAPI.get_serverOSPath( nim_serverID, platform.system() )
	serverOSPath = serverOsPathInfo[0]['serverOSPath']

	if nim_showID :
		shots = nimAPI.get_shots(showID=nim_showID)
	if nim_shotID :
		shotInfo = nimAPI.get_shotInfo(shotID=nim_shotID)
		shots = []
		if shotInfo :
			shots.append( {'ID':nim_shotID, 'name':shotInfo[0]['shotName'] } )
	
	# Iterate through shots in show or single shot
	for shot in shots :
		if 'ID' in shot :
			nim_shotID = shot['ID']
			nim_shotName = shot['name']
			print "Looking for elements in shot %s" % nim_shotName
			# Iterate through elements types to find nim elements
			if len(folders)>0:
				for folder in folders:
					folderName = ''

					if folder == '<nim_shot_plates>' :
						folderName = 'plates'
					if folder == '<nim_shot_render>' :
						folderName = 'renders'
					if folder == '<nim_shot_comp>' :
						folderName = 'comps'

					nim_folder_path = os.path.join(serverOSPath,folder)
					nim_folder_path = nimResolvePath(nim_shotID=nim_shotID, keyword_string=nim_folder_path)
					# print "nim_folder_path: %s" % nim_folder_path

					clipPath = nim_folder_path.encode('utf-8')
					clipName = nim_shotName+"_nimProject_"+folderName+".clip"
					clipFile = os.path.join(clipPath,clipName)
					
					# Get Subfolders in nim_folder_path
					subfolders = []
					
					for root, dirs, files in os.walk(nim_folder_path, topdown=False) :
						for name in dirs :
							subfolders.append(os.path.join(root, name))
					
					for subfolder in subfolders :
						print("------folder iteration------------------------------------------------------------->")

						elementPath = subfolder.encode('utf-8')
						elementName = subfolder.rpartition('/')[2].encode('utf-8')
						
						# Update elementPath using server os resolution
						# print "Raw Element Path: %s" % elementPath
						elementPath = resolveServerOsPath(elementPath)
						# print "OS ElementPath: %s" % elementPath
						
						# print "clipFile: %s" % clipFile

						clipUpdated = updateOpenClip( masterFile=clipFile, elementPath=elementPath, \
														elementName=elementName, recursive=False )
						if clipUpdated :
							# TODO: Add newly created openClip to shot elements
							# 		found_clips = nimAPI.find_elements(name=clipName, shotID=nim_shotID)
							#		if len(found_clips) == 0 :
							#			nimAPI.add_elements()
							if clipUpdated == -1 :
								clipFail += 1
							else :
								clipCount += 1
					

	clipSucess = {}
	clipSucess['clipCount'] = clipCount
	clipSucess['clipFail'] = clipFail
	return clipSucess					


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


def resolveServerOsPath(path='') :
	#Convert path from known NIM server to OS relavtive path
	#print("resolveServerOsPath")

	_os = platform.system()
	serverID = ''
	servers = {}
	servers = nimAPI.get_allServers()
	
	path = path.replace('\\', '/')
	resolvedPath = path

	# Find matching server from path
	if len(servers) > 0:
		print "Servers Found: %s" % str(len(servers))
		for server in servers :
			linuxPath = ""
			winPath = ""
			osxPath = ""

			if server['path'] :
				linuxPath 	= server['path'].replace('\\', '/')
			if server['winPath'] :
				winPath 	= server['winPath'].replace('\\', '/')
			if server['osxPath'] :
				osxPath 	= server['osxPath'].replace('\\', '/')

			#print "Linux Path: %s" % linuxPath
			#print "Windows Path: %s" % winPath
			#print "OSX Path: %s" % osxPath

			if _os.lower() in ['darwin', 'mac'] :
				print "OS: OSX"
				# Compare against windows and linux & set to osx
				if winPath and path.startswith(winPath) :
					print "Translating Windows Path"
					pathTail = path[path.startswith(winPath) and len(winPath):]
					if pathTail.startswith('/') :
						pathTail = pathTail[1:]
					resolvedPath = os.path.join(osxPath,pathTail)
					break

				elif linuxPath and path.startswith(linuxPath) :
					print "Translating Linux Path"
					pathTail = path[path.startswith(linuxPath) and len(linuxPath):]
					if pathTail.startswith('/') :
						pathTail = pathTail[1:]
					resolvedPath = os.path.join(osxPath,pathTail)
					break


			elif _os.lower() in ['linux', 'linux2'] :
				print "OS: Linux"
				# Compare against windows and osx & set to linux
				if winPath and path.startswith(winPath) :
					print "Translating Windows Path"
					pathTail = path[path.startswith(winPath) and len(winPath):]
					if pathTail.startswith('/') :
						pathTail = pathTail[1:]
					resolvedPath = os.path.join(linuxPath,pathTail)
					break

				elif osxPath and path.startswith(osxPath) :
					print "Translating OSX Path"
					pathTail = path[path.startswith(osxPath) and len(osxPath):]
					if pathTail.startswith('/') :
						pathTail = pathTail[1:]
					resolvedPath = os.path.join(linuxPath,pathTail)
					break

	return resolvedPath


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


def updateOpenClip( masterFile='', elementPath='', elementName='', elementWildcard='', recursive=False ) :
	# print "MasterFile: 	%s" % masterFile
	# print "ElementPath: %s" % elementPath
	# print "ElementName: %s" % elementName
	# print "elementWildcard: %s" % elementWildcard

	clipUpdated = False

	# Filter filetype by extension
	# Allow only image sequence due to issue with possible mismatch frame rates for container media (.mov, etc )
	ext_whitelist = ['cin','als','jpg','jpeg','pict','pct','picio','sgi','pic','tga' \
					'iff','tdi','tif','tiff','rla','cin.pxz','tif.pxz','tiff.pxz','dpx','dpx.pxz' \
					'hdr','png','exr','exr.pxz','psd']

	# Get extension from elementName
	# assumes name.#.ext format
	elementExt = os.path.splitext(elementName)[1][1:].strip().lower()
	
	# if no extension (folder) carry on and catch later:
	if elementExt :
		# print "Ext: %s" % elementExt
		# Test file type to see if element is .clip
		# If file is type not in ext_whitelist then skip
		if elementExt in ext_whitelist :
			pass
		else :
			print "Media of type %s not supported. skipping update" % elementExt
			return False 
	else :
		print "Reading Folder..."

	elementBasename = elementName.rpartition('.')[0].rpartition('.')[0]
	if elementBasename == '' :
		elementBasename = elementName
	# print "elementBasename: %s" % elementBasename

	getMediaScript = ""
	mediaScriptPaths = ["/opt/Autodesk/mio/current/dl_get_media_info", \
						"/usr/discreet/mio/current/dl_get_media_info"]

	mediaScriptFound = False
	for getMediaScript in mediaScriptPaths :
		if os.path.isfile(getMediaScript) :
			mediaScriptFound = True
			break

	if not mediaScriptFound :
		print "ERROR: Flame script not installed: file %s missing" % getMediaScript
	else :
		print "Media Script Path: %s" % getMediaScript

		createNewClip = False

		if not os.path.isfile(masterFile) :
			print "Creating new openClip"
			apath = os.path.abspath(elementPath)
			tmpfile = masterFile
			createNewClip = True
			clipUpdated = True
		else :
			tmpfile = "tmp.clip"
			apath = os.path.abspath(elementPath)
			print "Adding folder %s" % apath
			#output a temp file 
			tmpfile = apath+"/"+tmpfile
			if os.path.isfile(tmpfile):
				os.remove(tmpfile)
			print "Temp File: %s" % tmpfile

		if elementWildcard :
			apath = apath+"/"+elementWildcard

		# Test if item is directory and if empty
		if os.path.isdir(apath) :
			if not os.listdir(apath):
				print "Skipping empty directory"
				return False

		try :
			# Write output of getMediaScript to file
			cmd_args = getMediaScript+" "+apath
			if recursive :
				print "dl_get_media_info recursive enabled"
				cmd_args = getMediaScript+" -r "+apath

			print "cmd: %s" % cmd_args

			pipes = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
			std_out, std_err = pipes.communicate()

			if pipes.returncode != 0:
				# Error
				err_msg = "%s. Code: %s" % (std_err.strip(), pipes.returncode)
				print '%s' % err_msg
				return False
			elif len(std_err):
				# return code is 0 (no error) : but we might have warning messages indicating failure
				print "ERROR: %s" % std_err
				if std_err.startswith("Could not get metadata from") :
					print "Possible directory attempted for scan - keep trying"
				else :
					print "Unknown Error - skipping media import"
					return False

			# Process Output
			print "Successfully parsed media"
			# print "std_out: %s" % std_out

			with open(tmpfile, "w") as f:
				f.write("{0}".format(std_out))


			# Check media type for valid extension
			try :
				tmpXML = ET.parse(tmpfile)
			except :
				print "Failed to parse XML. XML could be empty."
				if os.path.isfile(tmpfile):
					os.remove(tmpfile)
				return False

			for newTrack in tmpXML.iter('track') :
				newPathObject = newTrack.find("feeds/feed/spans/span/path")
				newPath = newPathObject.text
				print "tmpXML - newPath: %s" % newPath
				
				# If file is type not in ext_whitelist then skip
				newPath_ext = os.path.splitext(newPath)[1][1:].strip().lower()
				if newPath_ext in ext_whitelist :
					print "Valid media found %s: " % newPath_ext
				else :
					print "Media of type %s not supported. skipping append" % newPath_ext
					if os.path.isfile(tmpfile):
						os.remove(tmpfile)
					return False

		except :
			print "Failed to read media: %s" % apath
			print'%s' % traceback.print_exc()
			return -1


		# Only splice XML when masterFile does not exist
		if not createNewClip :
			print "Updating openClip..."
			
			try :
				sourceXML 	= ET.parse(masterFile)
			except :
				print "Failed to parse XML. XML could be empty."
				# print'%s' % traceback.print_exc()
				if os.path.isfile(tmpfile):
					os.remove(tmpfile)
				return False

			try :
				newXML 		= ET.parse(tmpfile)
			except :
				print "Failed to parse XML. XML could be empty."
				# print'%s' % traceback.print_exc()
				if os.path.isfile(tmpfile):
					os.remove(tmpfile)
				return False

			try :
				vuid = ''
				elementExists = False


				# Get first item in feed and use as the nbTicks reference
				src_nbTicks = None
				for srcTrack in sourceXML.iter('track') :
					for srcFeed in srcTrack.iter('feed') :
						src_nbTicksObj = srcFeed.find('startTimecode/nbTicks')
						src_nbTicks = src_nbTicksObj.text
						break
					else :
						continue
					break
				# print "Source nbTicks: %s" % src_nbTicks


				# Get new feed from file
				for newTrack in newXML.iter('track') :
					uid = newTrack.get('uid')
					newFeed = newTrack.find('feeds/feed')

					feedHandler = newFeed.find("./handler")
					newFeed.remove(feedHandler)
					
					if src_nbTicks :
						new_nbTicksObject = newTrack.find("feeds/feed/startTimecode/nbTicks")
						new_nbTicksObject.text = src_nbTicks

					newPathObject = newTrack.find("feeds/feed/spans/span/path")
					newPath = newPathObject.text
					# print "uid: %s" % uid
					# print "newFeed: %s" % ET.tostring(newFeed)
					# print "newPath: %s" % newPath
					
					# Check for path in sourceFile 
					# If Path exists ... skip append
					for srcPath in sourceXML.iter('path') :
						# print "srcPath: %s" % srcPath.text
						if newPath == srcPath.text :
							print "Element exists in clip... skipping append"
							elementExists = True

					if not elementExists :
						# Append new feed to source track
						for srcTrack in sourceXML.iter('track') :
							newFeed.set('vuid', elementBasename)
							srcTrack.find('feeds').append(newFeed)

				if not elementExists:
					# Append vUID to versions
					newVersion = sourceXML.find('versions')
					newVersionElement = ET.Element("version", {"type": "version", "uid": elementBasename})
					newVersion.insert(0, newVersionElement)
					xmlRoot = sourceXML.getroot()

					# Clean tmpfile - brute force remove errant <root/handler>
					print "Removing Handler"
					for handler in xmlRoot.findall("./handler") :
						print "Handler found"
						xmlRoot.remove(handler)

					resultXML	= ET.tostring(xmlRoot)

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

					print " Adding feed version %s" % vuid
					
					with open(outFile,"w") as f:
						f.write( resultXML )

					clipUpdated = True

				if os.path.isfile(tmpfile):
					os.remove(tmpfile)

			except :
				print "Failed reading XML"
				print'%s' % traceback.print_exc()
				if os.path.isfile(tmpfile):
					os.remove(tmpfile)
				return False

		else :
			# New openClip
			print "Building new openClip"

			# Update uid name with elementName
			try :
				newXML = ET.parse(tmpfile)
			except :
				print "Failed reading XML"
				print'%s' % traceback.print_exc()
				if os.path.isfile(tmpfile):
					os.remove(tmpfile)
				return False
			
			try :
				vuid = ''	
				
				for newFeed in newXML.iter('feeds') :
					feed = newFeed.find('feed')
					feed.set('vuid', elementBasename)

					feedHandler = feed.find("./handler")
					feed.remove(feedHandler)

				for newVersion in newXML.iter('versions') :
					newVersion.set('currentVersion', elementBasename)
					version = newVersion.find('version')
					version.set('uid', elementBasename)
					version.set('type', 'version')
				
				xmlRoot = newXML.getroot()

				# Clean tmpfile - brute force remove errant <root/handler>
				print "Removing Handler"
				for handler in xmlRoot.findall("./handler") :
					print "Handler found"
					xmlRoot.remove(handler)

				resultXML	= ET.tostring(xmlRoot)

				with open(tmpfile,"w") as f:
					f.write( resultXML )

			except :
				print "Failed to update openClip: %s" % tmpfile
				print'%s' % traceback.print_exc()

	return clipUpdated


def readFlamePrefs() :
	# Read Flame Specific Preferences
	
	flamePrefs = {}
	flamePrefs["sequencePreset"] = ""
	flamePrefs["editPreset"] = ""
	flamePrefs["dailyPreset"] = ""

	flamePrefs["jobID"] = ""
	flamePrefs["serverID"] = ""
	flamePrefs["showID"] = ""
	flamePrefs["shotID"] = ""
	flamePrefs["taskID"] = ""

	flamePrefs["videoElementID"] = ""
	flamePrefs["audioElementID"] = ""
	flamePrefs["sourceElementID"] = ""
	flamePrefs["batchElementID"] = ""
	flamePrefs["batchTaskTypeID"] = ""

	try :
		#  Read NIM preferences file :
		if os.path.isfile( flamePrefFile ) :
			with open(flamePrefFile) as flameFile :
				for line in flameFile :
					lineValues = line.rstrip('\n').split('=', 1)
					if lineValues[0] and lineValues[1] :
						flamePrefs[lineValues[0]] = lineValues[1]
	except Exception, e :
		print "Error: Unable to read Flame NIM preferences."
		
	return flamePrefs


def writeFlamePrefs( flamePrefs=None ) :
	# Write Flame Specifc Preferences
	if not flamePrefs :
		print "No preferences found. Not updating NIM Flame preferences."
		return False

	#  Retrieve old preferences :
	oldPrefs = {}
	try :
		if os.path.isfile( flamePrefFile ) :
			with open(flamePrefFile) as flameFile :
				for line in flameFile :
					lineValues = line.rstrip('\n').split('=', 1)
					if lineValues[0] and lineValues[1] :
						oldPrefs[lineValues[0]] = lineValues[1]
	except :
		print "Failed to read NIM Flame Preferences for updating"
		print 'NIM - ERROR: %s' % traceback.print_exc()
		return False

	# Update All Exsting Keys
	for oldKey, oldValue in oldPrefs.iteritems() :
		for key, value in flamePrefs.iteritems() :
			if key == oldKey :
				oldPrefs[oldKey] = value

	# Add New Keys
	for key, value in flamePrefs.iteritems() :
		keyFound = False
		for oldKey, oldValue in oldPrefs.iteritems() :
			if oldKey == key :
				keyFound = True
				break
		if not keyFound :
			oldPrefs[key] = value

	#  Write new preferences :
	try :
		with open(flamePrefFile, 'w') as flameFile :
			for key, value in oldPrefs.iteritems() :
				line = key+"="+value+"\n"
				flameFile.write(line)
	except :
		print "Failed to write NIM Flame Preferences"
		print 'NIM - ERROR: %s' % traceback.print_exc()
		return False

	return True