###############################################################
# Andrew Sinagra
#
# custom/events/Draft.py v1.0.22
#
# 02.12.13 MODIFIED TO INCLUDE NIM 
# 06.14.13 Updated for Deadline 6
# 02.12.14 Updated for Deadline 6.1
#
###############################################################

###############################################################
## Imports
###############################################################
from System.Diagnostics import *
from System.IO import *
from System import TimeSpan

from Deadline.Events import *
from Deadline.Scripting import *
from FranticX.Utils import *

import re, sys, os, subprocess

###############################################################
## This is the function called by Deadline to get an instance of the Shotgun event listener.
###############################################################
def GetDeadlineEventListener():
    return DraftEventListener()

def CleanupDeadlineEventListener( eventListener ):
    eventListener.Cleanup()

###############################################################
## The Draft event listener class.
###############################################################
class DraftEventListener (DeadlineEventListener):
    def __init__( self ):
        self.OnJobFinishedCallback += self.OnJobFinished
    
    def Cleanup( self ):
        del self.OnJobFinishedCallback
    
    ## This is called when the job finishes rendering.
    def OnJobFinished( self, job ):
        # If this job has a DraftTemplate, submit a Draft job
        draftTemplate = job.GetJobExtraInfoKeyValue( "DraftTemplate" )
        draftTemplate = RepositoryUtils.CheckPathMapping( draftTemplate, True )
        
        if draftTemplate != "":
            ClientUtils.LogText( "Found Draft Template: '%s'" % draftTemplate )
            
            #Get all the other Draft-related KVPs
            username = job.GetJobExtraInfoKeyValue( "DraftUsername" )
            entity = job.GetJobExtraInfoKeyValue( "DraftEntity" )
            version = job.GetJobExtraInfoKeyValue( "DraftVersion" )
            width = job.GetJobExtraInfoKeyValue( "DraftFrameWidth" )
            height = job.GetJobExtraInfoKeyValue( "DraftFrameHeight" )
            uploadToShotgun = StringUtils.ParseBooleanWithDefault( job.GetJobExtraInfoKeyValue( "DraftUploadToShotgun" ), False )
            extraArgs = job.GetJobExtraInfoKeyValue( "DraftExtraArgs" )
            
            deadlineTemp = ClientUtils.GetDeadlineTempPath()
                
            outputDirectories = job.JobOutputDirectories
            outputFilenames = job.JobOutputFileNames

            if len(outputFilenames) == 0:
                raise Exception( "ERROR: Could not find an output path in Job properties; No Draft job will be created." )

            # Submit a Draft job for each output sequence.
            for i in range( 0, len(outputFilenames) ):
                outputDirectory = outputDirectories[i]
                outputFileName = outputFilenames[i]
                
                frameOffset = 0
                strFrameOffset = job.GetJobExtraInfoKeyValue( "OutputFrameOffset" + str(i) )
                if ( strFrameOffset != None and strFrameOffset != "" ):
                    try:
                        frameOffset = int( strFrameOffset )
                    except:
                        pass
                
                #some apps use '?' instead of '#' to mark frame padding
                draftInputFile = re.sub( "\?", "#", Path.GetFileName( outputFileName ) )
                
                relativeFolder = self.GetConfigEntryWithDefault( "OutputFolder", "Draft" )
                draftOutputFolder = Path.Combine( outputDirectory, relativeFolder )
                draftOutputFolder = RepositoryUtils.CheckPathMapping( draftOutputFolder, True )
                draftOutputFolder = PathUtils.ToPlatformIndependentPath( draftOutputFolder )
                
                if not Directory.Exists( draftOutputFolder ):
                    ClientUtils.LogText( "Creating output directory '%s'..." % draftOutputFolder )
                    Directory.CreateDirectory( draftOutputFolder )
                
                #remove frame padding, and strip trailing separator-type characters
                outputFileName = Path.GetFileNameWithoutExtension( draftInputFile ).replace( "#", "" ).rstrip( "_-. " )
                draftOutput = Path.Combine( draftOutputFolder, outputFileName + ".mov" )
                
                #calculate our frame list
                frames = job.Frames
                if ( frameOffset != 0 ):
                    ClientUtils.LogText( "Applying Frame Offset of %s to Frame List..." % frameOffset )
                    for i in range( 0, len(frames) ):
                        frames[i] = frames[i] + frameOffset
                        
                frameList = FrameListUtils.ToString( frames )
                
                ClientUtils.LogText( "Preparing Draft Job for output %d/%d: %s" %(i + 1, len(outputFilenames), draftOutput) )
                
                #Build the Draft submission files
                jobInfoFile = Path.Combine( deadlineTemp, "draft_event_submit_info%d.job" % i )
                fileHandle = open( jobInfoFile, "w" )
                try:
                    fileHandle.write( "Plugin=Draft\n" )
                    
                    jobName = ""
                    if len(outputFilenames) > 1:
                        jobName = ("%s (%d/%d) [DRAFT]" % (job.Name, i + 1, len(outputFilenames) ) )
                    else:
                        jobName = ( "%s [DRAFT]" % job.Name )
                    
                    fileHandle.write( "Name=%s\n" % jobName )
                    fileHandle.write( "Comment=Draft Slate and Template\n" )
                    fileHandle.write( "Department=%s\n" % job.Department )
                    fileHandle.write( "UserName=%s\n" % job.UserName )
                    fileHandle.write( "%s=%s\n" %("Frames", frameList) )
                    
                    #Assume we're creating a quicktime, set a huge chunk size & machine limit of 1
                    fileHandle.write( "ChunkSize=1000000\n" )
                    fileHandle.write( "MachineLimit=1\n" )
                    
                    pool = self.GetConfigEntryWithDefault( "DraftPool", job.Pool )
                    if pool.strip() == "":
                        pool = job.Pool
                    
                    fileHandle.write( "Pool=%s\n" % pool )
                    
                    group = self.GetConfigEntryWithDefault( "DraftGroup", job.Group )
                    if group.strip() == "":
                        group = job.Group
                    
                    fileHandle.write( "Group=%s\n" % group )
                    
                    limit = self.GetConfigEntryWithDefault( "DraftLimit", "" )
                    if limit != None and limit.strip() != "":
                        fileHandle.write( "LimitGroups=%s\n" % limit.strip() )
                    
                    #apply the draft priority offset, clamping between 0 and 100
                    priorityOffset = self.GetIntegerConfigEntryWithDefault( "PriorityOffset", 0 )
                    priority = max(0, min(100, job.Priority + priorityOffset))
                    
                    fileHandle.write( "Priority=%s\n" % priority )
                    fileHandle.write( "OnJobComplete=%s\n" % job.JobOnJobComplete )
                    fileHandle.write( "OutputFilename0=%s\n" % draftOutput )

 
