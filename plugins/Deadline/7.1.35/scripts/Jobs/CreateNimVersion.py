import os, sys, traceback, re

from Deadline.Scripting import *
from Deadline.Jobs import *

NimEvent = os.path.join( RepositoryUtils.GetEventsDirectory(), "NIM" )
import NIM as nim

########################################################################
## Main Function Called By Deadline
########################################################################
def __main__( *args ):
    try:
        NimUIPath = os.path.join( RepositoryUtils.GetEventsDirectory(), "NIM" )
        NimUIScript = os.path.join( NimUIPath, "NIM_UI.py" )
        args = ( "-executescript", NimUIScript, "DeadlineMonitor" )

        ClientUtils.LogText( "Launching UI..." )
        output = ClientUtils.ExecuteCommandAndGetOutput( args )
        ClientUtils.LogText( "UI returned." )

        outputLines = output.splitlines()

        nimKVPs = {}
        for line in outputLines:
            tokens = line.strip().split( '=', 1 )

            if len( tokens ) > 1:
                key = tokens[0]
                value = tokens[1]

                nimKVPs[key] = value

        if len( nimKVPs ) > 0:
            #we have stuff, do things!
            selectedJobs = MonitorUtils.GetSelectedJobs()

            #TODO: Handle multiple jobs?
            job = selectedJobs[0]

            # If this job has a nimJob then Log to NIM
            nim_jobName = job.GetJobExtraInfoKeyValue( "nim_jobName" )

            nim_jobPlugin = job.JobPlugin
            ClientUtils.LogText( "NIM - Plugin Type: %s" % nim_jobPlugin )
            
            if nim_jobName:
                ClientUtils.LogText( "Found NIM Job: '%s'" % nim_jobName )
                
                #Get all the other Draft-related KVPs
                self.nim_jobName = job.GetJobExtraInfoKeyValue( "nim_jobName" )
                self.nim_jobID = job.GetJobExtraInfoKeyValue( "nim_jobID" )
                self.nim_class = job.GetJobExtraInfoKeyValue( "nim_class" )
                self.nim_taskID = job.GetJobExtraInfoKeyValue( "nim_taskID" )
                self.nim_fileID = job.GetJobExtraInfoKeyValue( "nim_fileID" )
                
                #self.nim_encodeSRGB = job.GetJobExtraInfoKeyValue( "DraftNimEncodeSRGB" )
                #self.nim_elementTypeID = job.GetJobExtraInfoKeyValue( "elementTypeID" )
                self.nim_encodeSRGB = False
                self.nim_elementTypeID = 1

                ClientUtils.LogText("NIM jobID: "+self.nim_jobID )
                ClientUtils.LogText("NIM taskID: "+self.nim_taskID )

                ClientUtils.LogText("Ready to Add Render")
                nim.AddNimRender(job)
                nim.updateThumbnail(job)

            '''
            versionID = CreateFTrackVersion( job, nimKVPs )
            ClientUtils.LogText( "Created Asset Version with ID '%s'." % versionID )

            job.ExtraInfo0 = nimKVPs.get( "FT_TaskName", "" )
            job.ExtraInfo1 = nimKVPs.get( "FT_ProjectName", "" )
            job.ExtraInfo2 = nimKVPs.get( "FT_AssetName", "" )
            job.ExtraInfo3 = str( versionID )
            job.ExtraInfo4 = nimKVPs.get( "FT_Description", "" )
            job.ExtraInfo5 = nimKVPs.get( "FT_Username", "" )

            job.SetJobExtraInfoKeyValue( "FT_VersionId", str(versionID) )

            for key, value in nimKVPs.iteritems():
                job.SetJobExtraInfoKeyValue( key.strip(), value.strip() )

            ClientUtils.LogText( "Saving updated Job...")
            RepositoryUtils.SaveJob( job )
            ClientUtils.LogText( "Successfully saved updated Job.")
            '''
        else:
            ClientUtils.LogText( "No Task/Asset selected, FTrack version will not be created." )


        
    except:
        ClientUtils.LogText( "An unexpected error occurred:" )
        ClientUtils.LogText( traceback.format_exc() )


