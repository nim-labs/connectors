##########################################################################################
## NIM
'''
	DeadlineGlobals.py
	Andrew Sinagra
	04.02.13
	
        #import DeadlineGlobals
	#SubmitToDeadline(nuke.root().name())

	04.02.13    		Updated to Include NIM Submission
        06.26.13    v6.0.0	Updated to Deadline 6
        06.29.13    v6.0.1	Fixed issue when submitting NON-NIM shot
        02.10.14    v6.1.4	Updated to Deadline 6.1
        02.12.14    v6.1.5	Updated to NIM 5.0
				URL is now read from ~/.nim/prefs.nim
        06.04.14    v6.1.6	Changed URL pref variable to match connector NIM_URL
        06.05.14    v6.2.0      Updated to Deadline 6.2
        09.08.14    v6.2.1      Added sRGB encoding option for Draft
        11.24.14    v6.2.2	Upated user lookup to read global first then fallback to OS ENV
                    
'''
##########################################################################################

import os, sys, re, traceback, subprocess
import ast
import threading
import time

##########################################################################################
# NIM
##########################################################################################

import urllib, urllib2
import json
import array
import string, re
import datetime
import os.path
from os.path import expanduser

##########################################################################################
# END NIM
##########################################################################################

try:
    import ConfigParser
except:
    print( "Could not load ConfigParser module, sticky settings will not be loaded/saved" )

import nuke, nukescripts

dialog = None
#deadlineCommand = None
nukeScriptPath = None
deadlineHome = None

shotgunKVPs = None

