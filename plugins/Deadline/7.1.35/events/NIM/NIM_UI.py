import os, sys, traceback, time, threading

from collections import deque

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Deadline.Scripting import *

from DeadlineUI.Controls.Scripting.DeadlineScriptDialog import DeadlineScriptDialog

#Add NIM event/nim_core dir to search path
nim_event = os.path.join( RepositoryUtils.GetEventsDirectory(), "NIM")
sys.path.append( nim_event )
import nim_getPrefs

########################################################################
## Globals
########################################################################
scriptDialog = None
nimScriptPath = ''
nim_prefs = None
nim_URL = None

nim_userID = ''
nim_user = ''
nim_serverID = ''
nim_jobID = ''
nim_showID = ''
nim_shotID = ''
nim_fileID = ''
nim_typeID = ''
nim_assetID = ''

nim_basename = ''
nim_jobName = ''
nim_showName = ''
nim_class = ''
nim_taskID = ''
nim_shotName = ''
nim_assetName = ''
nim_itemID = ''

nim_renderName = ''

nimScriptPath = nim_getPrefs.getNimScriptPath()
if nimScriptPath:
	#print "NIM Prefs Found in Dialog"

	if not nimScriptPath in sys.path :
		sys.path.append( nimScriptPath )
		#print 'NIM ~> Appended NIM Python directory to system paths...\nNIM ~>     %s' % nimScriptPath

	#print 'NIM ~> Importing NIM Libraries'

	try:
		import nim_core.nim_api as nimAPI
		import nim_core.nim_file as nimFile
		import nim_core.nim_print as nimPrint
		import nim_core.nim_prefs as nimPrefs
	except:
		print( traceback.format_exc() )

	try:
		#print ('NIM ~> Reading NIM Preferences')
		nim_prefs=nimPrefs.read()
	except:
		print( traceback.format_exc() )

########################################################################
## Main Function Called By Deadline
########################################################################
def __main__( *args ):
	global scriptDialog
	global nim_URL
	global nim_prefs

	global nim_userID
	global nim_user
	global nim_serverID
	global nim_jobID
	global nim_showID
	global nim_shotID
	global nim_fileID
	global nim_typeID
	global nim_assetID

	global nim_basename
	global nim_jobName
	global nim_showName
	global nim_class
	global nim_taskID
	global nim_shotName
	global nim_assetName
	global nim_itemID

	global nim_renderName

	config = RepositoryUtils.GetEventPluginConfig( "NIM" )
	nim_URL = config.GetConfigEntryWithDefault("NimURL","").strip()

	if len( args ) > 0:
		#Parse out the args (if any)
		for arg in args:
			if arg.startswith( "nim_userID" ):
				nim_userID = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_user" ):
				nim_user = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_serverID" ):
				nim_serverID = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_jobID" ):
				nim_jobID = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_showID" ):
				nim_showID = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_shotID" ):
				nim_shotID = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_fileID" ):
				nim_fileID = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_typeID" ):
				nim_typeID = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_assetID" ):
				nim_assetID = arg.split( '=', 1 )[1]

			elif arg.startswith( "nim_basename" ):
				nim_basename = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_jobName" ):
				nim_jobName = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_showName" ):
				nim_showName = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_class" ):
				nim_class = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_taskID" ):
				nim_taskID = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_shotName" ):
				nim_shotName = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_assetName" ):
				nim_assetName = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_itemID" ):
				nim_itemID = arg.split( '=', 1 )[1]
			elif arg.startswith( "nim_renderName" ):
				nim_renderName = arg.split( '=', 1 )[1]
			else:
				appName = arg

		scriptDialog = NimDialog( nim_URL, nimScriptPath, parentAppName=args[-1] )
	else:
		scriptDialog = NimDialog( nim_URL, nimScriptPath )

	scriptDialog.setWindowFlags( Qt.WindowStaysOnTopHint )
	scriptDialog.ShowDialog( True )

