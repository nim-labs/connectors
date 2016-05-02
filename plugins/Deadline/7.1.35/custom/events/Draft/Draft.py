###############################################################
# Andrew Sinagra
#
# custom/events/Draft.py v7.1.23
#
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

import re, sys, os, subprocess, traceback, shlex

###############################################################
## This is the function called by Deadline to get an instance of the Draft event listener.
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

    #Utility function that creates a Deadline Job based on given parameters
    def CreateDraftJob( self, draftScript, job, jobTag, outputIndex=0, outFileNameOverride=None, draftArgs=[], shotgunMode=None ):
        #Grab the draf-related job settings
        outputFilenames = job.JobOutputFileNames

        if len( outputFilenames ) == 0:
            raise Exception( "ERROR: Could not find a full output path in Job properties; No Draft job will be created." )
        elif len( outputFilenames ) <= outputIndex:
            raise Exception( "ERROR: Output Index out of range for given Job; No Draft job will be created." )

        outputDirectories = job.JobOutputDirectories

        jobOutputFile = outputFilenames[outputIndex]
        jobOutputDir = outputDirectories[outputIndex]

        #Grab the Frame Offset (if applicable)
        frameOffset = 0
        strFrameOffset = job.GetJobExtraInfoKeyValue( "OutputFrameOffset{0}".format( outputIndex ) )
        if strFrameOffset:
            try:
                frameOffset = int( strFrameOffset )
            except:
                pass

        #calculate our frame list
        frames = []
        if frameOffset != 0:
            ClientUtils.LogText( "Applying Frame Offset of %s to Frame List..." % frameOffset )

        for frame in job.Frames:
            frames.append( frame + frameOffset )

        inputFrameList = FrameUtils.ToFrameString( frames )

        #Grab the submission-related plugin settings
        relativeFolder = self.GetConfigEntryWithDefault( "OutputFolder", "Draft" )
        draftGroup = self.GetConfigEntryWithDefault( "DraftGroup", "" ).strip()
        draftPool = self.GetConfigEntryWithDefault( "DraftPool", "" ).strip()
        draftLimit = self.GetConfigEntryWithDefault( "DraftLimit", "" ).strip()
        draftPriorityOffset = self.GetIntegerConfigEntryWithDefault( "PriorityOffset", 0 )

        if not draftGroup:
            draftGroup = job.Group

        if not draftPool:
            draftPool = job.Pool

        #TODO: Handle custom max priority?
        draftPriority = max(0, min(100, job.Priority + draftPriorityOffset))

        draftOutputFolder = Path.Combine( jobOutputDir, relativeFolder )
        draftOutputFolder = RepositoryUtils.CheckPathMapping( draftOutputFolder, True )
        draftOutputFolder = PathUtils.ToPlatformIndependentPath( draftOutputFolder )

        if not Directory.Exists( draftOutputFolder ):
            ClientUtils.LogText( "Creating output directory '%s'..." % draftOutputFolder )
            Directory.CreateDirectory( draftOutputFolder )

        #Check if we have a name override, else pull from Job
        if outFileNameOverride:
            draftOutputFile = outFileNameOverride
        else:
            jobOutputFile = re.sub( "\?", "#", Path.GetFileName( jobOutputFile ) )
            draftOutputFile = Path.GetFileNameWithoutExtension( jobOutputFile ).replace( "#", "" ).rstrip( "_-. " )
            draftOutputFile += ".mov"

        draftOutput = Path.Combine( draftOutputFolder, draftOutputFile )

        deadlineTemp = ClientUtils.GetDeadlineTempPath()
        jobInfoFile = Path.Combine( deadlineTemp, "draft_event_{0}_{1}.job".format( jobTag.replace( ' ', '_' ), outputIndex ) )
        fileHandle = open( jobInfoFile, "w" )

        try:
            fileHandle.write( "Plugin=Draft\n" )
            fileHandle.write( "Name={0} [{1}]\n".format( job.Name, jobTag ) )
            fileHandle.write( "BatchName={0}\n".format( job.BatchName ) )
            fileHandle.write( "Comment=Job Created by Draft Event Plugin\n" )
            fileHandle.write( "Department={0}\n".format( job.Department ) )
            fileHandle.write( "UserName={0}\n".format( job.UserName ) )
            fileHandle.write( "Pool={0}\n".format( draftPool ) )
            fileHandle.write( "Group={0}\n".format( draftGroup ) )
            fileHandle.write( "Priority={0}\n".format( draftPriority) )
            fileHandle.write( "OnJobComplete=%s\n" % job.JobOnJobComplete )

            if draftLimit:
                fileHandle.write( "LimitGroups={0}\n".format( draftLimit ) )

            fileHandle.write( "OutputFilename0={0}\n".format( draftOutput ) )
            fileHandle.write( "Frames=1-{0}\n".format( len( frames ) ) )
            fileHandle.write( "ChunkSize=1000000\n" )
            
            if shotgunMode:
                #Get the shotgun ID from the job
                shotgunID = job.GetJobExtraInfoKeyValue( "VersionId" )
                if ( shotgunID == "" ):
                    ClientUtils.LogText( "WARNING: Could not find an associated Shotgun Version ID.  The Draft output will not be uploaded to Shotgun." )
                else:
                    #Pull any SG info from the other job
                    fileHandle.write( "ExtraInfo0={0}\n".format( job.ExtraInfo0 ) )
                    fileHandle.write( "ExtraInfo1={0}\n".format( job.ExtraInfo1 ) )
                    fileHandle.write( "ExtraInfo2={0}\n".format( job.ExtraInfo2 ) )
                    fileHandle.write( "ExtraInfo3={0}\n".format( job.ExtraInfo3 ) )
                    fileHandle.write( "ExtraInfo4={0}\n".format( job.ExtraInfo4 ) )
                    fileHandle.write( "ExtraInfo5={0}\n".format( job.ExtraInfo5 ) )

                    #Only bother with the necessary KVPs
                    fileHandle.write( "ExtraInfoKeyValue0=VersionId={0}\n".format( shotgunID ) )
                    fileHandle.write( "ExtraInfoKeyValue1=TaskId={0}\n".format( job.GetJobExtraInfoKeyValue( 'TaskId' ) ) )
                    fileHandle.write( "ExtraInfoKeyValue2=Mode={0}\n".format( shotgunMode ) )
        

            #============================================================================================================
            # NIM
            #   Draft       DL 7.1.23
            #   03.25.15    Updated 
            
            uploadToNim = StringUtils.ParseBooleanWithDefault( job.GetJobExtraInfoKeyValue( "DraftUploadToNim" ), False )
            if uploadToNim :
                nim_jobName = job.GetJobExtraInfoKeyValue( "nim_jobName" )
                nim_jobID = job.GetJobExtraInfoKeyValue( "nim_jobID" )
                nim_taskID = job.GetJobExtraInfoKeyValue( "nim_taskID" )
                DraftNimEncodeSRGB = StringUtils.ParseBooleanWithDefault( job.GetJobExtraInfoKeyValue( "DraftNimEncodeSRGB" ), False )
                nimSrcJob = job.JobId
                
                ClientUtils.LogText( "Upload To Nim : %s" % str(uploadToNim))
                ClientUtils.LogText( "NIM jobName: %s" % str(nim_jobName))
                ClientUtils.LogText( "NIM jobID: %s" % str(nim_jobID))
                ClientUtils.LogText( "NIM taskID %s" % str(nim_taskID))
                ClientUtils.LogText( "NIM encode sRGB: %s" % str(DraftNimEncodeSRGB))
                
                fileHandle.write( "ExtraInfoKeyValue0=DraftUploadToNim=True\n" )
                fileHandle.write( "ExtraInfoKeyValue1=nim_jobName=%s\n" % nim_jobName )
                fileHandle.write( "ExtraInfoKeyValue2=nim_jobID=%s\n" % nim_jobID )
                fileHandle.write( "ExtraInfoKeyValue3=nim_taskID=%s\n" % nim_taskID )
                fileHandle.write( "ExtraInfoKeyValue4=DraftNimEncodeSRGB=%s\n" % DraftNimEncodeSRGB )
                fileHandle.write( "ExtraInfoKeyValue5=nimSrcJob=%s\n" % nimSrcJob )
                
            # END NIM
            #=============================================================================================================


        finally:
            fileHandle.close()

        #Build the Draft plugin info file
        pluginInfoFile = Path.Combine( deadlineTemp, "draft_event_plugin_info_{0}_{1}.job".format( jobTag, outputIndex ) )
        fileHandle = open( pluginInfoFile, "w" )
        try:
            #build up the script arguments
            scriptArgs = draftArgs

            #================================================================================================================================================
            # NIM
            
            DraftNimEncodeSRGB = StringUtils.ParseBooleanWithDefault( job.GetJobExtraInfoKeyValue( "DraftNimEncodeSRGB" ), False )
            scriptArgs.append( 'nimEncodeSRGB=%s ' % DraftNimEncodeSRGB )
            
            # END NIM
            #================================================================================================================================================
            
            scriptArgs.append( 'frameList=%s ' % inputFrameList )
            scriptArgs.append( 'startFrame=%s ' % frames[0] )
            scriptArgs.append( 'endFrame=%s ' % frames[-1] )
            
            scriptArgs.append( 'inFile="%s" ' % Path.Combine( jobOutputDir, jobOutputFile  ) )
            scriptArgs.append( 'outFile="%s" ' % draftOutput )
            scriptArgs.append( 'outFolder="%s" ' % Path.GetDirectoryName( draftOutput ) )

            scriptArgs.append( 'deadlineJobID=%s ' % job.JobId )

            #Write the stuff to the plugin info file
            fileHandle.write( "scriptFile=%s\n" % draftScript )

            i = 0
            for scriptArg in scriptArgs:
                fileHandle.write( "ScriptArg%d=%s\n" % ( i, scriptArg ) )
                i += 1
        finally:
            fileHandle.close()

        ClientUtils.LogText( "Submitting {0} Job to Deadline...".format( jobTag ) )
        output = self.CallDeadlineCommand( [jobInfoFile, pluginInfoFile])
        ClientUtils.LogText( output )


    
    ## This is called when the job finishes rendering.
    def OnJobFinished( self, job ):
        try:

            # if job.BatchName == "":
            #     #TODO: Should we actually do this? seems a bit jarring if the artist is actively watching their job
            #     ClientUtils.LogText( "Adding original Job to Batch '{0}'".format( job.Name ) )
            #     job.BatchName = job.Name
            #     RepositoryUtils.SaveJob( job )

            #Check if we need to generate movies to upload to Shotgun
            createShotgunMovie = (job.GetJobExtraInfoKeyValueWithDefault( "Draft_CreateSGMovie", "false" ).lower() != "false")
            if createShotgunMovie:
                #create a Draft job that will create and upload a SG quicktime
                shotgunDir = RepositoryUtils.GetEventPluginDirectory( "Shotgun" )
                self.CreateDraftJob( os.path.join( shotgunDir, "Draft_CreateShotgunMovie.py" ), job, "Shotgun H264 Movie Creation", outFileNameOverride="shotgun_h264.mov", shotgunMode="UploadMovie" )

            #Check if we need to generate a filmstrip to upload to Shotgun
            createShotgunFilmstrip = (job.GetJobExtraInfoKeyValueWithDefault( "Draft_CreateSGFilmstrip", "false" ).lower() != "false")

            if createShotgunFilmstrip:
                #create a Draft job that will create and upload a SG filmstrip
                shotgunDir = RepositoryUtils.GetEventPluginDirectory( "Shotgun" )
                self.CreateDraftJob( os.path.join( shotgunDir, "Draft_CreateShotgunFilmstrip.py" ), job, "Shotgun Filmstrip Creation", outFileNameOverride="shotgun_filmstrip.png", shotgunMode="UploadFilmstrip" )



            # If this job has a DraftTemplate, submit a Draft job per output
            draftTemplate = job.GetJobExtraInfoKeyValue( "DraftTemplate" )
            draftTemplate = RepositoryUtils.CheckPathMapping( draftTemplate, True )

            if draftTemplate != "":
                ClientUtils.LogText( "Found Draft Template: '%s'" % draftTemplate )

                #Get all the other Draft-related KVPs from the Job
                username = job.GetJobExtraInfoKeyValue( "DraftUsername" )
                entity = job.GetJobExtraInfoKeyValue( "DraftEntity" )
                version = job.GetJobExtraInfoKeyValue( "DraftVersion" )
                width = job.GetJobExtraInfoKeyValue( "DraftFrameWidth" )
                height = job.GetJobExtraInfoKeyValue( "DraftFrameHeight" )
                extraArgs = job.GetJobExtraInfoKeyValue( "DraftExtraArgs" )
                uploadToShotgun = (not createShotgunMovie) and StringUtils.ParseBooleanWithDefault( job.GetJobExtraInfoKeyValue( "DraftUploadToShotgun" ), False )

                scriptArgs = []
                scriptArgs.append( 'username="%s" ' % username )
                scriptArgs.append( 'entity="%s" ' % entity )
                scriptArgs.append( 'version="%s" ' % version )
                
                if width != "":
                    scriptArgs.append( 'width=%s ' % width )
                
                if height != "":
                    scriptArgs.append( 'height=%s ' % height )

                regexStr = r"(\S*)\s*=\s*(\S*)"
                replStr = r"\1=\2"
                extraArgs = re.sub( regexStr, replStr, extraArgs )

                tokens = shlex.split( extraArgs )
                for token in tokens:
                    scriptArgs.append( token )

                outputCount = len(job.JobOutputFileNames)
                for i in range( 0, outputCount ):
                    sgMode = None
                    if uploadToShotgun and i == 0:
                        sgMode = "UploadMovie"

                    ClientUtils.LogText( "====Submitting Job for Output {0} of {1}====".format( i + 1, outputCount ) )
                    self.CreateDraftJob( draftTemplate, job, "Draft Template", outputIndex=i, draftArgs=scriptArgs, shotgunMode=sgMode )

        except:
            ClientUtils.LogText( traceback.format_exc() )


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