class DeadlineDialog( nukescripts.PythonPanel ):
    pools = []
    groups = []
    
    def __init__( self, maximumPriority, pools, secondaryPools, groups ):
        nukescripts.PythonPanel.__init__( self, "Submit To Deadline", "com.thinkboxsoftware.software.deadlinedialog" )
        
        self.setMinimumSize( 600, 705 )
        
        self.jobTab = nuke.Tab_Knob( "jobOptionsTab", "Job Options" )
        self.addKnob( self.jobTab )
        
        ##########################################################################################
        ## Job Description
        ##########################################################################################
        
        # Job Name
        self.jobName = nuke.String_Knob( "jobName", "Job Name" )
        self.addKnob( self.jobName )
        self.jobName.setTooltip( "The name of your job. This is optional, and if left blank, it will default to 'Untitled'." )
        self.jobName.setValue( "Untitled" )
        
        # Comment
        self.comment = nuke.String_Knob( "comment", "Comment" )
        self.addKnob( self.comment )
        self.comment.setTooltip( "A simple description of your job. This is optional and can be left blank." )
        self.comment.setValue( "" )
        
        # Department
        self.department = nuke.String_Knob( "department", "Department" )
        self.addKnob( self.department )
        self.department.setTooltip( "The department you belong to. This is optional and can be left blank." )
        self.department.setValue( "" )
        
        # Separator
        self.separator1 = nuke.Text_Knob( "separator1", "" )
        self.addKnob( self.separator1 )
        
        ##########################################################################################
        ## Job Scheduling
        ##########################################################################################
        
        # Pool
        self.pool = nuke.Enumeration_Knob( "pool", "Pool", pools )
        self.addKnob( self.pool )
        self.pool.setTooltip( "The pool that your job will be submitted to." )
        self.pool.setValue( "none" )
        
        # Secondary Pool
        self.secondaryPool = nuke.Enumeration_Knob( "secondaryPool", "Secondary Pool", secondaryPools )
        self.addKnob( self.secondaryPool )
        self.secondaryPool.setTooltip( "The secondary pool lets you specify a Pool to use if the primary Pool does not have any available Slaves." )
        self.secondaryPool.setValue( " " )
        
        # Group
        self.group = nuke.Enumeration_Knob( "group", "Group", groups )
        self.addKnob( self.group )
        self.group.setTooltip( "The group that your job will be submitted to." )
        self.group.setValue( "none" )
        
        # Priority
        self.priority = nuke.Int_Knob( "priority", "Priority" )
        self.addKnob( self.priority )
        self.priority.setTooltip( "A job can have a numeric priority ranging from 0 to " + str(maximumPriority) + ", where 0 is the lowest priority." )
        self.priority.setValue( 50 )
        
        # Task Timeout
        self.taskTimeout = nuke.Int_Knob( "taskTimeout", "Task Timeout" )
        self.addKnob( self.taskTimeout )
        self.taskTimeout.setTooltip( "The number of minutes a slave has to render a task for this job before it requeues it. Specify 0 for no limit." )
        self.taskTimeout.setValue( 0 )
        
        # Auto Task Timeout
        self.autoTaskTimeout = nuke.Boolean_Knob( "autoTaskTimeout", "Enable Auto Task Timeout" )
        self.addKnob( self.autoTaskTimeout )
        self.autoTaskTimeout.setTooltip( "If the Auto Task Timeout is properly configured in the Repository Options, then enabling this will allow a task timeout to be automatically calculated based on the render times of previous frames for the job." )
        self.autoTaskTimeout.setValue( False )
        
        # Concurrent Tasks
        self.concurrentTasks = nuke.Int_Knob( "concurrentTasks", "Concurrent Tasks" )
        self.addKnob( self.concurrentTasks )
        self.concurrentTasks.setTooltip( "The number of tasks that can render concurrently on a single slave. This is useful if the rendering application only uses one thread to render and your slaves have multiple CPUs." )
        self.concurrentTasks.setValue( 1 )
        
        # Limit Concurrent Tasks
        self.limitConcurrentTasks = nuke.Boolean_Knob( "limitConcurrentTasks", "Limit Tasks To Slave's Task Limit" )
        self.addKnob( self.limitConcurrentTasks )
        self.limitConcurrentTasks.setTooltip( "If you limit the tasks to a slave's task limit, then by default, the slave won't dequeue more tasks then it has CPUs. This task limit can be overridden for individual slaves by an administrator." )
        self.limitConcurrentTasks.setValue( False )
        
        # Machine Limit
        self.machineLimit = nuke.Int_Knob( "machineLimit", "Machine Limit" )
        self.addKnob( self.machineLimit )
        self.machineLimit.setTooltip( "Use the Machine Limit to specify the maximum number of machines that can render your job at one time. Specify 0 for no limit." )
        self.machineLimit.setValue( 0 )
        
        # Machine List Is Blacklist
        self.isBlacklist = nuke.Boolean_Knob( "isBlacklist", "Machine List Is A Blacklist" )
        self.addKnob( self.isBlacklist )
        self.isBlacklist.setTooltip( "You can force the job to render on specific machines by using a whitelist, or you can avoid specific machines by using a blacklist." )
        self.isBlacklist.setValue( False )
        
        # Machine List
        self.machineList = nuke.String_Knob( "machineList", "Machine List" )
        self.addKnob( self.machineList )
        self.machineList.setTooltip( "The whitelisted or blacklisted list of machines." )
        self.machineList.setValue( "" )
        
        self.machineListButton = nuke.PyScript_Knob( "machineListButton", "Browse" )
        self.addKnob( self.machineListButton )
        
        # Limit Groups
        self.limitGroups = nuke.String_Knob( "limitGroups", "Limits" )
        self.addKnob( self.limitGroups )
        self.limitGroups.setTooltip( "The Limits that your job requires." )
        self.limitGroups.setValue( "" )
        
        self.limitGroupsButton = nuke.PyScript_Knob( "limitGroupsButton", "Browse" )
        self.addKnob( self.limitGroupsButton )
        
        # Dependencies
        self.dependencies = nuke.String_Knob( "dependencies", "Dependencies" )
        self.addKnob( self.dependencies )
        self.dependencies.setTooltip( "Specify existing jobs that this job will be dependent on. This job will not start until the specified dependencies finish rendering." )
        self.dependencies.setValue( "" )
        
        self.dependenciesButton = nuke.PyScript_Knob( "dependenciesButton", "Browse" )
        self.addKnob( self.dependenciesButton )
        
        # On Complete
        self.onComplete = nuke.Enumeration_Knob( "onComplete", "On Job Complete", ("Nothing", "Archive", "Delete") )
        self.addKnob( self.onComplete )
        self.onComplete.setTooltip( "If desired, you can automatically archive or delete the job when it completes." )
        self.onComplete.setValue( "Nothing" )
        
        # Submit Suspended
        self.submitSuspended = nuke.Boolean_Knob( "submitSuspended", "Submit Job As Suspended" )
        self.addKnob( self.submitSuspended )
        self.submitSuspended.setTooltip( "If enabled, the job will submit in the suspended state. This is useful if you don't want the job to start rendering right away. Just resume it from the Monitor when you want it to render." )
        self.submitSuspended.setValue( False )
        
        # Separator
        self.separator1 = nuke.Text_Knob( "separator1", "" )
        self.addKnob( self.separator1 )
        
        ##########################################################################################
        ## Nuke Options
        ##########################################################################################
        
        # Frame List
        self.frameListMode = nuke.Enumeration_Knob( "frameListMode", "Frame List", ("Global", "Input", "Custom") )
        self.addKnob( self.frameListMode )
        self.frameListMode.setTooltip( "Select the Global, Input, or Custom frame list mode." )
        self.frameListMode.setValue( "Global" )
        
        self.frameList = nuke.String_Knob( "frameList", "" )
        self.frameList.clearFlag(nuke.STARTLINE)
        self.addKnob( self.frameList )
        self.frameList.setTooltip( "If Custom frame list mode is selected, this is the list of frames to render." )
        self.frameList.setValue( "" )
        
        # Chunk Size
        self.chunkSize = nuke.Int_Knob( "chunkSize", "Frames Per Task" )
        self.addKnob( self.chunkSize )
        self.chunkSize.setTooltip( "This is the number of frames that will be rendered at a time for each job task." )
        self.chunkSize.setValue( 10 )
        
        # NukeX
        self.useNukeX = nuke.Boolean_Knob( "useNukeX", "Render With NukeX" )
        self.addKnob( self.useNukeX )
        self.useNukeX.setTooltip( "If checked, NukeX will be used instead of just Nuke." )
        self.useNukeX.setValue( False )
        
        # Batch Mode
        self.batchMode = nuke.Boolean_Knob( "batchMode", "Use Batch Mode" )
        self.addKnob( self.batchMode )
        self.batchMode.setTooltip( "This uses the Nuke plugin's Batch Mode. It keeps the Nuke script loaded in memory between frames, which reduces the overhead of rendering the job." )
        self.batchMode.setValue( False )
        
        # Threads
        self.threads = nuke.Int_Knob( "threads", "Render Threads" )
        self.addKnob( self.threads )
        self.threads.setTooltip( "The number of threads to use for rendering. Set to 0 to have Nuke automatically determine the optimal thread count." )
        self.threads.setValue( 0 )
        
        # Use GPU
        self.useGpu = nuke.Boolean_Knob( "useGpu", "Use The GPU For Rendering" )
        if int(nuke.env[ 'NukeVersionMajor' ]) >= 7:
            self.addKnob( self.useGpu )
        self.useGpu.setTooltip( "If Nuke should also use the GPU for rendering." )
        self.useGpu.setValue( False )
        
        # Memory Usage
        self.memoryUsage = nuke.Int_Knob( "memoryUsage", "Maximum RAM Usage" )
        self.addKnob( self.memoryUsage )
        self.memoryUsage.setTooltip( "The maximum RAM usage (in MB) to be used for rendering. Set to 0 to not enformace a maximum amount of RAM." )
        self.memoryUsage.setValue( 0 )
        
        # Enforce Write Node Render Order
        self.enforceRenderOrder = nuke.Boolean_Knob( "enforceRenderOrder", "Enforce Write Node Render Order" )
        self.addKnob( self.enforceRenderOrder )
        self.enforceRenderOrder.setTooltip( "Forces Nuke to obey the render order of Write nodes." )
        self.enforceRenderOrder.setValue( False )
        
        # Stack Size
        self.stackSize = nuke.Int_Knob( "stackSize", "Minimum Stack Size" )
        self.addKnob( self.stackSize )
        self.stackSize.setTooltip( "The minimum stack size (in MB) to be used for rendering. Set to 0 to not enformace a minimum stack size." )
        self.stackSize.setValue( 0 )
        
        # Continue On Error
        self.continueOnError = nuke.Boolean_Knob( "continueOnError", "Continue On Error" )
        self.addKnob( self.continueOnError )
        self.continueOnError.setTooltip( "Enable to allow Nuke to continue rendering if it encounters an error." )
        self.continueOnError.setValue( False )
        
        # Build
        self.build = nuke.Enumeration_Knob( "build", "Build To Force", ("None", "32bit", "64bit") )
        self.addKnob( self.build )
        self.build.setTooltip( "You can force 32 or 64 bit rendering with this option." )
        self.build.setValue( "None" )
        
        # Submit Scene
        self.submitScene = nuke.Boolean_Knob( "submitScene", "Submit Nuke Script File With Job" )
        self.addKnob( self.submitScene )
        self.submitScene.setTooltip( "If this option is enabled, the Nuke script file will be submitted with the job, and then copied locally to the slave machine during rendering." )
        self.submitScene.setValue( False )
        
        # Views
        self.chooseViewsToRender = nuke.Boolean_Knob( "chooseViewsToRender", "Choose Views To Render" )
        self.chooseViewsToRender.setFlag(0x1000)
        self.addKnob( self.chooseViewsToRender)
        self.chooseViewsToRender.setTooltip( "Choose the view(s) you wish to render. This is optional." )
      
        currentViews = nuke.views()
        self.viewToRenderKnobs = []
        for x, v in enumerate(currentViews):
            currKnob = nuke.Boolean_Knob(('viewToRender_%d' % x), v)
            currKnob.setFlag(0x1000)
            self.viewToRenderKnobs.append((currKnob, v))
            self.addKnob(currKnob)
            currKnob.setValue(True)
            currKnob.setVisible(False) # Hide for now until the checkbox above is enabled.
        
        # Separator
        self.separator1 = nuke.Text_Knob( "separator1", "" )
        self.addKnob( self.separator1 )
        
        # Separate Jobs
        self.separateJobs = nuke.Boolean_Knob( "separateJobs", "Submit Write Nodes As Separate Jobs" )
        self.addKnob( self.separateJobs )
        self.separateJobs.setTooltip( "Enable to submit each write node to Deadline as a separate job." )
        self.separateJobs.setValue( False )
        
        # Use Node's Frame List
        self.useNodeRange = nuke.Boolean_Knob( "useNodeRange", "Use Node's Frame List" )
        self.addKnob( self.useNodeRange )
        self.useNodeRange.setTooltip( "If submitting each write node as a separate job, enable this to pull the frame range from the write node, instead of using the global frame range." )
        self.useNodeRange.setValue( True )
        
        #Separate Job Dependencies
        self.separateJobDependencies = nuke.Boolean_Knob( "separateJobDependencies", "Set Dependencies Based on Write Node Render Order" )
        self.separateJobDependencies.setFlag(nuke.STARTLINE)
        self.addKnob( self.separateJobDependencies )
        self.separateJobDependencies.setTooltip( "Enable each separate job to be dependent on the previous job." )
        self.separateJobDependencies.setValue( False )
        
        # Separate Tasks
        self.separateTasks = nuke.Boolean_Knob( "separateTasks", "Submit Write Nodes As Separate Tasks For The Same Job" )
        self.separateTasks.setFlag(nuke.STARTLINE)
        self.addKnob( self.separateTasks )
        self.separateTasks.setTooltip( "Enable to submit a job to Deadline where each task for the job represents a different write node, and all frames for that write node are rendered by its corresponding task." )
        self.separateTasks.setValue( False )
        
        # Only Submit Selected Nodes
        self.selectedOnly = nuke.Boolean_Knob( "selectedOnly", "Selected Nodes Only" )
        self.selectedOnly.setFlag(nuke.STARTLINE)
        self.addKnob( self.selectedOnly )
        self.selectedOnly.setTooltip( "If enabled, only the selected Write nodes will be rendered." )
        self.selectedOnly.setValue( False )
        
        # Only Submit Read File Nodes
        self.readFileOnly = nuke.Boolean_Knob( "readFileOnly", "Nodes With 'Read File' Enabled Only" )
        self.addKnob( self.readFileOnly )
        self.readFileOnly.setTooltip( "If enabled, only the Write nodes that have the 'Read File' option enabled will be rendered." )
        self.readFileOnly.setValue( False )
        
        ##########################################################################################
        ## Shotgun Options
        ##########################################################################################
        
        self.shotgunDraftTab = nuke.Tab_Knob( "shotgunDraftTab", "Shotgun/Draft" )
        self.addKnob( self.shotgunDraftTab )
        
        self.connectToShotgunButton = nuke.PyScript_Knob( "connectToShotgunButton", "Connect to Shotgun..." )
        self.addKnob( self.connectToShotgunButton )
        self.connectToShotgunButton.setTooltip( "Opens the Shotgun connection window." )
        
        self.useShotgunInfo = nuke.Boolean_Knob( "useShotgunInfo", "Submit Shotgun Info With Job" )
        self.addKnob( self.useShotgunInfo )
        self.useShotgunInfo.setEnabled( False )
        self.useShotgunInfo.setTooltip( "If enabled, Deadline will connect to Shotgun and create a new version for this job." )
        self.useShotgunInfo.setValue( False )
        
        self.shotgunVersion = nuke.String_Knob( "shotgunVersion", "Version Name" )
        self.addKnob( self.shotgunVersion )
        self.shotgunVersion.setEnabled( False )
        self.shotgunVersion.setTooltip( "The Shotgun version name." )
        self.shotgunVersion.setValue( "" )
        
        self.shotgunDescription = nuke.String_Knob( "shotgunDescription", "Description" )
        self.addKnob( self.shotgunDescription )
        self.shotgunDescription.setEnabled( False )
        self.shotgunDescription.setTooltip( "The Shotgun version description." )
        self.shotgunDescription.setValue( "" )
        
        self.shotgunInfo = nuke.Multiline_Eval_String_Knob( "shotgunInfo", "Selected Entity" )
        self.addKnob( self.shotgunInfo )
        self.shotgunInfo.setEnabled( False )
        self.shotgunInfo.setTooltip( "Information about the Shotgun entity that the version will be created for." )
        self.shotgunDescription.setValue( "" )
        
        ##########################################################################################
        ## Draft Options
        ##########################################################################################
        
        #~ self.draftTab = nuke.Tab_Knob( "draftTab", "Draft" )
        #~ self.addKnob( self.draftTab )
        
        self.draftSeparator1 = nuke.Text_Knob( "draftSeparator1", "" )
        self.addKnob( self.draftSeparator1 )
        
        self.submitDraftJob = nuke.Boolean_Knob( "submitDraftJob", "Submit Dependent Draft Job" )
        self.addKnob( self.submitDraftJob )
        self.submitDraftJob.setValue( False )
        
        self.uploadToShotgun = nuke.Boolean_Knob( "uploadToShotgun", "Upload to Shotgun" )
        self.addKnob( self.uploadToShotgun )
        self.uploadToShotgun.setEnabled( False )
        self.uploadToShotgun.setTooltip( "If enabled, the Draft results will be uploaded to Shotgun when it is complete." )
        self.uploadToShotgun.setValue( True )
        
        self.templatePath = nuke.File_Knob( "templatePath", "Draft Template" )
        self.addKnob( self.templatePath )
        self.templatePath.setEnabled( False )
        self.templatePath.setTooltip( "The Draft template file to use." )
        self.templatePath.setValue( "" )
        
        self.draftUser = nuke.String_Knob( "draftUser", "User" )
        self.addKnob( self.draftUser )
        self.draftUser.setEnabled( False )
        self.draftUser.setTooltip( "The user name used by the Draft template." )
        self.draftUser.setValue( "" )
        
        self.draftEntity = nuke.String_Knob( "draftEntity", "Entity" )
        self.addKnob( self.draftEntity )
        self.draftEntity.setEnabled( False )
        self.draftEntity.setTooltip( "The entity name used by the Draft template." )
        self.draftEntity.setValue( "" )
        
        self.draftVersion = nuke.String_Knob( "draftVersion", "Version" )
        self.addKnob( self.draftVersion )
        self.draftVersion.setEnabled( False )
        self.draftVersion.setTooltip( "The version name used by the Draft template." )
        self.draftVersion.setValue( "" )
        
        self.draftExtraArgs = nuke.String_Knob( "draftExtraArgs", "Additional Args" )
        self.addKnob( self.draftExtraArgs )
        self.draftExtraArgs.setEnabled( False )
        self.draftExtraArgs.setTooltip( "The additional arguments used by the Draft template." )
        self.draftExtraArgs.setValue( "" )
        
        self.useShotgunDataButton = nuke.PyScript_Knob( "useShotgunDataButton", "Use Shotgun Data" )
        self.useShotgunDataButton.setFlag(nuke.STARTLINE)
        self.addKnob( self.useShotgunDataButton )
        self.useShotgunDataButton.setEnabled( False )
        self.useShotgunDataButton.setTooltip( "Pulls the Draft settings directly from the Shotgun data above (if there is any)." )
        
        ##########################################################################################
        ## NIM Options
        ##########################################################################################
        self.taskDict = {}
        self.nim_job_id = None
        self.nim_show_id = None
        self.nim_shot_id = None
        
        # NIM TAB
        self.nimDraftTab = nuke.Tab_Knob( "nimDraftTab", "NIM/Draft" )
        self.addKnob( self.nimDraftTab )
        
        # UseNimInfo
        self.useNimInfo = nuke.Boolean_Knob( "useNimInfo", "Submit NIM Info With Job" )
        self.addKnob( self.useNimInfo )
        #if self.nim_shot_id == '':
        #	self.useNimInfo.setEnabled( False )
        self.useNimInfo.setValue( False )
        
        # Artist
        self.nimArtist = nuke.String_Knob( "nimArtist", "Artist:" )
        self.addKnob( self.nimArtist )
        self.nimArtist.setEnabled( False )
        self.nimArtist.setFlag(0x10000000) #READ ONLY
        
        # Job
        self.nimJob = nuke.String_Knob( "nimJob", "Job:" )
        self.addKnob( self.nimJob )
        #self.nimJob.setValue( self.nim_job_folder )
        self.nimJob.setEnabled( False )
        self.nimJob.setFlag(0x10000000) #READ ONLY
        
        # Asset
        #self.nimAsset = nuke.String_Knob( "nimAsset", "Asset:" )
        #self.addKnob( self.nimAsset )
        #self.nimAsset.setValue( "" )
        #self.nimAsset.setEnabled( False )
        
        # Show
        self.nimShow = nuke.String_Knob( "nimShow", "Show:" )
        self.addKnob( self.nimShow )
        #self.nimShow.setValue( self.nim_show_folder )
        self.nimShow.setEnabled( False )
        self.nimShow.setFlag(0x10000000) #READ ONLY
        
        # Shot
        self.nimShot = nuke.String_Knob( "nimShot", "Shot:" )
        self.addKnob( self.nimShot )
        #self.nimShot.setValue( self.nim_shot_folder )
        self.nimShot.setEnabled( False )
        self.nimShot.setFlag(0x10000000) #READ ONLY
        
        # Task
        self.nimTask = nuke.Enumeration_Knob( "nimTask", "Task", ("Select...", "") )
        self.addKnob( self.nimTask )
        #self.nimTask.setValue( "Select..." )
        self.nimTask.setEnabled( False )
        #self.nimTask.setValues(nim_task_list)
        #if selected != None:
        #	self.nimTask.setValue(str(selected))
        
        # Divider
        self.nimSeparator1 = nuke.Text_Knob( "nimSeparator1", "" )
        self.addKnob( self.nimSeparator1 )
        
        # Submit NimDraft
        self.submitNimDraftJob = nuke.Boolean_Knob( "submitNimDraftJob", "Submit Dependent Draft Job" )
        self.addKnob( self.submitNimDraftJob )
        self.submitNimDraftJob.setValue( False )
        
        self.nimTemplatePath = nuke.File_Knob( "nimTemplatePath", "Draft Template" )
        self.addKnob( self.nimTemplatePath )
        self.nimTemplatePath.setValue( "R:/Draft/Templates/NIM_Draft_Dailies.py" )
        self.nimTemplatePath.setEnabled( False )
        
        # Divider
        self.nimSeparator3 = nuke.Text_Knob( "nimSeparator3", "" )
        self.addKnob( self.nimSeparator3 )
        self.nimSeparator3.setVisible(False)
        
        self.nimEncodeSRGB = nuke.Boolean_Knob( "nimEncodeSRGB", "Encode sRGB" )
        self.addKnob( self.nimEncodeSRGB )
        self.nimEncodeSRGB.setValue( False )
        self.nimEncodeSRGB.setEnabled( False )
                
        self.uploadToNim = nuke.Boolean_Knob( "uploadToNim", "Upload Draft to NIM" )
        self.addKnob( self.uploadToNim )
        self.uploadToNim.setValue( True )
        self.uploadToNim.setEnabled( False )
        
        
        
        ##########################################################################################
        ## END NIM Options
        ##########################################################################################
        
        
    def knobChanged( self, knob ):
        global draftTemplateField
        global shotgunValues
        global shotgunKVPs
        
        if knob == self.machineListButton:
            GetMachineListFromDeadline()
            
        if knob == self.limitGroupsButton:
            GetLimitGroupsFromDeadline()
        
        if knob == self.dependenciesButton:
            GetDependenciesFromDeadline()
        
        if knob == self.frameList:
            self.frameListMode.setValue( "Custom" )
        
        if knob == self.frameListMode:
            # In Custom mode, don't change anything
            if self.frameListMode.value() != "Custom":
                startFrame = nuke.Root().firstFrame()
                endFrame = nuke.Root().lastFrame()
                if self.frameListMode.value() == "Input":
                    try:
                        activeInput = nuke.activeViewer().activeInput()
                        startFrame = nuke.activeViewer().node().input(activeInput).frameRange().first()
                        endFrame = nuke.activeViewer().node().input(activeInput).frameRange().last()
                    except:
                        pass
                
                if startFrame == endFrame:
                    self.frameList.setValue( str(startFrame) )
                else:
                    self.frameList.setValue( str(startFrame) + "-" + str(endFrame) )
            
        if knob == self.separateJobs or knob == self.separateTasks:
            self.separateJobs.setEnabled( not self.separateTasks.value() )
            self.separateTasks.setEnabled( not self.separateJobs.value() )
            
            self.separateJobDependencies.setEnabled( self.separateJobs.value() )
            if not self.separateJobs.value():
                self.separateJobDependencies.setValue( self.separateJobs.value() )
            
            self.useNodeRange.setEnabled( self.separateJobs.value() or self.separateTasks.value() )
            self.frameList.setEnabled( not (self.separateJobs.value() and self.useNodeRange.value()) and not self.separateTasks.value() )
            self.chunkSize.setEnabled( not self.separateTasks.value() )
        
        if knob == self.useNodeRange:
            self.frameListMode.setEnabled( not (self.separateJobs.value() and self.useNodeRange.value()) and not self.separateTasks.value() )
            self.frameList.setEnabled( not (self.separateJobs.value() and self.useNodeRange.value()) and not self.separateTasks.value() )
        
        if knob == self.chooseViewsToRender:
            visible = self.chooseViewsToRender.value()
            for vk in self.viewToRenderKnobs:
                vk[0].setVisible(visible)
        
        if knob == self.connectToShotgunButton:
            GetShotgunInfo()
        
        if knob == self.useShotgunDataButton:
            user = shotgunKVPs.get( 'UserName', "" )
            task = shotgunKVPs.get( 'TaskName', "" )
            project = shotgunKVPs.get( 'ProjectName', "" )
            entity = shotgunKVPs.get( 'EntityName', "" )
            version = shotgunKVPs.get( 'VersionName', "" )
            draftTemplate = shotgunKVPs.get( 'DraftTemplate', "" )
            
            #set any relevant values
            self.draftUser.setValue( user )
            self.draftVersion.setValue( version )
            
            if task.strip() != "":
                self.draftEntity.setValue( "%s" % task )
            elif project.strip() != "" and entity.strip() != "":
                self.draftEntity.setValue( "%s > %s" % (project, entity) )
                
            if draftTemplate.strip() != "" and draftTemplate != "None":
                self.templatePath.setValue( draftTemplate )
        
        if knob == self.shotgunVersion:
            shotgunKVPs['VersionName'] = self.shotgunVersion.value()
        
        if knob == self.shotgunDescription:
            shotgunKVPs['Description'] = self.shotgunDescription.value()
        
        if knob == self.useShotgunInfo:
            self.shotgunVersion.setEnabled( self.useShotgunInfo.value() )
            self.shotgunDescription.setEnabled( self.useShotgunInfo.value() )
            
            #draft controls that require shotgun to be used
            self.uploadToShotgun.setEnabled( self.useShotgunInfo.value() and self.submitDraftJob.value() )
            self.useShotgunDataButton.setEnabled( self.useShotgunInfo.value() and self.submitDraftJob.value() )
        
        
        if knob == self.submitDraftJob:
            self.templatePath.setEnabled( self.submitDraftJob.value() )
            self.draftUser.setEnabled( self.submitDraftJob.value() )
            self.draftEntity.setEnabled( self.submitDraftJob.value() )
            self.draftVersion.setEnabled( self.submitDraftJob.value() )
            self.draftExtraArgs.setEnabled( self.submitDraftJob.value() )
            
            #these two settings also depend on shotgun being enabled
            self.useShotgunDataButton.setEnabled( self.useShotgunInfo.value() and self.submitDraftJob.value() )
            self.uploadToShotgun.setEnabled( self.useShotgunInfo.value() and self.submitDraftJob.value() )
            
        
        ##########################################################################################
        ## NIM 
        ##########################################################################################
        
        if knob == self.useNimInfo:
            self.nimJob.setEnabled( self.useNimInfo.value() )
            self.nimShow.setEnabled( self.useNimInfo.value() )
            self.nimShot.setEnabled( self.useNimInfo.value() )
            self.nimTask.setEnabled( self.useNimInfo.value() )
            
            if self.submitNimDraftJob.value() == True:
                self.uploadToNim.setEnabled( self.useNimInfo.value() )
                #self.nimEncodeSRGB.setEnabled( self.useNimInfo.value() )
                        
        if knob == self.submitNimDraftJob:
            self.nimTemplatePath.setEnabled( self.submitNimDraftJob.value() )
            self.nimEncodeSRGB.setEnabled( self.submitNimDraftJob.value() )
            if self.useNimInfo.value() == True:
                self.uploadToNim.setEnabled( self.submitNimDraftJob.value() )
                
        ##########################################################################################
        ## END NIM 
        ##########################################################################################
        
        
    def ShowDialog( self ):
        return nukescripts.PythonPanel.showModalDialog( self )


