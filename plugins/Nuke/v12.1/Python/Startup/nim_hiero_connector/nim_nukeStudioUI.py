#!/usr/bin/env python
#******************************************************************************
#
# Filename: Nuke/Python/Startup/nim_hiero_connector/nim_nukeStudioUI.py
# Version:  v7.2.0.250228
#
# Copyright (c) 2014-2022 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

from hiero.core import *
import hiero.ui
from hiero.core import log

from PySide2.QtWidgets import *
from PySide2.QtCore import *

import sys,os,re,string
import base64
import platform
import ntpath

import nim_core.UI as nimUI
import nim_core.nim_api as nimAPI
import nim_core.nim_prefs as nimPrefs
import nim_core.nim_file as nimFile
import nim_core.nim as nim
import nim_core.nim_print as P

import nimHieroConnector
import nimProjectHelpers

def get_main_window():
    window_name = 'Foundry::UI::DockMainWindow'

    for w in QApplication.topLevelWidgets():
        if w.inherits('QMainWindow') and window_name in w.metaObject().className():
            return w
    return None

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        parent = parent or get_main_window()
        super(MainWindow, self).__init__(parent)

def statusBar():
	"""Returns an instance of the MainWindow's status bar, displayed at the bottom of the main window()"""
	main_window = MainWindow()
 	return main_window.statusBar()

# def statusBar():
# 	"""Returns an instance of the MainWindow's status bar, displayed at the bottom of the main window()"""
# 	return hiero.ui.mainWindow().statusBar()

hiero.ui.statusBar = statusBar

g_nim_jobID = None
g_nim_showID = None
g_nim_showFolder = ''
g_nim_element = ''
g_nim_elementTypeID = None
g_nim_publishElement = False
g_nim_serverID = None
g_nim_serverOSPath = ''
g_nim_taskID = None
g_nim_taskFolder = ''
g_nim_basename = ''
g_nim_versionID = None


def openDialog():
	'''Open the NIM Open Project Dialog'''
	dialog = NimNS_openDialog()
	if dialog.exec_():
		P.info("Open Project")
		#versionID = nimHieroConnector.g_nim_versionID
		versionID = dialog.nim_versionID
		verInfo = nimAPI.get_verInfo(versionID)
		nim_OS = platform.system()
		verOsPath = nimAPI.get_osPath(versionID, nim_OS)
		if verInfo:
			print "VerInfo: %s" % verInfo
		if verOsPath:
			print "verOsPath: %s" % verOsPath

		# Get Server OS Path from server ID
		serverOsPathInfo = nimAPI.get_serverOSPath( verInfo[0]['serverID'], platform.system() )
		P.info("Server OS Path: %s" % serverOsPathInfo)
		if serverOsPathInfo:
			serverOSPath = serverOsPathInfo[0]['serverOSPath']
		else:
			print "Server OS path not returned from NIM"
			# Show warning
			msgBox = QMessageBox()
			msgBox.setTextFormat(Qt.RichText)
			result = msgBox.information(None, "Warning", "Could not open project. Server OS path not returned from NIM.", QMessageBox.Ok)
			return

		projectPath = os.path.join(verOsPath['path'], verInfo[0]['filename'])
		projectPath = projectPath.replace('\\','/')
		print "Path: %s" % projectPath
		try:
			hiero.core.openProject(projectPath)
			project = hiero.core.projects()[-1]

			print "Storing NIM Globals"
			nimHieroConnector.g_nim_jobID = dialog.nim_jobID
			nimHieroConnector.g_nim_serverID = dialog.nim_serverID
			nimHieroConnector.g_nim_serverOSPath = serverOSPath
			nimHieroConnector.g_nim_serverID = verInfo[0]['serverID']
			nimHieroConnector.g_nim_showID = dialog.nim_showID
			nimHieroConnector.g_nim_showFolder = dialog.nim_showFolder
			nimHieroConnector.g_nim_taskID = dialog.nim_taskID
			nimHieroConnector.g_nim_taskFolder = dialog.nim_taskFolder
			nimHieroConnector.g_nim_basename = dialog.nim_basename
			nimHieroConnector.g_nim_versionID = dialog.nim_versionID

			print "Saving Preferences"
			nimPrefs.update( 'Job', 'Nuke', dialog.nim_jobChooser.currentText() )
			nimPrefs.update( 'ServerPath', 'Nuke', serverOSPath )
			nimPrefs.update( 'Show', 'Nuke', dialog.nim_showChooser.currentText() )
			nimPrefs.update( 'Task', 'Nuke', dialog.nim_taskChooser.currentText() )
			nimPrefs.update( 'Basename', 'Nuke', dialog.nim_basename )
			nimPrefs.update( 'Version', 'Nuke', dialog.nim_versionChooser.currentItem().text() )

		except:
			print "Could not open project.", sys.exc_info()[0]
			# Show warning
			msgBox = QMessageBox()
			msgBox.setTextFormat(Qt.RichText)
			result = msgBox.information(None, "Warning", "Could not open project. Check to see if the file exists or if project is already open.", QMessageBox.Ok)

