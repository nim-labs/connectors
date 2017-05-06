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
'''
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET
'''

# Relative path to append for NIM Scripts
nimFlamePythonPath = os.path.dirname(os.path.realpath(__file__))
nimFlamePythonPath = nimFlamePythonPath.replace('\\','/')
nimScriptPath = re.sub(r"\/plugins/Flame/python$", "", nimFlamePythonPath)
nimFlamePresetPath = os.path.join(re.sub(r"\/python$", "", nimFlamePythonPath),'presets')

print "NIM Script Path: %s" % nimScriptPath
print "NIM Python Path: %s" % nimFlamePythonPath
print "NIM Preset Path: %s" % nimFlamePresetPath



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

		
		#Get NIM Element Types
		self.nim_elementTypes = []
		self.nim_elementTypesDict = {}
		self.nim_elementTypes = nimAPI.get_elementTypes()
		if len(self.nim_elementTypes)>0:
			for element in self.nim_elementTypes:
				self.nim_elementTypesDict[element['name']] = element['ID']


		#Get NIM Task Types
		self.nim_taskTypes = []
		self.nim_taskTypesDict = {}
		self.nim_taskFolderDict = {}
		self.nim_taskTypes = nimAPI.get_tasks(app='NUKE', userType='all')
		
		if len(self.nim_taskTypes)>0:
			for task in self.nim_taskTypes:
				self.nim_taskTypesDict[task['name']] = task['ID']
				self.nim_taskFolderDict[task['ID']] = task['folder']


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
		connectorImage = QPixmap(nimFlamePythonPath+"/flm2nim.png")
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
		#Saving Preferences
		nimPrefs.update( 'Job', 'Flame', self.nim_jobID )
		nimPrefs.update( 'Show', 'Flame', self.nim_showID )
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


def nimExportElement(nim_shotID=None, info=None) :
	# Update Elements in NIM on postAssetExport

	# TODO: Get NIM Element type from dialog for each assetType option

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
		nim_destinationPath = info['destinationPath']
		nim_resolvedPath = info['resolvedPath']
		nim_fullPath = os.path.join(nim_destinationPath, nim_resolvedPath)

		nim_element_path = nim_fullPath.rpartition('/')
		nim_path = nim_element_path[0]
		nim_name = nim_element_path[2]
		
		# Add Media Item as Element
		element_result = nimAPI.add_element( parent='shot', parentID=nim_shotID, path=nim_path, name=nim_name, \
									startFrame=nim_sourceIn, endFrame=nim_sourceOut, handles=nim_handleIn, isPublished=False )

		print "NIM - %s has been added to %s in NIM." % (nim_assetType, nim_shotName)
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