##########################################################################################
## NIM 
##########################################################################################

def getSqlData(nim_URL, sqlCmd):
    '''Querys mySQL server and returns decoded json array'''
    actionURL = nim_URL+urllib.urlencode(sqlCmd)		#actionURL = self.nim_URL+'q=getShows&ID='+jobID
    #self.debugPrint(actionURL)
    f = urllib2.urlopen(actionURL)
    result = json.loads( f.read() )
    f.close()
    return result
	
##########################################################################################
## END NIM 
##########################################################################################


def CallDeadlineCommand( arguments, hideWindow=True ):
    # On OSX, we look for the DEADLINE_PATH file. On other platforms, we use the environment variable.
    if os.path.exists( "/Users/Shared/Thinkbox/DEADLINE_PATH" ):
        with open( "/Users/Shared/Thinkbox/DEADLINE_PATH" ) as f: deadlineBin = f.read().strip()
        deadlineCommand = deadlineBin + "/deadlinecommand"
    else:
        deadlineBin = os.environ['DEADLINE_PATH']
        if os.name == 'nt':
            deadlineCommand = deadlineBin + "\\deadlinecommand.exe"
        else:
            deadlineCommand = deadlineBin + "/deadlinecommand"
    
    startupinfo = None
    if hideWindow and os.name == 'nt' and hasattr( subprocess, 'STARTF_USESHOWWINDOW' ):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    environment = {}
    for key in os.environ.keys():
        environment[key] = os.environ[key]
        
    # Need to set the PATH, cuz windows seems to load DLLs from the PATH earlier that cwd....
    if os.name == 'nt':
        environment['PATH'] = deadlineBin + os.pathsep + os.environ['PATH']
    
    arguments.insert( 0, deadlineCommand)
    
    # Specifying PIPE for all handles to workaround a Python bug on Windows. The unused handles are then closed immediatley afterwards.
    proc = subprocess.Popen(arguments, cwd=deadlineBin, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, env=environment)
    proc.stdin.close()
    proc.stderr.close()
    
    output = proc.stdout.read()
    
    return output

def GetShotgunInfo():
    global dialog
    global nukeScriptPath
    global shotgunValues
    global shotgunJobSettings
    global shotgunKVPs
    
    tempKVPs = {}
    
    shotgunPath = nukeScriptPath.replace( "/submission/Nuke/Main", "" ) + "/events/Shotgun"
    shotgunScript = shotgunPath + "/ShotgunUI.py"
    
    output = CallDeadlineCommand( ["ExecuteScript", shotgunScript, "Nuke"], False )
    outputLines = output.splitlines()
    
    for line in outputLines:
        line = line.strip()
        
        tokens = line.split( '=', 1 )
        
        if len( tokens ) > 1:
            key = tokens[0]
            value = tokens[1]
            
            tempKVPs[key] = value
    
    if len( tempKVPs ) > 0:
        shotgunKVPs = tempKVPs
        UpdateShotgunUI( True )


def UpdateShotgunUI( forceOn=False ):
    global dialog
    global shotgunKVPs
    
    if shotgunKVPs != None:
        dialog.useShotgunInfo.setEnabled( len(shotgunKVPs) > 0 )
        
        if forceOn:
            dialog.useShotgunInfo.setValue( True )
        
        dialog.shotgunVersion.setValue( shotgunKVPs.get( 'VersionName', "" ) )
        dialog.shotgunVersion.setEnabled( dialog.useShotgunInfo.value() )
        dialog.shotgunDescription.setValue( shotgunKVPs.get( 'Description', "" ) )
        dialog.shotgunDescription.setEnabled( dialog.useShotgunInfo.value() )
        
        #update the draft stuff that relies on shotgun
        dialog.uploadToShotgun.setEnabled( dialog.submitDraftJob.value() and dialog.useShotgunInfo.value() )
        dialog.useShotgunDataButton.setEnabled( dialog.submitDraftJob.value() and dialog.useShotgunInfo.value() )
            
        displayText = ""
        if 'UserName' in shotgunKVPs:
            displayText += "User Name: %s\n" % shotgunKVPs[ 'UserName' ]
        if 'TaskName' in shotgunKVPs:
            displayText += "Task Name: %s\n" % shotgunKVPs[ 'TaskName' ]
        if 'ProjectName' in shotgunKVPs:
            displayText += "Project Name: %s\n" % shotgunKVPs[ 'ProjectName' ]
        if 'EntityName' in shotgunKVPs:
            displayText += "Entity Name: %s\n" % shotgunKVPs[ 'EntityName' ]	
        if 'EntityType' in shotgunKVPs:
            displayText += "Entity Type: %s\n" % shotgunKVPs[ 'EntityType' ]
        if 'DraftTemplate' in shotgunKVPs:
            displayText += "Draft Template: %s\n" % shotgunKVPs[ 'DraftTemplate' ]
            
        dialog.shotgunInfo.setValue( displayText )
    else:
        dialog.useShotgunInfo.setEnabled( False )
        dialog.useShotgunInfo.setValue( False )
    
    
def GetMachineListFromDeadline():
    global dialog
    output = CallDeadlineCommand( ["-selectmachinelist", dialog.machineList.value()] )
    output = output.replace( "\r", "" ).replace( "\n", "" )
    if output != "Action was cancelled by user":
        dialog.machineList.setValue( output )
    

def GetLimitGroupsFromDeadline():
    global dialog
    output = CallDeadlineCommand( ["-selectlimitgroups", dialog.limitGroups.value()] )
    output = output.replace( "\r", "" ).replace( "\n", "" )
    if output != "Action was cancelled by user":
        dialog.limitGroups.setValue( output )

def GetDependenciesFromDeadline():
    global dialog
    output = CallDeadlineCommand( ["-selectdependencies", dialog.dependencies.value()] )
    output = output.replace( "\r", "" ).replace( "\n", "" )
    if output != "Action was cancelled by user":
        dialog.dependencies.setValue( output )

# Checks a path to make sure it has an extension
def HasExtension( path ):
    filename = os.path.basename( path )
    
    return filename.rfind( "." ) > -1

# Checks if path is local (c, d, or e drive).
def IsPathLocal( path ):
    lowerPath = path.lower()
    if lowerPath.startswith( "c:" ) or lowerPath.startswith( "d:" ) or lowerPath.startswith( "e:" ):
        return True
    return False

# Checks if the given filename ends with a movie extension
def IsMovie( path ):
    lowerPath = path.lower()
    if lowerPath.endswith( ".mov" ):
        return True
    return False

# Checks if the filename is padded (ie: \\output\path\filename_%04.tga).
def IsPadded( path ):
    paddingRe = re.compile( "%([0-9]+)d", re.IGNORECASE )
    if paddingRe.search( path ) != None:
        return True
    elif path.find( "#" ) > -1:
        return True
    return False

def RightReplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def StrToBool(str):
    return str.lower() in ("yes", "true", "t", "1", "on")

# Parses through the filename looking for the last padded pattern, replaces
# it with the correct number of #'s, and returns the new padded filename.
def GetPaddedPath( path ):
    #~ paddingRe = re.compile( "%([0-9]+)d", re.IGNORECASE )
    
    #~ paddingMatch = paddingRe.search( path )
    #~ if paddingMatch != None:
        #~ paddingSize = int(paddingMatch.lastgroup)
        
        #~ padding = ""
        #~ while len(padding) < paddingSize:
            #~ padding = padding + "#"
        
        #~ path = paddingRe.sub( padding, path, 1 )
    
    paddingRe = re.compile( "([0-9]+)", re.IGNORECASE )
    
    paddingMatches = paddingRe.findall( path )
    if paddingMatches != None and len( paddingMatches ) > 0:
        paddingString = paddingMatches[ len( paddingMatches ) - 1 ]
        paddingSize = len(paddingString)
        
        padding = ""
        while len(padding) < paddingSize:
            padding = padding + "#"
        
        path = RightReplace( path, paddingString, padding, 1 )
    
    return path
    
def buildKnob(name, abr):
    try:
        root = nuke.Root()
        if name in root.knobs():
            return root.knob( name )
        else:
            tKnob = nuke.String_Knob( name, abr )
            root.addKnob ( tKnob )
            return  tKnob
    except:
        print "Error in knob creation. "+ name + " " + abr
        