#================================================================================================================================================
# NIM
#	Draft 	06.14.13
#		09.08.14	Added taskID variable to work with new upload paths
		    
                    uploadToNim = StringUtils.ParseBooleanWithDefault( job.GetJobExtraInfoKeyValue( "DraftUploadToNim" ), False )
                    nimJobID = job.GetJobExtraInfoKeyValue( "nimJobID" )
		    nimTaskID = job.GetJobExtraInfoKeyValue( "nimTaskID" )
		    DraftNimEncodeSRGB = StringUtils.ParseBooleanWithDefault( job.GetJobExtraInfoKeyValue( "DraftNimEncodeSRGB" ), False )
                    nimSrcJob = job.JobId
                    
                    ClientUtils.LogText( "Upload To Nim : %s" % str(uploadToNim))
		    ClientUtils.LogText( "NIM jobID: %s" % str(nimJobID))
		    ClientUtils.LogText( "NIM taskID %s" % str(nimTaskID))
		    ClientUtils.LogText( "NIM encode sRGB: %s" % str(DraftNimEncodeSRGB))
                    
		    if ( uploadToNim ):
                            fileHandle.write( "ExtraInfoKeyValue0=DraftUploadToNim=True\n" )
                            fileHandle.write( "ExtraInfoKeyValue1=nimJobID=%s\n" % nimJobID )
			    fileHandle.write( "ExtraInfoKeyValue2=nimTaskID=%s\n" % nimTaskID )
			    fileHandle.write( "ExtraInfoKeyValue3=DraftNimEncodeSRGB=%s\n" % DraftNimEncodeSRGB )
                            fileHandle.write( "ExtraInfoKeyValue4=nimSrcJob=%s\n" % nimSrcJob )
			    