def CreateNimVersion( job, nimKVPs ):
    #Set up the environment needed to connect to FTrack
    config = RepositoryUtils.GetEventPluginConfig( "NIM" )
    nim_URL = config.GetConfigEntryWithDefault("NimURL").strip()
    ClientUtils.LogText( 'NIM URL: %s' % nim_URL)

    '''
    username = ftrackKVPs.get( "FT_Username", "" )

    os.environ["FTRACK_SERVER"] = ftrackURL
    os.environ["FTRACK_APIKEY"] = ftrackKey

    if ftrackProxy:
        os.environ["FTRACK_PROXY"] = ftrackProxy

    if username:
        os.environ["LOGNAME"] = username

    #Import FTrack API
    eggPath = ftrackPath = os.path.join( RepositoryUtils.GetEventsDirectory(), "FTrack", "API" )
    sys.path.append( eggPath )

    import ftrack
    ftrack.setup( False )

    #TODO: Handle errors in a nicer way
    projectID = ftrackKVPs.get( "FT_ProjectId", "" )
    project = ftrack.Project( id=projectID ) #Fetch project with given ID

    taskID = ftrackKVPs.get( "FT_TaskId", "" )
    task = ftrack.Task( id=taskID ) #Fetch task with given ID

    assetID = ftrackKVPs.get( "FT_AssetId", "" )
    asset = ftrack.Asset( id=assetID ) #Fetch asset with given ID

    description = ftrackKVPs.get( "FT_Description", "" )
    version = asset.createVersion( comment=description, taskid=taskID )

    #Set version status based on the Deadline Job's status
    dlStatus = job.Status
    ftStatusName = ""
    if dlStatus == JobStatus.Active:
        if job.RenderingChunks > 0:
            ftStatusName = config.GetConfigEntryWithDefault( "VersionStatusStarted", "" ).strip()
        else:
            ftStatusName = config.GetConfigEntryWithDefault( "VersionStatusQueued", "" ).strip()
    elif dlStatus == JobStatus.Failed:
        ftStatusName = config.GetConfigEntryWithDefault( "VersionStatusFailed", "" ).strip()
    elif dlStatus == JobStatus.Completed:
        ftStatusName = config.GetConfigEntryWithDefault( "VersionStatusFinished", "" ).strip()
        
        #Set the components based on the Job's output (if available)
        for i in range( len(job.OutputDirectories) ):
            outPath = os.path.normpath( job.OutputDirectories[i] )
            outPath = RepositoryUtils.CheckPathMapping( outPath, True )

            if i < len( job.OutputFileNames ):
                outPath = os.path.join( outPath, job.OutputFileNames[i] )

                #Change out our '#' padding for python-style padding, which FTrack expects
                match = re.search( "#+", outPath )
                if match:
                    padding = match.group( 0 )
                    outPath = "{0} [{1}]".format( outPath.replace( padding, "%%0%dd" % len(padding) ), job.FramesList )

            ClientUtils.LogText( "Creating Component for Deadline output '{0}'...".format( outPath ) )
            try:
                #Job's complete, so output should be present now, let FTrack pick a location for us
                version.createComponent( name=("Deadline_Output_%d" % i), path=outPath )
            except:
                #That failed =/
                ClientUtils.LogText( traceback.format_exc() )
                ClientUtils.LogText( "Failed to create component for output '%s'. No component will be created." % outPath )

        ClientUtils.LogText( "Done creating Components." )
    


    if ftStatusName:
        statuses = project.getVersionStatuses()

        ftStatus = None
        for status in statuses:
            if status.getName().lower() == ftStatusName.lower():
                ftStatus = status
                break

        if ftStatus == None:
            ClientUtils.LogText( "Could not find valid Asset Version Status with name '%s'.  The Version Status might not be set properly." % ftStatusName )
        else:
            ClientUtils.LogText( "Setting Asset Version to status '%s'." % ftStatusName )
            version.setStatus( ftStatus )

    version.publish()
    '''
    
    ClientUtils.LogText(" Done ")
    
    #return version.getId()
    nim_render_id = 0
    return nim_render_id