def saveDialog():
	'''Open the NIM SaveAs Project Dialog'''
	#Get Current Project
	currentProject = nimProjectHelpers.currentProject()
	print "Current Project: %s" % currentProject.name()

	dialog = NimNS_saveDialog(currentProject=currentProject)
	if dialog.exec_():
		P.info("Save Project")
		
		#Get Server Path
		serverOSPath = dialog.nim_serverOSPath
		print "serverOSPath: %s" % serverOSPath
		if serverOSPath == '':
			# Show Error
			msgBox = QMessageBox()
			msgBox.setTextFormat(Qt.RichText)
			result = msgBox.information(None, "Server Info Missing",  \
				"The server path is missing.\nCheck to make sure the job is online and you have selected a server.", \
				QMessageBox.Ok )
			return

		#Get Show Root
		showRoot = dialog.nim_showRootFolder
		if showRoot == '':
			# Show Error
			msgBox = QMessageBox()
			msgBox.setTextFormat(Qt.RichText)
			result = msgBox.information(None, "Show Info Missing",  \
				"The show root path is missing.\nCheck to make sure the job is online and you have selected a show.", \
				QMessageBox.Ok )
			return
		
		#Append Task Folder
		taskFolder = dialog.nim_taskFolder
		if taskFolder == '':
			# Show Error
			msgBox = QMessageBox()
			msgBox.setTextFormat(Qt.RichText)
			result = msgBox.information(None, "Task Info Missing",  \
				"The task folder is missing.\nCheck to make sure the job is online and you have selected a task.", \
				QMessageBox.Ok )
			return
		
		#set filename to Showname_Task_Tag_v01
		showName = dialog.nim_showNameClean
		if showName == '':
			# Show Error
			msgBox = QMessageBox()
			msgBox.setTextFormat(Qt.RichText)
			result = msgBox.information(None, "Show Info Missing",  \
				"The show name is missing.\nCheck to make sure the job is online and you have selected a show.", \
				QMessageBox.Ok )
			return

		#Get Basename
		basename = dialog.nim_basename
		
		#Get Tag
		tag = dialog.nim_tag.strip()
		#Sanitize Tag
		valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
		tag = ''.join(c for c in tag if c in valid_chars)
		tag = tag.replace(' ','_') # replace spaces with _
		tag = tag.replace('.','_') # replace . with _

		#check if basename is selected
		projectBasename = ''
		basenameVersion = 1
		version = "_v01"

		use_basename = dialog.use_basename
		if use_basename:
			# check latest version of basename and incremeant
			# version = basenameVersion+1
			basenameVersionInfo = nimAPI.get_baseVer(showID=dialog.nim_showID, basename=basename)
			if not basenameVersionInfo:
				print "Basename Information Not Found"
				return

			print "Current Basename Version: %s" % basenameVersionInfo[0]['version']
			basenameVersion = int(basenameVersionInfo[0]['version'])+1
			version = '_v'+format(basenameVersion, '02')
			print "New Basename Version: %s" % version
			projectBasename = basename
		else:
			projectBasename = showName+"_"+taskFolder
			if tag != '':
				print "Tag: %s" % tag
				projectBasename = projectBasename+"_"+tag
			# check existing basename to see if there is a conflict
			basenameList = dialog.nim_basenames
			print "BasenameList: %s" % basenameList
			for basenameItem in basenameList:
				if projectBasename == basenameItem['basename']:
					#	if conflict ask to save new version or enter a new tag
					print "Conflict: %s" % projectBasename
					# Show warning
					msgBox = QMessageBox()
					msgBox.setTextFormat(Qt.RichText)
					result = msgBox.information(None, "Basename Conflict", "The generated basename conflicts with an existing basename: %s \n\n \
						Select OK to create a new version in the existing basename.\n\n \
						Select CANCEL to create a unique tag." % projectBasename, \
						QMessageBox.Ok | QMessageBox.Cancel)
					# Continue if user clicks OK
					if result == QMessageBox.Ok:
						#print "OK"
						basenameVersionInfo = nimAPI.get_baseVer(showID=dialog.nim_showID, basename=projectBasename)
						if not basenameVersionInfo:
							print "Basename Information Not Found"
							return
						print "Current Basename Version: %s" % basenameVersionInfo[0]['version']
						basenameVersion = int(basenameVersionInfo[0]['version'])+1
						version = '_v'+format(basenameVersion, '02')
						print "New Basename Version: %s" % version
					else:
						#print "CANCEL"
						saveDialog()
						return
				else:
					#	else  version = "_v01"
					print "No Conflict"
					basenameVersion = 1
					version = "_v01"

		
		projectOutputPath = os.path.join(serverOSPath, showRoot, taskFolder, projectBasename)
		projectOutputPath = projectOutputPath.replace('\\','/')
		
		# append extension
		ext = ".hrox"
		import nuke
		if nuke.env['nc'] :
			ext = '.hroxnc'
		
		projectVersion = projectBasename+version+ext
		
		projectOutputFullPath = os.path.join(projectOutputPath, projectVersion)
		projectOutputFullPath = projectOutputFullPath.replace('\\','/')

		#save project
		P.info("Saving Project: %s" % projectOutputFullPath)
		#check if file path exists - create if not
		try:
			os.makedirs( projectOutputPath )
		except OSError:
			pass
		currentProject.saveAs(projectOutputFullPath)
		P.info("Project Saved")

		#log to NIM
		P.info("Logging to NIM")

		nimResult = nimAPI.save_file( parent='SHOW', parentID=dialog.nim_showID,	\
							task_type_ID=dialog.nim_taskID, task_folder=dialog.nim_taskFolder,	\
							userID=dialog.nim_userID, basename=projectBasename, filename=projectVersion,
							path=projectOutputPath, ext=ext, version=basenameVersion,
							comment=dialog.nim_comment, serverID=dialog.nim_serverID )

		#get returned fileID and store globals
		if nimResult['success'] == True:
			print "Save File Result: %s" % nimResult
			print "Storing NIM Globals..."
			nimHieroConnector.g_nim_versionID = nimResult
			nimHieroConnector.g_nim_jobID = dialog.nim_jobID
			nimHieroConnector.g_nim_serverID = dialog.nim_serverID
			nimHieroConnector.g_nim_serverOSPath = dialog.nim_serverOSPath
			nimHieroConnector.g_nim_showID = dialog.nim_showID
			nimHieroConnector.g_nim_showFolder = dialog.nim_showRootFolder
			nimHieroConnector.g_nim_taskID = dialog.nim_taskID
			nimHieroConnector.g_nim_taskFolder = dialog.nim_taskFolder
			nimHieroConnector.g_nim_basename = projectBasename
			nimHieroConnector.g_nim_versionID = dialog.nim_versionID
			
			print "Saving Preferences"
			nimPrefs.update( 'Job', 'Nuke', dialog.nim_jobChooser.currentText() )
			nimPrefs.update( 'ServerPath', 'Nuke', serverOSPath )
			nimPrefs.update( 'Show', 'Nuke', dialog.nim_showChooser.currentText() )
			nimPrefs.update( 'Task', 'Nuke', dialog.nim_taskChooser.currentText() )
			nimPrefs.update( 'Basename', 'Nuke', projectBasename )
			nimPrefs.update( 'Version', 'Nuke', projectVersion )
	return