def WriteStickySettings( dialog, configFile ):
    global shotgunKVPs
    
    try:
        print "Writing sticky settings..."
        config = ConfigParser.ConfigParser()
        config.add_section( "Sticky" )
        
        config.set( "Sticky", "FrameListMode", dialog.frameListMode.value() )
        config.set( "Sticky", "CustomFrameList", dialog.frameList.value().strip() )
        
        config.set( "Sticky", "Department", dialog.department.value() )
        config.set( "Sticky", "Pool", dialog.pool.value() )
        config.set( "Sticky", "SecondaryPool", dialog.secondaryPool.value() )
        config.set( "Sticky", "Group", dialog.group.value() )
        config.set( "Sticky", "Priority", str( dialog.priority.value() ) )
        config.set( "Sticky", "MachineLimit", str( dialog.machineLimit.value() ) )
        config.set( "Sticky", "IsBlacklist", str( dialog.isBlacklist.value() ) )
        config.set( "Sticky", "MachineList", dialog.machineList.value() )
        config.set( "Sticky", "LimitGroups", dialog.limitGroups.value() )
        config.set( "Sticky", "SubmitSuspended", str( dialog.submitSuspended.value() ) )
        config.set( "Sticky", "ChunkSize", str( dialog.chunkSize.value() ) )
        config.set( "Sticky", "ConcurrentTasks", str( dialog.concurrentTasks.value() ) )
        config.set( "Sticky", "LimitConcurrentTasks", str( dialog.limitConcurrentTasks.value() ) )
        config.set( "Sticky", "Threads", str( dialog.threads.value() ) )
        config.set( "Sticky", "SubmitScene", str( dialog.submitScene.value() ) )
        config.set( "Sticky", "BatchMode", str( dialog.batchMode.value() ) )
        config.set( "Sticky", "ContinueOnError", str( dialog.continueOnError.value() ) )
        config.set( "Sticky", "UseNodeRange", str( dialog.useNodeRange.value() ) )
        config.set( "Sticky", "UseGpu", str( dialog.useGpu.value() ) )
        config.set( "Sticky", "EnforceRenderOrder", str( dialog.enforceRenderOrder.value() ) )
        
        config.set( "Sticky", "UseDraft", str( dialog.submitDraftJob.value() ) )
        config.set( "Sticky", "DraftTemplate", dialog.templatePath.value() )
        config.set( "Sticky", "DraftUser", dialog.draftUser.value() )
        config.set( "Sticky", "DraftEntity", dialog.draftEntity.value() )
        config.set( "Sticky", "DraftVersion", dialog.draftVersion.value() )
        config.set( "Sticky", "DraftExtraArgs", dialog.draftExtraArgs.value() )
        
        
        ##########################################################################################
        ## NIM 
        ##########################################################################################
        
        config.set( "Sticky", "useNimInfo", dialog.useNimInfo.value() )
        config.set( "Sticky", "nimShotID", str(dialog.nim_shot_id) )
        config.set( "Sticky", "nimTaskID", str(dialog.taskDict[dialog.nimTask.value()]) )
        config.set( "Sticky", "submitNimDraftJob", dialog.submitNimDraftJob.value() )
        config.set( "Sticky", "uploadToNim", dialog.uploadToNim.value() )
        config.set( "Sticky", "nimTemplatePath", str(dialog.nimTemplatePath.value()) )
        config.set( "Sticky", "nimEncodeSRGB", dialog.nimEncodeSRGB.value() )
        
        ##########################################################################################
        ## END NIM 
        ##########################################################################################
        
        
        fileHandle = open( configFile, "w" )
        config.write( fileHandle )
        fileHandle.close()
        
        root = nuke.Root()
        sgDataKnob = None
        if "DeadlineSGData" in root.knobs():
            sgDataKnob = root.knob( "DeadlineSGData" )
        else:
            #~ sgDataKnob = nuke.String_Knob( "DeadlineSGData", "ShotgunKVPs" )
            #~ root.addKnob( sgDataKnob )
            
            # The code above places this in the default "User" tab. We want it in its own tab.
            sgTab = nuke.Tab_Knob('Deadline')
            sgDataKnob = nuke.String_Knob( "DeadlineSGData", "ShotgunKVPs" )
            root.addKnob( sgTab )
            root.addKnob( sgDataKnob )
            
        sgDataKnob.setValue( str(shotgunKVPs) )
        tKnob = None
    except:
        print( "Could not write sticky settings" )
    
    try:
        #Saves all the sticky setting to the root
        tKnob = buildKnob( "FrameListMode" , "FLM")
        tKnob.setValue( dialog.frameListMode.value() )
        
        tKnob = buildKnob( "CustomFrameList", "CFL" )
        tKnob.setValue( dialog.frameList.value().strip() )
        
        tKnob = buildKnob( "Department", "DPT" )
        tKnob.setValue( dialog.department.value() )
        
        tKnob = buildKnob( "Pool", "POOL" )
        tKnob.setValue( dialog.pool.value() )
        
        tKnob = buildKnob( "SecondarPool", "SECPOOL" )
        tKnob.setValue( dialog.secondaryPool.value() )
        
        tKnob = buildKnob( "Group", "GRP" )
        tKnob.setValue( dialog.group.value() )
        
        tKnob = buildKnob( "Priority", "PRT" )
        tKnob.setValue( str( dialog.priority.value() ) )
        
        tKnob = buildKnob( "MachineLimit", "MLM" )
        tKnob.setValue( str( dialog.machineLimit.value() ) )
        
        tKnob = buildKnob( "IsBlacklist", "IBL" )
        tKnob.setValue( str( dialog.isBlacklist.value() ) )
        
        tKnob = buildKnob( "MachineList", "MLT" )
        tKnob.setValue( dialog.machineList.value() )
        
        tKnob = buildKnob( "LimitGroups", "LGP" )
        tKnob.setValue( dialog.limitGroups.value() )
        
        tKnob = buildKnob( "SubmitSuspended", "SUS" )
        tKnob.setValue( str( dialog.submitSuspended.value() ) )
        
        tKnob = buildKnob( "ChunkSize", "CSZ" ) 
        tKnob.setValue( str( dialog.chunkSize.value() ) )
        
        tKnob = buildKnob( "ConcurrentTasks", "CCT" ) 
        tKnob.setValue( str( dialog.concurrentTasks.value() ) )
        
        tKnob = buildKnob( "LimitConcurrentTasks", "LCT" )
        tKnob.setValue( str( dialog.limitConcurrentTasks.value() ) )
        
        tKnob = buildKnob( "Threads", "TRD" )
        tKnob.setValue( str( dialog.threads.value() ) )
        
        tKnob = buildKnob( "SubmitScene", "SSC" )
        tKnob.setValue( str( dialog.submitScene.value() ) )
        
        tKnob = buildKnob( "BatchMode", "BTM" )
        tKnob.setValue( str( dialog.batchMode.value() ) )
        
        tKnob = buildKnob( "ContinueOnError", "COE" )
        tKnob.setValue( str( dialog.continueOnError.value() ) )
        
        tKnob = buildKnob( "UseNodeRange", "UNR" )
        tKnob.setValue( str( dialog.useNodeRange.value() ) )
        
        tKnob = buildKnob( "UseGpu", "GPU" )
        tKnob.setValue( str( dialog.useGpu.value() ) )
        
        tKnob = buildKnob( "EnforceRenderOrder", "ERO" )
        tKnob.setValue( str( dialog.enforceRenderOrder.value() ) )
        
        tKnob = buildKnob( "UseDraft", "UDR" )
        tKnob.setValue( str( dialog.submitDraftJob.value() ) )
        
        tKnob = buildKnob( "DraftTemplate", "DRT" )
        tKnob.setValue( dialog.templatePath.value() )
        
        tKnob = buildKnob( "DraftUser", "DUR" )
        tKnob.setValue( dialog.draftUser.value() )
        
        tKnob = buildKnob( "DraftEntity", "DEN" )
        tKnob.setValue( dialog.draftEntity.value() )
        
        tKnob = buildKnob( "DraftVersion", "DVR" )
        tKnob.setValue( dialog.draftVersion.value() )
        
        tKnob = buildKnob( "DraftExtraArgs", "DEA" )          
        tKnob.setValue( dialog.draftExtraArgs.value() )
        
        # If the Nuke script has been modified, then save it to preserve SG settings.
        if root.modified():
            nuke.scriptSave( root.name() )
        
    except:
        print( "Could not write knob settings." )