# END NIM
#================================================================================================================================================


                finally:
                    fileHandle.close()
                
                #Build the Draft plugin info file
                pluginInfoFile = Path.Combine( deadlineTemp, "draft_event_plugin_info%d.job" % i )
                fileHandle = open( pluginInfoFile, "w" )
                try:
                    scriptArgs = []

#================================================================================================================================================
# NIM		    
		    # NIM Args #
		    DraftNimEncodeSRGB = StringUtils.ParseBooleanWithDefault( job.GetJobExtraInfoKeyValue( "DraftNimEncodeSRGB" ), False )
		    scriptArgs.append( 'nimEncodeSRGB=%s ' % DraftNimEncodeSRGB )
		    # END NIM #
# END NIM
#================================================================================================================================================
		    
                    scriptArgs.append( 'username="%s" ' % username )
                    scriptArgs.append( 'entity="%s" ' % entity )
                    scriptArgs.append( 'version="%s" ' % version )
                    
                    if width != "":
                        scriptArgs.append( 'width=%s ' % width )
                    
                    if height != "":
                        scriptArgs.append( 'height=%s ' % height )
                    
                    scriptArgs.append( 'frameList=%s ' % frameList )
                    scriptArgs.append( 'startFrame=%s ' % frames[0] )
                    scriptArgs.append( 'endFrame=%s ' % frames[-1] )
                    
                    scriptArgs.append( 'inFile="%s" ' % Path.Combine( outputDirectory, draftInputFile  ) )
                    scriptArgs.append( 'outFile="%s" ' % draftOutput )
                    scriptArgs.append( 'outFolder="%s" ' % Path.GetDirectoryName( draftOutput ) )
                    
                    scriptArgs.append( 'deadlineJobID=%s ' % job.JobId )
                    
                    regexStr = r"(\S*)\s*=\s*(\S*)"
                    replStr = r"\1=\2"
                    extraArgs = re.sub(regexStr, replStr, extraArgs)
                    
                    scriptArgs.append( extraArgs )
                    
                    fileHandle.write( "scriptfile=%s\n" % draftTemplate )
                    i = 0
                    for scriptArg in scriptArgs:
                        fileHandle.write( "ScriptArg%d=%s\n" % ( i, scriptArg ) )
                        i += 1
                    
                    #fileHandle.write( "arguments=%s\n" % scriptArgs )
                    
                    if ( uploadToShotgun ):
                        #Get the shotgun ID from the job
                        shotgunID = job.GetJobExtraInfoKeyValue( "VersionId" )
                        if ( shotgunID == "" ):
                            ClientUtils.LogText( "WARNING: Could not find an associated Shotgun Version ID.  The Draft output will not be uploaded to Shotgun." )
                        else:
                            sgScript = '"%s" Upload %s "%s"' % (Path.Combine( RepositoryUtils.GetEventsDirectory(), Path.Combine( "Shotgun", "ShotgunUtils.py" ) ), shotgunID, draftOutput)
                            fileHandle.write( "postRenderScript=%s\n" % sgScript )
                            
                finally:
                    fileHandle.close()
                
                ClientUtils.LogText( "Submitting Draft Job to Deadline: " + jobName )
                output = self.CallDeadlineCommand( [jobInfoFile, pluginInfoFile, draftTemplate] )
                ClientUtils.LogText( output )

    def CallDeadlineCommand( self, arguments ):
        deadlineBin = ClientUtils.GetBinDirectory()
        
        deadlineCommand = ""
        if os.name == 'nt':
            deadlineCommand = Path.Combine(deadlineBin, "deadlinecommandbg.exe")
        else:
            deadlineCommand = Path.Combine(deadlineBin, "deadlinecommandbg")
        
        arguments.insert(0, deadlineCommand)
        proc = subprocess.Popen(arguments, cwd=deadlineBin)
        proc.wait()
        
        outputPath = Path.Combine( ClientUtils.GetDeadlineTempPath(), "dsubmitoutput.txt" )
        output = File.ReadAllText(outputPath)
        
        return output