def versionDialog():
	'''Open the NIM Version Up Project Dialog'''
	#Get Current Project
	currentProject = nimProjectHelpers.currentProject()
	print "Current Project: %s" % currentProject.name()

	dialog = NimNS_versionDialog(currentProject=currentProject)
	if dialog.exec_():
		P.info("Version Project")
		currentVersionID = nimHieroConnector.g_nim_versionID
		
		print "Current ShowID: %s" % nimHieroConnector.g_nim_showID
		print "Current Basename: %s" % nimHieroConnector.g_nim_basename
		print "Current Version: %s" % currentVersionID

		basenameVersionInfo = nimAPI.get_baseVer(showID=nimHieroConnector.g_nim_showID, basename=nimHieroConnector.g_nim_basename)
		if not basenameVersionInfo:
			# Basename Error
			print "Basename Information Not Found"
			msgBox = QMessageBox()
			msgBox.setTextFormat(Qt.RichText)
			result = msgBox.information(None, "Basename Info Missing",  \
				"The current basename information is missing.\nPlease use the NIM Save As menu to save the project.", \
				QMessageBox.Ok )
			return

		print "Current Basename Version: %s" % basenameVersionInfo[0]['version']
		basenameVersion = int(basenameVersionInfo[0]['version'])+1
		version = '_v'+format(basenameVersion, '02')
		print "New Basename Version: %s" % version
		projectBasename = nimHieroConnector.g_nim_basename

		projectOutputPath = os.path.join(nimHieroConnector.g_nim_serverOSPath, nimHieroConnector.g_nim_showFolder, nimHieroConnector.g_nim_taskFolder)
		projectOutputPath = projectOutputPath.replace('\\','/')
		
		# append extension
		ext = ".hrox"
		import nuke
		if nuke.env['nc'] :
			ext = '.hroxnc'

		projectVersion = projectBasename+version+ext
		
		projectOutputFullPath = os.path.join(projectOutputPath, projectBasename, projectVersion)
		projectOutputFullPath = projectOutputFullPath.replace('\\','/')

		#save project
		P.info("Saving Project: %s" % projectOutputFullPath)
		currentProject.saveAs(projectOutputFullPath)
		P.info("Project Saved")

		#log to NIM
		P.info("Logging to NIM")

		nimResult = nimAPI.save_file( parent='SHOW', parentID=nimHieroConnector.g_nim_showID,	\
							task_type_ID=nimHieroConnector.g_nim_taskID, task_folder=nimHieroConnector.g_nim_taskFolder,	\
							userID=dialog.nim_userID, basename=projectBasename, filename=projectVersion,
							path=projectOutputPath, ext=ext, version=basenameVersion,
							comment=dialog.nim_comment, serverID=nimHieroConnector.g_nim_serverID )

		#get returned fileID and store in global
		if nimResult['success'] == True:
			print "Save File Result: %s" % nimResult
			print "Storing NIM Globals..."
			nimHieroConnector.g_nim_versionID = nimResult
			
			print "Saving Preferences"
			nimPrefs.update( 'Version', 'Nuke', projectVersion )

		return