def SubmitJob( dialog, root, node, writeNodes, deadlineTemp, tempJobName, tempFrameList, tempDependencies, tempChunkSize, tempIsMovie, jobCount, semaphore ):
    global shotgunJobSettings
    global shotgunKVPs
    
    print "Preparing job #%d for submission.." % jobCount
    
    # Create a task in Nuke's progress  bar dialog
    #progressTask = nuke.ProgressTask("Submitting %s to Deadline" % tempJobName)
    progressTask = nuke.ProgressTask("Job Submission")
    progressTask.setMessage("Creating Job Info File")
    progressTask.setProgress(0)
    
    # Create the submission info file (append job count since we're submitting multiple jobs at the same time in different threads)
    jobInfoFile = deadlineTemp + ("/nuke_submit_info%d.job" % jobCount)
    fileHandle = open( jobInfoFile, "w" )
    fileHandle.write( "Plugin=Nuke\n" )
    fileHandle.write( "Name=%s\n" % tempJobName )
    fileHandle.write( "Comment=%s\n" % dialog.comment.value() )
    fileHandle.write( "Department=%s\n" % dialog.department.value() )
    fileHandle.write( "Pool=%s\n" % dialog.pool.value() )
    if dialog.secondaryPool.value() == "":
        fileHandle.write( "SecondaryPool=\n" )
    else:
        fileHandle.write( "SecondaryPool=%s\n" % dialog.secondaryPool.value() )
    fileHandle.write( "Group=%s\n" % dialog.group.value() )
    fileHandle.write( "Priority=%s\n" % dialog.priority.value() )
    fileHandle.write( "MachineLimit=%s\n" % dialog.machineLimit.value() )
    fileHandle.write( "TaskTimeoutMinutes=%s\n" % dialog.taskTimeout.value() )
    fileHandle.write( "EnableAutoTimeout=%s\n" % dialog.autoTaskTimeout.value() )
    fileHandle.write( "ConcurrentTasks=%s\n" % dialog.concurrentTasks.value() )
    fileHandle.write( "LimitConcurrentTasksToNumberOfCpus=%s\n" % dialog.limitConcurrentTasks.value() )
    fileHandle.write( "LimitGroups=%s\n" % dialog.limitGroups.value() )
    fileHandle.write( "JobDependencies=%s\n" %  tempDependencies)
    fileHandle.write( "OnJobComplete=%s\n" % dialog.onComplete.value() )
    
    if dialog.separateTasks.value():
        writeNodeCount = 0
        for tempNode in writeNodes:
            if not tempNode.knob( 'disable' ).value():
                enterLoop = True
                if dialog.readFileOnly.value() and tempNode.knob( 'reading' ):
                    enterLoop = enterLoop and tempNode.knob( 'reading' ).value()
                if dialog.selectedOnly.value():
                    enterLoop = enterLoop and tempNode.isSelected()
                
                if enterLoop:
                    writeNodeCount += 1
        
        
        fileHandle.write( "Frames=0-%s\n" % (writeNodeCount-1) )
        fileHandle.write( "ChunkSize=1\n" )
    else:
        fileHandle.write( "Frames=%s\n" % tempFrameList )
        fileHandle.write( "ChunkSize=%s\n" % tempChunkSize )
    
    if dialog.submitSuspended.value():
        fileHandle.write( "InitialStatus=Suspended\n" )
    
    if dialog.isBlacklist.value():
        fileHandle.write( "Blacklist=%s\n" % dialog.machineList.value() )
    else:
        fileHandle.write( "Whitelist=%s\n" % dialog.machineList.value() )
    
    extraKVPIndex = 0
    
    if dialog.separateJobs.value():
        if ( root.proxy() and node.knob( 'proxy' ).value() != "" ):
            fileValue = node.knob( 'proxy' ).value()
            evaluatedValue = node.knob( 'proxy' ).evaluate()
        else:
            fileValue = node.knob( 'file' ).value()
            evaluatedValue = node.knob( 'file' ).evaluate()
        
        if fileValue != None and fileValue != "" and evaluatedValue != None and evaluatedValue != "":
            tempPath, tempFilename = os.path.split( evaluatedValue )
            if IsPadded( os.path.basename( fileValue ) ):
                tempFilename = GetPaddedPath( tempFilename )
                
            paddedPath = os.path.join( tempPath, tempFilename )
            fileHandle.write( "OutputFilename0=%s\n" % paddedPath )
            
            #Check if the Write Node will be modifying the output's Frame numbers
            if node.knob( 'frame_mode' ):
                if ( node.knob( 'frame_mode' ).value() == "offset" ):
                    fileHandle.write( "ExtraInfoKeyValue%d=OutputFrameOffset0=%s\n" % (extraKVPIndex, str( int(node.knob( 'frame' ).value()) )) )
                    extraKVPIndex += 1
                elif ( node.knob( 'frame_mode' ).value() == "start at" or node.knob( 'frame_mode' ).value() == "start_at"):
                    franges = nuke.FrameRanges( tempFrameList )
                    fileHandle.write( "ExtraInfoKeyValue%d=OutputFrameOffset0=%s\n" % (extraKVPIndex, str( int(node.knob( 'frame' ).value()) - franges.minFrame() )) )
                    extraKVPIndex += 1
                else:
                    #TODO: Handle 'expression'? Would be much harder
                    pass
    else:
        index = 0
        for tempNode in writeNodes:
            if not tempNode.knob( 'disable' ).value():
                enterLoop = True
                if dialog.readFileOnly.value() and tempNode.knob( 'reading' ):
                    enterLoop = enterLoop and tempNode.knob( 'reading' ).value()
                if dialog.selectedOnly.value():
                    enterLoop = enterLoop and tempNode.isSelected()
                
                if enterLoop:
                    if ( root.proxy() and tempNode.knob( 'proxy' ).value() != "" ):
                        fileValue = tempNode.knob( 'proxy' ).value()
                        evaluatedValue = tempNode.knob( 'proxy' ).evaluate()
                    else:
                        fileValue = tempNode.knob( 'file' ).value()
                        evaluatedValue = tempNode.knob( 'file' ).evaluate()
                    
                    if fileValue != None and fileValue != "" and evaluatedValue != None and evaluatedValue != "":
                        tempPath, tempFilename = os.path.split( evaluatedValue )
                        
                        if dialog.separateTasks.value():
                            fileHandle.write( "OutputDirectory%s=%s\n" % (index, tempPath) )
                        else:
                            if IsPadded( os.path.basename( fileValue ) ):
                                tempFilename = GetPaddedPath( tempFilename )
                                
                            paddedPath = os.path.join( tempPath, tempFilename )
                            fileHandle.write( "OutputFilename%s=%s\n" % (index, paddedPath ) )
                            
                            #Check if the Write Node will be modifying the output's Frame numbers
                            if tempNode.knob( 'frame_mode' ):
                                if ( tempNode.knob( 'frame_mode' ).value() == "offset" ):
                                    fileHandle.write( "ExtraInfoKeyValue%d=OutputFrameOffset%s=%s\n" % (extraKVPIndex, index, str( int(tempNode.knob( 'frame' ).value()) )) )
                                    extraKVPIndex += 1
                                elif ( tempNode.knob( 'frame_mode' ).value() == "start at" or tempNode.knob( 'frame_mode' ).value() == "start_at"):
                                    franges = nuke.FrameRanges( tempFrameList )
                                    fileHandle.write( "ExtraInfoKeyValue%d=OutputFrameOffset%s=%s\n" % (extraKVPIndex, index, str( int(tempNode.knob( 'frame' ).value()) - franges.minFrame() )) )
                                    extraKVPIndex += 1
                                else:
                                    #TODO: Handle 'expression'? Would be much harder
                                    pass
                            
                        index = index + 1        
        
    # Write the shotgun data.
    if dialog.useShotgunInfo.value():
        if 'TaskName' in shotgunKVPs:
            fileHandle.write( "ExtraInfo0=%s\n" % shotgunKVPs['TaskName'] )
            
        if 'ProjectName' in shotgunKVPs:
            fileHandle.write( "ExtraInfo1=%s\n" % shotgunKVPs['ProjectName'] )
            
        if 'EntityName' in shotgunKVPs:
            fileHandle.write( "ExtraInfo2=%s\n" % shotgunKVPs['EntityName'] )
            
        if 'VersionName' in shotgunKVPs:
            fileHandle.write( "ExtraInfo3=%s\n" % shotgunKVPs['VersionName'] )
            
        if 'Description' in shotgunKVPs:
            fileHandle.write( "ExtraInfo4=%s\n" % shotgunKVPs['Description'] )
            
        if 'UserName' in shotgunKVPs:
            fileHandle.write( "ExtraInfo5=%s\n" % shotgunKVPs['UserName'] )
        
        #dump the rest in as KVPs
        for key in shotgunKVPs:
            if key != "DraftTemplate":
                fileHandle.write( "ExtraInfoKeyValue%d=%s=%s\n" % (extraKVPIndex, key, shotgunKVPs[key]) )
                extraKVPIndex += 1
    
    #Draft stuff
    if dialog.submitDraftJob.value():
        draftNode = node
        #TODO: Need to figure out if we want to do something else in this case (all write nodes being submitted in one job)
        if node == None:
            draftNode = writeNodes[0] 
        
        fileHandle.write( "ExtraInfoKeyValue%d=DraftTemplate=%s\n" % (extraKVPIndex, dialog.templatePath.value()) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftUsername=%s\n" % (extraKVPIndex, dialog.draftUser.value()) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftEntity=%s\n" % (extraKVPIndex, dialog.draftEntity.value()) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftVersion=%s\n" % (extraKVPIndex, dialog.draftVersion.value()) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftFrameWidth=%s\n" % (extraKVPIndex, draftNode.width()) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftFrameHeight=%s\n" % (extraKVPIndex, draftNode.height()) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftUploadToShotgun=%s\n" % (extraKVPIndex, str(dialog.uploadToShotgun.enabled() and dialog.uploadToShotgun.value())) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftExtraArgs=%s\n" % (extraKVPIndex, dialog.draftExtraArgs.value()) )
        extraKVPIndex += 1
    
    
    ##########################################################################################
    ## NIM 
    ##########################################################################################
    
    if dialog.useNimInfo.value():
        nim_job = str(dialog.nimJob.value())+":"+str(dialog.nimShow.value())+":"+str(dialog.nimShot.value())
        nim_class = "SHOT"
        nim_taskID = dialog.taskDict[dialog.nimTask.value()]
        nim_fileID = None
        #os.getenv('nim_job_id')
        nim_jobID = dialog.nim_job_id
        
        fileHandle.write( "ExtraInfo0=%s\n" % nim_job )
        fileHandle.write( "ExtraInfoKeyValue%d=nimJob=%s\n" % (extraKVPIndex, nim_job) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfo1=%s\n" % nim_class )
        fileHandle.write( "ExtraInfoKeyValue%d=nimClass=%s\n" % (extraKVPIndex, nim_class) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=nimTaskID=%s\n" % (extraKVPIndex, nim_taskID) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=nimFileID=%s\n" % (extraKVPIndex, nim_fileID) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=nimJobID=%s\n" % (extraKVPIndex, nim_jobID) )
        extraKVPIndex += 1
            
    if dialog.submitNimDraftJob.value():
        nimDraftNode = node
        if node == None:
            nimDraftNode = writeNodes[0]
        
        (outFileHead, outFileTail) = os.path.split( nuke.root().name() )
        
        fileHandle.write( "ExtraInfoKeyValue%d=DraftUsername=%s\n" % (extraKVPIndex, dialog.nimArtist.value()) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftEntity=%s\n" % (extraKVPIndex, outFileTail ) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftTemplate=%s\n" % (extraKVPIndex, str(dialog.nimTemplatePath.value())) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftFrameWidth=%s\n" % (extraKVPIndex, nimDraftNode.width()) )
        extraKVPIndex += 1
        fileHandle.write( "ExtraInfoKeyValue%d=DraftFrameHeight=%s\n" % (extraKVPIndex, nimDraftNode.height()) )
        extraKVPIndex += 1
        
        if (dialog.uploadToNim.value() and dialog.uploadToNim.enabled()):
            fileHandle.write( "ExtraInfoKeyValue%d=DraftUploadToNim=True\n" % (extraKVPIndex) )
        else:
            fileHandle.write( "ExtraInfoKeyValue%d=DraftUploadToNim=False\n" % (extraKVPIndex) )
        extraKVPIndex += 1
        
        if dialog.nimEncodeSRGB.value():
            fileHandle.write( "ExtraInfoKeyValue%d=DraftNimEncodeSRGB=True\n" % (extraKVPIndex) )
        else:
            fileHandle.write( "ExtraInfoKeyValue%d=DraftNimEncodeSRGB=False\n" % (extraKVPIndex) )
        extraKVPIndex += 1
        
    ##########################################################################################
    ## END NIM 
    ##########################################################################################
    
    
    fileHandle.close()
    
    # Update task progress
    progressTask.setMessage("Creating Plugin Info File")
    progressTask.setProgress(10)
    
    # Create the plugin info file
    pluginInfoFile = deadlineTemp + ("/nuke_plugin_info%d.job" % jobCount)
    fileHandle = open( pluginInfoFile, "w" )
    if not dialog.submitScene.value():
        fileHandle.write( "SceneFile=%s\n" % root.name() )
    
    fileHandle.write( "Version=%s.%s\n" % (nuke.env[ 'NukeVersionMajor' ], nuke.env['NukeVersionMinor']) )
    fileHandle.write( "Threads=%s\n" % dialog.threads.value() )
    fileHandle.write( "RamUse=%s\n" % dialog.memoryUsage.value() )
    fileHandle.write( "Build=%s\n" % dialog.build.value() )
    fileHandle.write( "BatchMode=%s\n" % dialog.batchMode.value())
    fileHandle.write( "BatchModeIsMovie=%s\n" % tempIsMovie )
    
    if dialog.separateJobs.value():
        #we need the fullName of the node here, otherwise write nodes that are embedded in groups won't work
        fileHandle.write( "WriteNode=%s\n" % node.fullName() )
    elif dialog.separateTasks.value():
        fileHandle.write( "WriteNodesAsSeparateJobs=True\n" )
        
        writeNodeIndex = 0
        for tempNode in writeNodes:
            if not tempNode.knob( 'disable' ).value():
                enterLoop = True
                if dialog.readFileOnly.value() and tempNode.knob( 'reading' ):
                    enterLoop = enterLoop and tempNode.knob( 'reading' ).value()
                if dialog.selectedOnly.value():
                    enterLoop = enterLoop and tempNode.isSelected()
                
                if enterLoop:
                    #we need the fullName of the node here, otherwise write nodes that are embedded in groups won't work
                    fileHandle.write( "WriteNode%s=%s\n" % (writeNodeIndex,tempNode.fullName()) )
                    
                    if dialog.useNodeRange.value() and tempNode.knob( 'use_limit' ).value():
                        startFrame = int(tempNode.knob('first').value())
                        endFrame = int(tempNode.knob('last').value())
                    else:
                        startFrame = nuke.Root().firstFrame()
                        endFrame = nuke.Root().lastFrame()
                        if dialog.frameListMode.value() == "Input":
                            try:
                                activeInput = nuke.activeViewer().activeInput()
                                startFrame = nuke.activeViewer().node().input(activeInput).frameRange().first()
                                endFrame = nuke.activeViewer().node().input(activeInput).frameRange().last()
                            except:
                                pass
                    
                    fileHandle.write( "WriteNode%sStartFrame=%s\n" % (writeNodeIndex,startFrame) )
                    fileHandle.write( "WriteNode%sEndFrame=%s\n" % (writeNodeIndex,endFrame) )
                    writeNodeIndex += 1
    else:
        if dialog.readFileOnly.value() or dialog.selectedOnly.value():
            writeNodesStr = ""
            
            for tempNode in writeNodes:
                if not tempNode.knob( 'disable' ).value():
                    enterLoop = True
                    if dialog.readFileOnly.value() and tempNode.knob( 'reading' ):
                        enterLoop = enterLoop and tempNode.knob( 'reading' ).value()
                    if dialog.selectedOnly.value():
                        enterLoop = enterLoop and tempNode.isSelected()
                    
                    if enterLoop:
                        #we need the fullName of the node here, otherwise write nodes that are embedded in groups won't work
                        writeNodesStr += ("%s," % tempNode.fullName())
                        
            writeNodesStr = writeNodesStr.strip( "," )
            fileHandle.write( "WriteNode=%s\n" % writeNodesStr )
    
    fileHandle.write( "NukeX=%s\n" % dialog.useNukeX.value() )
    fileHandle.write( "ContinueOnError=%s\n" % dialog.continueOnError.value() )
    
    fileHandle.write( "EnforceRenderOrder=%s\n" % dialog.enforceRenderOrder.value() )
    
    viewsToRender = []
    if dialog.chooseViewsToRender.value():
        for vk in dialog.viewToRenderKnobs:
            if vk[0].value():
                viewsToRender.append(vk[1])
    
    if len(viewsToRender) > 0:
        fileHandle.write( "Views=%s\n" % ','.join(viewsToRender) )
    else:
        fileHandle.write( "Views=\n" )
    
    fileHandle.write( "StackSize=%s\n" % dialog.stackSize.value() )
    
    if int(nuke.env[ 'NukeVersionMajor' ]) >= 7:
        fileHandle.write( "UseGpu=%s\n" % dialog.useGpu.value() )
    
    fileHandle.close()
    
    # Update task progress
    progressTask.setMessage("Submitting Job %d to Deadline" % jobCount)
    progressTask.setProgress(30)
    
    # Submit the job to Deadline
    args = []
    args.append( jobInfoFile )
    args.append( pluginInfoFile )
    if dialog.submitScene.value():
        args.append( root.name() )
    
    tempResults = ""
    
    # Submit Job
    progressTask.setProgress(50)
    
    # If submitting multiple jobs, acquire the semaphore so that only one job is submitted at a time.
    if semaphore:
        semaphore.acquire()
        
    try:
        tempResults = CallDeadlineCommand( args )
    finally:
        # Release the semaphore if necessary.
        if semaphore:
            semaphore.release()
    
    # Update task progress
    progressTask.setMessage("Complete!")
    progressTask.setProgress(100)
    
    print "Job submission #%d complete" % jobCount
    
    # If submitting multiple jobs, just print the results to the console, otherwise show them to the user.
    if semaphore:
        print tempResults
    else:
        nuke.executeInMainThread( nuke.message, tempResults )
    
    return tempResults

#This will recursively find nodes of the given class (used to find write nodes, even if they're embedded in groups).  
def RecursiveFindNodes(nodeClass, startNode):
    nodeList = []
    
    if startNode != None:
        if startNode.Class() == nodeClass:
            nodeList = [startNode]
        elif isinstance(startNode, nuke.Group):
            for child in startNode.nodes():
                nodeList.extend( RecursiveFindNodes(nodeClass, child) )
        
    return nodeList

# The main submission function.
def SubmitToDeadline( currNukeScriptPath ):
    global dialog
    #global deadlineCommand
    global nukeScriptPath
    global deadlineHome
    global shotgunKVPs
    
    # Add the current nuke script path to the system path.
    nukeScriptPath = currNukeScriptPath
    sys.path.append( nukeScriptPath )
    
    # DeadlineGlobals contains initial values for the submission dialog. These can be modified
    # by an external sanity scheck script.
    import DeadlineGlobals
    
    # Get the root node.
    root = nuke.Root()
    
    # If the Nuke script hasn't been saved, its name will be 'Root' instead of the file name.
    if root.name() == "Root":
        nuke.message( "The Nuke script must be saved before it can be submitted to Deadline." )
        return
    
    # Check if proxy mode is enabled, and warn the user.
    if root.proxy():
        answer = nuke.ask( "Proxy Mode is enabled, which may cause problems when rendering through Deadline. Do you wish to continue?" )
        if not answer:
            return
    
    # If the Nuke script has been modified, then save it.
    if root.modified():
        nuke.scriptSave( root.name() )
    
    # Get the current user Deadline home directory, which we'll use to store settings and temp files.
    deadlineHome = CallDeadlineCommand( ["-GetCurrentUserHomeDirectory",] )
    
    deadlineHome = deadlineHome.replace( "\n", "" ).replace( "\r", "" )
    deadlineSettings = deadlineHome + "/settings"
    deadlineTemp = deadlineHome + "/temp"
    
    # Get the maximum priority.
    try:
        output = CallDeadlineCommand( ["-getmaximumpriority",] )
        maximumPriority = int(output)
    except:
        maximumPriority = 100
    
    # Get the pools.
    output = CallDeadlineCommand( ["-pools",] )
    pools = output.splitlines()
    
    secondaryPools = []
    secondaryPools.append(" ")
    for currPool in pools:
        secondaryPools.append(currPool)
    
    # Get the groups.
    output = CallDeadlineCommand( ["-groups",] )
    groups = output.splitlines()
    
    initFrameListMode = "Global"
    initCustomFrameList = None
    
    # Set initial settings for submission dialog.
    DeadlineGlobals.initJobName = os.path.basename( nuke.Root().name() )
    DeadlineGlobals.initComment = ""
    
    DeadlineGlobals.initDepartment = ""
    DeadlineGlobals.initPool = "none"
    DeadlineGlobals.initSecondaryPool = " "
    DeadlineGlobals.initGroup = "none"
    DeadlineGlobals.initPriority = 50
    DeadlineGlobals.initTaskTimeout = 0
    DeadlineGlobals.initAutoTaskTimeout = False
    DeadlineGlobals.initConcurrentTasks = 1
    DeadlineGlobals.initLimitConcurrentTasks = True
    DeadlineGlobals.initMachineLimit = 0
    DeadlineGlobals.initIsBlacklist = False
    DeadlineGlobals.initMachineList = ""
    DeadlineGlobals.initLimitGroups = ""
    DeadlineGlobals.initDependencies = ""
    DeadlineGlobals.initOnComplete = "Nothing"
    DeadlineGlobals.initSubmitSuspended = False
    DeadlineGlobals.initChunkSize = 10
    DeadlineGlobals.initThreads = 0
    DeadlineGlobals.initMemoryUsage = 0
    
    DeadlineGlobals.initBuild = "32bit"
    if nuke.env[ '64bit' ]:
        DeadlineGlobals.initBuild = "64bit"
    
    DeadlineGlobals.initSeparateJobs = False
    DeadlineGlobals.initSeparateJobDependencies = False
    DeadlineGlobals.initSeparateTasks = False
    DeadlineGlobals.initUseNodeRange = True
    DeadlineGlobals.initReadFileOnly = False
    DeadlineGlobals.initSelectedOnly = False
    DeadlineGlobals.initSubmitScene = False
    DeadlineGlobals.initBatchMode = False
    DeadlineGlobals.initContinueOnError = False
    DeadlineGlobals.initUseGpu = False
    DeadlineGlobals.initEnforceRenderOrder = False
    DeadlineGlobals.initStackSize = 0
    
    DeadlineGlobals.initUseNukeX = False
    if nuke.env[ 'nukex' ]:
        DeadlineGlobals.initUseNukeX = True
        
    DeadlineGlobals.initUseDraft = False
    DeadlineGlobals.initDraftTemplate = ""
    DeadlineGlobals.initDraftUser = ""
    DeadlineGlobals.initDraftEntity = ""
    DeadlineGlobals.initDraftVersion = ""
    DeadlineGlobals.initDraftExtraArgs = ""
    
    
    ##########################################################################################
    ## NIM 
    ##########################################################################################
    DeadlineGlobals.initUseNimInfo = False
    DeadlineGlobals.initNimShotID = None
    DeadlineGlobals.initNimTaskID = None
    DeadlineGlobals.initSubmitNimDraftJob = False
    DeadlineGlobals.initUploadToNim = False
    DeadlineGlobals.initNimTemplatePath = "R:/Draft/Templates/NIM_Draft_Dailies.py"
    DeadlineGlobals.initNimEncodeSRGB = False
    ##########################################################################################
    ## END NIM 
    ##########################################################################################
    
    
    # Read In Sticky Settings
    configFile = deadlineSettings + "/nuke_py_submission.ini"
    print "Reading sticky settings from %s" % configFile
    try:
        if os.path.isfile( configFile ):
            config = ConfigParser.ConfigParser()
            config.read( configFile )
            
            if config.has_section( "Sticky" ):
                if config.has_option( "Sticky", "FrameListMode" ):
                    initFrameListMode = config.get( "Sticky", "FrameListMode" )
                if config.has_option( "Sticky", "CustomFrameList" ):
                    initCustomFrameList = config.get( "Sticky", "CustomFrameList" )
                
                if config.has_option( "Sticky", "Department" ):
                    DeadlineGlobals.initDepartment = config.get( "Sticky", "Department" )
                if config.has_option( "Sticky", "Pool" ):
                    DeadlineGlobals.initPool = config.get( "Sticky", "Pool" )
                if config.has_option( "Sticky", "SecondaryPool" ):
                    DeadlineGlobals.initSecondaryPool = config.get( "Sticky", "SecondaryPool" )
                if config.has_option( "Sticky", "Group" ):
                    DeadlineGlobals.initGroup = config.get( "Sticky", "Group" )
                if config.has_option( "Sticky", "Priority" ):
                    DeadlineGlobals.initPriority = config.getint( "Sticky", "Priority" )
                if config.has_option( "Sticky", "MachineLimit" ):
                    DeadlineGlobals.initMachineLimit = config.getint( "Sticky", "MachineLimit" )
                if config.has_option( "Sticky", "IsBlacklist" ):
                    DeadlineGlobals.initIsBlacklist = config.getboolean( "Sticky", "IsBlacklist" )
                if config.has_option( "Sticky", "MachineList" ):
                    DeadlineGlobals.initMachineList = config.get( "Sticky", "MachineList" )
                if config.has_option( "Sticky", "LimitGroups" ):
                    DeadlineGlobals.initLimitGroups = config.get( "Sticky", "LimitGroups" )
                if config.has_option( "Sticky", "SubmitSuspended" ):
                    DeadlineGlobals.initSubmitSuspended = config.getboolean( "Sticky", "SubmitSuspended" )
                if config.has_option( "Sticky", "ChunkSize" ):
                    DeadlineGlobals.initChunkSize = config.getint( "Sticky", "ChunkSize" )
                if config.has_option( "Sticky", "ConcurrentTasks" ):
                    DeadlineGlobals.initConcurrentTasks = config.getint( "Sticky", "ConcurrentTasks" )
                if config.has_option( "Sticky", "LimitConcurrentTasks" ):
                    DeadlineGlobals.initLimitConcurrentTasks = config.getboolean( "Sticky", "LimitConcurrentTasks" )
                if config.has_option( "Sticky", "Threads" ):
                    DeadlineGlobals.initThreads = config.getint( "Sticky", "Threads" )
                if config.has_option( "Sticky", "SubmitScene" ):
                    DeadlineGlobals.initSubmitScene = config.getboolean( "Sticky", "SubmitScene" )
                if config.has_option( "Sticky", "BatchMode" ):
                    DeadlineGlobals.initBatchMode = config.getboolean( "Sticky", "BatchMode" )
                if config.has_option( "Sticky", "ContinueOnError" ):
                    DeadlineGlobals.initContinueOnError = config.getboolean( "Sticky", "ContinueOnError" )
                if config.has_option( "Sticky", "UseNodeRange" ):
                    DeadlineGlobals.initUseNodeRange = config.getboolean( "Sticky", "UseNodeRange" )
                if config.has_option( "Sticky", "UseGpu" ):
                    DeadlineGlobals.initUseGpu = config.getboolean( "Sticky", "UseGpu" )
                if config.has_option( "Sticky", "EnforceRenderOrder" ):
                    DeadlineGlobals.initEnforceRenderOrder = config.getboolean( "Sticky", "EnforceRenderOrder" )
                if config.has_option( "Sticky", "UseDraft" ):
                    DeadlineGlobals.initUseDraft = config.getboolean( "Sticky", "UseDraft" )
                if config.has_option( "Sticky", "DraftTemplate" ):
                    DeadlineGlobals.initDraftTemplate = config.get( "Sticky", "DraftTemplate" )
                if config.has_option( "Sticky", "DraftUser" ):
                    DeadlineGlobals.initDraftUser = config.get( "Sticky", "DraftUser" )
                if config.has_option( "Sticky", "DraftEntity" ):
                    DeadlineGlobals.initDraftEntity = config.get( "Sticky", "DraftEntity" )
                if config.has_option( "Sticky", "DraftVersion" ):
                    DeadlineGlobals.initDraftVersion = config.get( "Sticky", "DraftVersion" )
                if config.has_option( "Sticky", "DraftExtraArgs"):
                    DeadlineGlobals.initDraftExtraArgs = config.get( "Sticky", "DraftExtraArgs" )
                
                
                ##########################################################################################
                ## NIM 
                ##########################################################################################
                
                if config.has_option( "Sticky", "useNimInfo" ):
                    DeadlineGlobals.initUseNimInfo = config.getboolean( "Sticky", "useNimInfo" )
                if config.has_option( "Sticky", "nimShotID" ):
                    DeadlineGlobals.initNimShotID = config.get( "Sticky", "nimShotID" )
                if config.has_option( "Sticky", "nimTaskID" ):
                    DeadlineGlobals.initNimTaskID = config.get( "Sticky", "nimTaskID" )
                if config.has_option( "Sticky", "submitNimDraftJob" ):
                    DeadlineGlobals.initSubmitNimDraftJob = config.getboolean( "Sticky", "submitNimDraftJob" )
                if config.has_option( "Sticky", "uploadToNim" ):
                    DeadlineGlobals.initUploadToNim = config.getboolean( "Sticky", "uploadToNim" )
                if config.has_option( "Sticky", "nimTemplatePath" ):
                    DeadlineGlobals.initNimTemplatePath = config.get( "Sticky", "nimTemplatePath" )
                if config.has_option( "Sticky", "nimEncodeSRGB" ):
                     DeadlineGlobals.initNimEncodeSRGB = config.getboolean( "Sticky", "nimEncodeSRGB" )
                
                ##########################################################################################
                ## END NIM 
                ##########################################################################################
                
                
                root = nuke.Root()
                if "DeadlineSGData" in root.knobs():
                    sgDataKnob = root.knob( "DeadlineSGData" )
                    shotgunKVPs = ast.literal_eval( sgDataKnob.value() )
    except:
        print( "Could not read sticky settings")
    
    try:
                root = nuke.Root()
                if "FrameListMode" in root.knobs():
                    initFrameListMode = ( root.knob( "FrameListMode" ) ).value() 
                    
                if "CustomFrameList" in root.knobs():
                    initCustomFrameList = ( root.knob( "CustomFrameList" ) ).value() 
                    
                if "Department" in root.knobs():
                    DeadlineGlobals.initDepartment = ( root.knob( "Department" ) ).value()
                    
                if "Pool" in root.knobs():
                    DeadlineGlobals.initPool = ( root.knob( "Pool" ) ).value()
                    
                if "SecondaryPool" in root.knobs():
                    DeadlineGlobals.initSecondaryPool = ( root.knob( "SecondaryPool" ) ).value()
                    
                if "Group" in root.knobs():
                    DeadlineGlobals.initGroup = ( root.knob( "Group" ) ).value()
                    
                if "Priority" in root.knobs():
                    DeadlineGlobals.initPriority = int( ( root.knob( "Priority" ) ).value() )
                    
                if "MachineLimit" in root.knobs():
                    DeadlineGlobals.initMachineLimit = int( ( root.knob( "MachineLimit" ) ).value() )
                    
                if "IsBlacklist" in root.knobs():
                    DeadlineGlobals.initIsBlacklist = StrToBool( ( root.knob( "IsBlacklist" ) ).value() )
                
                if "MachineList" in root.knobs():
                    DeadlineGlobals.initMachineList = ( root.knob( "MachineList" ) ).value()
                
                if "LimitGroups" in root.knobs():
                    DeadlineGlobals.initLimitGroups = ( root.knob( "LimitGroups" ) ).value()
                
                if "SubmitSuspended" in root.knobs():
                    DeadlineGlobals.initSubmitSuspended = StrToBool( ( root.knob( "SubmitSuspended" ) ).value() )
                
                if "ChunkSize" in root.knobs():
                    DeadlineGlobals.initChunkSize = int( ( root.knob( "ChunkSize" ) ).value() )
                
                if "ConcurrentTasks" in root.knobs():
                    DeadlineGlobals.initConcurrentTasks = int( ( root.knob( "ConcurrentTasks" ) ).value() )
                
                if "LimitConcurrentTasks" in root.knobs():
                    DeadlineGlobals.initLimitConcurrentTasks = StrToBool( ( root.knob( "LimitConcurrentTasks" ) ).value() )
                
                if "Threads" in root.knobs():
                    DeadlineGlobals.initThreads = int( ( root.knob( "Threads" ) ).value() )
                
                if "SubmitScene" in root.knobs():
                    DeadlineGlobals.initSubmitScene = StrToBool( ( root.knob( "SubmitScene" ) ).value() )
                
                if "BatchMode" in root.knobs():
                    DeadlineGlobals.initBatchMode = StrToBool( ( root.knob( "BatchMode" ) ).value() )
                
                if "ContinueOnError" in root.knobs():
                    DeadlineGlobals.initContinueOnError = StrToBool( ( root.knob( "ContinueOnError" ) ).value() )
                
                if "UseNodeRange" in root.knobs():
                    DeadlineGlobals.initUseNodeRange = StrToBool( ( root.knob( "UseNodeRange" ) ).value() )
                
                if "UseGpu" in root.knobs():
                    DeadlineGlobals.initUseGpu = StrToBool( ( root.knob( "UseGpu" ) ).value() )
                    
                if "EnforceRenderOrder" in root.knobs():
                    DeadlineGlobals.initEnforceRenderOrder = StrToBool( ( root.knob( "EnforceRenderOrder" ) ).value() )
                
                if "UseDraft" in root.knobs():
                    DeadlineGlobals.initUseDraft = StrToBool( ( root.knob( "UseDraft" ) ).value() )
                
                if "DraftTemplate" in root.knobs():
                    DeadlineGlobals.initDraftTemplate = ( root.knob( "DraftTemplate" ) ).value()
                
                if "DraftUser" in root.knobs():
                    DeadlineGlobals.initDraftUser = ( root.knob( "DraftUser" ) ).value()
                
                if "DraftEntity" in root.knobs():
                    DeadlineGlobals.initDraftEntity = ( root.knob( "DraftEntity" ) ).value()
                
                if "DraftVersion" in root.knobs():
                    DeadlineGlobals.initDraftVersion = ( root.knob( "DraftVersion" ) ).value()
                    
                if "DraftExtraArgs" in root.knobs():
                    DeadlineGlobals.initDraftExtraArgs = ( root.knob( "DraftExtraArgs" ) ).value()
                
    except:
        print "Could not read knob settings."
    
    if initFrameListMode != "Custom":
        startFrame = nuke.Root().firstFrame()
        endFrame = nuke.Root().lastFrame()
        if initFrameListMode == "Input":
            try:
                activeInput = nuke.activeViewer().activeInput()
                startFrame = nuke.activeViewer().node().input(activeInput).frameRange().first()
                endFrame = nuke.activeViewer().node().input(activeInput).frameRange().last()
            except:
                pass
        
        if startFrame == endFrame:
            DeadlineGlobals.initFrameList = str(startFrame)
        else:
            DeadlineGlobals.initFrameList = str(startFrame) + "-" + str(endFrame)
    else:
        if initCustomFrameList == None or initCustomFrameList.strip() == "":
            startFrame = nuke.Root().firstFrame()
            endFrame = nuke.Root().lastFrame()
            if startFrame == endFrame:
                DeadlineGlobals.initFrameList = str(startFrame)
            else:
                DeadlineGlobals.initFrameList = str(startFrame) + "-" + str(endFrame)
        else:
            DeadlineGlobals.initFrameList = initCustomFrameList.strip()
    
    # Run the sanity check script if it exists, which can be used to set some initial values.
    sanityCheckFile = nukeScriptPath + "/CustomSanityChecks.py"
    if os.path.isfile( sanityCheckFile ):
        print( "Running sanity check script: " + sanityCheckFile )
        try:
            import CustomSanityChecks
            sanityResult = CustomSanityChecks.RunSanityCheck()
            if not sanityResult:
                print( "Sanity check returned false, exiting" )
                return
        except:
            print( "Could not run CustomSanityChecks.py script" )
            print( traceback.format_exc() )
    
    if DeadlineGlobals.initPriority > maximumPriority:
        DeadlineGlobals.initPriority = (maximumPriority / 2)
    
    # Both of these can't be enabled!
    if DeadlineGlobals.initSeparateJobs and DeadlineGlobals.initSeparateTasks:
        DeadlineGlobals.initSeparateTasks = False
    
    # Check for potential issues and warn user about any that are found.
    warningMessages = ""
    writeNodes = RecursiveFindNodes( "Write", nuke.Root() )
    deepWriteNodes = RecursiveFindNodes( "DeepWrite", nuke.Root() )
    writeGeoNodes = RecursiveFindNodes( "WriteGeo", nuke.Root() )
    
    writeNodes.extend(deepWriteNodes)
    writeNodes.extend(writeGeoNodes)
    
    
    print "Found a total of %d write nodes" % len( writeNodes )
    
    # Check all the output filenames if they are local or not padded (non-movie files only).
    outputCount = 0
    for node in writeNodes:
        reading = False
        if node.knob( 'reading' ):
            reading = node.knob( 'reading' ).value()
        
        # Need at least one write node that is enabled, and not set to read in as well.
        if not node.knob( 'disable' ).value() and not reading:
            outputCount = outputCount + 1
            
            #~ if root.proxy() and node.knob( 'proxy' ).value() != "":
                #~ filename = node.knob( 'proxy' ).value()
            #~ else:
                #~ filename = node.knob( 'file' ).value()
                
            filename = nuke.filename(node)
            if filename == "":
                warningMessages = warningMessages + "No output path for write node '" + node.name() + "' is defined\n\n"
            else:
                fileType = node.knob( 'file_type' ).value()
                
                if filename == None or filename == "":
                    warningMessages = warningMessages + "Output path for write node '" + node.name() + "' is empty\n\n"
                else:
                    if IsPathLocal( filename ):
                        warningMessages = warningMessages + "Output path for write node '" + node.name() + "' is local:\n" + filename + "\n\n"
                    if not HasExtension( filename ) and fileType.strip() == "":
                        warningMessages = warningMessages + "Output path for write node '%s' has no extension:\n%s\n\n"  % (node.name(), filename)
                    if not IsMovie( filename ) and not IsPadded( os.path.basename( filename ) ):
                        warningMessages = warningMessages + "Output path for write node '" + node.name() + "' is not padded:\n" + filename + "\n\n"
    
    # Warn if there are no write nodes.
    if outputCount == 0:
        warningMessages = warningMessages + "At least one enabled write node that has 'read file' disabled is required to render\n\n"
    
    # If there are any warning messages, show them to the user.
    if warningMessages != "":
        warningMessages = warningMessages + "Do you still wish to submit this job to Deadline?"
        answer = nuke.ask( warningMessages )
        if not answer:
            return
    
    print "Creating submission dialog..."
    
    # Create an instance of the submission dialog.
    dialog = DeadlineDialog( maximumPriority, pools, secondaryPools, groups )
    
    # Set the initial values.
    dialog.jobName.setValue( DeadlineGlobals.initJobName )
    dialog.comment.setValue( DeadlineGlobals.initComment )
    dialog.department.setValue( DeadlineGlobals.initDepartment )
    
    dialog.pool.setValue( DeadlineGlobals.initPool )
    dialog.secondaryPool.setValue( DeadlineGlobals.initSecondaryPool )
    dialog.group.setValue( DeadlineGlobals.initGroup )
    dialog.priority.setValue( DeadlineGlobals.initPriority )
    dialog.taskTimeout.setValue( DeadlineGlobals.initTaskTimeout )
    dialog.autoTaskTimeout.setValue( DeadlineGlobals.initAutoTaskTimeout )
    dialog.concurrentTasks.setValue( DeadlineGlobals.initConcurrentTasks )
    dialog.limitConcurrentTasks.setValue( DeadlineGlobals.initLimitConcurrentTasks )
    dialog.machineLimit.setValue( DeadlineGlobals.initMachineLimit )
    dialog.isBlacklist.setValue( DeadlineGlobals.initIsBlacklist )
    dialog.machineList.setValue( DeadlineGlobals.initMachineList )
    dialog.limitGroups.setValue( DeadlineGlobals.initLimitGroups )
    dialog.dependencies.setValue( DeadlineGlobals.initDependencies )
    dialog.onComplete.setValue( DeadlineGlobals.initOnComplete )
    dialog.submitSuspended.setValue( DeadlineGlobals.initSubmitSuspended )
    
    dialog.frameListMode.setValue( initFrameListMode )
    dialog.frameList.setValue( DeadlineGlobals.initFrameList )
    dialog.chunkSize.setValue( DeadlineGlobals.initChunkSize )
    dialog.threads.setValue( DeadlineGlobals.initThreads )
    dialog.memoryUsage.setValue( DeadlineGlobals.initMemoryUsage )
    dialog.build.setValue( DeadlineGlobals.initBuild )
    dialog.separateJobs.setValue( DeadlineGlobals.initSeparateJobs )
    dialog.separateJobDependencies.setValue( DeadlineGlobals.initSeparateJobDependencies )
    dialog.separateTasks.setValue( DeadlineGlobals.initSeparateTasks )
    dialog.readFileOnly.setValue( DeadlineGlobals.initReadFileOnly )
    dialog.selectedOnly.setValue( DeadlineGlobals.initSelectedOnly )
    dialog.submitScene.setValue( DeadlineGlobals.initSubmitScene )
    dialog.useNukeX.setValue( DeadlineGlobals.initUseNukeX )
    dialog.continueOnError.setValue( DeadlineGlobals.initContinueOnError )
    dialog.batchMode.setValue( DeadlineGlobals.initBatchMode )
    dialog.useNodeRange.setValue( DeadlineGlobals.initUseNodeRange )
    dialog.useGpu.setValue( DeadlineGlobals.initUseGpu )
    dialog.enforceRenderOrder.setValue( DeadlineGlobals.initEnforceRenderOrder )
    #dialog.viewsToRender.setValue( DeadlineGlobals.initViews )
    dialog.stackSize.setValue( DeadlineGlobals.initStackSize )
    
    dialog.separateJobs.setEnabled( len( writeNodes ) > 0 )
    dialog.separateTasks.setEnabled( len( writeNodes ) > 0 )
    
    dialog.separateJobDependencies.setEnabled( dialog.separateJobs.value() )
    dialog.useNodeRange.setEnabled( dialog.separateJobs.value() or dialog.separateTasks.value() )
    dialog.frameList.setEnabled( not (dialog.separateJobs.value() and dialog.useNodeRange.value()) and not dialog.separateTasks.value() )
    
    dialog.submitDraftJob.setValue( DeadlineGlobals.initUseDraft )
    dialog.templatePath.setValue( DeadlineGlobals.initDraftTemplate )
    dialog.draftUser.setValue( DeadlineGlobals.initDraftUser )
    dialog.draftEntity.setValue( DeadlineGlobals.initDraftEntity )
    dialog.draftVersion.setValue( DeadlineGlobals.initDraftVersion )
    dialog.draftExtraArgs.setValue( DeadlineGlobals.initDraftExtraArgs )
    
    dialog.templatePath.setEnabled( dialog.submitDraftJob.value() )
    dialog.draftUser.setEnabled( dialog.submitDraftJob.value() )
    dialog.draftEntity.setEnabled( dialog.submitDraftJob.value() )
    dialog.draftVersion.setEnabled( dialog.submitDraftJob.value() )
    dialog.draftExtraArgs.setEnabled( dialog.submitDraftJob.value() )
    
    UpdateShotgunUI()
    
    
    ##########################################################################################
    ## NIM 
    ##########################################################################################
    
    
    # GET INFO FROM ~/nim
    userHome = expanduser("~")
    if userHome.endswith('Documents'):
        userHome = userHome[:-9]
    nimPrefsFile = os.path.join(userHome,'.nim','prefs.nim')
    nimPrefs = {}
    with open(nimPrefsFile) as prefsFile:
        for line in prefsFile:
            name, var = line.partition("=")[::2]
            var = var.rstrip(' \r\n')
            nimPrefs[name.strip()] = var
    prefsFile.close()
    #nim_URL = nimPrefs["nimURL"]
    nim_URL = nimPrefs["NIM_URL"]
    
    # GET INFO FROM nimPublish
    root = nuke.Root()
    
    nim_user = "No Artist Found"
    if "nim_user" in root.knobs():
        nim_user = ( root.knob( "nim_user" ) ).value()
    else:
        #FALLBACK TO READ FROM OS ENV
        print('NIM No User Found in Root')
        nim_user = os.environ['USERNAME']
        
    nim_username = "No Artist Found"
    try:
        sqlCmd = {
                    'q':'getUserFullName',
                    'u': nim_user
                }  
        userResult = getSqlData(nim_URL, sqlCmd)
        if len(userResult)>0:
            nim_username = userResult[0]['first_name']+" "+userResult[0]['last_name']
        else:
            print('NIM No User Found')
    except:
        print("NIM User Query Failed")

    
    nim_job_id = None
    nim_job_folder = None
    nim_show_id = None
    nim_show_folder = None
    nim_shot_id = None
    nim_shot_folder = None
    
    #nim_job_id = os.getenv('nim_job_id')
    #dialog.nim_job_id = nim_job_id
    if "nim_jobID" in root.knobs():
        nim_job_id = ( root.knob( "nim_jobID" ) ).value()
        dialog.nim_job_id = nim_job_id
    
    #nim_job_folder = os.getenv('nim_job_folder')
    if "nim_compPath" in root.knobs():
        nim_job_folder = ( root.knob( "nim_compPath" ) ).value()
        
    #nim_show_id = os.getenv('nim_show_id')
    #dialog.nim_show_id = nim_show_id
    if "nim_showID" in root.knobs():
        nim_show_id = ( root.knob( "nim_showID" ) ).value()
        dialog.nim_show_id = nim_show_id
        
    #nim_show_folder = os.getenv('nim_show_folder')
    if "nim_show" in root.knobs():
        nim_show_folder = ( root.knob( "nim_show" ) ).value()
    
    #nim_shot_id = os.getenv('nim_shot_id')
    #dialog.nim_shot_id = nim_shot_id
    if "nim_shotID" in root.knobs():
        nim_shot_id = ( root.knob( "nim_shotID" ) ).value()
        dialog.nim_shot_id = nim_shot_id
        
    #nim_shot_folder = os.getenv('nim_shot_folder')
    if "nim_shot" in root.knobs():
        nim_shot_folder = ( root.knob( "nim_shot" ) ).value()
    
    try:
        print('NIM ShotID: '+ nim_shot_id)
    except:
        print('NIM No Associated Shot')
    
    # GET ALL COMP TASKS FOR GIVEN SHOT
    # STORE IN ARRAY FOR TAB
    
    sqlCmd = {'q':'getCompTasks','itemID': nim_shot_id}
    nim_task_array = getSqlData(nim_URL, sqlCmd)
    
    #self.taskFolderDict = {}
    nim_task_list = []
    nim_task_list.append('Select...')
    
    selectedTask = None
    for task in nim_task_array:
        task_username = str(task['username'])
        task_taskName = str(task['taskName'])
        task_taskDesc = str(task['taskDesc'])
        task_listName = task_username +' : '+ task_taskName
        if(task_taskDesc != 'None' and task_taskDesc != ''):
            task_listName += ' : '+task_taskDesc
        nim_task_list.append(task_listName)
        dialog.taskDict[task_listName] = task['taskID']
        #self.taskFolderDict[task['username']+' : '+task['taskName']+' : '+task['taskDesc']] = str(task['username'])+' : '+str(task['taskName'])+' : '+str(task['taskDesc'])
        #IF shotID Globals are = to CURRENT ShotID Then Set task to saved TaskID
        if nim_shot_id == DeadlineGlobals.initNimShotID and task['taskID'] == DeadlineGlobals.initNimTaskID:
            selectedTask = task_listName
    
    if nim_shot_id == '':
        dialog.useNimInfo.setEnabled( False )
    dialog.useNimInfo.setValue( DeadlineGlobals.initUseNimInfo )
    print "Use NIM Info: %s" % DeadlineGlobals.initUseNimInfo
    
    dialog.nimArtist.setValue(str(nim_username))
    dialog.nimJob.setValue( nim_job_folder )
    dialog.nimShow.setValue( nim_show_folder )
    dialog.nimShot.setValue( nim_shot_folder )
    dialog.nimTask.setValues(nim_task_list)
    if selectedTask != None:
        dialog.nimTask.setValue(str(selectedTask))
    dialog.submitNimDraftJob.setValue( DeadlineGlobals.initSubmitNimDraftJob )
    dialog.uploadToNim.setValue( DeadlineGlobals.initUploadToNim )
    dialog.nimTemplatePath.setValue( DeadlineGlobals.initNimTemplatePath )
    dialog.nimEncodeSRGB.setValue( DeadlineGlobals.initNimEncodeSRGB )
    
    if dialog.useNimInfo.enabled():
        dialog.nimArtist.setEnabled( dialog.useNimInfo.value() )
        dialog.nimJob.setEnabled( dialog.useNimInfo.value() )
        dialog.nimShow.setEnabled( dialog.useNimInfo.value() )
        dialog.nimShot.setEnabled( dialog.useNimInfo.value() )
        dialog.nimTask.setEnabled( dialog.useNimInfo.value() )
            
        if dialog.submitNimDraftJob.value():
            dialog.uploadToNim.setEnabled( dialog.useNimInfo.value() )
            #dialog.nimEncodeSRGB.setEnabled( dialog.useNimInfo.value() )
                    
    if dialog.submitNimDraftJob.enabled():
        dialog.uploadToNim.setEnabled( dialog.useNimInfo.value() )
        dialog.nimTemplatePath.setEnabled( dialog.submitNimDraftJob.value() )
        dialog.nimEncodeSRGB.setEnabled( dialog.nimEncodeSRGB.value() )
            
    ##########################################################################################
    ## END NIM 
    ##########################################################################################
    
    
    
    # Show the dialog.
    success = False
    while not success:
        success = dialog.ShowDialog()
        if not success:
            WriteStickySettings( dialog, configFile )
            return
        
        errorMessages = ""
        warningMessages = ""
        
        # Check that frame range is valid.
        if dialog.frameList.value().strip() == "":
            errorMessages = errorMessages + "No frame list has been specified.\n\n"
        
        # If submitting separate write nodes, make sure there are jobs to submit
        if dialog.readFileOnly.value() or dialog.selectedOnly.value():
            validNodeFound = False
            for node in writeNodes:
                if not node.knob( 'disable' ).value():
                    validNodeFound = True
                    if dialog.readFileOnly.value():
                        if node.knob( 'reading' ) and not node.knob( 'reading' ).value():
                            validNodeFound = False
                    if dialog.selectedOnly.value() and not node.isSelected():
                        validNodeFound = False
                    
                    if validNodeFound:
                        break
                    
            if not validNodeFound:
                if dialog.readFileOnly.value() and dialog.selectedOnly.value():
                    errorMessages = errorMessages + "There are no selected write nodes with 'Read File' enabled, so there are no jobs to submit.\n\n"
                elif dialog.readFileOnly.value():
                    errorMessages = errorMessages + "There are no write nodes with 'Read File' enabled, so there are no jobs to submit.\n\n"
                elif dialog.selectedOnly.value():
                    errorMessages = errorMessages + "There are no selected write nodes, so there are no jobs to submit.\n\n"
        
        # Check if at least one view has been selected.
        if dialog.chooseViewsToRender.value():
            viewCount = 0
            for vk in dialog.viewToRenderKnobs:
                if vk[0].value():
                    viewCount = viewCount + 1
                    
            if viewCount == 0:
                errorMessages = errorMessages + "There are no views selected.\n\n"
        
        # Check if the script file is local and not being submitted to Deadline.
        if not dialog.submitScene.value():
            if IsPathLocal( root.name() ):
                warningMessages = warningMessages + "Nuke script path is local and is not being submitted to Deadline:\n" + root.name() + "\n\n"
        
        # Check Draft template path
        if dialog.submitDraftJob.value():
            if not os.path.exists( dialog.templatePath.value() ):
                errorMessages += "Draft job submission is enabled, but a Draft template has not been selected (or it does not exist).  Either select a valid template, or disable Draft job submission.\n\n"
        
        if dialog.separateTasks.value() and dialog.frameListMode.value() == "Custom" and not dialog.useNodeRange.value():
            errorMessages += "Custom frame list is not supported when submitting write nodes as separate tasks. Please choose Global or Input, or enable Use Node's Frame List.\n\n"
        
        
        ##########################################################################################
        ## NIM 
        ##########################################################################################
        
        if dialog.useNimInfo.value() and dialog.nimTask.value() == "Select...":
                errorMessages += "Submit NIM Info is selected. You must select a NIM Task to Submit and/or Upload to NIM.\n\n"
        
        ##########################################################################################
        ## END NIM 
        ##########################################################################################
        
        
        # Alert the user of any errors.
        if errorMessages != "":
            errorMessages = errorMessages + "Please fix these issues and submit again."
            nuke.message( errorMessages )
            success = False
        
        # Alert the user of any warnings.
        if success and warningMessages != "":
            warningMessages = warningMessages + "Do you still wish to submit this job to Deadline?"
            answer = nuke.ask( warningMessages )
            if not answer:
                WriteStickySettings( dialog, configFile )
                return
    
    # Save sticky settings
    WriteStickySettings( dialog, configFile )
    
    tempJobName = dialog.jobName.value()
    tempDependencies = dialog.dependencies.value()
    tempFrameList = dialog.frameList.value().strip()
    tempChunkSize = dialog.chunkSize.value()
    tempIsMovie = False
    
    # Check if we should be submitting a separate job for each write node.
    if dialog.separateJobs.value():
        jobCount = 0
        previousJobId = ""
        submitThreads = []
        semaphore = threading.Semaphore()
        
        writeNodes = sorted( writeNodes, key = lambda node: node['render_order'].value() )
        
        for node in writeNodes:
            print "Now processing %s" % node.name()
            #increment job count -- will be used so not all submissions try to write to the same .job files simultaneously
            jobCount += 1
                
            # Check if we should enter the loop for this node.
            enterLoop = False
            if not node.knob( 'disable' ).value():
                enterLoop = True
                if dialog.readFileOnly.value() and node.knob( 'reading' ):
                    enterLoop = enterLoop and node.knob( 'reading' ).value()
                if dialog.selectedOnly.value():
                    enterLoop = enterLoop and node.isSelected()
            
            if enterLoop:
                tempJobName = dialog.jobName.value() + " - " + node.name()
                
                # Check if the write node is overriding the frame range
                if dialog.useNodeRange.value() and node.knob( 'use_limit' ).value():
                    tempFrameList = str(int(node.knob('first').value())) + "-" + str(int(node.knob('last').value()))
                else:
                    tempFrameList = dialog.frameList.value().strip()
                
                if IsMovie( node.knob( 'file' ).value() ):
                    tempChunkSize = 1000000
                    tempIsMovie = True
                else:
                    tempChunkSize = dialog.chunkSize.value()
                    tempIsMovie = False
                
                #if creating sequential dependencies, parse for JobId to be used for the next Job's dependencies
                if dialog.separateJobDependencies.value():
                    if jobCount > 1 and not tempDependencies == "":
                        tempDependencies = tempDependencies + "," + previousJobId
                    elif tempDependencies == "":
                        tempDependencies = previousJobId
                        
                    submitJobResults = SubmitJob( dialog, root, node, writeNodes, deadlineTemp, tempJobName, tempFrameList, tempDependencies, tempChunkSize, tempIsMovie, jobCount, semaphore )                         
                    for line in submitJobResults.splitlines():
                        if line.startswith("JobID="):
                            previousJobId = line[6:]
                            break
                    tempDependencies = dialog.dependencies.value() #reset dependencies
                else: #Create a new thread to do the submission
                    print "Spawning submission thread #%d..." % jobCount
                    submitThread = threading.Thread( None, SubmitJob, args = ( dialog, root, node, writeNodes, deadlineTemp, tempJobName, tempFrameList, tempDependencies, tempChunkSize, tempIsMovie, jobCount, semaphore ) )
                    submitThread.start()
                    submitThreads.append( submitThread )
        
        if not dialog.separateJobDependencies.value():
            print "Spawning results thread..."
            resultsThread = threading.Thread( None, WaitForSubmissions, args = ( submitThreads, ) )
            resultsThread.start()
            
    elif dialog.separateTasks.value():
        #Create a new thread to do the submission
        print "Spawning submission thread..."
        submitThread = threading.Thread( None, SubmitJob, None, ( dialog, root, None, writeNodes, deadlineTemp, tempJobName, tempFrameList, tempDependencies, tempChunkSize, tempIsMovie, 1, None ) )
        submitThread.start()
    else:
        for tempNode in writeNodes:
            if not tempNode.knob( 'disable' ).value():
                enterLoop = True
                if dialog.readFileOnly.value() and tempNode.knob( 'reading' ):
                    enterLoop = enterLoop and tempNode.knob( 'reading' ).value()
                if dialog.selectedOnly.value():
                    enterLoop = enterLoop and tempNode.isSelected()
                
                if enterLoop:
                    if IsMovie( tempNode.knob( 'file' ).value() ):
                        tempChunkSize = 1000000
                        tempIsMovie = True
                        break
        
        #Create a new thread to do the submission
        print "Spawning submission thread..."
        submitThread = threading.Thread( None, SubmitJob, None, ( dialog, root, None, writeNodes, deadlineTemp, tempJobName, tempFrameList, tempDependencies, tempChunkSize, tempIsMovie, 1, None ) )
        submitThread.start()  
    
    print "Main Deadline thread exiting"

def WaitForSubmissions( submitThreads ):
    for thread in submitThreads:
        thread.join()
    
    results = "Job submission complete. See the Script Editor output window for more information."
    nuke.executeInMainThread( nuke.message, results )
    
    print "Results thread exiting"

def GetRepositoryRoot():
    # On OSX, we look for the DEADLINE_PATH file. On other platforms, we use the environment variable.
    if os.path.exists( "/Users/Shared/Thinkbox/DEADLINE_PATH" ):
        with open( "/Users/Shared/Thinkbox/DEADLINE_PATH" ) as f: deadlineBin = f.read().strip()
        deadlineCommand = deadlineBin + "/deadlinecommand"
    else:
        try:
            deadlineBin = os.environ['DEADLINE_PATH']
        except KeyError:
            return ""
            
        if os.name == 'nt':
            deadlineCommand = deadlineBin + "\\deadlinecommand.exe"
        else:
            deadlineCommand = deadlineBin + "/deadlinecommand"
    
    startupinfo = None
    if os.name == 'nt' and hasattr( subprocess, 'STARTF_USESHOWWINDOW' ):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    proc = subprocess.Popen([deadlineCommand, "-root"], cwd=deadlineBin, stdout=subprocess.PIPE, startupinfo=startupinfo)
    
    root = proc.stdout.read()
    root = root.replace("\n","").replace("\r","")
    return root

################################################################################
## DEBUGGING
################################################################################

#~ # Get the repository root
#~ path = GetRepositoryRoot()
#~ if path != "":
    #~ path += "/submission/Nuke/Main"
    #~ path = path.replace( "\\", "/" )
    
    #~ # Add the path to the system path
    #~ if path not in sys.path :
        #~ print "Appending \"" + path + "\" to system path to import SubmitNukeToDeadline module"
        #~ sys.path.append( path )
        
    #~ # Call the main function to begin job submission.
    #~ SubmitToDeadline( path )
#~ else:
    #~ nuke.message( "The SubmitNukeToDeadline.py script could not be found in the Deadline Repository. Please make sure that the Deadline Client has been installed on this machine, that the Deadline Client bin folder is set in the DEADLINE_PATH environment variable, and that the Deadline Client has been configured to point to a valid Repository." )