########################################################################
## Subclass of DeadlineScriptDialog for the UI
########################################################################
class NimDialog( DeadlineScriptDialog ):
	global nim_URL
	global nim_prefs
	global nimScriptPath
	
	global nim_userID
	global nim_user
	global nim_serverID
	global nim_jobID
	global nim_showID
	global nim_shotID
	global nim_fileID
	global nim_typeID
	global nim_assetID

	global nim_basename
	global nim_jobName
	global nim_showName
	global nim_class
	global nim_taskID
	global nim_shotName
	global nim_assetName
	global nim_itemID

	global nim_renderName

	#currentUser = None

	#defaultProject = None
	#defaultTask = None
	#defaultAsset = None

	parentApp = ""
	settings = ()
	stickySettings = {}

	logMessages = [""]

	#These dictionaries map from string keys displayed in combo boxes to actual Ftrack objects
	#curJobDict = {}
	#curTaskDict = {}
	#curAssetDict = {}

	#These dictionaries cache tasks/assets from projects/tasks (respectively) not currently selected
	#cachedTasks = {}
	#cachedAssets = {}

	def __init__( self, nim_URL, nimScriptPath, parentAppName="", parent=None ):
		super( NimDialog, self ).__init__( parent )

		self.nim_URL = nim_URL

		if nim_user is '':
			#print "Reading NIM Prefs for User"
			self.nim_user = nim_prefs['NIM_User']
		else:
			self.nim_user = nim_user
		
		self.nim_userID = nim_userID
		if nim_userID is '':
			if self.nim_user is not '':
				self.nim_userID = nimAPI.get_userID(self.nim_user)

		self.nim_serverID = nim_serverID
		self.nim_jobID = nim_jobID
		self.nim_showID = nim_showID
		self.nim_shotID = nim_shotID
		self.nim_fileID = nim_fileID
		self.nim_typeID = nim_typeID
		self.nim_assetID = nim_assetID

		self.nim_basename = nim_basename
		self.nim_jobName = nim_jobName
		self.nim_showName = nim_showName
		self.nim_class = nim_class
		self.nim_taskID = nim_taskID
		self.nim_shotName = nim_shotName
		self.nim_assetName = nim_assetName
		self.nim_itemID = nim_itemID

		self.nim_renderName = nim_renderName

		self.nim_users = nimAPI.get_userList()
		self.nim_usersDict = {}
		self.pref_user = self.nim_user

		#Get NIM Jobs
		self.nim_jobs = []
		self.nim_jobsDict = {}
		self.pref_job = self.nim_jobID
		
		self.nim_assets = []
		self.nim_assetsDict = {}
		self.pref_asset = self.nim_assetID

		self.nim_shows = []
		self.nim_showsDict = {}
		self.pref_show = self.nim_showID

		self.nim_shots = []
		self.nim_shotsDict = {}
		self.pref_shot = self.nim_shotID

		self.nim_tasks = []
		self.nim_tasksDict = {}
		self.pref_task = self.nim_taskID

		self.parentApp = parentAppName

		# dialogHeight = 410
		# self.SetSize( dialogWidth, dialogHeight )

		self.SetTitle( "NIM Scene Information" )
		self.SetIcon( os.path.join( RepositoryUtils.GetEventsDirectory(), "NIM", "NIM.ico" ) )

		self.AddGrid()
		curRow = 0
		self.AddControlToGrid( "Separator1", "SeparatorControl", "NIM Fields", curRow, 0, colSpan=3 )
		curRow += 1

		#User
		self.AddControlToGrid( "UserLabel", "LabelControl", "User", curRow, 0, "The current user.", expand=False )
		self.nim_userChooser = self.AddControlToGrid( "nim_userChooser", "ComboControl", "", curRow, 1, colSpan=2 )
		curRow += 1

		userIndex = 0
		userIter = 0
		if self.nim_users:
			if len(self.nim_users)>0:
				for userInfo in self.nim_users:
						self.nim_usersDict[userInfo['username']] = userInfo['ID']
				for key, value in sorted(self.nim_usersDict.items(), reverse=False):
					self.nim_userChooser.addItem(key)
					if self.nim_userID == value:
						#print "Found matching userID, user=", key
						self.pref_user = key
						userIndex = userIter
					userIter += 1

				if self.pref_user != '':
					self.nim_userChooser.setCurrentIndex(userIndex)
		else:
			#print "Failed to get NIM users"
			pass
		


		#Job Name
		self.AddControlToGrid( "JobLabel", "LabelControl", "Job", curRow, 0, "The job for the current task.", expand=False )
		self.nim_jobChooser = self.AddControlToGrid( "nim_jobChooser", "ComboControl", "", curRow, 1, colSpan=2 )
		curRow += 1

		

		#Type Name
		self.AddControlToGrid( "TypeLabel", "LabelControl", "Type", curRow, 0, "Select a task type.", expand=False )
		self.nim_typeChooser = self.AddComboControlToGrid( "nim_typeChooser", "ComboControl", "", (), curRow, 1, colSpan=2 )
		self.nim_typeChooser.addItem("Asset")
		self.nim_typeChooser.addItem("Shot")
		self.nim_typeChooser.currentIndexChanged.connect(self.nim_typeChanged)
		if self.nim_class == "ASSET" :
			self.nim_typeChooser.setCurrentIndex(0)
		else :
			self.nim_typeChooser.setCurrentIndex(1)
		
		curRow += 1

		#Asset Name
		'''
		self.AddControlToGrid( "AssetNameLabel", "LabelControl", "Asset", curRow, 0, "The asset for the current task.", expand=False )
		self.AssetNameBox = self.AddControlToGrid( "AssetNameBox", "ReadOnlyTextControl", "", curRow, 1, colSpan=2 )
		self.AssetNameBox.setText( self.nim_assetName )
		curRow += 1
		'''

		#Asset Name
		self.AddControlToGrid( "nim_assetLabel", "LabelControl", "Asset", curRow, 0, "The asset for the current task.", expand=False )
		self.nim_assetChooser = self.AddControlToGrid( "nim_assetChooser", "ComboControl", "", curRow, 1, colSpan=2 )
		curRow += 1


		'''
		#Show Name
		self.AddControlToGrid( "ShowNameLabel", "LabelControl", "Show", curRow, 0, "The asset for the current task.", expand=False )
		self.ShowNameBox = self.AddControlToGrid( "ShowNameBox", "ReadOnlyTextControl", "", curRow, 1, colSpan=2 )
		self.ShowNameBox.setText( self.nim_showName )
		curRow += 1
		'''

		#Show Name
		self.AddControlToGrid( "nim_showLabel", "LabelControl", "Show", curRow, 0, "The show for the current task.", expand=False )
		self.nim_showChooser = self.AddControlToGrid( "nim_showChooser", "ComboControl", "", curRow, 1, colSpan=2 )
		curRow += 1

		'''
		#Shot Name
		self.AddControlToGrid( "ShotNameLabel", "LabelControl", "Shot", curRow, 0, "The asset for the current task.", expand=False )
		self.ShotNameBox = self.AddControlToGrid( "ShotNameBox", "ReadOnlyTextControl", "", curRow, 1, colSpan=2 )
		self.ShotNameBox.setText( self.nim_shotName )
		curRow += 1
		'''

		#Show Name
		self.AddControlToGrid( "nim_shotLabel", "LabelControl", "Shot", curRow, 0, "The shot for the current task.", expand=False )
		self.nim_shotChooser = self.AddControlToGrid( "nim_shotChooser", "ComboControl", "", curRow, 1, colSpan=2 )
		curRow += 1

		self.AddControlToGrid( "TaskLabel", "LabelControl", "Task", curRow, 0, "Select a task that is assigned to the current user.", expand=False )
		self.nim_taskChooser = self.AddComboControlToGrid( "TaskBox", "ComboControl", "", (), curRow, 1, colSpan=2 )
		curRow += 1
		
		self.AddControlToGrid( "RenderLabel", "LabelControl", "Render Name", curRow, 0, "The name to give the new Render.", expand=False )
		self.AddControlToGrid( "RenderBox", "TextControl", "", curRow, 1, colSpan=2 )
		curRow += 1

		self.AddControlToGrid( "DescriptionLabel", "LabelControl", "Description", curRow, 0, "A comment describing the render.", expand=False )
		self.AddControlToGrid( "DescriptionBox", "TextControl", "", curRow, 1, colSpan=2 )
		curRow += 1
		self.EndGrid()

		self.AddGrid()
		curRow = 0
		self.AddControlToGrid( "LogLabel", "LabelControl", "NIM Log:", curRow, 0, expand=False )
		curRow += 1

		self.logBox = self.AddComboControlToGrid( "LogBox", "ListControl", "", (""), curRow, 0, colSpan=5 )
		self.logBox.setSelectionMode( QAbstractItemView.ExtendedSelection )
		curRow += 1

		self.EndGrid()

		self.AddGrid()
		curRow = 0
		self.AddRangeControlToGrid( "ProgressBar", "ProgressBarControl", 0, 0, 100, 0, 0, curRow, 0, expand=False )
		self.statusLabel = self.AddControlToGrid( "StatusLabel", "LabelControl", "", curRow, 1 )
		self.statusLabel.setMinimumWidth( 100 )
		self.okButton = self.AddControlToGrid( "OkButton", "ButtonControl", "OK", curRow, 2, expand=False )
		self.okButton.ValueModified.connect( self.accept )
		self.cancelButton = self.AddControlToGrid( "CancelButton", "ButtonControl", "Cancel", curRow, 3, colSpan=2, expand=False )
		self.cancelButton.ValueModified.connect( self.reject )
		curRow += 1
		self.EndGrid()

		self.nim_userChooser.currentIndexChanged.connect(self.nim_userChanged)
		self.nim_userChanged() #trigger user changed to load choosers

		self.nim_jobChooser.currentIndexChanged.connect(self.nim_jobChanged)
		self.nim_jobChanged() #trigger job changed to load choosers

		self.nim_typeChanged()
		
		self.nim_assetChooser.currentIndexChanged.connect(self.nim_assetChanged)
		self.nim_assetChanged() #trigger asset changed to load choosers

		self.nim_showChooser.currentIndexChanged.connect(self.nim_showChanged)
		self.nim_showChanged() #trigger show changed to load choosers

		self.nim_shotChooser.currentIndexChanged.connect(self.nim_shotChanged)
		self.nim_shotChanged() #trigger show changed to load choosers

		self.nim_taskChooser.currentIndexChanged.connect(self.nim_taskChanged)
		#self.nim_taskChanged() #trigger task changed to load choosers

		self.updateEnabledStatus()

		if self.nim_userID : self.writeToLogBox( "nim_userID: %s" % self.nim_userID )
		if self.nim_user : self.writeToLogBox( "nim_user: %s" % self.nim_user )
		if self.nim_serverID : self.writeToLogBox( "nim_serverID: %s" % self.nim_serverID )
		if self.nim_jobID : self.writeToLogBox( "nim_jobID: %s" % self.nim_jobID )
		if self.nim_showID : self.writeToLogBox( "nim_showID: %s" % self.nim_showID )
		if self.nim_shotID : self.writeToLogBox( "nim_shotID: %s" % self.nim_shotID )
		if self.nim_fileID : self.writeToLogBox( "nim_fileID: %s" % self.nim_fileID )
		if self.nim_typeID : self.writeToLogBox( "nim_typeID: %s" % self.nim_typeID )
		if self.nim_assetID : self.writeToLogBox( "nim_assetID: %s" % self.nim_assetID )

		if self.nim_basename : self.writeToLogBox( "nim_basename: %s" % self.nim_basename )
		if self.nim_jobName : self.writeToLogBox( "nim_jobName: %s" % self.nim_jobName )
		if self.nim_class : self.writeToLogBox( "nim_class: %s" % self.nim_class )
		if self.nim_showName : self.writeToLogBox( "nim_showName: %s" % self.nim_showName )
		if self.nim_shotName : self.writeToLogBox( "nim_shotName: %s" % self.nim_shotName )
		if self.nim_assetName : self.writeToLogBox( "nim_assetName: %s" % self.nim_assetName )
		if self.nim_taskID : self.writeToLogBox( "nim_taskID: %s" % self.nim_taskID )
		if self.nim_itemID : self.writeToLogBox( "nim_itemID: %s" % self.nim_itemID )
		
		self.writeToLogBox( "NIM Tasks Found: %s" % len(self.nim_tasks))
		self.writeToLogBox( "parentAppName: %s" % parentAppName )


	########################################################################
	## Utility Functions
	########################################################################
	#Updates which controls are enabled based on the UI's current state
	def updateEnabledStatus( self ):

		job = self.nim_jobChooser.currentText()
		#taskEmpty = False if self.GetValue( "TaskBox" ) else True

		if self.nim_class == "ASSET":
			self.SetEnabled( "nim_assetLabel", 1)
			self.SetEnabled( "nim_assetChooser", 1)
			self.SetEnabled( "nim_showLabel", 0)
			self.SetEnabled( "nim_showChooser", 0)
			self.SetEnabled( "nim_shotLabel", 0)
			self.SetEnabled( "nim_shotChooser", 0)
		else:
			self.SetEnabled( "nim_assetLabel", 0)
			self.SetEnabled( "nim_assetChooser", 0)
			self.SetEnabled( "nim_showLabel", 1)
			self.SetEnabled( "nim_showChooser", 1)
			self.SetEnabled( "nim_shotLabel", 1)
			self.SetEnabled( "nim_shotChooser", 1)

		self.SetEnabled( "OkButton", True )
		self.SetEnabled( "CancelButton", True)


	def writeToLogBox( self, logMessage, suppressNewLine=False ):
		try:
			#Make sure it's a python string! (and not a filthy QString)
			logMessage = unicode( logMessage )
			lines = logMessage.splitlines()

			if not self.logMessages:
				self.logMessages = [""]
			
			for i in range( 0, len(lines) ):
				line = lines[ i ]
				self.logMessages[ -1 ] += line

				#check if we should add a new line or not
				if not suppressNewLine or i < (len( lines ) - 1):
					self.logMessages.append( "" )

			self.SetItems( "LogBox", tuple( self.logMessages ) )
		except:
			#log box might not be initialized yet, just suppress the exception and write to trace
			ClientUtils.LogText( traceback.format_exc() )



	########################################################################
	## UI Event Handlers
	########################################################################
	def loginNameChanged( self, *args ):
		self.updateEnabledStatus()

	def nim_userChanged(self):
		'''Action when user is selected'''
		self.nim_user = self.nim_userChooser.currentText()
		if self.nim_user:
			self.nim_userID = self.nim_usersDict[self.nim_user]
			self.nim_updateJob()
			#print "NIM: user=%s" % self.nim_user
			#print "NIM: userID=%s" % self.nim_userID
			#print "done updating jobs"


	def nim_updateJob(self):
		self.nim_jobs = []
		self.nim_jobsDict = {}
		
		self.nim_jobs = nimAPI.get_jobs(self.nim_userID)

		jobIndex = 0
		jobIter = 0
		self.nim_jobChooser.clear()
		try:
			if len(self.nim_jobs)>0:
				for key, value in sorted(self.nim_jobs.items(), reverse=True):
					#print "key: %s" % key
					self.nim_jobChooser.addItem(key)
					#print "jobID: %s - value: %s" % (self.nim_jobID, value)
					if self.nim_jobID == value:
						#print "Found matching jobID, job=", key
						self.pref_job = key
						jobIndex = jobIter
					jobIter += 1

				if self.pref_job != '':
					self.nim_jobChooser.setCurrentIndex(jobIndex)
			else:
				#print "No Jobs Found"
				self.nim_assetChooser.clear()
				self.nim_showChooser.clear()
				self.nim_shotChooser.clear()
				self.nim_taskChooser.clear()
		except:
			print "Failed to Update Jobs"
			print ( traceback.format_exc() )
			self.nim_assetChooser.clear()
			self.nim_showChooser.clear()
			self.nim_shotChooser.clear()
			self.nim_taskChooser.clear()
			pass
			


	def nim_jobChanged(self):
		'''Action when job is selected'''
		#print "JOB CHANGED"
		job = self.nim_jobChooser.currentText()
		try:
			if job:
				self.pref_job = job
				self.nim_jobName = job
				self.nim_jobID = self.nim_jobs[job]
				
				#print "Job Changed: %s" % self.nim_jobID
				self.nim_updateAsset()
				self.nim_updateShow()
			else:
				#print "No Jobs Found"
				pass
		except:
			print "Failed to Read Current Job"
			print ( traceback.format_exc() )


	def nim_typeChanged(self):
		nimType = self.nim_typeChooser.currentText()

		if nimType == "Asset":
			self.nim_class = "ASSET"
			self.SetEnabled( "nim_assetLabel", 1)
			self.SetEnabled( "nim_assetChooser", 1)
			self.SetEnabled( "nim_showLabel", 0)
			self.SetEnabled( "nim_showChooser", 0)
			self.SetEnabled( "nim_shotLabel", 0)
			self.SetEnabled( "nim_shotChooser", 0)
		else:
			self.nim_class = "SHOT"
			self.SetEnabled( "nim_assetLabel", 0)
			self.SetEnabled( "nim_assetChooser", 0)
			self.SetEnabled( "nim_showLabel", 1)
			self.SetEnabled( "nim_showChooser", 1)
			self.SetEnabled( "nim_shotLabel", 1)
			self.SetEnabled( "nim_shotChooser", 1)


	def nim_updateAsset(self):
		self.nim_assets = []
		self.nim_assetsDict = {}
		
		self.nim_assets = nimAPI.get_assets(self.nim_jobID)

		assetIndex = 0
		assetIter = 0
		self.nim_assetChooser.clear()
		try:
			if len(self.nim_assets)>0:
				for asset in self.nim_assets:
					self.nim_assetsDict[asset['name']] = asset['ID']
				for key, value in sorted(self.nim_assetsDict.items(), reverse=False):
					#print "key: %s" % key
					self.nim_assetChooser.addItem(key)
					#print "assetID: %s - value: %s" % (self.nim_assetID, value)
					if self.nim_assetID == value:
						#print "Found matching assetID, asset=", key
						self.pref_asset = key
						assetIndex = assetIter
					assetIter += 1

				if self.pref_asset != '':
					self.nim_assetChooser.setCurrentIndex(assetIndex)
			else:
				#print "No Assets Found"
				self.nim_taskChooser.clear()
		except:
			print "Failed to Update Assets"
			print ( traceback.format_exc() )
			self.nim_taskChooser.clear()
			pass

	def nim_assetChanged(self):
		'''Action when asset is selected'''
		self.nim_assetName = self.nim_assetChooser.currentText()
		if self.nim_assetName:
			#print "NIM: asset=%s" % self.nim_assetName
			self.nim_assetID = self.nim_assetsDict[self.nim_assetName]
			self.nim_itemID = nim_assetID
			self.pref_asset = self.nim_assetName

			if self.nim_class == "ASSET":
				self.nim_updateTask()


	def nim_updateShow(self):
		self.nim_shows = []
		self.nim_showsDict = {}
		
		self.nim_shows = nimAPI.get_shows(self.nim_jobID)

		showIndex = 0
		showIter = 0
		self.nim_showChooser.clear()
		try:
			if len(self.nim_shows)>0:
				for show in self.nim_shows:
					self.nim_showsDict[show['showname']] = show['ID']
				for key, value in sorted(self.nim_showsDict.items(), reverse=False):
					#print "key: %s" % key
					self.nim_showChooser.addItem(key)
					#print "showID: %s - value: %s" % (self.nim_showID, value)
					if self.nim_showID == value:
						#print "Found matching showID, show=", key
						self.pref_show = key
						showIndex = showIter
					showIter += 1

				if self.pref_show != '':
					self.nim_showChooser.setCurrentIndex(showIndex)
			else:
				#print "No Shows Found"
				self.nim_shotChooser.clear()
				self.nim_taskChooser.clear()
		except:
			print "Failed to Update Shows"
			print ( traceback.format_exc() )
			self.nim_shotChooser.clear()
			self.nim_taskChooser.clear()
			pass

	def nim_showChanged(self):
		'''Action when show is selected'''
		self.nim_showName = self.nim_showChooser.currentText()
		if self.nim_showName:
			#print "NIM: show=%s" % self.nim_showName
			self.nim_showID = self.nim_showsDict[self.nim_showName]
			self.pref_show = self.nim_showName
			self.nim_updateShot()


	def nim_updateShot(self):
		self.nim_shots = []
		self.nim_shotsDict = {}
		
		self.nim_shots = nimAPI.get_shots(self.nim_showID)

		shotIndex = 0
		shotIter = 0
		self.nim_shotChooser.clear()
		try:
			if len(self.nim_shots)>0:
				for shot in self.nim_shots:
					self.nim_shotsDict[shot['name']] = shot['ID']
				for key, value in sorted(self.nim_shotsDict.items(), reverse=False):
					#print "key: %s" % key
					self.nim_shotChooser.addItem(key)
					#print "shotID: %s - value: %s" % (self.nim_shotID, value)
					if self.nim_shotID == value:
						#print "Found matching shotID, shot=", key
						self.pref_shot = key
						shotIndex = shotIter
					shotIter += 1

				if self.pref_shot != '':
					self.nim_shotChooser.setCurrentIndex(shotIndex)
			else:
				#print "No Shots Found"
				self.nim_taskChooser.clear()
		except:
			print "Failed to Update Shots"
			print ( traceback.format_exc() )
			pass

	def nim_shotChanged(self):
		'''Action when shot is selected'''
		self.nim_shotName = self.nim_shotChooser.currentText()
		if self.nim_shotName:
			#print "NIM: shot=%s" % self.nim_shotName
			self.nim_shotID = self.nim_shotsDict[self.nim_shotName]
			self.nim_itemID = self.nim_shotID
			self.pref_shot = self.nim_shotName
			
			if self.nim_class == "SHOT":
				self.nim_updateTask()


	def nim_updateTask(self):
		self.nim_tasks = []
		self.nim_tasksDict = {}
		
		self.nim_tasks = nimAPI.get_taskInfo(self.nim_class, self.nim_itemID)

		pref_task = 0
		taskIndex = 0
		taskIter = 0
		self.nim_taskChooser.clear()
		try:
			if len(self.nim_tasks)>0:
				self.nim_tasksDict['Select...'] = 0
				for task in self.nim_tasks:
					taskID = task['taskID'] if task['taskID'] else 0
					taskName = task['taskName'] if task['taskName'] else ''
					taskDesc = task['taskDesc'] if task['taskDesc'] else ''
					taskUser = task['username'] if task['username'] else ''
					task_key = taskID+": "+taskName+" - "+taskUser
					self.nim_tasksDict[task_key] = taskID
				
				self.nim_taskChooser.addItem("Select...")
				for key, value in self.nim_tasksDict.items():
					#print "key: %s" % key
					if key is not "Select...":
						self.nim_taskChooser.addItem(key)
					#print "taskID: %s - value: %s" % (self.nim_taskID, value)
					#Set to passed taskID
					if self.nim_taskID == value:
						#print "Found matching taskID, task=", key
						pref_task = key
						taskIndex = taskIter
					taskIter += 1
					
					
				if pref_task != '':
					self.nim_taskChooser.setCurrentIndex(taskIndex)
				
			else:
				#print "No Tasks Found"
				pass
		except:
			print "Failed to Update Tasks"
			print ( traceback.format_exc() )
			pass


	def nim_taskChanged( self, *args ):
		taskKey = self.nim_taskChooser.currentText()
		self.nim_taskID = self.nim_tasksDict[taskKey]



	def selectedJobChanged( self, *args ):
		selectedJobID = self.GetValue( "nim_jobChooser" )



	def reject( self ):
		#invoke parent function to handle closing properly
		super( NimDialog, self ).reject()

	def accept( self ):
		'''Accept'''
		ClientUtils.LogText( "nim_renderName=%s" % self.GetValue("RenderBox"))
		ClientUtils.LogText( "nim_description=%s" % self.GetValue("DescriptionBox"))
		ClientUtils.LogText( "nim_jobName=%s" % self.nim_jobName )
		
		if self.nim_class == "ASSET":
			ClientUtils.LogText( "nim_assetName=%s" % self.nim_assetName )
		else:
			ClientUtils.LogText( "nim_showName=%s" % self.nim_showName )
			ClientUtils.LogText( "nim_shotName=%s" % self.nim_shotName )
		
		ClientUtils.LogText( "nim_jobID=%s" % self.nim_jobID )
		ClientUtils.LogText( "nim_class=%s" % self.nim_class )
		ClientUtils.LogText( "nim_fileID=%s" % self.nim_fileID )

		ClientUtils.LogText( "nim_taskID=%s" % self.nim_taskID )
		
		#invoke parent function to handle closing properly
		super( NimDialog, self ).accept()