class NimNS_openDialog(QDialog):
	def __init__(self):
		super(NimNS_openDialog, self).__init__()
		'''NIM NukeStudio Project Management UI'''

		self.app=nimFile.get_app()
		self.prefs=nimPrefs.read()

		try:
			self.user=self.prefs['NIM_User']
			self.pref_job=self.prefs[self.app+'_Job']
			self.pref_show=self.prefs[self.app+'_Show']
			self.pref_server=self.prefs[self.app+'_ServerPath']
			self.pref_task=self.prefs[self.app+'_Task']
			self.pref_basename=self.prefs[self.app+'_Basename']
			self.pref_version=self.prefs[self.app+'_Version']
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

		print "NIM: user=%s" % self.user
		print "NIM: userID=%s" % self.nim_userID
		print "NIM: default job=%s" % self.pref_job



		self.nim_jobPaths = {}
		self.nim_showPaths = {}
		self.nim_shotPaths = {}
		self.nim_showFolder = ''
		self.nim_servers = {}
		self.nim_serverID = None
		self.nim_serverOSPath = ''
		self.nim_tasks = {}
		self.nim_taskDict = {}
		self.nim_taskID = None
		self.nim_taskFolder = ''
		self.nim_taskFolderDict = {}
		self.nim_basename = ''
		self.nim_basenames = {}
		self.nim_versions = {}
		self.nim_versionDict = {}
		self.nim_versionID = None

		self.useBasename = False

		#Get NIM Jobs
		self.nim_jobID = None
		self.nim_jobs = nimAPI.get_jobs(self.nim_userID)
		if not self.nim_jobs :
			print "No Jobs Found"
			self.nim_jobs["None"]="0"

		self.nim_jobChooser = QComboBox()

		self.nim_shows = []
		self.nim_showDict = {}
		self.nim_showID = None
		self.nim_showChooser = QComboBox()

		self.nim_tasks = nimAPI.get_tasks(app='HIERO', userType='all')
		print "Tasks: %s" % self.nim_tasks
		self.nim_taskChooser = QComboBox()

		self.nim_basenameChooser = QListWidget()
		self.nim_versionChooser = QListWidget()
		
		self.setWindowTitle("NIM Project Open")
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
		horizontalLayout0 = QHBoxLayout()
		horizontalLayout0.setSpacing(-1)
		horizontalLayout0.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout0.setObjectName("HorizontalLayout0")
		self.nimJobLabel = QLabel()
		self.nimJobLabel.setFixedWidth(64)
		self.nimJobLabel.setText("Job:")
		horizontalLayout0.addWidget(self.nimJobLabel)
		self.nim_jobChooser.setToolTip("Choose the job you wish to export shots to.")
		horizontalLayout0.addWidget(self.nim_jobChooser)
		horizontalLayout0.setStretch(1, 40)
		groupLayout.setLayout(0, QFormLayout.SpanningRole, horizontalLayout0)


		# JOBS: Add dictionary in ordered list
		jobIndex = 0
		jobIter = 0
		if len(self.nim_jobs)>0:
			for key, value in sorted(self.nim_jobs.items(), reverse=True):
				self.nim_jobChooser.addItem(key)
				if nimHieroConnector.g_nim_jobID:
					if nimHieroConnector.g_nim_jobID == value:
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
		horizontalLayout1 = QHBoxLayout()
		horizontalLayout1.setSpacing(-1)
		horizontalLayout1.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout1.setObjectName("HorizontalLayout1")
		self.nimShowLabel = QLabel()
		self.nimShowLabel.setFixedWidth(64)
		self.nimShowLabel.setText("Show:")
		horizontalLayout1.addWidget(self.nimShowLabel)
		self.nim_showChooser.setToolTip("Choose the show you wish to export shots to.")
		horizontalLayout1.addWidget(self.nim_showChooser)
		horizontalLayout1.setStretch(1, 40)
		groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout1)
		self.nim_showChooser.currentIndexChanged.connect(self.nim_showChanged)

		
		
		# TASKS: List box for server selection
		horizontalLayout2 = QHBoxLayout()
		horizontalLayout2.setSpacing(-1)
		horizontalLayout2.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout2.setObjectName("HorizontalLayout2")
		self.nimTaskLabel = QLabel()
		self.nimTaskLabel.setFixedWidth(64)
		self.nimTaskLabel.setText("Task:")
		horizontalLayout2.addWidget(self.nimTaskLabel)
		self.nim_taskChooser.setToolTip("Choose the task for the project.")
		horizontalLayout2.addWidget(self.nim_taskChooser)
		horizontalLayout2.setStretch(1, 40)
		groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout2)

		# TASKS: Add dictionary in ordered list
		taskIndex=1
		taskIter=1
		if len(self.nim_tasks)>0:
			self.nim_taskChooser.addItem("Select...")
			for task in self.nim_tasks:
				self.nim_taskDict[task['name']] = task['ID']
				self.nim_taskFolderDict[task['ID']] = task['folder']
			for key, value in sorted(self.nim_taskDict.items(), reverse=False):
				self.nim_taskChooser.addItem(key)
				if nimHieroConnector.g_nim_taskID:
					if nimHieroConnector.g_nim_taskID == value:
						self.pref_task = key
						taskIndex = taskIter
						print "Found matching taskID, task=", key
						print "taskIndex=",taskIndex
				else:
					if self.pref_task == key:
						print "Found matching Task Name, task=", key
						taskIndex = taskIter
				taskIter +=1

			if self.pref_task != '':
				print "self.pref_task=",self.pref_task
				self.nim_taskChooser.setCurrentIndex(taskIndex)
		self.nim_taskChooser.currentIndexChanged.connect(self.nim_taskChanged)

		

		# BASENAMES: List box for basename selection
		horizontalLayout3 = QHBoxLayout()
		horizontalLayout3.setSpacing(-1)
		horizontalLayout3.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout3.setObjectName("HorizontalLayout3")
		self.nimBasenameLabel = QLabel()
		self.nimBasenameLabel.setFixedWidth(64)
		self.nimBasenameLabel.setText("Basename:")
		horizontalLayout3.addWidget(self.nimBasenameLabel)
		#self.nim_basenameChooser = QListWidget()
		self.nim_basenameChooser.setToolTip("Choose the basename of the project.")
		horizontalLayout3.addWidget(self.nim_basenameChooser)
		horizontalLayout3.setStretch(1, 40)
		groupLayout.setLayout(3, QFormLayout.SpanningRole, horizontalLayout3)
		self.nim_basenameChooser.currentItemChanged.connect(self.nim_basenameChanged)



		# VERSIONS: List box for server selection
		horizontalLayout4 = QHBoxLayout()
		horizontalLayout4.setSpacing(-1)
		horizontalLayout4.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout4.setObjectName("HorizontalLayout4")
		self.nimVersionLabel = QLabel()
		self.nimVersionLabel.setFixedWidth(64)
		self.nimVersionLabel.setText("Version:")
		horizontalLayout4.addWidget(self.nimVersionLabel)
		self.nim_versionChooser.setToolTip("Choose the version of the project.")
		horizontalLayout4.addWidget(self.nim_versionChooser)
		horizontalLayout4.setStretch(1, 40)
		groupLayout.setLayout(4, QFormLayout.SpanningRole, horizontalLayout4)
		self.nim_versionChooser.currentItemChanged.connect(self.nim_versionChanged)

		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("Open Project")
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Executes exports on selection for each selected preset")
		self._buttonbox.accepted.connect(self.acceptTest)
		self._buttonbox.rejected.connect(self.reject)
		horizontalLayout9 = QHBoxLayout()
		horizontalLayout9.setSpacing(-1)
		horizontalLayout9.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout9.setObjectName("HorizontalLayout4")
		spacerItem4 = QSpacerItem(175, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
		horizontalLayout9.addItem(spacerItem4)
		horizontalLayout9.addWidget(self._buttonbox)
		horizontalLayout9.setStretch(1, 40)
		groupLayout.setLayout(5, QFormLayout.SpanningRole, horizontalLayout9)

		#self.setLayout(layout)
		self.setLayout(groupLayout)
		layout.addWidget(groupBox)

		self.nim_jobChanged() #trigger job changed to load choosers


	def nim_jobChanged(self):
		'''Action when job is selected'''
		#print "JOB CHANGED"
		job = self.nim_jobChooser.currentText()
		self.nim_jobID = self.nim_jobs[job]
		self.nim_jobPaths = nimAPI.get_paths('job', self.nim_jobID)

		##set jobID global
		#--nimHieroConnector.g_nim_jobID = self.nim_jobID

		#self.nim_updateServer()
		self.nim_updateShow()
		

	def nim_updateServer(self):
		self.nim_servers = {}
		self.nim_servers = nimAPI.get_jobServers(self.nim_jobID)

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

			self.nim_serverID = serverID
			#--nimHieroConnector.g_nim_serverID = self.nim_serverID

			#print "Setting serverID=",serverID

			serverInfo = nimAPI.get_serverOSPath(serverID, self.nim_OS)
			if serverInfo:
				if len(serverInfo)>0:
					self.nim_serverOSPath = serverInfo[0]['serverOSPath']
					print "NIM: serverOSPath=%s" % self.nim_serverOSPath
					#set nim global
					#--nimHieroConnector.g_nim_serverOSPath = self.nim_serverOSPath
				else:
					print "NIM: No Server Found"
			else:
				print "NIM: No Data Returned"


	def nim_updateShow(self):
		self.nim_shows = []
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
						if nimHieroConnector.g_nim_showID:
							if nimHieroConnector.g_nim_showID == value:
								print "Found matching showID, show=", key
								self.pref_show == key
								showIndex = showIter
						else:
							if self.pref_show == key:
								print "Found matching Show Name, show=", key
								showIndex = showIter
						showIter += 1

					if self.pref_show != '':
						self.nim_showChooser.setCurrentIndex(showIndex)
		except:
			pass


	def nim_showChanged(self):
		'''Action when job is selected'''
		print "SHOW CHANGED"
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

			#Clear Lists
			self.nim_basenameChooser.clear()
			self.nim_versionChooser.clear()

			#Load Lists
			self.nim_updateTask()


	def nim_updateTask(self):
		self.nim_tasks = {}
		self.nim_tasks = nimAPI.get_tasks(app='HIERO', userType='all')

		self.nim_taskDict = {}
		self.nim_taskFolderDict = {}
		taskIter=1
		taskIndex=1
		try:
			self.nim_taskChooser.clear()
			if self.nim_taskChooser:
				self.nim_taskChooser.addItem("Select...")
				if len(self.nim_tasks)>0:  
					for task in self.nim_tasks:
						self.nim_taskDict[task['name']] = task['ID']
						self.nim_taskFolderDict[task['ID']] = task['folder']
					for key, value in sorted(self.nim_taskDict.items(), reverse=False):
						self.nim_taskChooser.addItem(key)
						if nimHieroConnector.g_nim_taskID:
							if nimHieroConnector.g_nim_taskID == value:
								self.pref_task = key
								taskIndex = taskIter
								print "Found matching taskID, task=", key
								print "taskIndex=",taskIndex
						else:
							if self.pref_task == key:
								print "Found matching Task Name, task=", key
								taskIndex = taskIter
						taskIter +=1

					if self.pref_task != '':
						print "self.pref_task=",self.pref_task
						self.nim_taskChooser.setCurrentIndex(taskIndex)
		except:
			pass


	def nim_taskChanged(self):
		'''Action when task is selected'''
		#print "TASK CHANGED"
		taskName = self.nim_taskChooser.currentText()
		if taskName:
			print "NIM: task=%s" % taskName
			if taskName != 'Select...':
				taskID = self.nim_taskDict[taskName]
				taskFolder = self.nim_taskFolderDict[taskID]

				self.nim_taskID = taskID
				self.nim_taskFolder = taskFolder

				print "Setting taskID=%s" % taskID
				print "Setting taskFolder=%s" % taskFolder

				self.nim_updateBasename()


	def nim_updateBasename(self):
		print "Update Basename"
		print "ShowID=%s" % self.nim_showID
		self.nim_basenames = {}
		self.nim_basenames = nimAPI.get_bases(showID=self.nim_showID, taskID=self.nim_taskID)

		print "Basenames: %s" % self.nim_basenames

		baseIter=0
		baseIndex=0
		try:
			self.nim_basenameChooser.clear()
			if self.nim_basenameChooser:
				if len(self.nim_basenames)>0:
					for basename in self.nim_basenames:
						print "Basename: ",basename['basename']
						item=QListWidgetItem( self.nim_basenameChooser )
						item.setText( basename['basename'] )
						#item.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled )
					
						if nimHieroConnector.g_nim_basename:
							if nimHieroConnector.g_nim_basename == basename['basename']:
								self.pref_basename = basename['basename']
								baseIndex = baseIter
								print "Found matching basename in globals, basename=", basename['basename']
						else:
							if self.pref_basename == basename['basename']:
								baseIndex = baseIter
								print "Found matching basename in prefs, basename=", basename['basename']
						baseIter +=1

					if self.pref_basename != '':
						print "selecting basename: ",self.pref_basename
						self.nim_basenameChooser.setCurrentRow(baseIndex)
					

		except:
			print "Failed to update Basenames"
			pass


	def nim_basenameChanged(self):
		'''Action when basename is selected'''
		#print "BASENAME CHANGED"
		if self.nim_basenameChooser.currentItem():
			basename = self.nim_basenameChooser.currentItem().text()
			if basename:
				print "NIM: basename=%s" % basename
				self.nim_basename = basename
				#--nimHieroConnector.g_nim_basename = self.nim_basename

				print "Setting basename=%s" % basename
				self.nim_updateVersion()


	def nim_updateVersion(self):
		self.nim_versions = {}
		self.nim_versions = nimAPI.get_vers(showID=self.nim_showID, basename=self.nim_basename)
		print "Versions: %s" % self.nim_versions

		self.nim_versionDict = {}
		verIndex=0
		verIter=0
		try:
			self.nim_versionChooser.clear()
			print "Versions Cleared"
			if self.nim_versionChooser:
				if len(self.nim_versions)>0:
					print "Versions Found" 
					for version in self.nim_versions:
						self.nim_versionDict[version['filename']] = version['fileID']
						
					for key, value in sorted(self.nim_versionDict.items(), reverse=True):
						item=QListWidgetItem( self.nim_versionChooser )
						item.setText( key )
						#item.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled )

						if nimHieroConnector.g_nim_versionID:
							if nimHieroConnector.g_nim_versionID == value:
								self.pref_version = key
								verIndex = verIter
								print "Found matching versionID, version=", key
						else:
							if self.pref_version == key:
								verIndex = verIter
								print "Found matching version, version=", key
						verIter +=1

					if self.pref_version != '':
						print "selecting version: ",self.pref_version
						print "verIndex: ",verIndex
						self.nim_versionChooser.setCurrentRow(verIndex)
					
		except:
			print "Failed to update Versions"
			pass


	def nim_versionChanged(self):
		'''Action when job is selected'''
		#print "VERSION CHANGED"
		if self.nim_versionChooser.currentItem():
			versionname = self.nim_versionChooser.currentItem().text()
			if versionname:
				print "NIM: version=%s" % versionname

				versionID = self.nim_versionDict[versionname]

				##set versionID
				self.nim_versionID = versionID

				'''
				self.nim_versionPaths = nimAPI.get_paths('version', versionID)
				if self.nim_versionPaths:
					if len(self.nim_versionPaths)>0:
						#print "NIM: versionPaths=", self.nim_versionPaths
						self.nim_versionFolder = self.nim_versionPaths['root']
						nimHieroConnector.g_nim_versionFolder = self.nim_versionFolder
					else:
						print "NIM: No Versions Found"
				else:
					print "NIM: No Data Returned"
				'''

	def acceptTest(self):
		self.accept()


class NimNS_saveDialog(QDialog):
	def __init__(self, currentProject=''):
		super(NimNS_saveDialog, self).__init__()
		'''NIM NukeStudio Project Management UI'''

		self.app=nimFile.get_app()
		self.prefs=nimPrefs.read()
		try:
			self.user=self.prefs['NIM_User']
			self.pref_job=self.prefs[self.app+'_Job']
			self.pref_show=self.prefs[self.app+'_Show']
			self.pref_server=self.prefs[self.app+'_ServerPath']
			self.pref_task=self.prefs[self.app+'_Task']
			self.pref_basename=self.prefs[self.app+'_Basename']
			self.pref_version=self.prefs[self.app+'_Version']
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

		print "NIM: user=%s" % self.user
		print "NIM: userID=%s" % self.nim_userID
		print "NIM: default job=%s" % self.pref_job

		

		self.nim_jobChooser = QComboBox()

		self.nim_jobPaths = {}
		self.nim_showPaths = {}
		self.nim_shotPaths = {}
		
		self.nim_shows = []
		self.nim_showDict = {}
		self.nim_showID = None
		self.nim_showNameClean = ''
		self.nim_showRootFolder = ''
		self.nim_showFolderDict = {}
		self.nim_showChooser = QComboBox()

		self.nim_servers = {}
		self.nim_serverID = None
		self.nim_serverOSPath = ''
		self.nim_serverChooser = QComboBox()

		self.nim_tasks = {}
		self.nim_taskDict = {}
		self.nim_taskID = None
		self.nim_taskFolder = ''
		self.nim_taskFolderDict = {}
		self.nim_taskChooser = QComboBox()

		self.nim_basename = ''
		self.nim_basenames = {}
		self.use_basename = False
		self.nim_basenameChooser = QListWidget()

		self.nim_versions = {}
		self.nim_versionDict = {}
		self.nim_versionID = None
		self.nim_versionChooser = QListWidget()

		self.nim_tag = ''
		self.nim_tagEdit = QLineEdit()

		self.nim_comment = ''
		self.nim_commentEdit = QLineEdit()

		#Get NIM Jobs
		self.nim_jobID = None
		self.nim_jobs = nimAPI.get_jobs(self.nim_userID)
		if not self.nim_jobs :
			print "No Jobs Found"
			self.nim_jobs["None"]="0"
		
		
		
		self.nim_tasks = nimAPI.get_tasks(app='HIERO', userType='all')
		print "Tasks: %s" % self.nim_tasks

		self.setWindowTitle("NIM Project Save")
		self.setSizeGripEnabled(True)

		self._exportTemplate = None

		tag_jobID = None
		tag_showID = None

		layout = QVBoxLayout()
		formLayout = QFormLayout()
		groupBox = QGroupBox()
		groupLayout = QFormLayout()
		groupBox.setLayout(groupLayout)

		# PROJECT: Display label for the current project
		projectName = ''
		if currentProject:
			projectName = currentProject.name()
		horizontalLayoutA = QHBoxLayout()
		horizontalLayoutA.setSpacing(-1)
		horizontalLayoutA.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayoutA.setObjectName("HorizontalLayout6")
		self.nimProjectLabel = QLabel()
		self.nimProjectLabel.setFixedWidth(64)
		self.nimProjectLabel.setText("Project:")
		horizontalLayoutA.addWidget(self.nimProjectLabel)
		self.nim_projectName = QLabel()
		self.nim_projectName.setText(projectName)
		self.nim_projectName.setToolTip("The name of the current project.")
		horizontalLayoutA.addWidget(self.nim_projectName)
		horizontalLayoutA.setStretch(1, 40)
		groupLayout.setLayout(0, QFormLayout.SpanningRole, horizontalLayoutA)

		# JOBS: List box for job selection
		horizontalLayout0 = QHBoxLayout()
		horizontalLayout0.setSpacing(-1)
		horizontalLayout0.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout0.setObjectName("HorizontalLayout0")
		self.nimJobLabel = QLabel()
		self.nimJobLabel.setFixedWidth(64)
		self.nimJobLabel.setText("Job:")
		horizontalLayout0.addWidget(self.nimJobLabel)
		self.nim_jobChooser.setToolTip("Choose the job you wish to export shots to.")
		horizontalLayout0.addWidget(self.nim_jobChooser)
		horizontalLayout0.setStretch(1, 40)
		groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout0)

		# JOBS: Add dictionary in ordered list
		jobIndex = 0
		jobIter = 0
		if len(self.nim_jobs)>0:
			for key, value in sorted(self.nim_jobs.items(), reverse=True):
				self.nim_jobChooser.addItem(key)
				if nimHieroConnector.g_nim_jobID:
					if nimHieroConnector.g_nim_jobID == value:
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
		horizontalLayout1 = QHBoxLayout()
		horizontalLayout1.setSpacing(-1)
		horizontalLayout1.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout1.setObjectName("HorizontalLayout1")
		self.nimServerLabel = QLabel()
		self.nimServerLabel.setFixedWidth(64)
		self.nimServerLabel.setText("Server:")
		horizontalLayout1.addWidget(self.nimServerLabel)
		#self.nim_serverChooser = QComboBox()
		self.nim_serverChooser.setToolTip("Choose the server you wish to export shots to.")
		horizontalLayout1.addWidget(self.nim_serverChooser)
		horizontalLayout1.setStretch(1, 40)
		groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout1)
		self.nim_serverChooser.currentIndexChanged.connect(self.nim_serverChanged)

		# SHOWS: List box for show selection
		horizontalLayout2 = QHBoxLayout()
		horizontalLayout2.setSpacing(-1)
		horizontalLayout2.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout2.setObjectName("HorizontalLayout2")
		self.nimShowLabel = QLabel()
		self.nimShowLabel.setFixedWidth(64)
		self.nimShowLabel.setText("Show:")
		horizontalLayout2.addWidget(self.nimShowLabel)
		self.nim_showChooser.setToolTip("Choose the show you wish to export shots to.")
		horizontalLayout2.addWidget(self.nim_showChooser)
		horizontalLayout2.setStretch(1, 40)
		groupLayout.setLayout(3, QFormLayout.SpanningRole, horizontalLayout2)
		self.nim_showChooser.currentIndexChanged.connect(self.nim_showChanged)
		
		# TASKS: List box for server selection
		horizontalLayout3 = QHBoxLayout()
		horizontalLayout3.setSpacing(-1)
		horizontalLayout3.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout3.setObjectName("HorizontalLayout3")
		self.nimTaskLabel = QLabel()
		self.nimTaskLabel.setFixedWidth(64)
		self.nimTaskLabel.setText("Task:")
		horizontalLayout3.addWidget(self.nimTaskLabel)
		self.nim_taskChooser.setToolTip("Choose the task for the project.")
		horizontalLayout3.addWidget(self.nim_taskChooser)
		horizontalLayout3.setStretch(1, 40)
		groupLayout.setLayout(4, QFormLayout.SpanningRole, horizontalLayout3)

		# TASKS: Add dictionary in ordered list
		taskIndex = 0
		taskIter=0
		if len(self.nim_tasks)>0:
			self.nim_taskChooser.addItem("Select...")
			for task in self.nim_tasks:
				self.nim_taskDict[task['name']] = task['ID']
				self.nim_taskFolderDict[task['ID']] = task['folder']
			for key, value in sorted(self.nim_taskDict.items(), reverse=False):
				self.nim_taskChooser.addItem(key)
				if nimHieroConnector.g_nim_taskID:
					if nimHieroConnector.g_nim_taskID == value:
						self.pref_task = key
						taskIndex = taskIter
						print "Found matching taskID, task=", key
						print "taskIndex=",taskIndex
				else:
					if self.pref_task == key:
						print "Found matching Task Name, task=", key
						taskIndex = taskIter
				taskIter +=1

			if self.pref_task != '':
				#print "self.pref_task=",self.pref_task
				self.nim_taskChooser.setCurrentIndex(taskIndex)

		self.nim_taskChooser.currentIndexChanged.connect(self.nim_taskChanged)
		

		# BASENAMES: List box for basename selection
		horizontalLayout4 = QHBoxLayout()
		horizontalLayout4.setSpacing(-1)
		horizontalLayout4.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout4.setObjectName("HorizontalLayout4")
		self.nimBasenameLabel = QLabel()
		self.nimBasenameLabel.setFixedWidth(64)
		self.nimBasenameLabel.setText("Basename:")
		horizontalLayout4.addWidget(self.nimBasenameLabel)
		self.nim_basenameChooser.setToolTip("Choose the basename of the project.")
		horizontalLayout4.addWidget(self.nim_basenameChooser)
		horizontalLayout4.setStretch(1, 40)
		groupLayout.setLayout(5, QFormLayout.SpanningRole, horizontalLayout4)
		self.nim_basenameChooser.currentItemChanged.connect(self.nim_basenameChanged)


		# TAG: List box for tag entry
		horizontalLayout5 = QHBoxLayout()
		horizontalLayout5.setSpacing(-1)
		horizontalLayout5.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout5.setObjectName("HorizontalLayout5")
		self.nimTagLabel = QLabel()
		self.nimTagLabel.setFixedWidth(64)
		self.nimTagLabel.setText("Tag:")
		horizontalLayout5.addWidget(self.nimTagLabel)
		self.nim_tagEdit.setToolTip("Enter a unique tag.")
		horizontalLayout5.addWidget(self.nim_tagEdit)
		horizontalLayout5.setStretch(1, 40)
		groupLayout.setLayout(6, QFormLayout.SpanningRole, horizontalLayout5)

		self.nim_tagEdit.textEdited.connect(self.nim_tagChanged)

		# VERSIONS: List box for version display
		horizontalLayout6 = QHBoxLayout()
		horizontalLayout6.setSpacing(-1)
		horizontalLayout6.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout6.setObjectName("HorizontalLayout5")
		self.nimVersionLabel = QLabel()
		self.nimVersionLabel.setFixedWidth(64)
		self.nimVersionLabel.setText("Version:")
		horizontalLayout6.addWidget(self.nimVersionLabel)
		self.nim_versionChooser.setToolTip("Current versions of the project.")
		horizontalLayout6.addWidget(self.nim_versionChooser)
		horizontalLayout6.setStretch(1, 40)
		groupLayout.setLayout(7, QFormLayout.SpanningRole, horizontalLayout6)
		self.nim_versionChooser.currentItemChanged.connect(self.nim_versionChanged)


		# COMMENT: List box for comment entry
		horizontalLayout7 = QHBoxLayout()
		horizontalLayout7.setSpacing(-1)
		horizontalLayout7.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout7.setObjectName("HorizontalLayout7")
		self.nimCommentLabel = QLabel()
		self.nimCommentLabel.setFixedWidth(64)
		self.nimCommentLabel.setText("Comment:")
		horizontalLayout7.addWidget(self.nimCommentLabel)
		self.nim_commentEdit.setToolTip("Enter a unique comment.")
		horizontalLayout7.addWidget(self.nim_commentEdit)
		horizontalLayout7.setStretch(1, 40)
		groupLayout.setLayout(8, QFormLayout.SpanningRole, horizontalLayout7)
		self.nim_commentEdit.textEdited.connect(self.nim_commentChanged)

		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("Save Project")
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Executes exports on selection for each selected preset")
		self._buttonbox.accepted.connect(self.acceptTest)
		self._buttonbox.rejected.connect(self.reject)
		horizontalLayout8 = QHBoxLayout()
		horizontalLayout8.setSpacing(-1)
		horizontalLayout8.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout8.setObjectName("HorizontalLayout8")
		spacerItem4 = QSpacerItem(175, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
		horizontalLayout8.addItem(spacerItem4)
		horizontalLayout8.addWidget(self._buttonbox)
		horizontalLayout8.setStretch(1, 40)
		groupLayout.setLayout(9, QFormLayout.SpanningRole, horizontalLayout8)

		#self.setLayout(layout)
		self.setLayout(groupLayout)
		layout.addWidget(groupBox)

		self.nim_jobChanged() #trigger job changed to load choosers


	def nim_jobChanged(self):
		'''Action when job is selected'''
		#print "JOB CHANGED"
		job = self.nim_jobChooser.currentText()
		self.nim_jobID = self.nim_jobs[job]
		self.nim_jobPaths = nimAPI.get_paths('job', self.nim_jobID)

		#update dropdowns
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
		self.nim_showRootFolder = ''
		#print self.nim_shows

		showIndex = 0
		showIter = 0
		self.nim_showDict = {}
		self.nim_showFolderDict = {}
		try:
			self.nim_showChooser.clear()
			if self.nim_showChooser:
				if len(self.nim_shows)>0:  
					for show in self.nim_shows:
						self.nim_showDict[show['showname']] = show['ID']
						self.nim_showFolderDict[show['ID']] = show['folder']
					for key, value in sorted(self.nim_showDict.items(), reverse=False):
						self.nim_showChooser.addItem(key)
						if nimHieroConnector.g_nim_showID:
							if nimHieroConnector.g_nim_showID == value:
								print "Found matching showID, show=", key
								self.pref_show == key
								showIndex = showIter
						else:
							if self.pref_show == key:
								print "Found matching Show Name, show=", key
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
			print "NIM: show=%s" % showname

			showID = self.nim_showDict[showname]

			##set showID 
			self.nim_showID = showID
			self.nim_showNameClean = self.nim_showFolderDict[showID]

			self.nim_showPaths = nimAPI.get_paths('show', showID)
			if self.nim_showPaths:
				if len(self.nim_showPaths)>0:
					#print "NIM: showPaths=", self.nim_showPaths
					#set task dropdown to "Select..."
					if self.nim_taskChooser:
						self.nim_taskChooser.setCurrentIndex(0)

					#set vars
					self.nim_showRootFolder = self.nim_showPaths['root']
				else:
					print "NIM: No Show Paths Found"
			else:
				print "NIM: No Data Returned"

			#Clear Lists
			self.nim_basenameChooser.clear()
			self.nim_versionChooser.clear()

			#Update Lists
			self.nim_updateTask()


	def nim_updateTask(self):
		self.nim_tasks = {}
		self.nim_tasks = nimAPI.get_tasks(app='HIERO', userType='all')
		self.nim_taskID = 0
		self.nim_taskFolder = ''
		self.nim_taskDict = {}
		self.nim_taskFolderDict = {}
		taskIter=1
		taskIndex=1
		try:
			self.nim_taskChooser.clear()
			if self.nim_taskChooser:
				self.nim_taskChooser.addItem("Select...")
				if len(self.nim_tasks)>0:  
					for task in self.nim_tasks:
						self.nim_taskDict[task['name']] = task['ID']
						self.nim_taskFolderDict[task['ID']] = task['folder']
					for key, value in sorted(self.nim_taskDict.items(), reverse=False):
						self.nim_taskChooser.addItem(key)
						if nimHieroConnector.g_nim_taskID:
							if nimHieroConnector.g_nim_taskID == value:
								self.pref_task = key
								taskIndex = taskIter
								print "Found matching taskID, task=", key
								print "taskIndex=",taskIndex
						else:
							if self.pref_task == key:
								print "Found matching Task Name, task=", key
								taskIndex = taskIter
						taskIter +=1

					if self.pref_task != '':
						print "self.pref_task=",self.pref_task
						self.nim_taskChooser.setCurrentIndex(taskIndex)
		except:
			pass


	def nim_taskChanged(self):
		'''Action when task is selected'''
		#print "TASK CHANGED"
		taskName = self.nim_taskChooser.currentText()
		if taskName:
			print "NIM: task=%s" % taskName
			if taskName != 'Select...':
				taskID = self.nim_taskDict[taskName]
				taskFolder = self.nim_taskFolderDict[taskID]
				
				#set vars
				self.nim_taskID = taskID
				self.nim_taskFolder = taskFolder

				print "Setting taskID=%s" % taskID
				print "Setting taskFolder=%s" % taskFolder

				self.nim_updateBasename()


	def nim_updateBasename(self):
		print "Update Basename"
		print "ShowID=%s" % self.nim_showID
		#clear vars
		self.nim_basenames = ''
		self.nim_basenames = {}
		self.nim_basenames = nimAPI.get_bases(showID=self.nim_showID, taskID=self.nim_taskID)

		#print "Basenames: %s" % self.nim_basenames

		baseIter=0
		baseIndex=0
		try:
			self.nim_basenameChooser.clear()
			if self.nim_basenameChooser:
				if len(self.nim_basenames)>0:
					for basename in self.nim_basenames:
						#print basename['basename']
						item=QListWidgetItem( self.nim_basenameChooser )
						item.setText( basename['basename'] )
						#item.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled )

						'''
						if nimHieroConnector.g_nim_basename:
							if nimHieroConnector.g_nim_basename == basename['basename']:
								self.pref_basename = basename['basename']
								baseIndex = baseIter
								print "Found matching basename in globals, basename=", basename['basename']
						else:
							if self.pref_basename == basename['basename']:
								baseIndex = baseIter
								print "Found matching basename in prefs, basename=", basename['basename']
						baseIter +=1
						'''
					'''
					if self.pref_basename != '':
						print "selecting basename: ",self.pref_basename
						self.nim_basenameChooser.setCurrentRow(baseIndex)
					'''
		except:
			print "Failed to update Basenames"
			pass


	def nim_basenameChanged(self):
		'''Action when basename is selected'''
		#print "BASENAME CHANGED"
		if self.nim_basenameChooser.currentItem():
			basename = self.nim_basenameChooser.currentItem().text()
			if basename:
				#set vars
				self.nim_basename = basename

				print "Setting basename=%s" % basename
				self.nim_updateVersion()
				self.use_basename = True


	def nim_updateVersion(self):
		#clear vars
		self.nim_versions = ''
		self.nim_versionDict = {}
		self.nim_versions = {}
		self.nim_versions = nimAPI.get_vers(showID=self.nim_showID, basename=self.nim_basename)
		#print "Versions: %s" % self.nim_versions

		try:
			self.nim_versionChooser.clear()
			#print "Versions Cleared"
			if self.nim_versionChooser:
				if len(self.nim_versions)>0:
					print "Versions Found" 
					for version in self.nim_versions:
						self.nim_versionDict[version['filename']] = version['fileID']
						#print "Version: %s" % version
						
					for key, value in sorted(self.nim_versionDict.items(), reverse=True):
						#print "Key: %s" % key
						item=QListWidgetItem( self.nim_versionChooser )
						item.setText( key )
						item.setFlags( Qt.NoItemFlags )
					
		except:
			print "Failed to update Versions"
			pass


	def nim_versionChanged(self):
		'''Action when job is selected'''
		#print "SHOW CHANGED"
		if self.nim_versionChooser.currentItem():
			versionname = self.nim_versionChooser.currentItem().text()
			if versionname:
				print "NIM: version=%s" % versionname
				#set versionID
				versionID = self.nim_versionDict[versionname]
				self.nim_versionID = versionID


	def nim_tagChanged(self):
		'''Action when tag is changed'''
		self.nim_basenameChooser.clearSelection()
		self.nim_basenameChooser.clearFocus()
		self.use_basename = False
		self.nim_tag = self.nim_tagEdit.text()


	def nim_commentChanged(self):
		'''Action when comment is changed'''
		self.nim_comment = self.nim_commentEdit.text()


	def acceptTest(self):
		self.accept()


class NimNS_versionDialog(QDialog):
	def __init__(self, currentProject=''):
		super(NimNS_versionDialog, self).__init__()
		'''NIM NukeStudio Project Management UI'''

		self.prefs=nimPrefs.read()
		try:
			self.user=self.prefs['NIM_User']
			#self.pref_job=self.prefs[self.app+'_Job']
			#self.pref_show=self.prefs[self.app+'_Show']
			#self.pref_server=self.prefs[self.app+'_ServerPath']
			#self.pref_task=self.prefs[self.app+'_Task']
			#self.pref_basename=self.prefs[self.app+'_Basename']
			#self.pref_version=self.prefs[self.app+'_Version']
		except:
			#return False
			pass

		self.nim_userID = nimAPI.get_userID(self.user)
		if not self.nim_userID :
			nimUI.GUI().update_user()
			userInfo=nim.NIM().userInfo()
			self.user = userInfo['name']
			self.nim_userID = userInfo['ID']

		print "NIM: user=%s" % self.user
		print "NIM: userID=%s" % self.nim_userID

		

		self.nim_comment = ''

		self.setWindowTitle("NIM Project Version")
		self.setSizeGripEnabled(True)

		self._exportTemplate = None

		layout = QVBoxLayout()
		formLayout = QFormLayout()
		groupBox = QGroupBox()
		groupLayout = QFormLayout()
		groupBox.setLayout(groupLayout)

		# PROJECT: Display label for the current project
		projectName = ''
		if currentProject:
			projectName = currentProject.name()
		horizontalLayout0 = QHBoxLayout()
		horizontalLayout0.setSpacing(-1)
		horizontalLayout0.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout0.setObjectName("HorizontalLayout6")
		self.nimProjectLabel = QLabel()
		self.nimProjectLabel.setFixedWidth(64)
		self.nimProjectLabel.setText("Project:")
		horizontalLayout0.addWidget(self.nimProjectLabel)
		self.nim_projectName = QLabel()
		self.nim_projectName.setText(projectName)
		self.nim_projectName.setToolTip("The name of the current project.")
		horizontalLayout0.addWidget(self.nim_projectName)
		horizontalLayout0.setStretch(1, 40)
		groupLayout.setLayout(0, QFormLayout.SpanningRole, horizontalLayout0)

		
		# COMMENT: List box for comment entry
		horizontalLayout1 = QHBoxLayout()
		horizontalLayout1.setSpacing(-1)
		horizontalLayout1.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout1.setObjectName("HorizontalLayout7")
		self.nimCommentLabel = QLabel()
		self.nimCommentLabel.setFixedWidth(64)
		self.nimCommentLabel.setText("Comment:")
		horizontalLayout1.addWidget(self.nimCommentLabel)
		self.nim_commentEdit = QLineEdit()
		self.nim_commentEdit.setToolTip("Enter a unique comment.")
		horizontalLayout1.addWidget(self.nim_commentEdit)
		horizontalLayout1.setStretch(1, 40)
		groupLayout.setLayout(1, QFormLayout.SpanningRole, horizontalLayout1)

		self.nim_commentEdit.textEdited.connect(self.nim_commentChanged)

		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("Save Project")
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
		self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Executes exports on selection for each selected preset")
		self._buttonbox.accepted.connect(self.acceptTest)
		self._buttonbox.rejected.connect(self.reject)
		#layout.addWidget(self._buttonbox)
		horizontalLayout2 = QHBoxLayout()
		horizontalLayout2.setSpacing(-1)
		horizontalLayout2.setSizeConstraint(QLayout.SetDefaultConstraint)
		horizontalLayout2.setObjectName("HorizontalLayout8")
		spacerItem4 = QSpacerItem(175, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
		horizontalLayout2.addItem(spacerItem4)
		horizontalLayout2.addWidget(self._buttonbox)
		horizontalLayout2.setStretch(1, 40)
		groupLayout.setLayout(2, QFormLayout.SpanningRole, horizontalLayout2)

		#self.setLayout(layout)
		self.setLayout(groupLayout)
		layout.addWidget(groupBox)

	def nim_commentChanged(self):
		'''Action when comment is changed'''
		self.nim_comment = self.nim_commentEdit.text()

	def acceptTest(self):
		self.accept()