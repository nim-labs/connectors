/*
Copyright (c) 2015, NIM Labs LLC
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
*/
{
	// NIM Modified - Andrew Sinagra - 15.06.02
	// Deadline 7.1.0.35

	// The global variable that will hold the AE sticky settings filename.
	var AfterEffectsIniFilename = "";
	
	/**************** CHECKS ****************/
	var safeToRunScript = true;
	var tempFolder = "";
	//Check 0 - Ensure the client file is installed
    if( typeof sentinal === 'undefined')
    {
        alert("Client script not installed or was not run. Please copy the script from your Deadline Repository (submission/AfterEffects/Client/DeadlineAfterEffectsClient.jsx) to your After Effects installation folder (Support Files/Scripts), and make sure to run that client script and not the main script found in the repository.");
        safeToRunScript = false
    }
	// Check 1 - Ensure a project is open
    if ( safeToRunScript )
	{
        safeToRunScript = app.project != null;
        if( ! app.project )
            alert( "A project must be open to run this script." );
	}
	// Check 2 - Ensure the project has been saved in the past
	if( safeToRunScript )
	{
		if( ! app.project.file )
		{
			alert ( "This project must be saved before running this script." );
			safeToRunScript = false;
		}
		else
			app.project.save( app.project.file );
	}
	
	// Check 3 - Ensure that at least 1 comp is queued, or that at least 1 layer is selected
	if( safeToRunScript )
	{
		var queuedCount = GetQueuedCompCount();
		
		var activeComp = app.project.activeItem;
		
		if( queuedCount == 0 && activeComp != null && activeComp.length == 0 )
		{
			safeToRunScript = false;
			alert( "You do not have any items set to render and do not have any selected layers in the active composition." );
		}
	}
	
	// Check 4 - Ensure that no 2 comps in the Render Queue have the same name
	if( safeToRunScript )
	{
		var compItem1;
		var compItem2;
		for( i = 1; i < app.project.renderQueue.numItems; ++i )
		{
			compItem1 = app.project.renderQueue.item( i ).comp;
			for( j = i + 1; j <= app.project.renderQueue.numItems; ++j )
			{
				if( app.project.renderQueue.item( j ).status != RQItemStatus.QUEUED )
					continue;
				
				compItem2 = app.project.renderQueue.item( j ).comp;
				if( compItem1.name == compItem2.name )
				{
					safeToRunScript = false;
					break;
				}
			}
			if( ! safeToRunScript )
				break;
		}
		if( ! safeToRunScript )
			alert( "At least 2 of your items in the Render Queue have the same name. Please ensure that all of your items have unique names." );
	}
	 
	// Check 5 - Ensure were are running at least version 8 (CS3)
	if( safeToRunScript )
	{
		var version = app.version.substring( 0, app.version.indexOf( 'x' ) );
		while( version.indexOf( '.' ) != version.lastIndexOf( '.' ) )
			version = version.substring( 0, version.lastIndexOf( '.' ) );
			
			if( parseInt( version ) < 8 )
				safeToRunScript = false;
				
		if( ! safeToRunScript )
			alert( "This script only supports After Effects CS3 and later." );
	}
	
	/**************** PROCESSING ****************/
	// Collect all the parameters required to render the comps in the Render Queue
	if( safeToRunScript )
	{
		var compName;           // comp to be rendered
		var outputPath;         // full path to output rendered comp
		var startFrame;         // frame to start rendering at
		var endFrame;           // frame to stop rendering at
		var version;            // after effects major and minor version
		var movieFormat;        // boolean -- T if output is a movie format
		
		var index;              // used to get the file's prefix and extension
		var outputFile;         // used to get the file's prefix and extension
		var outputPrefix;       // the output file's prefix
		var outputExt;          // the output file's extension
		
		tempFolder = callDeadlineCommand( "GetCurrentUserHomeDirectory" ).replace("\r","").replace("\n","")
		if (system.osName == "MacOS")
			tempFolder = tempFolder + "/temp/";
		else
			tempFolder = tempFolder + "\\temp\\";
		Folder( tempFolder ).create();
		
		// file paths
		var projectName = app.project.file.name;
		var projectPath = app.project.file.fsName;
		
		// version
		var version = app.version.substring( 0, app.version.indexOf( 'x' ) );
		while( version.indexOf( '.' ) != version.lastIndexOf( '.' ) )
			version = version.substring( 0, version.lastIndexOf( '.' ) );
		
		SubmitToDeadline( projectName, projectPath, version )
	}
	
	//Calls deadline with the given arguments.  Checks the OS and calls DeadlineCommand appropriately.
	function callDeadlineCommand( args )
	{
		var commandLine = "";
		
		//On OSX, we look for the DEADLINE_PATH file. On other platforms, we use the environment variable.
		if (system.osName == "MacOS")
		{
			var deadlinePathFile = File( "/Users/Shared/Thinkbox/DEADLINE_PATH" );
			if( deadlinePathFile.exists )
			{
				deadlinePathFile.open( "r" );
				deadlineBin = deadlinePathFile.read().replace( "\n","" ).replace( "\r", "" );
				deadlinePathFile.close();
				
				commandLine = "\"" + deadlineBin + "/deadlinecommand\" ";
			}
			else
				commandLine = "deadlinecommand ";
		}
		else
		{
			deadlineBin = system.callSystem( "cmd.exe /c \"echo %DEADLINE_PATH%\"" ).replace( "\n","" ).replace( "\r", "" );
			commandLine = "\"" + deadlineBin + "\\deadlinecommand.exe\" ";
		}
		
		commandLine = commandLine + args;
		
		result = system.callSystem(commandLine);
		
		if( system.osName == "MacOS" )
		{
			result = cleanUpResults( result, "Could not set X local modifiers" );
			result = cleanUpResults( result, "Could not find platform independent libraries" );
			result = cleanUpResults( result, "Could not find platform dependent libraries" );
			result = cleanUpResults( result, "Consider setting $PYTHONHOME to" );
			result = cleanUpResults( result, "using built-in colorscheme" );
		}
		
		//result = result.replace("\n", "");
		//result = result.replace("\r", "");
		return result;
	}
	
	// Looks for the given txt in result, and if found, that line and all previous lines are removed.
	function cleanUpResults( result, txt )
	{
		newResult = result;
		
		txtIndex = result.indexOf( txt );
		if( txtIndex >= 0 )
		{
			eolIndex = result.indexOf( "\n", txtIndex );
			if( eolIndex >= 0 )
				newResult = result.substring( eolIndex + 1 );
		}
		
		return newResult;
	}
	
	// Submits a job to Deadline.
	function SubmitToDeadline( projectName, projectPath, version )
	{
		var startFrame = 0;
		var endFrame = 0;
		for( i = 1; i <= app.project.renderQueue.numItems; ++i )
		{
			if( app.project.renderQueue.item( i ).status != RQItemStatus.QUEUED )
				continue;
			
			// get the frame duration and start/end times
			var frameDuration = app.project.renderQueue.item( i ).comp.frameDuration;
			var frameOffset = app.project.displayStartFrame;
			var displayStartTime = app.project.renderQueue.item( i ).comp.displayStartTime;
			if( displayStartTime == undefined )
			{
				// After Effects 6.0
				startFrame = frameOffset + Math.round( app.project.renderQueue.item( i ).comp.workAreaStart / frameDuration );
				endFrame = startFrame + Math.round( app.project.renderQueue.item( i ).comp.workAreaDuration / frameDuration ) - 1;
			}
			else
			{
				// After Effects 6.5 +
				// This gets the frame range from what's specified in the render queue, instead of just the comp settings.
				startFrame = frameOffset + Math.round( displayStartTime / frameDuration ) + Math.round( app.project.renderQueue.item( i ).timeSpanStart / frameDuration );
				endFrame = startFrame + Math.round( app.project.renderQueue.item( i ).timeSpanDuration / frameDuration ) - 1;
			}
			
			break;
		}
		
		//If you couldn't grab it from render queue, take from active comp
		if ( startFrame == 0 && endFrame == 0 )
		{
			activeComp = app.project.activeItem;
			
			if ( activeComp != null )
			{
				//get the frame offset & duration
				var frameOffset = app.project.displayStartFrame;
				var frameDuration = activeComp.frameDuration;
				
				startFrame = frameOffset + Math.round( activeComp.workAreaStart / frameDuration );
				endFrame = startFrame + Math.round( activeComp.workAreaDuration / frameDuration ) - 1;
			}
		}
		
		var tabbedView = (parseInt( version ) > 8);
		var queuedCount = GetQueuedCompCount();
		
		var initUseCompName = parseBool( getIniSetting( "UseCompName", "false" ) );
		var initDepartment = getIniSetting( "Department", "" );
		var initGroup = getIniSetting( "Group", "none" );
		var initPool = getIniSetting( "Pool", "none" );
        var initSecondaryPool = getIniSetting( "SecondaryPool", "" );
		var initPriority = parseInt( getIniSetting( "Priority", "50" ) );
		var initMachineLimit = parseInt( getIniSetting( "MachineLimit", 0 ) );
		var initLimitGroups = getIniSetting( "LimitGroups", "" );
		var initMachineList = getIniSetting( "MachineList", "" );
		var initIsBlacklist = parseBool( getIniSetting( "IsBlacklist", "false" ) );
		var initSubmitSuspended = parseBool( getIniSetting( "SubmitSuspended", "false" ) );
		var initOnComplete = "Nothing";
		var initChunkSize = parseInt( getIniSetting( "ChunkSize", "1" ) );
		var initSubmitScene = parseBool( getIniSetting( "SubmitScene", "false" ) );
		var initMultiProcess = parseBool( getIniSetting( "MultiProcess", "false" ) );
		var initMissingFootage = parseBool( getIniSetting( "MissingFootage", "false" ) );
		var initExportAsXml = parseBool( getIniSetting( "ExportAsXml", "false" ) );
		var initUseCompFrameRange = parseBool( getIniSetting( "UseCompFrame", "false" ) );
		var initFirstAndLast = parseBool( getIniSetting( "First And Last", "false" ) );
		var initIgnoreMissingLayers = parseBool( getIniSetting( "MissingLayers", "false" ) );
		var initIgnoreMissingEffects = parseBool( getIniSetting( "MissingEffects", "false" ) );
		var initFailOnWarnings = parseBool( getIniSetting( "FailOnWarnings", "false" ) );
		var initDependentComps = parseBool( getIniSetting( "DependentComps", "false" ) );
		var initSubmitEntireQueue = parseBool( getIniSetting( "SubmitEntireQueue", "false" ) );
		var initLocalRendering = parseBool( getIniSetting( "LocalRendering", "false" ) );   
        var initOverrideFailOnExistingAEProcess = parseBool( getIniSetting( "OverrideFailOnExistingAEProcess", "false" ) );
        var initFailOnExistingAEProcess = parseBool( getIniSetting ( "FailOnExistingAEProcess", "false" ) );

		var initMultiMachine = parseBool( getIniSetting( "MultiMachine", "false" ) );
		var initMultiMachineTasks = parseInt( getIniSetting( "MultiMachineTasks", "10" ) );
		var initFileSize = parseInt(getIniSetting( "FileSize", 0));
		var initMemoryManagement = parseBool( getIniSetting( "MemoryManagement", "false" ) );
		var initImageCachePercentage = parseInt( getIniSetting( "ImageCachePercentage", 100 ) );
		var initMaxMemoryPercentage = parseInt( getIniSetting( "MaxMemoryPercentage", 100 ) );
		var initUseDraft = parseBool( getIniSetting( "UseDraft", "false" ) );
		var initDraftTemplate = getIniSetting( "DraftTemplate", "" );
		var initDraftUser = getIniSetting( "DraftUser", "" );
		var initDraftEntity = getIniSetting( "DraftEntity", "" );
		var initDraftVersion = getIniSetting( "DraftVersion", "" );
		var initDraftExtraArgs = getIniSetting( "DraftExtraArgs", "");
		
		// If not in tabbed view, set these to their defaults since they aren't shown to the user.
		if( !tabbedView )
		{
			initMultiMachine = false;
			initMultiMachineTasks = 10;
			initFileSize = 0;
			initMemoryManagement = false;
			initImageCachePercentage = 100;
			initMaxMemoryPercentage = 100;
			initUseDraft = false;
			initDraftTemplate = "";
			initDraftUser = "";
			initDraftEntity = "";
			initDraftVersion = "";
			initDraftExtraArgs = "";
		}
		
		var initConcurrentTasks = 1;
		var initTaskTimeout = 0;
		
		var sanityScriptPath;
		if (system.osName == "MacOS")
			sanityScriptPath = root + "/submission/AfterEffects/Main/CustomSanityChecks.jsx";
		else
			sanityScriptPath = root + "\\submission\\AfterEffects\\Main\\CustomSanityChecks.jsx";
		
		// If there is a custom sanity script, run it before displaying the submission window.
		var sanityFile = File( sanityScriptPath );
		if( sanityFile.exists )
		{
			sanityFile.open( "r" );
			eval( sanityFile.read() );
			sanityFile.close();
		}
		
		labelSize = [120, 20];
		textSize = [500, 18];
		shortTextSize = [160, 18];
		browseTextSize = [456, 18];
		comboSize = [160, 20];
		shortComboSize = [160, 20];
		buttonSize = [36, 20];
		sliderSize = [336, 20];
		checkBoxASize = [320, 20];
		checkBoxBSize = [200, 20];
		checkBoxCSize = [250, 20];
        checkBoxDSize = [175, 20];
		
		// Create the dialog
		dialog = new Window( 'dialog', 'Submit After Effects To Deadline' );
		
		// Tabbed views aren't supported in CS3 or earlier, so here's some magic to only show the first tab without breaking anything.
		if( tabbedView )
		{
			// Create the tab control and the general tab
			dialog.tabPanel = dialog.add( 'tabbedpanel', undefined );
			dialog.generalTab = dialog.tabPanel.add( 'tab', undefined, 'General' );
		}
		else
		{
			dialog.generalTab = dialog.add( 'panel', undefined );
		}
		
		// Job Description Section
		dialog.descPanel = dialog.generalTab.add( 'panel', undefined, 'Job Description' );
		dialog.descPanel.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		
		// Job Name
		dialog.jobNameGroup = dialog.descPanel.add( 'group', undefined );
		dialog.jobNameGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.jobNameLabel = dialog.jobNameGroup.add( 'statictext', undefined, 'Job Name' );
		dialog.jobNameLabel.size = labelSize;
		dialog.jobNameLabel.helpTip = 'The name of your job. This is optional, and if left blank, it will default to "Untitled". Disabled if Use Comp Name is enabled.';
		dialog.jobName = dialog.jobNameGroup.add( 'edittext', undefined, replaceAll( projectName, "%20", " " ) );
		dialog.jobName.size = textSize;
		dialog.jobName.enabled = !initUseCompName;
		
		dialog.useCompNameGroup = dialog.descPanel.add( 'group', undefined );
		dialog.useCompNameGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.useCompNameLabel = dialog.useCompNameGroup.add( 'statictext', undefined, '' );
		dialog.useCompNameLabel.size = labelSize;
		dialog.useCompName = dialog.useCompNameGroup.add( 'checkbox', undefined, 'Use Comp Name As Job Name' );
		dialog.useCompName.helpTip = "If enabled, the job's name will be the Comp name.";
		dialog.useCompName.value = initUseCompName;
		
		dialog.useCompName.onClick = function()
		{
			dialog.jobName.enabled = !this.value;
		}
		
		// Comment
		dialog.commentGroup = dialog.descPanel.add( 'group', undefined );
		dialog.commentGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.commentLabel = dialog.commentGroup.add( 'statictext', undefined, 'Comment' );
		dialog.commentLabel.size = labelSize;
		dialog.commentLabel.helpTip = 'A simple description of your job. This is optional and can be left blank.';
		dialog.comment = dialog.commentGroup.add( 'edittext', undefined, '' );
		dialog.comment.size = textSize;
		
		// Department
		dialog.departmentGroup = dialog.descPanel.add( 'group', undefined );
		dialog.departmentGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.departmentLabel = dialog.departmentGroup.add( 'statictext', undefined, 'Department' );
		dialog.departmentLabel.size = labelSize;
		dialog.departmentLabel.helpTip = 'The department you belong to. This is optional and can be left blank.';
		dialog.department = dialog.departmentGroup.add( 'edittext', undefined, initDepartment );
		dialog.department.size = textSize;
		
		// Job Scheduling Section
		dialog.schedPanel = dialog.generalTab.add( 'panel', undefined, 'Job Scheduling' );
		dialog.schedPanel.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		
		// Pool
		dialog.poolGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.poolGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.poolLabel = dialog.poolGroup.add( 'statictext', undefined, 'Pool' );
		dialog.poolLabel.size = labelSize;
		dialog.poolLabel.helpTip = 'The pool that your job will be submitted to.';
		dialog.pool = dialog.poolGroup.add( 'dropdownlist', undefined );
		dialog.pool.size = comboSize;
		
		var poolString = callDeadlineCommand( "-pools" );
		var pools = deadlineStringToArray( poolString );
		
		var selectedIndex = -1;
		for( var i = 0; i < pools.length; i ++ )
		{
			if( pools[i] == initPool )
				selectedIndex = i;
			
			dialog.pool.add( 'item', pools[i] );
		}
		
		if( selectedIndex >= 0 )
			dialog.pool.selection = dialog.pool.items[selectedIndex];
		else if( dialog.pool.items.length > 0 )
			dialog.pool.selection = dialog.pool.items[0];

        // Secondary Pool
		dialog.secondaryPoolGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.secondaryPoolGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.secondaryPoolLabel = dialog.secondaryPoolGroup.add( 'statictext', undefined, 'Secondary Pool' );
		dialog.secondaryPoolLabel.size = labelSize;
		dialog.secondaryPoolLabel.helpTip = 'The secondary pool lets you specify a Pool to use if the primary Pool does not have any available Slaves.';
		dialog.secondaryPool = dialog.secondaryPoolGroup.add( 'dropdownlist', undefined );
		dialog.secondaryPool.size = comboSize;
        
        var secondaryPools = pools.slice(0);
        secondaryPools.splice(0, 0, "" );
		
		var selectedIndex = -1;
		for( var i = 0; i < secondaryPools.length; i ++ )
		{
			if( secondaryPools[i] == initSecondaryPool )
				selectedIndex = i;
			
			dialog.secondaryPool.add( 'item', secondaryPools[i] );
		}
		
		if( selectedIndex >= 0 )
			dialog.secondaryPool.selection = dialog.secondaryPool.items[selectedIndex];
		else if( dialog.secondaryPool.items.length > 0 )
			dialog.secondaryPool.selection = dialog.secondaryPool.items[0];
        
		// Group
		dialog.groupGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.groupGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.groupLabel = dialog.groupGroup.add( 'statictext', undefined, 'Group' );
		dialog.groupLabel.size = labelSize;
		dialog.groupLabel.helpTip = 'The group that your job will be submitted to.';
		dialog.group = dialog.groupGroup.add( 'dropdownlist', undefined, '' );
		dialog.group.size = comboSize;
		
		var groupString = callDeadlineCommand( "-groups" );
		var groups = deadlineStringToArray( groupString );
		
		var selectedIndex = -1;
		for( var i = 0; i < groups.length; i ++ )
		{		
			if( groups[i] == initGroup )
				selectedIndex = i;
			
			dialog.group.add( 'item', groups[i] );
		}
		
		if( selectedIndex >= 0 )
			dialog.group.selection = dialog.group.items[selectedIndex];
		else if( dialog.group.items.length > 0 )
			dialog.group.selection = dialog.group.items[0];
		
		// Priority
		var maximumPriorityString = callDeadlineCommand( "-getmaximumpriority" );
		var maximumPriority = parseInt(maximumPriorityString);
		if( initPriority > maximumPriority )
			initPriority = Math.round( maximumPriority / 2 );
		
		dialog.priorityGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.priorityGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.priorityLabel = dialog.priorityGroup.add( 'statictext', undefined, 'Priority' );
		dialog.priorityLabel.size = labelSize;
		dialog.priorityLabel.helpTip = 'A job can have a numeric priority range, with 0 being the lowest priority.';
		dialog.priority = dialog.priorityGroup.add( 'edittext', undefined, initPriority );
		dialog.priority.size = shortTextSize;
		
		dialog.priority.onChange = function()
		{
			setSliderValue( this.text, 0, maximumPriority, dialog.prioritySlider )
			this.text = Math.round( dialog.prioritySlider.value ); 
		}
		dialog.prioritySlider = dialog.priorityGroup.add( 'slider', undefined, initPriority, 0, maximumPriority );
		dialog.prioritySlider.onChange = function() { dialog.priority.text = Math.round( this.value ); }
		dialog.prioritySlider.size = sliderSize;
		
		// Machine Limit
		dialog.machineLimitGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.machineLimitGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.machineLimitLabel = dialog.machineLimitGroup.add( 'statictext', undefined, 'Machine Limit' );
		dialog.machineLimitLabel.size = labelSize;
		dialog.machineLimitLabel.helpTip = 'Use the Machine Limit to specify the maximum number of machines that can render your job at one time. Specify 0 for no limit.';
		dialog.machineLimitLabel.enabled = !initMultiMachine;
		dialog.machineLimit = dialog.machineLimitGroup.add( 'edittext', undefined, initMachineLimit );
		dialog.machineLimit.size = shortTextSize;
		dialog.machineLimit.enabled = !initMultiMachine;
		dialog.machineLimit.onChange = function()
		{
			setSliderValue( this.text, 0, 9999, dialog.machineLimitSlider )
			this.text = Math.round( dialog.machineLimitSlider.value ); 
		}
		dialog.machineLimitSlider = dialog.machineLimitGroup.add( 'slider', undefined, initMachineLimit, 0, 9999 );
		dialog.machineLimitSlider.onChange = function() { dialog.machineLimit.text = Math.round( this.value ); }
		dialog.machineLimitSlider.size = sliderSize;
		dialog.machineLimitSlider.enabled = !initMultiMachine;

		// Concurrent Tasks
		dialog.concurrentTasksGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.concurrentTasksGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.concurrentTasksLabel = dialog.concurrentTasksGroup.add( 'statictext', undefined, 'Concurrent Tasks' );
		dialog.concurrentTasksLabel.size = labelSize;
		dialog.concurrentTasksLabel.helpTip = 'The number of tasks that can render concurrently on a single slave. This is useful if the rendering application only uses one thread to render and your slaves have multiple CPUs.';
		dialog.concurrentTasks = dialog.concurrentTasksGroup.add( 'edittext', undefined, initConcurrentTasks );
		dialog.concurrentTasks.size = shortTextSize;
		dialog.concurrentTasks.onChange = function()
		{
			setSliderValue( this.text, 1, 16, dialog.concurrentTasksSlider )
			this.text = Math.round( dialog.concurrentTasksSlider.value ); 
		}
		dialog.concurrentTasksSlider = dialog.concurrentTasksGroup.add( 'slider', undefined, initConcurrentTasks, 1, 16 );
		dialog.concurrentTasksSlider.onChange = function() { dialog.concurrentTasks.text = Math.round( this.value ); }
		dialog.concurrentTasksSlider.size = sliderSize;
		
		// Task Timeout
		dialog.taskTimeoutGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.taskTimeoutGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.taskTimeoutLabel = dialog.taskTimeoutGroup.add( 'statictext', undefined, 'Task Timeout' );
		dialog.taskTimeoutLabel.size = labelSize;
		dialog.taskTimeoutLabel.helpTip = 'The number of minutes a slave has to render a task for this job before it requeues it. Specify 0 for no limit.';
		dialog.taskTimeout = dialog.taskTimeoutGroup.add( 'edittext', undefined, initTaskTimeout );
		dialog.taskTimeout.size = shortTextSize;
		dialog.taskTimeout.onChange = function()
		{
			setSliderValue( this.text, 0, 9999, dialog.taskTimeoutSlider )
			this.text = Math.round( dialog.taskTimeoutSlider.value ); 
		}
		dialog.taskTimeoutSlider = dialog.taskTimeoutGroup.add( 'slider', undefined, 0, 0, 9999 );
		dialog.taskTimeoutSlider.onChange = function() { dialog.taskTimeout.text = Math.round( this.value ); }
		dialog.taskTimeoutSlider.size = sliderSize;
		
		// Limit Groups
		dialog.limitGroupsGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.limitGroupsGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.limitGroupsLabel = dialog.limitGroupsGroup.add( 'statictext', undefined, 'Limits' );
		dialog.limitGroupsLabel.size = labelSize;
		dialog.limitGroupsLabel.helpTip = 'The Limits that your job requires.';
		dialog.limitGroups = dialog.limitGroupsGroup.add( 'edittext', undefined, initLimitGroups );
		dialog.limitGroups.size = browseTextSize;
		dialog.limitGroupsButton = dialog.limitGroupsGroup.add( 'button', undefined, "..." );
		dialog.limitGroupsButton.size = buttonSize;
		dialog.limitGroupsButton.onClick = function()
		{
			var origValue = dialog.limitGroups.text;
			var newValue = callDeadlineCommand( "-selectlimitgroups \"" + origValue + "\"" ).replace( "\n", "" ).replace( "\r", "" );
			if( newValue.indexOf( "Action was cancelled by user" ) == -1 )
				dialog.limitGroups.text = newValue;
		}
			
		// Dependencies
		dialog.dependenciesGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.dependenciesGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.dependenciesLabel = dialog.dependenciesGroup.add( 'statictext', undefined, 'Dependencies' );
		dialog.dependenciesLabel.size = labelSize;
		dialog.dependenciesLabel.helpTip = 'Specify existing jobs that this job will be dependent on. This job will not start until the specified dependencies finish rendering. ';
		dialog.dependencies = dialog.dependenciesGroup.add( 'edittext', undefined );
		dialog.dependencies.size = browseTextSize;
		dialog.dependenciesButton = dialog.dependenciesGroup.add( 'button', undefined, "..." );
		dialog.dependenciesButton.size = buttonSize;
		dialog.dependenciesButton.onClick = function()
		{
			var origValue = dialog.dependencies.text;
			var newValue = callDeadlineCommand( "-selectdependencies \"" + origValue + "\"" ).replace( "\n", "" ).replace( "\r", "" );
			if( newValue.indexOf( "Action was cancelled by user" ) == -1 )
				dialog.dependencies.text = newValue;
		}
		
		// Machine List
		dialog.machineListGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.machineListGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.machineListLabel = dialog.machineListGroup.add( 'statictext', undefined, 'Machine List' );
		dialog.machineListLabel.size = labelSize;
		dialog.machineListLabel.helpTip = 'Specify the machine list. This can be a whitelist or a blacklist.';
		dialog.machineList = dialog.machineListGroup.add( 'edittext', undefined, initMachineList );
		dialog.machineList.size = browseTextSize;
		dialog.machineListButton = dialog.machineListGroup.add( 'button', undefined, "..." );
		dialog.machineListButton.size = buttonSize;
		dialog.machineListButton.onClick = function()
		{
			var origValue = dialog.machineList.text;
			var newValue = callDeadlineCommand( "-selectmachinelist \"" + origValue + "\"" ).replace( "\n", "" ).replace( "\r", "" );
			if( newValue.indexOf( "Action was cancelled by user" ) == -1 )
				dialog.machineList.text = newValue;
		}
		
		// On Job Complete and Submit Suspended
		dialog.onCompleteGroup = dialog.schedPanel.add( 'group', undefined );
		dialog.onCompleteGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.onCompleteLabel = dialog.onCompleteGroup.add( 'statictext', undefined, 'On Job Complete' );
		dialog.onCompleteLabel.size = labelSize;
		dialog.onCompleteLabel.helpTip = 'If desired, you can automatically archive or delete the job when it completes. ';
		dialog.onComplete = dialog.onCompleteGroup.add( 'dropdownlist', undefined, '' );
		dialog.onComplete.size = shortComboSize;
		
		onCompletes = new Array( 3 );
		onCompletes[0] = "Nothing";
		onCompletes[1] = "Archive";
		onCompletes[2] = "Delete";
		
		for( var i = 0; i < onCompletes.length; i ++ )
			dialog.onComplete.add( 'item', onCompletes[i] );
		dialog.onComplete.selection = dialog.onComplete.items[0];
		
		dialog.submitSuspended = dialog.onCompleteGroup.add( 'checkbox', undefined, 'Submit As Suspended' );
		dialog.submitSuspended.helpTip = 'If enabled, the job will submit in the suspended state. This is useful if you do not want the job to start rendering right away. Just resume it from the Monitor when you want it to render.';
		dialog.submitSuspended.value = initSubmitSuspended;
		
		dialog.isBlacklist = dialog.onCompleteGroup.add( 'checkbox', undefined, 'Machine List is a Blacklist' );
		dialog.isBlacklist.helpTip = 'If enabled, the specified machine list will be a blacklist. Otherwise, it is a whitelist';
		dialog.isBlacklist.value = initIsBlacklist;
		
		// After Effects Options Section
		dialog.aeOptionsPanel = dialog.generalTab.add( 'panel', undefined, 'After Effects Options' );
		dialog.aeOptionsPanel.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		
		// Frame List
		dialog.frameListGroup = dialog.aeOptionsPanel.add( 'group', undefined );
		dialog.frameListGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.frameListLabel = dialog.frameListGroup.add( 'statictext', undefined, 'Frame List' );
		dialog.frameListLabel.size = labelSize;
		dialog.frameListLabel.enabled = !initSubmitEntireQueue && !initMultiMachine;
		dialog.frameListLabel.helpTip = 'The list of frames to render.';
		dialog.frameList = dialog.frameListGroup.add( 'edittext', undefined, startFrame + "-" + endFrame );
		dialog.frameList.size = shortTextSize;
		dialog.frameList.enabled = !initUseCompFrameRange && !initSubmitEntireQueue && !initMultiMachine;
		dialog.useCompFrameList = dialog.frameListGroup.add( 'checkbox', undefined, 'Use Frame List From The Comp' );
		dialog.useCompFrameList.value = initUseCompFrameRange;
		dialog.useCompFrameList.enabled = !initSubmitEntireQueue && !initMultiMachine;
		dialog.useCompFrameList.helpTip = 'If enabled, the Comp\'s frame list will be used instead of the frame list in this submitter.';
		dialog.useCompFrameList.onClick = function()
		{
			dialog.frameList.enabled = !this.value && !dialog.submitEntireQueue.value && !dialog.multiMachine.value;
			dialog.firstAndLast.enabled = this.value && !dialog.submitEntireQueue.value && !dialog.multiMachine.value;
		}
		
		// Task Group Size
		dialog.chunkSizeGroup = dialog.aeOptionsPanel.add( 'group', undefined );
		dialog.chunkSizeGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.chunkSizeLabel = dialog.chunkSizeGroup.add( 'statictext', undefined, 'Frames Per Task' );
		dialog.chunkSizeLabel.size = labelSize;
		dialog.chunkSizeLabel.enabled = !initSubmitEntireQueue && !initMultiMachine;
		dialog.chunkSizeLabel.helpTip = 'This is the number of frames that will be rendered at a time for each job task.';
		dialog.chunkSize = dialog.chunkSizeGroup.add( 'edittext', undefined, initChunkSize );
		dialog.chunkSize.size = shortTextSize;
		dialog.chunkSize.enabled = !initSubmitEntireQueue && !initMultiMachine;
		dialog.chunkSize.onChange = function()
		{
			setSliderValue( this.text, 1, 100000, dialog.chunkSizeSlider )
			this.text = Math.round( dialog.chunkSizeSlider.value ); 
		}
		dialog.chunkSizeSlider = dialog.chunkSizeGroup.add( 'slider', undefined, initChunkSize, 1, 100000 );
		dialog.chunkSizeSlider.onChange = function() { dialog.chunkSize.text = Math.round( this.value ); }
		dialog.chunkSizeSlider.size = sliderSize;
		dialog.chunkSizeSlider.enabled = !initSubmitEntireQueue && !initMultiMachine;
		
		// Comps are dependent
		dialog.dependentCompsGroup = dialog.aeOptionsPanel.add( 'group', undefined );
		dialog.dependentCompsGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.dependentComps = dialog.dependentCompsGroup.add( 'checkbox', undefined, 'Comps Are Dependent On Previous Comps' );
		dialog.dependentComps.value = initDependentComps;
		dialog.dependentComps.enabled = (queuedCount > 1) && !initSubmitEntireQueue;
		dialog.dependentComps.size = checkBoxCSize;
		dialog.dependentComps.helpTip = 'If enabled, the job for each comp in the render queue will be dependent on the job for the comp ahead of it. This is useful if a comp in the render queue uses footage rendered by a comp ahead of it.';
		dialog.firstAndLast = dialog.dependentCompsGroup.add( 'checkbox', undefined, 'Render First And Last Frames Of The Comp First' );
		dialog.firstAndLast.value = initFirstAndLast;
		dialog.firstAndLast.enabled = initUseCompFrameRange && !initSubmitEntireQueue && !initMultiMachine;
		dialog.firstAndLast.helpTip = 'If using the Comp\'s frame list, you can enable this so that the job renders the first and last frames first.';
		
		// Submit Entire Render Queue
		dialog.submitEntireQueueGroup = dialog.aeOptionsPanel.add( 'group', undefined );
		dialog.submitEntireQueueGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.submitEntireQueue = dialog.submitEntireQueueGroup.add( 'checkbox', undefined, 'Submit Entire Render Queue As One Job' );
		dialog.submitEntireQueue.value = initSubmitEntireQueue;
		dialog.submitEntireQueue.size = checkBoxCSize;
		dialog.submitEntireQueue.helpTip = 'Use this option when the entire render queue needs to be rendered all at once because some queue items are dependent on others or use proxies. Note though that only one machine will be able to work on this job, unless you also enable Multi-Machine Rendering.';
		dialog.submitEntireQueue.onClick = function()
		{
			dialog.frameListLabel.enabled = !this.value && !dialog.multiMachine.value;
			dialog.frameList.enabled = !dialog.useCompFrameList.value && !this.value && !dialog.multiMachine.value;
			dialog.useCompFrameList.enabled = !this.value && !dialog.multiMachine.value;
			dialog.firstAndLast.enabled = dialog.useCompFrameList.value && !this.value && !dialog.multiMachine.value;
			dialog.chunkSizeLabel.enabled = !this.value  && !dialog.multiMachine.value;
			dialog.chunkSize.enabled = !this.value && !dialog.multiMachine.value;
			dialog.chunkSizeSlider.enabled = !this.value && !dialog.multiMachine.value;
			dialog.dependentComps.enabled = (queuedCount > 1) && !this.value;
		}
		dialog.multiProcess = dialog.submitEntireQueueGroup.add( 'checkbox', undefined, 'Multi-Process Rendering' );
		dialog.multiProcess.value = initMultiProcess;
		dialog.multiProcess.size = checkBoxBSize;
		dialog.multiProcess.enabled = true;
		dialog.multiProcess.helpTip = 'Enable to use multiple processes to render multiple frames simultaneously (After Effects CS3 and later).';
		dialog.submitScene = dialog.submitEntireQueueGroup.add( 'checkbox', undefined, 'Submit Project File With Job' );
		dialog.submitScene.value = initSubmitScene;
        dialog.submitScene.size = checkBoxDSize;
		dialog.submitScene.helpTip = 'If enabled, the After Effects Project File will be submitted with the job.';
        
		// Ignore Missing Layers and Submit Project File
		dialog.ignoreMissingLayersGroup = dialog.aeOptionsPanel.add( 'group', undefined );
		dialog.ignoreMissingLayersGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.ignoreMissingLayers = dialog.ignoreMissingLayersGroup.add( 'checkbox', undefined, 'Ignore Missing Layer Dependencies' );
		dialog.ignoreMissingLayers.value = initIgnoreMissingLayers;
		dialog.ignoreMissingLayers.size = checkBoxCSize;
		dialog.ignoreMissingLayers.helpTip = 'If enabled, Deadline will ignore errors due to missing layer dependencies.';
		dialog.failOnWarnings = dialog.ignoreMissingLayersGroup.add( 'checkbox', undefined, 'Fail On Warning Messages' );
		dialog.failOnWarnings.value = initFailOnWarnings;
		dialog.failOnWarnings.size = checkBoxBSize;
		dialog.failOnWarnings.helpTip = 'If enabled, Deadline will fail the job whenever After Effects prints out a warning message.';
		dialog.exportAsXml = dialog.ignoreMissingLayersGroup.add( 'checkbox', undefined, 'Export XML Project File' );
		dialog.exportAsXml.value = initExportAsXml;
        dialog.exportAsXml.size = checkBoxDSize;
		dialog.exportAsXml.enabled = (parseInt( version ) > 8);
		dialog.exportAsXml.helpTip = 'Enable to export the project file as an XML file for Deadline to render (After Effects CS4 and later). The original project file will be restored after submission. If the current project file is already an XML file, this will do nothing.';
        
		// Ignore Missing Effects and Local Rendering
		dialog.ignoreMissingEffectsGroup = dialog.aeOptionsPanel.add( 'group', undefined );
		dialog.ignoreMissingEffectsGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.ignoreMissingEffects = dialog.ignoreMissingEffectsGroup.add( 'checkbox', undefined, 'Ignore Missing Effect References' );
		dialog.ignoreMissingEffects.value = initIgnoreMissingEffects;
		dialog.ignoreMissingEffects.size = checkBoxCSize;
		dialog.ignoreMissingEffects.helpTip = 'If enabled, Deadline will ignore errors due to missing effect references.';
		dialog.missingFootage = dialog.ignoreMissingEffectsGroup.add( 'checkbox', undefined, 'Continue On Missing Footage' );
		dialog.missingFootage.value = initMissingFootage;
		dialog.missingFootage.size = checkBoxBSize;
		dialog.missingFootage.enabled = (parseInt( version ) > 8);
		dialog.missingFootage.helpTip = 'If enabled, rendering will not stop when missing footage is detected (After Effects CS4 and later).';
		dialog.localRendering = dialog.ignoreMissingEffectsGroup.add( 'checkbox', undefined, 'Enable Local Rendering' );
		dialog.localRendering.value = initLocalRendering;
        dialog.localRendering.size = checkBoxDSize;
		dialog.localRendering.helpTip = 'If enabled, the frames will be rendered locally, and then copied to their final network location.\n\nNote that this feature is not supported if using Multi-Machine Rendering.';
		dialog.localRendering.enabled = !initMultiMachine;
        
        // Fail On Existing AE Process
        dialog.failOnExistingProcessGroup = dialog.aeOptionsPanel.add( 'group', undefined );
        dialog.failOnExistingProcessGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.OverrideFailOnExistingAEProcess = dialog.failOnExistingProcessGroup.add( 'checkbox', undefined, 'Override Fail On Existing AE Process' );
        dialog.OverrideFailOnExistingAEProcess.value = initOverrideFailOnExistingAEProcess;
        dialog.OverrideFailOnExistingAEProcess.size = checkBoxCSize;
        dialog.OverrideFailOnExistingAEProcess.helpTip = 'If enabled, the global repository setting "Fail on Existing AE Process" will be overridden.';
        dialog.OverrideFailOnExistingAEProcess.onClick = function()
        {
             dialog.FailOnExistingAEProcess.enabled = this.value;
        }
        dialog.FailOnExistingAEProcess = dialog.failOnExistingProcessGroup.add( 'checkbox', undefined, 'Fail On Existing AE Process' );
        dialog.FailOnExistingAEProcess.value = initFailOnExistingAEProcess;
        dialog.FailOnExistingAEProcess.enabled = initOverrideFailOnExistingAEProcess;
        dialog.FailOnExistingAEProcess.size = checkBoxBSize;
        dialog.FailOnExistingAEProcess.helpTip = 'If enabled, the job will be failed if any After Effects instances are currently running on the slave.\n\nExisting After Effects instances can sometimes cause 3rd party AE plugins to malfunction during network rendering.';
		
		// Tabbed views aren't supported in CS3 or earlier, so here's some magic to only hide the second tab without breaking anything.
		if(parseInt( version ) > 8)
		{
			// Advanced tab
			dialog.advancedTab = dialog.tabPanel.add( 'tab', undefined, 'Advanced' );
		}
		else
		{
			// Place the panel at [0,0,0,0] and then hide it.
			dialog.advancedTab = dialog.add( 'panel', [0,0,0,0] );
			dialog.advancedTab.visible = false;
		}
		
		// Multi Machine Section
		dialog.multiMachinePanel = dialog.advancedTab.add( 'panel', undefined, 'Multi-Machine Rendering (requires "Skip existing frames" to be enabled for each comp)' );
		dialog.multiMachinePanel.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		
		// Enable Multi Machine Mode
		dialog.multiMachineGroup = dialog.multiMachinePanel.add( 'group', undefined );
		dialog.multiMachineGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.multiMachine = dialog.multiMachineGroup.add( 'checkbox', undefined, 'Enable Multi-Machine Rendering' );
		dialog.multiMachine.value = initMultiMachine;
		dialog.multiMachine.size = textSize;
		dialog.multiMachine.helpTip = 'This mode submits a special job where each task represents the full frame range. The slaves will all work on the same frame range, but because "Skip existing frames" is enabled for the comps, they will skip frames that other slaves are already rendering.\n\nNote that this mode does not support Local Rendering or Output File Checking. In addition, the Frame List, Machine Limit, and Frames Per Task settings will be ignored.';
		dialog.multiMachine.onClick = function()
		{
			dialog.multiMachineTasksLabel.enabled = this.value;
			dialog.multiMachineTasks.enabled = this.value;
			dialog.multiMachineTasksSlider.enabled = this.value;
			
			dialog.fileSizeLabel.enabled = !this.value;
			dialog.fileSize.enabled = !this.value;
			dialog.fileSizeSlider.enabled = !this.value;
			
			dialog.localRendering.enabled = !this.value
			
			dialog.firstAndLast.enabled = dialog.useCompFrameList.value && !dialog.submitEntireQueue.value && !this.value;
			
			dialog.machineLimitLabel.enabled = !this.value;
			dialog.machineLimit.enabled = !this.value;
			dialog.machineLimitSlider.enabled = !this.value;
			
			dialog.chunkSizeLabel.enabled = !dialog.submitEntireQueue.value && !this.value;
			dialog.chunkSize.enabled = !dialog.submitEntireQueue.value && !this.value;
			dialog.chunkSizeSlider.enabled = !dialog.submitEntireQueue.value && !this.value;
			
			dialog.frameListLabel.enabled = !dialog.submitEntireQueue.value && !this.value;
			dialog.frameList.enabled = !dialog.useCompFrameList.value && !dialog.submitEntireQueue.value && !this.value;
			dialog.useCompFrameList.enabled = !dialog.submitEntireQueue.value && !this.value;
		}
		
		// Multi Machine Tasks
		dialog.multiMachineTasksGroup = dialog.multiMachinePanel.add( 'group', undefined );
		dialog.multiMachineTasksGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.multiMachineTasksLabel = dialog.multiMachineTasksGroup.add( 'statictext', undefined, 'Number Of Machines' );
		dialog.multiMachineTasksLabel.size = labelSize;
		dialog.multiMachineTasksLabel.enabled = initMultiMachine;
		dialog.multiMachineTasksLabel.helpTip = 'The number of slaves that can work on this job at the same time. Each slave gets a task, which represents the full frame range, and they will work together until all frames are complete.';
		dialog.multiMachineTasks = dialog.multiMachineTasksGroup.add( 'edittext', undefined, initMultiMachineTasks );
		dialog.multiMachineTasks.size = shortTextSize;
		dialog.multiMachineTasks.enabled = initMultiMachine;
		dialog.multiMachineTasks.onChange = function()
		{
			setSliderValue( this.text, 1, 9999, dialog.multiMachineTasksSlider )
			this.text = Math.round( dialog.multiMachineTasksSlider.value ); 
		}
		dialog.multiMachineTasksSlider = dialog.multiMachineTasksGroup.add( 'slider', undefined, initMultiMachineTasks, 1, 9999 );
		dialog.multiMachineTasksSlider.onChange = function() { dialog.multiMachineTasks.text = Math.round( this.value ); }
		dialog.multiMachineTasksSlider.size = sliderSize;
		dialog.multiMachineTasksSlider.enabled = initMultiMachine;
		
		// Output Checking Section
		dialog.outputPanel = dialog.advancedTab.add( 'panel', undefined, 'Output File Checking' );
		dialog.outputPanel.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];

		// Output Checking Options
		dialog.fileSizeGroup = dialog.outputPanel.add( 'group', undefined );
		dialog.fileSizeGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.fileSizeLabel = dialog.fileSizeGroup.add( 'statictext', undefined, 'Minimum File Size KB' );
		dialog.fileSizeLabel.size = labelSize;
		dialog.fileSizeLabel.helpTip = 'If the output file size is less then this value, Deadline will fail the task and requeue it. Set to 0 to disable this feature.\n\nNote that this feature is not supported if using Multi-Machine Rendering.';
		dialog.fileSizeLabel.enabled = !initMultiMachine
		dialog.fileSize = dialog.fileSizeGroup.add( 'edittext', undefined, initFileSize);
		dialog.fileSize.size = shortTextSize;
		dialog.fileSize.enabled = !initMultiMachine
		dialog.fileSize.onChange = function()
		{
			setSliderValue( this.text, 1, 100000, dialog.fileSizeSlider )
			this.text = Math.round( dialog.fileSizeSlider.value ); 
		}
		dialog.fileSizeSlider = dialog.fileSizeGroup.add( 'slider', undefined, initFileSize, 0, 100000 );
		dialog.fileSizeSlider.onChange = function() { dialog.fileSize.text = Math.round( this.value ); }
		dialog.fileSizeSlider.size = sliderSize;
		dialog.fileSizeSlider.enabled = !initMultiMachine
		
		// Memory Management Section
		dialog.memoryManagementPanel = dialog.advancedTab.add( 'panel', undefined, 'Memory Management' );
		dialog.memoryManagementPanel.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		
		// Enable Memory Management
		dialog.memoryManagementGroup = dialog.memoryManagementPanel.add( 'group', undefined );
		dialog.memoryManagementGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.memoryManagement = dialog.memoryManagementGroup.add( 'checkbox', undefined, 'Enable Memory Management' );
		dialog.memoryManagement.value = initMemoryManagement;
		dialog.memoryManagement.size = textSize;
		dialog.memoryManagement.helpTip = 'Enable to have Deadline control the amount of memory that After Effects uses.';
		dialog.memoryManagement.onClick = function()
		{
			dialog.imageCachePercentageLabel.enabled = this.value;
			dialog.imageCachePercentage.enabled = this.value;
			dialog.imageCachePercentageSlider.enabled = this.value;
			dialog.maxMemoryPercentageLabel.enabled = this.value;
			dialog.maxMemoryPercentage.enabled = this.value;
			dialog.maxMemoryPercentageSlider.enabled = this.value;
		}
		
		// Image Cache Percentage
		dialog.imageCachePercentageGroup = dialog.memoryManagementPanel.add( 'group', undefined );
		dialog.imageCachePercentageGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.imageCachePercentageLabel = dialog.imageCachePercentageGroup.add( 'statictext', undefined, 'Image Cache %' );
		dialog.imageCachePercentageLabel.size = labelSize;
		dialog.imageCachePercentageLabel.enabled = initMemoryManagement;
		dialog.imageCachePercentageLabel.helpTip = 'The maximum amount of memory after effects will use to cache frames.';
		dialog.imageCachePercentage = dialog.imageCachePercentageGroup.add( 'edittext', undefined, initImageCachePercentage );
		dialog.imageCachePercentage.size = shortTextSize;
		dialog.imageCachePercentage.enabled = initMemoryManagement;
		dialog.imageCachePercentage.onChange = function()
		{
			setSliderValue( this.text, 20, 100, dialog.imageCachePercentageSlider )
			this.text = Math.round( dialog.imageCachePercentageSlider.value ); 
		}
		dialog.imageCachePercentageSlider = dialog.imageCachePercentageGroup.add( 'slider', undefined, initImageCachePercentage, 20, 100 );
		dialog.imageCachePercentageSlider.onChange = function() { dialog.imageCachePercentage.text = Math.round( this.value ); }
		dialog.imageCachePercentageSlider.size = sliderSize;
		dialog.imageCachePercentageSlider.enabled = initMemoryManagement;
		
		// Max Memory Percentage
		dialog.maxMemoryPercentageGroup = dialog.memoryManagementPanel.add( 'group', undefined );
		dialog.maxMemoryPercentageGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.maxMemoryPercentageLabel = dialog.maxMemoryPercentageGroup.add( 'statictext', undefined, 'Maximum Memory %' );
		dialog.maxMemoryPercentageLabel.size = labelSize;
		dialog.maxMemoryPercentageLabel.enabled = initMemoryManagement;
		dialog.maxMemoryPercentageLabel.helpTip = 'The maximum amount of memory After Effects can use overall.';
		dialog.maxMemoryPercentage = dialog.maxMemoryPercentageGroup.add( 'edittext', undefined, initMaxMemoryPercentage );
		dialog.maxMemoryPercentage.size = shortTextSize;
		dialog.maxMemoryPercentage.enabled = initMemoryManagement;
		dialog.maxMemoryPercentage.onChange = function()
		{
			setSliderValue( this.text, 20, 100, dialog.maxMemoryPercentageSlider )
			this.text = Math.round( dialog.maxMemoryPercentageSlider.value );
		}
		dialog.maxMemoryPercentageSlider = dialog.maxMemoryPercentageGroup.add( 'slider', undefined, initMaxMemoryPercentage, 20, 100 );
		dialog.maxMemoryPercentageSlider.onChange = function() { dialog.maxMemoryPercentage.text = Math.round( this.value ); }
		dialog.maxMemoryPercentageSlider.size = sliderSize;
		dialog.maxMemoryPercentageSlider.enabled = initMemoryManagement;
		
		//===============SHOTGUN PANEL===============
		var shotgunKVPs = {};
		var ftrackKVPs = {};
		//-------------------------------------------
		// NIM
		var nimKVPs = {};
		// END NIM
		//-------------------------------------------

		function getProjMgmtInfo( scriptPath )
		{
			var keyValuePairs = {};
			var output = callDeadlineCommand( '-ExecuteScript "' + scriptPath + '" AfterEffects' );
			var outLines = output.split( "\n" );

			var validOutput = false;

			if (outLines.length > 1)
			{
				var regex = /(.*?)=([^\r\n]*)/;
				
				for ( var i = 0; i < outLines.length; i++ )
				{
					matches = regex.exec( outLines[ i ] );
					if (matches != null && matches.length > 2)
					{
						validOutput = true;
						key = matches[1];
						value = matches[2];
						keyValuePairs[key] = value;
					}
				}
			}

			if ( validOutput )
				return keyValuePairs;
			else
				return null;
		}

		function updateProjMgmtUI( forceOn )
		{
			var projectManager = dialog.projectMgmtCombo.selection.toString();

			var createValue = false;
			var createEnabled = false;

			var versionValue = "";
			var versionEnabled = false;

			var descValue = "";
			var descEnabled = false;

			var infoValue = "";
			var infoEnabled = false;

			var draftEnabled = false;
            var draftUploadEnabled = false;

            //--------------------------------------------------------------------------------------------
			// NIM - seed nim values - may be problem with this since IDs not persistant with file..
			//						   could end up with left over values
			/*
            nimKVPempty = true;
            for(var prop in nimKVPs) {
                if(nimKVPs.hasOwnProperty(prop))
                    nimKVPempty = false;
                    break;
            }
        
            $.writeln(nimKVPempty);
            if ( projectManager == "NIM" && nimKVPempty === true ){
            	var initNimKVPs = getIniSetting( "nimKVPs", "");
				$.writeln("initNimKVPs: "+initNimKVPs);
				nimKVPArray = JSON.parse(initNimKVPs);
				for(var nimKVPArrayItem in nimKVPArray) {
	                    var nimItem = nimKVPArrayItem[key];
	                    $.writeln(nimItem);
	                    
	                    if (nimItem.substr(0, 6) == "Class:") {
	                    	nimKVPs['nim_class'] = nimItem.substr(6,nimItem.length).trim();
	                    }
	                    
	            }
            }
            */
            // END NIM
            //--------------------------------------------------------------------------------------------

			if ( projectManager == "Shotgun" && shotgunKVPs && shotgunKVPs['UserName'] )
			{
				createEnabled = true;
				createValue = forceOn;
				versionEnabled = createValue;
				descEnabled = createValue;
                draftUploadEnabled = createValue;

				if ( shotgunKVPs['VersionName'] )
					versionValue = shotgunKVPs['VersionName'];

				if ( shotgunKVPs['Description'] )
					descValue = shotgunKVPs['Description'];

				infoEnabled = createValue;
				if ( shotgunKVPs['UserName'] )
					infoValue += "User Name: " + shotgunKVPs[ 'UserName' ] + "\n";
				if ( shotgunKVPs['TaskName'] )
					infoValue += "Task Name: " + shotgunKVPs[ 'TaskName' ] + "\n";
				if ( shotgunKVPs['ProjectName'] )
					infoValue += "Project Name: " + shotgunKVPs[ 'ProjectName' ] + "\n";
				if ( shotgunKVPs['EntityName'] )
					infoValue += "Entity Name: " + shotgunKVPs[ 'EntityName' ] + "\n";
				if ( shotgunKVPs['EntityType'] )
					infoValue += "Entity Type: " + shotgunKVPs[ 'EntityType' ] + "\n";
				if ( shotgunKVPs['DraftTemplate'] )
					infoValue += "Draft Template: " + shotgunKVPs[ 'DraftTemplate' ] + "\n";

				draftEnabled = createValue;
			}
			else if ( projectManager == "FTrack" && ftrackKVPs && ftrackKVPs['FT_AssetName'] )
			{
				createEnabled = true;
				createValue = forceOn;
				descEnabled = createValue;

				if ( ftrackKVPs['FT_AssetName'] )
					versionValue = ftrackKVPs['FT_AssetName'];

				if ( ftrackKVPs['FT_Description'] )
					descValue = ftrackKVPs['FT_Description'];

				infoEnabled = createValue;
				if ( ftrackKVPs['FT_Username'] )
					infoValue += "User Name: " + ftrackKVPs[ 'FT_Username' ] + "\n";
				if ( ftrackKVPs['FT_TaskName'] )
					infoValue += "Task Name: " + ftrackKVPs[ 'FT_TaskName' ] + "\n";
				if ( ftrackKVPs['FT_ProjectName'] )
					infoValue += "Project Name: " + ftrackKVPs[ 'FT_ProjectName' ] + "\n";
			}

			//--------------------------------------------------------------------------------------------
			// NIM
			else if ( projectManager == "NIM" && nimKVPs && nimKVPs['nim_taskID'] )
			{
				//alert("nim_taskID Found");
				createEnabled = true;
				createValue = forceOn;
				versionEnabled = createValue;
				descEnabled = createValue;
                draftUploadEnabled = createValue;

				if ( nimKVPs['nim_renderName'] )
					versionValue = nimKVPs['nim_renderName'];

				if ( nimKVPs['nim_description'] )
					descValue = nimKVPs['nim_description'];

				infoEnabled = createValue;
				
				if ( nimKVPs['nim_user'] )
					infoValue += "User Name: " + nimKVPs[ 'nim_user' ] + "\n";
				if ( nimKVPs['nim_class'] )
					infoValue += "Class: " + nimKVPs[ 'nim_class' ] + "\n";
				if ( nimKVPs['nim_jobID'] )
					infoValue += "Job ID: " + nimKVPs[ 'nim_jobID' ] + "\n";
				if ( nimKVPs['nim_jobName'] )
					infoValue += "Job Name: " + nimKVPs[ 'nim_jobName' ] + "\n";

				if ( nimKVPs['nim_class'] == "ASSET"){
					if ( nimKVPs['nim_assetID'] )
						infoValue += "Asset ID: " + nimKVPs[ 'nim_assetID' ] + "\n";
					if ( nimKVPs['nim_assetName'] )
						infoValue += "Asset Name: " + nimKVPs[ 'nim_assetName' ] + "\n";
				}

				if ( nimKVPs['nim_class'] == "SHOT"){
					if ( nimKVPs['nim_showID'] )
						infoValue += "Show ID: " + nimKVPs[ 'nim_showID' ] + "\n";
					if ( nimKVPs['nim_showName'] )
						infoValue += "Show Name: " + nimKVPs[ 'nim_showName' ] + "\n";
					if ( nimKVPs['nim_shotID'] )
						infoValue += "Shot ID: " + nimKVPs[ 'nim_shotID' ] + "\n";
					if ( nimKVPs['nim_shotName'] )
						infoValue += "Shot Name: " + nimKVPs[ 'nim_shotName' ] + "\n";
				}
				
				if ( nimKVPs['nim_taskName'] )
					infoValue += "Task Name: " + nimKVPs[ 'nim_taskName' ] + "\n";
				if ( nimKVPs['nim_taskID'] )
					infoValue += "Task ID: " + nimKVPs[ 'nim_taskID' ] + "\n";
				
				nimKVPs['nim_fileID'] = 0;
				if ( nimKVPs['nim_fileID'] )
					infoValue += "File ID: " + nimKVPs[ 'nim_fileID' ] + "\n";
				
				/*
				if ( nimKVPs['ProjectName'] )
					infoValue += "Project Name: " + nimKVPs[ 'ProjectName' ] + "\n";
				if ( nimKVPs['EntityName'] )
					infoValue += "Entity Name: " + nimKVPs[ 'EntityName' ] + "\n";
				if ( nimKVPs['EntityType'] )
					infoValue += "Entity Type: " + nimKVPs[ 'EntityType' ] + "\n";
				if ( nimKVPs['DraftTemplate'] )
					infoValue += "Draft Template: " + nimKVPs[ 'DraftTemplate' ] + "\n";
				*/
				draftEnabled = createValue;
			}
			// END NIM
			//--------------------------------------------------------------------------------------------

			dialog.createVersion.enabled = createEnabled;
			dialog.createVersion.value = createValue;

			dialog.projectMgmtVersionGroup.enabled = versionEnabled;
			dialog.projectMgmtVersion.text = versionValue;

			dialog.projectMgmtDescriptionGroup.enabled = descEnabled;
			dialog.projectMgmtDescription.text = descValue;

			dialog.projectMgmtInfoGroup.enabled = infoEnabled;
			dialog.projectMgmtInfoText.text = infoValue;
            
            //------------------------------------------------------------------------------------------
            // NIM - updating to accomodate both shotgun and NIM
            if (projectManager == "NIM" ){
            	dialog.draftCreateMovie.enabled = false;
            	dialog.draftCreateFilmStrip.enabled = false;
            }
            else {
            	dialog.draftCreateMovie.enabled = draftUploadEnabled;
            	dialog.draftCreateFilmStrip.enabled = draftUploadEnabled;
            }
            // END NIM
            //------------------------------------------------------------------------------------------
			dialog.draftUseSGDataButton.enabled = draftEnabled && dialog.useDraft.value;
			dialog.uploadDraftToShotgun.enabled = draftEnabled && dialog.useDraft.value;
		}
		
		//Connect/Use Shotgun
		dialog.projectMgmtPanel = dialog.advancedTab.add( 'panel', undefined, 'Project Management Integration' );
		dialog.projectMgmtPanel.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];

		dialog.projectMgmtConnectGroup = dialog.projectMgmtPanel.add( 'group', undefined );
		dialog.projectMgmtConnectGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.projectMgmtLabel = dialog.projectMgmtConnectGroup.add( 'statictext', undefined, 'Project Management' ).size = labelSize;
		dialog.projectMgmtLabel.size = labelSize;
		dialog.projectMgmtLabel.helpTip = 'The Project Management integration to use.';
		dialog.projectMgmtCombo = dialog.projectMgmtConnectGroup.add( 'dropdownlist', undefined, '' );
		shotgunItem = dialog.projectMgmtCombo.add( 'item', 'Shotgun' );
		dialog.projectMgmtCombo.add( 'item', 'FTrack' );
		
		//--------------------
		// NIM
		dialog.projectMgmtCombo.add( 'item', 'NIM' );
		// END NIM
		//--------------------

		dialog.projectMgmtCombo.selection = shotgunItem;
		dialog.projectMgmtCombo.size = comboSize;
		dialog.projectMgmtCombo.onChange = function()
		{
			var selection = this.selection.toString();

			//defaults
			versionLabel = "Version Name";
			descLabel = "Version Description";
			miscLabel = "Selected Entity Info";
			
			//--------------------
			// NIM - Adding Defaults
			draftCreateMovieEnabled = true;
			draftCreateFilmStripEnabled = true;
			draftUseValuesLabel = "Use Shotgun Data";
			draftUseValuesAnn = "Uses data from Shotgun to fill out the Draft settings";
			draftUploadlabel = "Upload Draft Results To Shotgun";
			draftAnnotation = "Check to upload Draft output to Shotgun.";
			draftOptionsVisible = false;
			
			if ( selection == "Shotgun" )
			{
				versionLabel = "Version Name";
				descLabel = "Version Description";
				miscLabel = "Selected Entity Info";
				
				draftUseValuesLabel = "Use Shotgun Data";
				draftUseValuesAnn = "Uses data from Shotgun to fill out the Draft settings";
				draftUploadlabel = "Upload to Shotgun";
				draftAnnotation = "Check to upload Draft output to Shotgun.";
				draftOptionsVisible = false;
				draftCreateMovieEnabled = true;
				draftCreateFilmStripEnabled = true;
			}
			if ( selection == "FTrack" )
			{
				versionLabel = "Selected Asset";
				miscLabel = "Miscellaneous Info";
				draftCreateMovieEnabled = false;
				draftCreateFilmStripEnabled = false;
			}
			if ( selection == "NIM" )
			{
				versionLabel = "Render Name";
				descLabel = "Description";
				miscLabel = "NIM Details";
				draftCreateMovieEnabled = false;
				draftCreateFilmStripEnabled = false;
				draftUseValuesLabel = "Use NIM Data";
				draftUseValuesAnn = "Uses data from NIM to fill out the Draft settings";
				draftUploadlabel = "Upload Draft Results To NIM";
				draftAnnotation = "Check to upload Draft output to NIM.";
				draftOptionsVisible = false;
			}

            dialog.draftCreateMovie.enabled = false;
            dialog.draftCreateFilmStrip.enabled = false;

			dialog.uploadDraftToShotgun.text = draftUploadlabel;
			dialog.draftUseSGDataButton.text = draftUseValuesLabel;
			// END NIM
			//--------------------
			
			dialog.projectMgmtVersionLabel.text = versionLabel;
			dialog.projectMgmtDescriptionLabel.text = descLabel;
			dialog.projectMgmtInfoLabel.text = miscLabel;

			updateProjMgmtUI( dialog.createVersion.value );
		}

		dialog.projectMgmtConnectButton = dialog.projectMgmtConnectGroup.add( 'button', undefined, 'Connect...' );
		dialog.projectMgmtConnectButton.size = labelSize;
		dialog.projectMgmtConnectButton.onClick = function()
		{
			var projectManager = dialog.projectMgmtCombo.selection.toString();

			if ( projectManager == "Shotgun" )
			{
				var sgPath = "";
				if (system.osName == "MacOS")
					sgPath = root + "/events/Shotgun/ShotgunUI.py";
				else
					sgPath = root + "\\events\\Shotgun\\ShotgunUI.py";

				result = getProjMgmtInfo( sgPath );

				if ( result )
					shotgunKVPs = result;
					updateProjMgmtUI( true );
			}
			else if ( projectManager == "FTrack" )
			{
				var ftPath = "";
				if (system.osName == "MacOS")
					ftPath = root + "/submission/FTrack/Main/FTrackUI.py";
				else
					ftPath = root + "\\submission\\FTrack\\Main\\FTrackUI.py";

				result = getProjMgmtInfo( ftPath );
				if ( result )
					ftrackKVPs = result;
					updateProjMgmtUI( true );
			}
			//---------------------------------------------------------------------
			// NIM
			if ( projectManager == "NIM" )
			{
				// GET NIM vars
				//arg_string = "nim_jobID=1";
				//'-ExecuteScript "' + scriptPath + '" AfterEffects'

				var nimPath = "";
				if (system.osName == "MacOS")
					nimPath = root + "/events/NIM/NIM_UI.py";
				else
					nimPath = root + "\\events\\NIM\\NIM_UI.py";

				//nimUIScript = nimPath + '" '+arg_string+' "';

				result = getProjMgmtInfo( nimPath );
				if ( result )
					nimKVPs = result;
					updateProjMgmtUI( true );
			}
			// END NIM
			//---------------------------------------------------------------------
		}
		dialog.createVersion = dialog.projectMgmtConnectGroup.add( 'checkbox', undefined, 'Create New Version' );
		dialog.createVersion.onClick = function()
		{
			updateProjMgmtUI( this.value );
		}
		dialog.createVersion.size = checkBoxBSize;
		dialog.createVersion.enabled = false;
		
		// Version Name
		dialog.projectMgmtVersionGroup = dialog.projectMgmtPanel.add( 'group', undefined );
		dialog.projectMgmtVersionGroup .alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.projectMgmtVersionLabel = dialog.projectMgmtVersionGroup.add( 'statictext', undefined, 'Version Name' );
		dialog.projectMgmtVersionLabel.size = labelSize;
		dialog.projectMgmtVersionLabel.helpTip = 'The name of the Version that will be created in Shotgun.';
		dialog.projectMgmtVersion = dialog.projectMgmtVersionGroup .add( 'edittext', undefined, '' );
		dialog.projectMgmtVersion.size = textSize;
		dialog.projectMgmtVersion.onChange = function() 
		{ 
			var projectManager = dialog.projectMgmtCombo.selection.toString();
			if ( projectManager == "Shotgun" )
				shotgunKVPs['VersionName'] = this.text;
			//--------------------------------------------
			// NIM
			if ( projectManager == "NIM" )
				nimKVPs['nim_renderName'] = this.text;
			// END NIM
			//--------------------------------------------
		}
		dialog.projectMgmtVersionGroup.enabled = false;
		
		// Description
		dialog.projectMgmtDescriptionGroup = dialog.projectMgmtPanel.add( 'group', undefined );
		dialog.projectMgmtDescriptionGroup .alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.projectMgmtDescriptionLabel = dialog.projectMgmtDescriptionGroup .add( 'statictext', undefined, 'Version Description' );
		dialog.projectMgmtDescriptionLabel.size = labelSize;
		dialog.projectMgmtDescriptionLabel.helpTip = 'The description of the Version that will be created in Shotgun.';
		dialog.projectMgmtDescription = dialog.projectMgmtDescriptionGroup .add( 'edittext', undefined, '' );
		dialog.projectMgmtDescription.size = textSize;
		dialog.projectMgmtDescription.onChange = function() 
		{ 
			var projectManager = dialog.projectMgmtCombo.selection.toString();
			if ( projectManager == "Shotgun" )
				shotgunKVPs['Description'] = this.text;
			else if ( projectManager == "FTrack" )
				shotgunKVPs['FT_Description'] = this.text;
			//--------------------------------------------
			// NIM
			else if ( projectManager == "NIM" )
				nimKVPs['nim_description'] = this.text;
			// END NIM
			//--------------------------------------------
		}
		dialog.projectMgmtDescriptionGroup.enabled = false;
		
		//Selected Entity Info
		dialog.projectMgmtInfoGroup = dialog.projectMgmtPanel.add( 'group', undefined );
		dialog.projectMgmtInfoGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.projectMgmtInfoLabel = dialog.projectMgmtInfoGroup.add( 'statictext', undefined, 'Selected Entity Info' );
		dialog.projectMgmtInfoLabel.size = labelSize;
		dialog.projectMgmtInfoLabel.alignment = [ScriptUI.Alignment.LEFT, ScriptUI.Alignment.TOP];
		dialog.projectMgmtInfoText = dialog.projectMgmtInfoGroup.add( 'edittext', undefined, '', {multiline:true, readonly:true, scrolling:false} );
		dialog.projectMgmtInfoText.size = [500, 96];
		dialog.projectMgmtInfoGroup.enabled = false;
		
        dialog.draftUploadGroup = dialog.projectMgmtPanel.add( 'group', undefined );
		dialog.draftUploadGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
        dialog.draftCreateMovie = dialog.draftUploadGroup.add( 'checkbox', undefined, 'Create/Upload Movie' );
        dialog.draftCreateMovie.enabled = false;
        dialog.draftCreateFilmStrip = dialog.draftUploadGroup.add( 'checkbox', undefined, 'Create/Upload Film Strip' );
		dialog.draftCreateFilmStrip.enabled = false;
        
        
		//===============DRAFT PANEL===============
		dialog.draftPanel = dialog.advancedTab.add( 'panel', undefined, 'Draft Options' );
		dialog.draftPanel.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.draftCheckboxGroup = dialog.draftPanel.add( 'group', undefined );
		dialog.draftCheckboxGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.useDraft = dialog.draftCheckboxGroup.add( 'checkbox', undefined, 'Submit Draft Job On Completion' );
		dialog.useDraft.value = initUseDraft;
		dialog.useDraft.onClick = function()
		{
			dialog.draftTemplateGroup.enabled = this.value;
			dialog.draftUserGroup.enabled = this.value;
			dialog.draftEntityGroup.enabled = this.value;
			dialog.draftVersionGroup.enabled = this.value;
			dialog.draftExtraArgsGroup.enabled = this.value;
			
			dialog.draftUseSGDataButton.enabled = this.value && dialog.createVersion.value;
			dialog.uploadDraftToShotgun.enabled = this.value && dialog.createVersion.value;
		}
		dialog.uploadDraftToShotgun = dialog.draftCheckboxGroup.add( 'checkbox', undefined, 'Upload Draft Results To Shotgun' );
		dialog.uploadDraftToShotgun.enabled = false;
		dialog.draftUseSGDataButton = dialog.draftCheckboxGroup.add( 'button', undefined, 'Use Shotgun Data' );
		dialog.draftUseSGDataButton.size = shortTextSize;
		dialog.draftUseSGDataButton.onClick = function()
		{
			//----------------------------------------------------------------------------------------------------
			// NIM - Updating to determine if shotgun
			var projectManager = dialog.projectMgmtCombo.selection.toString();

			if ( projectManager == "Shotgun" ) {
				if ( shotgunKVPs['UserName'] )
					dialog.draftUserText.text = shotgunKVPs['UserName'];
					
				if ( shotgunKVPs['DraftTemplate'] )
					dialog.draftTemplateText.text = shotgunKVPs['DraftTemplate'];
				
				if ( shotgunKVPs['VersionName'] )
					dialog.draftVersionText.text = shotgunKVPs['VersionName'];
				
				if ( shotgunKVPs['TaskName'] && shotgunKVPs['TaskName'] != "None" )
				{
					dialog.draftEntityText.text = shotgunKVPs['TaskName'];
				}
				else if ( shotgunKVPs['ProjectName'] && shotgunKVPs['EntityName'] )
				{
					dialog.draftEntityText.text = shotgunKVPs['ProjectName'] + " > " + shotgunKVPs['EntityName'];
				}
			}
			if ( projectManager == "NIM" ) {
				if ( nimKVPs['nim_user'] )
				dialog.draftUserText.text = nimKVPs['nim_user'];
				
				if ( nimKVPs['DraftTemplate'] )
					dialog.draftTemplateText.text = nimKVPs['DraftTemplate'];
				
				if ( nimKVPs['nim_renderName'] )
					dialog.draftVersionText.text = nimKVPs['nim_renderName'];
				
				//Entity Name should be NIM filename
				dialog.draftEntityText.text = replaceAll( projectName, "%20", " " );
				/* 
				else if ( nimKVPs['ProjectName'] && nimKVPs['EntityName'] )
				{
					dialog.draftEntityText.text = nimKVPs['ProjectName'] + " > " + nimKVPs['EntityName'];
				}
				*/
			}
			// END NIM
			//----------------------------------------------------------------------------------------------------
		}
		dialog.draftUseSGDataButton.enabled = false;
		
		dialog.draftTemplateGroup = dialog.draftPanel.add( 'group', undefined );
		dialog.draftTemplateGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.draftTemplateLabel = dialog.draftTemplateGroup.add( 'statictext', undefined, 'Draft Template' );
		dialog.draftTemplateLabel.size = labelSize;
		dialog.draftTemplateLabel.helpTip = "The Draft Template to use for the submitted Draft job.";
		dialog.draftTemplateText = dialog.draftTemplateGroup.add( 'edittext', undefined, initDraftTemplate );
		dialog.draftTemplateText.size = browseTextSize;
		dialog.draftTemplateButton = dialog.draftTemplateGroup.add( 'button', undefined, '...' );
		dialog.draftTemplateButton.onClick = function()
		{
			var origValue = dialog.draftTemplateText.text;
			var newValue = callDeadlineCommand( "-SelectFilenameLoad \"" + origValue + "\"" ).replace( "\n", "" ).replace( "\r", "" );
			if( newValue != "" )
				dialog.draftTemplateText.text = newValue;
		}
		dialog.draftTemplateButton.size = buttonSize
		dialog.draftTemplateGroup.enabled = false;
		
		dialog.draftUserGroup = dialog.draftPanel.add( 'group', undefined );
		dialog.draftUserGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.draftUserLabel = dialog.draftUserGroup.add( 'statictext', undefined, 'User Name' );
		dialog.draftUserLabel.size = labelSize;
		dialog.draftUserLabel.helpTip = "The value of the 'username' argument that will be passed to the Draft template.";
		dialog.draftUserText = dialog.draftUserGroup.add( 'edittext', undefined, initDraftUser );
		dialog.draftUserText.size = textSize;
		dialog.draftUserGroup.enabled = false;
		
		dialog.draftEntityGroup = dialog.draftPanel.add( 'group', undefined );
		dialog.draftEntityGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.draftEntityLabel = dialog.draftEntityGroup.add( 'statictext', undefined, 'Entity Name' );
		dialog.draftEntityLabel.size = labelSize;
		dialog.draftEntityLabel.helpTip = "The value of the 'entity' argument that will be passed to the Draft template.";
		dialog.draftEntityText = dialog.draftEntityGroup.add( 'edittext', undefined, initDraftEntity );
		dialog.draftEntityText.size = textSize;
		dialog.draftEntityGroup.enabled = false;
		
		dialog.draftVersionGroup = dialog.draftPanel.add( 'group', undefined );
		dialog.draftVersionGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.draftVersionLabel = dialog.draftVersionGroup.add( 'statictext', undefined, 'Version Name' );
		dialog.draftVersionLabel.size = labelSize;
		dialog.draftVersionLabel.helpTip = "The value of the 'version' argument that will be passed to the Draft template.";
		dialog.draftVersionText = dialog.draftVersionGroup.add( 'edittext', undefined, initDraftVersion );
		dialog.draftVersionText.size = textSize;
		dialog.draftVersionGroup.enabled = false;
		
		dialog.draftExtraArgsGroup = dialog.draftPanel.add( 'group', undefined );
		dialog.draftExtraArgsGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		dialog.draftExtraArgsLabel = dialog.draftExtraArgsGroup.add( 'statictext', undefined, 'Additional Args' );
		dialog.draftExtraArgsLabel.size = labelSize;
		dialog.draftExtraArgsLabel.helpTip = "Additional arguments that will be passed to the Draft template.";
		dialog.draftExtraArgsText = dialog.draftExtraArgsGroup.add( 'edittext', undefined, initDraftExtraArgs );
		dialog.draftExtraArgsText.size = textSize;
		dialog.draftExtraArgsGroup.enabled = false;
		
		//update enabled state of Draft controls
		dialog.useDraft.onClick();
		//===============END SHOTGUN/DRAFT===============
		
		// Buttons
		dialog.buttonsGroup = dialog.add( 'group', undefined );
		dialog.buttonsGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
		
		// Render Layers button (brings up new dialog)
		dialog.renderLayersButton = dialog.buttonsGroup.add( 'button', undefined, 'Submit Selected Layers...' )
		dialog.renderLayersButton.size = [180, 20];
		dialog.renderLayersButton.onClick = SubmitLayersToDeadline;
		dialog.progressBar = dialog.buttonsGroup.add( 'progressbar', undefined, '' );
		dialog.progressBar.size = [322, 20];
		dialog.progressBar.value = 0;

		// Submit and Close Buttons
		dialog.submitButton = dialog.buttonsGroup.add( 'button', undefined, 'Submit' );
		dialog.submitButton.onClick = function()
		{
			var queuedCount = GetQueuedCompCount();
			
			if ( queuedCount != 0 )
			{
				results = "";
				
				errors = "";
				warnings = "";
				
				var frameList = dialog.frameList.text;
				var overrideFrameList = dialog.useCompFrameList.value;
				var firstAndLast = dialog.firstAndLast.value;
				
				// Check frame range
				//if( ! overrideFrameList && ! firstAndLast && frameList == "" )
				if( ! overrideFrameList && frameList == "" )
					errors += "Please specify a frame list, or enable the option to use the frame list from the comp.\n";
				
				// Check project file if not submitting it to Deadline
				if( ! dialog.submitScene.value && isLocal( projectPath ) )
					warnings += "The project file \"" + projectPath + "\" is local and is not being submitted.\n";
				
				// Cycle through all the comps in the Render Queue and check the queued ones
				for( i = 1; i <= app.project.renderQueue.numItems; ++i )
				{
					if( app.project.renderQueue.item( i ).status != RQItemStatus.QUEUED )
						continue;
					
					// get the comp to be rendered
					var compName = app.project.renderQueue.item( i ).comp.name;
					
					// Check output module(s)
					for( j = 1; j <= app.project.renderQueue.item( i ).numOutputModules; ++j )
					{
						var outputPath = app.project.renderQueue.item( i ).outputModule( j ).file.fsName;
						
						var outputFile = File( outputPath );
						var outputFolder = Folder( outputFile.path );
						if( ! outputFolder.exists )
							warnings += compName + ": The path for the output file \"" + outputPath + "\" does not exist.\n";
						else if( isLocal( outputPath ) )
							warnings +=  compName + ": The output file \"" + outputPath + "\" is local.\n";
					}
				}
				
				if( errors != "" )
				{
					errors += "\nPlease fix these errors before submitting your job to Deadline.";
					alert( errors );
					return;
				}
				else if( warnings != "" )
				{
					warnings += "\nDo you still wish to submit this job to Deadline?";
					if( ! confirm( warnings ) )
						return;
				}
				
				var restoreProjectPath = false;
				var oldProjectPath = projectPath;
				
				// See if we need to save the current scene as an aepx file first.
				if( dialog.exportAsXml.value && projectPath.indexOf( ".aep", projectPath.length - 4 ) != -1 )
				{
					app.project.save( File( projectPath.substring( 0, projectPath.length - 4 ) + ".aepx" ) );
					projectPath = app.project.file.fsName;
					restoreProjectPath = true;
				}
				
				var totalJobs = app.project.renderQueue.numItems;
				queuedCount
				
				var jobCount = 0;
				var totalJobs = queuedCount;
				if( dialog.submitEntireQueue.value )
					totalJobs = 1;
				
				dialog.progressBar.value = 0;

				projMgmtKVPs = shotgunKVPs;
				if ( dialog.projectMgmtCombo.selection.toString() == "FTrack" )
					projMgmtKVPs = ftrackKVPs;
				
				//-------------------------------------------------------------------
				// NIM
				if ( dialog.projectMgmtCombo.selection.toString() == "NIM" )
					projMgmtKVPs = nimKVPs;
				// END NIM
				//-------------------------------------------------------------------

				// cycle through all the comps in the Render Queue and submit the queued ones
				var previousJobId = "";
				for( i = 1; i <= app.project.renderQueue.numItems; ++i )
				{
					if( app.project.renderQueue.item( i ).status != RQItemStatus.QUEUED )
						continue;
					
					jobCount = jobCount + 1;
					dialog.progressBar.value = (jobCount * 100) / (totalJobs + 1);
					
					previousJobId = SubmitComp( projectPath, app.project.renderQueue.item( i ), false, undefined, previousJobId, projMgmtKVPs );
					
					if( dialog.submitEntireQueue.value )
						break;
				}
				
				dialog.progressBar.value = 100;
				
				// Restore the original project path if necessary.
				if( restoreProjectPath )
					app.open( File( oldProjectPath ) )
				
				alert( results );
			}
			else
			{
				alert( "You do not have any items in the render queue!" );
			}
		}
		
		dialog.closeButton = dialog.buttonsGroup.add( 'button', undefined, 'Close' );
		dialog.closeButton.onClick = function()
		{
            setIniSetting( "UseCompName", toBooleanString( dialog.useCompName.value ) );
            setIniSetting( "Department", dialog.department.text );
            setIniSetting( "Group", dialog.group.selection.toString() );
            setIniSetting( "Pool", dialog.pool.selection.toString() );
            setIniSetting( "SecondaryPool", dialog.secondaryPool.selection.toString() );
            setIniSetting( "Priority", Math.round( dialog.prioritySlider.value ) );
            setIniSetting( "MachineLimit", Math.round( dialog.machineLimitSlider.value ) );
            setIniSetting( "LimitGroups", dialog.limitGroups.text );
            setIniSetting( "MachineList", dialog.machineList.text );
            setIniSetting( "IsBlacklist", toBooleanString( dialog.isBlacklist.value ) );
            setIniSetting( "SubmitSuspended", toBooleanString( dialog.submitSuspended.value ) );
            setIniSetting( "ChunkSize", Math.round( dialog.chunkSizeSlider.value ) );
            setIniSetting( "SubmitScene", toBooleanString( dialog.submitScene.value ) );
            setIniSetting( "MultiMachine", toBooleanString( dialog.multiMachine.value ) );
            setIniSetting( "MultiMachineTasks", Math.round( dialog.multiMachineTasksSlider.value ) );
            setIniSetting( "FileSize", Math.round( dialog.fileSizeSlider.value ) );
            setIniSetting( "MemoryManagement", toBooleanString( dialog.memoryManagement.value ) );
            setIniSetting( "ImageCachePercentage", Math.round( dialog.imageCachePercentageSlider.value ) );
            setIniSetting( "MaxMemoryPercentage", Math.round( dialog.maxMemoryPercentageSlider.value ) );
            setIniSetting( "UseCompFrame", toBooleanString( dialog.useCompFrameList.value ) );
            setIniSetting( "FirstAndLast", toBooleanString( dialog.firstAndLast.value ) );
            setIniSetting( "MissingLayers", toBooleanString( dialog.ignoreMissingLayers.value ) );
            setIniSetting( "MissingEffects", toBooleanString( dialog.ignoreMissingEffects.value ) );
            setIniSetting( "FailOnWarnings", toBooleanString( dialog.failOnWarnings.value ) );
            setIniSetting( "SubmitEntireQueue", toBooleanString( dialog.submitEntireQueue.value ) );
            setIniSetting( "LocalRendering", toBooleanString( dialog.localRendering.value ) );
            setIniSetting( "OverrideFailOnExistingAEProcess", toBooleanString( dialog.OverrideFailOnExistingAEProcess.value ) );
            setIniSetting( "FailOnExistingAEProcess", toBooleanString( dialog.FailOnExistingAEProcess.value ) );
            setIniSetting( "UseDraft", toBooleanString( dialog.useDraft.value ) );
            setIniSetting( "DraftTemplate", dialog.draftTemplateText.text );
            setIniSetting( "DraftUser", dialog.draftUserText.text );
            setIniSetting( "DraftEntity", dialog.draftEntityText.text );
            setIniSetting( "DraftVersion", dialog.draftVersionText.text );
            setIniSetting( "DraftExtraArgs", dialog.draftExtraArgsText.text );
			
			//--------------------------------------------------------------------------------------------------------------------------
			// NIM 
			// Removed for now as peristant values here may cause issues
			/*
			if ( dialog.projectMgmtCombo.selection.toString() == "NIM" ){
				nimTmpVarArray = dialog.projectMgmtInfoText.text.split(/\r\n|\r|\n/g);
				nimTmpVars = JSON.stringify(nimTmpVarArray);
				setIniSetting( "nimKVPs", nimTmpVars);
				$.writeln(nimTmpVars);
			}
			*/
			// END NIM
			//--------------------------------------------------------------------------------------------------------------------------

			if( queuedCount > 1 )
				setIniSetting( "DependentComps", toBooleanString( dialog.dependentComps.value ) );
			
			// Multiprocess was introduced in version 8
			setIniSetting( "MultiProcess", toBooleanString( dialog.multiProcess.value ) );
			setIniSetting( "ExportAsXml", toBooleanString( dialog.exportAsXml.value ) );
			
			if( parseInt( version ) > 8 )
				setIniSetting( "MissingFootage", toBooleanString( dialog.missingFootage.value ) );
			
			dialog.close();
		}
		
		// Show dialog
		dialog.show();
	}

	function SubmitComp( projectPath, renderQueueItem, layers, jobName, previousJobId, projMgmtKVPs )
	{
		var startFrame = ""
		var endFrame = ""
		var frameList = dialog.frameList.text;
		var overrideFrameList = dialog.useCompFrameList.value;
		var firstAndLast = dialog.firstAndLast.value;
		var multiMachine = dialog.multiMachine.value;
		var submitScene = (dialog.submitScene.value | layers); //MUST submit the scene file when rendering layers separately
		var entireQueue = (dialog.submitEntireQueue.value & !layers); //Not submitting from the queue when doing layers
		var dependentJobId = previousJobId;
		var dependentComps = false;
		if( GetQueuedCompCount() > 1 && !layers )
			dependentComps = dialog.dependentComps.value;
	
		var compName = renderQueueItem.comp.name;
		
		if ( entireQueue )
			compName = "Entire Render Queue";
				
		if( jobName === undefined )
			jobName = compName;
		
		// Check if there is an output module that is rendering to a movie.
		var isMovie = false;
		for( j = 1; j <= renderQueueItem.numOutputModules; ++j )
		{
			var outputPath = renderQueueItem.outputModule( j ).file.fsName;
			// get the output file's prefix and extension
			var index = outputPath.lastIndexOf( "\\" );
			var outputFile = outputPath.substring( index + 1, outputPath.length );
			index = outputFile.lastIndexOf( "." );
			var outputPrefix = outputFile.substring( 0, index );
			var outputExt = outputFile.substring( index + 1, outputFile.length );
			
			if( IsMovieFormat( outputExt ) )
			{
				isMovie = true;
				break;
			}
		}
		
		if( overrideFrameList || multiMachine )
		{
			// get the frame duration and start/end times
			frameDuration = renderQueueItem.comp.frameDuration;
			
			frameOffset = app.project.displayStartFrame;
			displayStartTime = renderQueueItem.comp.displayStartTime;
			if( displayStartTime == undefined )
			{
				// After Effects 6.0
				startFrame = frameOffset + Math.round( renderQueueItem.comp.workAreaStart / frameDuration );
				endFrame = startFrame + Math.round( renderQueueItem.comp.workAreaDuration / frameDuration ) - 1;
				frameList = startFrame + "-" + endFrame
			}
			else
			{
				// After Effects 6.5 +
				// This gets the frame range from what's specified in the render queue, instead of just the comp settings.
				startFrame = frameOffset + Math.round( displayStartTime / frameDuration ) + Math.round( renderQueueItem.timeSpanStart / frameDuration );
				endFrame = startFrame + Math.round( renderQueueItem.timeSpanDuration / frameDuration ) - 1;
				frameList = startFrame + "-" + endFrame
			}
			
			if( firstAndLast && !multiMachine )
				frameList = startFrame + "," + endFrame + "," + frameList
		}
		
		var currentJobDependencies = dialog.dependencies.text;
		if( !entireQueue && dependentComps && dependentJobId != "" )
		{
			if( currentJobDependencies == "" )
				currentJobDependencies = dependentJobId;
			else
				currentJobDependencies = dependentJobId + "," + currentJobDependencies;
		}
		
		if( dialog.useCompName.value == true)
			jobName = compName;
		else
			jobName = dialog.jobName.text + " - " + jobName;
		
		if( multiMachine )
			jobName = jobName + " (multi-machine rendering frames " + frameList + ")";
		
		// Create the submission info file
		var submitInfoFilename = tempFolder + "ae_submit_info.job";
		var submitInfoFile = File( submitInfoFilename );
		submitInfoFile.open( "w" );
		submitInfoFile.writeln( "Plugin=AfterEffects" );
		submitInfoFile.writeln( "Name=" + jobName );
        if(dependentComps)
            submitInfoFile.writeln( "BatchName=" + compName );
		submitInfoFile.writeln( "Comment=" + dialog.comment.text );
		submitInfoFile.writeln( "Department=" + dialog.department.text );
		submitInfoFile.writeln( "Group=" + dialog.group.selection.toString() );
		submitInfoFile.writeln( "Pool=" + dialog.pool.selection.toString() );
        submitInfoFile.writeln( "SecondaryPool=" + dialog.secondaryPool.selection.toString() );
		submitInfoFile.writeln( "Priority=" + Math.round( dialog.prioritySlider.value ) );
		submitInfoFile.writeln( "TaskTimeoutMinutes=" + Math.round( dialog.taskTimeoutSlider.value ) );
		submitInfoFile.writeln( "LimitGroups=" + dialog.limitGroups.text );
		submitInfoFile.writeln( "ConcurrentTasks=" + Math.round( dialog.concurrentTasksSlider.value ) );
		submitInfoFile.writeln( "JobDependencies=" + currentJobDependencies );
		submitInfoFile.writeln( "OnJobComplete=" + dialog.onComplete.selection.toString() );
		
		if( dialog.isBlacklist.value )
			submitInfoFile.writeln( "Blacklist=" + dialog.machineList.text );
		else
			submitInfoFile.writeln( "Whitelist=" + dialog.machineList.text );
		
		if( dialog.submitSuspended.value )
			submitInfoFile.writeln( "InitialStatus=Suspended" );
		
		if( !entireQueue )
		{
			// Only do multi machine rendering if we're rendering a frame sequence
			if( !isMovie && multiMachine )
				submitInfoFile.writeln( "Frames=1-" + Math.round( dialog.multiMachineTasksSlider.value ) );
			else
				submitInfoFile.writeln( "Frames=" + frameList );
			
			var index = 0;
			for( j = 1; j <= renderQueueItem.numOutputModules; ++j )
			{
				submitInfoFile.writeln( "OutputFilename" + index + "=" + renderQueueItem.outputModule( j ).file.fsName.replace( "[#", "#" ).replace( "#]", "#" ) );
				index = index + 1
			}
		}
		else
		{
			// If we're doing the full render queue, we only have 1 task unless we're doing multi frame rendering
			if( multiMachine )
				submitInfoFile.writeln( "Frames=1-" + Math.round( dialog.multiMachineTasksSlider.value ) );
			else
				submitInfoFile.writeln( "Frames=0" );
			
			var index = 0;
			for( i = 1; i <= app.project.renderQueue.numItems; ++i )
			{
				if( app.project.renderQueue.item( i ).status != RQItemStatus.QUEUED )
					continue;
				
				for( j = 1; j <= app.project.renderQueue.item( i ).numOutputModules; ++j )
				{
					submitInfoFile.writeln( "OutputDirectory" + index + "=" + app.project.renderQueue.item( i ).outputModule( j ).file.parent.fsName );
					index = index + 1
				}
			}
		}
		
		if( isMovie  )
		{
			// Override these settings for movies
			submitInfoFile.writeln( "MachineLimit=1" );
			submitInfoFile.writeln( "ChunkSize=100000" );
		}
		else
		{
			if( multiMachine )
			{
				// Machine limits don't make sense in multi-machine mode, because you want all machines working together. Chunking tasks doesn't make sense either.
				submitInfoFile.writeln( "MachineLimit=0" );
				submitInfoFile.writeln( "ChunkSize=1" );
			}
			else
			{
				submitInfoFile.writeln( "MachineLimit=" + Math.round( dialog.machineLimitSlider.value ) );
				submitInfoFile.writeln( "ChunkSize=" + Math.round( dialog.chunkSizeSlider.value ) );
			}
		}
		
		//==========Shotgun/Draft===================
		var nextKVP = 0;
		
		if ( dialog.createVersion.value && dialog.createVersion.enabled )
		{
			if ( dialog.projectMgmtCombo.selection.toString() == "Shotgun" )
			{
				submitInfoFile.writeln( "ExtraInfo0=" + projMgmtKVPs['TaskName'] );
				submitInfoFile.writeln( "ExtraInfo1=" + projMgmtKVPs['ProjectName'] );
				submitInfoFile.writeln( "ExtraInfo2=" + projMgmtKVPs['EntityName'] );
				submitInfoFile.writeln( "ExtraInfo3=" + projMgmtKVPs['VersionName'] );
				submitInfoFile.writeln( "ExtraInfo4=" + projMgmtKVPs['Description'] );
				submitInfoFile.writeln( "ExtraInfo5=" + projMgmtKVPs['UserName'] );
				
				for (var i in projMgmtKVPs)
				{
					if ( i != "DraftTemplate" )
					{
						submitInfoFile.writeln( "ExtraInfoKeyValue" + nextKVP + "=" + i + "=" + projMgmtKVPs[i] );
						nextKVP += 1;
					}
				}
                var groupBatch = false;
                if(dialog.draftCreateMovie.value)
                {
                    submitInfoFile.writeln("ExtraInfoKeyValue"+nextKVP+"=Draft_CreateSGMovie=True");
                    nextKVP += 1;
                    groupBatch = true
                }
                if(dialog.draftCreateFilmStrip.value)
                {
                    submitInfoFile.writeln("ExtraInfoKeyValue"+nextKVP+"=Draft_CreateSGFilmstrip=True");
                    nextKVP += 1;
                    groupBatch = true
                }
                
                if (groupBatch && !dependentComps)
                {
                    submitInfoFile.writeln("BatchName="+jobName);
                }
                
			}
			else if ( dialog.projectMgmtCombo.selection.toString() == "FTrack" )
			{
				submitInfoFile.writeln( "ExtraInfo0=" + projMgmtKVPs['FT_TaskName'] );
				submitInfoFile.writeln( "ExtraInfo1=" + projMgmtKVPs['FT_ProjectName'] );
				submitInfoFile.writeln( "ExtraInfo2=" + projMgmtKVPs['FT_AssetName'] );
				//EI3 gets filled in by the event plugin
				submitInfoFile.writeln( "ExtraInfo4=" + projMgmtKVPs['FT_Description'] );
				submitInfoFile.writeln( "ExtraInfo5=" + projMgmtKVPs['FT_Username'] );
				
				for (var i in projMgmtKVPs)
				{
					submitInfoFile.writeln( "ExtraInfoKeyValue" + nextKVP + "=" + i + "=" + projMgmtKVPs[i] );
					nextKVP += 1;
				}
			}
			//-----------------------------------------------------------------------------------------------------
			// NIM
			else if ( dialog.projectMgmtCombo.selection.toString() == "NIM" )
			{
				/*
				submitInfoFile.writeln( "ExtraInfo0=" + projMgmtKVPs['TaskName'] );
				submitInfoFile.writeln( "ExtraInfo1=" + projMgmtKVPs['ProjectName'] );
				submitInfoFile.writeln( "ExtraInfo2=" + projMgmtKVPs['EntityName'] );
				submitInfoFile.writeln( "ExtraInfo3=" + projMgmtKVPs['VersionName'] );
				submitInfoFile.writeln( "ExtraInfo4=" + projMgmtKVPs['Description'] );
				submitInfoFile.writeln( "ExtraInfo5=" + projMgmtKVPs['UserName'] );
				*/
				for (var i in projMgmtKVPs)
				{
					if ( i != "DraftTemplate" )
					{
						submitInfoFile.writeln( "ExtraInfoKeyValue" + nextKVP + "=" + i + "=" + projMgmtKVPs[i] );
						nextKVP += 1;
					}
				}
                var groupBatch = false;
                
                if (groupBatch && !dependentComps)
                {
                    submitInfoFile.writeln("BatchName="+jobName);
                }   
			}
			// END NIM
			//----------------------------------------------------------------------------------------------------
		}
		
		if ( dialog.useDraft.value )
		{
			submitInfoFile.writeln( "ExtraInfoKeyValue" + nextKVP + "=DraftTemplate=" + dialog.draftTemplateText.text )
			nextKVP += 1;
			submitInfoFile.writeln( "ExtraInfoKeyValue" + nextKVP + "=DraftUsername=" + dialog.draftUserText.text )
			nextKVP += 1;
			submitInfoFile.writeln( "ExtraInfoKeyValue" + nextKVP + "=DraftEntity=" + dialog.draftEntityText.text )
			nextKVP += 1;
			submitInfoFile.writeln( "ExtraInfoKeyValue" + nextKVP + "=DraftVersion=" + dialog.draftVersionText.text )
			nextKVP += 1;
			submitInfoFile.writeln( "ExtraInfoKeyValue" + nextKVP + "=DraftUploadToShotgun=" + toBooleanString(dialog.uploadDraftToShotgun.value) )
			nextKVP += 1;
			//----------------------------------------------------------------------------------------------------------------------------------------
			// NIM
			submitInfoFile.writeln( "ExtraInfoKeyValue" + nextKVP + "=DraftUploadToNim=" + toBooleanString(dialog.uploadDraftToShotgun.value) )
			nextKVP += 1;
			// END NIM
			//----------------------------------------------------------------------------------------------------------------------------------------
			submitInfoFile.writeln( "ExtraInfoKeyValue" + nextKVP + "=DraftExtraArgs=" + dialog.draftExtraArgsText.text )
			nextKVP += 1;
		}
		//==========End Shotgun/Draft===================
		submitInfoFile.close();
		
		// Create the plugin info file
		var pluginInfoFilename = tempFolder + "ae_plugin_info.job";
		var pluginInfoFile = File( pluginInfoFilename );
		pluginInfoFile.open( "w" );
		if( !submitScene )
			pluginInfoFile.writeln( "SceneFile=" + projectPath )
		
		if( !entireQueue )
		{
			pluginInfoFile.writeln( "Comp=" + compName );
			pluginInfoFile.writeln( "Output=" + outputPath );
		}
		else
			pluginInfoFile.writeln( "Comp=" );
		
		if( multiMachine )
		{
			pluginInfoFile.writeln( "MultiMachineMode=True" );
			pluginInfoFile.writeln( "MultiMachineStartFrame=" + startFrame );
			pluginInfoFile.writeln( "MultiMachineEndFrame=" + endFrame );
		}
		
		pluginInfoFile.writeln( "Version=" + version );
		pluginInfoFile.writeln( "IgnoreMissingLayerDependenciesErrors=" + toBooleanString( dialog.ignoreMissingLayers.value ) );
		pluginInfoFile.writeln( "IgnoreMissingEffectReferencesErrors=" + toBooleanString( dialog.ignoreMissingEffects.value ) );
		pluginInfoFile.writeln( "FailOnWarnings=" + toBooleanString( dialog.failOnWarnings.value ) );
		
		if( !multiMachine )
			pluginInfoFile.writeln( "MinFileSize=" + Math.round( dialog.fileSizeSlider.value ) );
			pluginInfoFile.writeln( "LocalRendering=" + toBooleanString( dialog.localRendering.value ) );

        // Fail On Existing AE Process
        pluginInfoFile.writeln( "OverrideFailOnExistingAEProcess=" + toBooleanString( dialog.OverrideFailOnExistingAEProcess.value ) );
        pluginInfoFile.writeln( "FailOnExistingAEProcess=" + toBooleanString( dialog.FailOnExistingAEProcess.value ) );

        pluginInfoFile.writeln( "MemoryManagement=" + toBooleanString( dialog.memoryManagement.value ) );
        pluginInfoFile.writeln( "ImageCachePercentage=" + Math.round( dialog.imageCachePercentageSlider.value ) );
        pluginInfoFile.writeln( "MaxMemoryPercentage=" + Math.round( dialog.maxMemoryPercentageSlider.value ) );

		// Multiprocess was introduced in version 8
		pluginInfoFile.writeln( "MultiProcess=" + toBooleanString( dialog.multiProcess.value ) );
		if( parseInt( version ) > 8 )
			pluginInfoFile.writeln( "ContinueOnMissingFootage=" + toBooleanString( dialog.missingFootage.value ) );

		pluginInfoFile.close();
		
		// Submit the job to Deadline
		var args = "\"" + submitInfoFilename + "\" \"" + pluginInfoFilename + "\"";
		if( submitScene )
			args = args + " \"" + projectPath + "\"";
		
		//results = results + callDeadlineCommand( args ) + "\n\n";
		var tempResults = callDeadlineCommand( args );
		if( layers )
		{
			if( tempResults.indexOf( "Result=Success" ) >= 0 )
				results += jobName + ": submitted successfully\n";
			else
				results += jobName + ": submission failed\n";
		}
		else
			results = tempResults;
		
		if( dependentComps )
		{
			tempResults = tempResults.replace("\r", "");
			tempResultLines = tempResults.split("\n");
			for( var i = 0; i < tempResultLines.length; i ++ )
			{
				var jobIdIndex = tempResultLines[i].indexOf( "JobID=" );
				if( jobIdIndex >= 0 )
				{
					dependentJobId = tempResultLines[i].substring( jobIdIndex + 6 );
					break;
				}
			}
		}
		
		return dependentJobId;
	}


	function SubmitLayersToDeadline()
	{
		var activeComp = app.project.activeItem;
		
		if ( activeComp === null || activeComp === undefined )
		{
			alert( "You do not have a composition selected. Please close this window and select a composition and layers first." );
		}
		else if ( activeComp.selectedLayers.length == 0 )
		{
			alert( "You do not have any selected layers in the active composition!" );
		}
		else
		{
			for( i = 1; i <= app.project.renderQueue.numItems; ++i )
			{
				if( activeComp == app.project.renderQueue.item( i ).comp && app.project.renderQueue.item( i ).status == RQItemStatus.QUEUED )
				{
					alert( "The active comp is already in the render queue and is set to render. Please close this window and remove the comp from the render queue." );
					return;
				}
			}
			
			//get the saved defaults from the ini file
			var initPreserveCam = parseBool( getIniSetting ( "Layers_PreserveCamera", "true" ) );
			var initPreserveLights = parseBool( getIniSetting ( "Layers_PreserveLights", "true" ) );
			var initPreserveAdjustments = parseBool( getIniSetting( "Layers_PreserveAdjustments", "true" ) );
			var initPreserveAV = parseBool( getIniSetting( "Layers_PreserveAV", "true" ) );
			var initPreserveUnselected = parseBool( getIniSetting( "Layers_PreserveUnselected", "true" ) );
			var initRenderSettings = getIniSetting( "Layers_RenderSettings", "" );
			var initOutputModule = getIniSetting( "Layers_OutputModule", "" );
			var initOutputFolder = getIniSetting( "Layers_OutputFolder", "" );
			var initOutputFormat = getIniSetting( "Layers_OutputFormat", "[compName]_[layerName].[fileExtension]" );
			var initUseSubfolders = parseBool( getIniSetting( "Layers_UseSubfolders", "false" ) );
			var initSubfolderFormat = getIniSetting( "Layers_SubfolderFormat", "[layerName]" );
			var initLayerNameParse = getIniSetting( "Layers_NameParsing", "" );
			
			layerCheckBoxSize = [180, 20];
			layerLabelSize = [105, 20];
			layerTextSize = [296, 18];
			layerBrowseTextSize = [251, 18];
			layerButtonSize = [36, 20];
			layerComboSize = [296, 20];
			
			var layersDialog = new Window( 'dialog', 'Submit Selected Layers to Deadline' );
			
			// Description
			layersDialog.descriptionGroup = layersDialog.add( 'group', undefined );
			layersDialog.descriptionGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			layersDialog.descriptionLabel = layersDialog.descriptionGroup.add( 'statictext', undefined, 'This will submit all selected layers to Deadline as separate Jobs. Settings set in the submission dialog will be used, but comps currently in the render queue will NOT be submitted by this dialog.', {multiline: true} );
			layersDialog.descriptionLabel.size = [400, 40];
			
			// Panel containing layer preservation related settings (if enabled, these layers will be rendered with each of the selected layers)
			layersDialog.preservePanel = layersDialog.add( 'panel', undefined, 'Choose Unselected Layers To Include In The Render' );
			layersDialog.preservePanel.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			
			layersDialog.preserveUnselectedGroup = layersDialog.preservePanel.add( 'group', undefined );
			layersDialog.preserveUnselectedGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			layersDialog.preserveUnselected = layersDialog.preserveUnselectedGroup.add( 'checkbox', undefined, 'All Unselected Layers' );
			layersDialog.preserveUnselected.value = initPreserveUnselected;
			layersDialog.preserveUnselected.size = layerCheckBoxSize;
			layersDialog.preserveUnselected.helpTip = 'Render all unselected layers with each of the selected layers.';
			layersDialog.preserveUnselected.onClick = function()
			{
				var enableOthers = !layersDialog.preserveUnselected.value;
				
				layersDialog.preserveCamera.enabled = enableOthers;
				layersDialog.preserveLights.enabled = enableOthers;
				layersDialog.preserveAV.enabled = enableOthers;
				layersDialog.preserveAdjustments.enabled = enableOthers;
			}
			
			layersDialog.preserveCameraGroup = layersDialog.preservePanel.add( 'group', undefined );
			layersDialog.preserveCameraGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			layersDialog.preserveCamera = layersDialog.preserveCameraGroup.add( 'checkbox', undefined, 'Topmost Camera Layer' );
			layersDialog.preserveCamera.value = initPreserveCam;
			layersDialog.preserveCamera.enabled = !initPreserveUnselected;
			layersDialog.preserveCamera.size = layerCheckBoxSize;
			layersDialog.preserveCamera.helpTip = 'Render the topmost camera layer with each of the selected layers.';
			layersDialog.preserveLights = layersDialog.preserveCameraGroup.add( 'checkbox', undefined, 'Light Layers' );
			layersDialog.preserveLights.value = initPreserveLights;
			layersDialog.preserveLights.enabled = !initPreserveUnselected;
			layersDialog.preserveLights.size = layerCheckBoxSize;
			layersDialog.preserveLights.helpTip = 'Render the light layers with each of the selected layers.';
			
			layersDialog.preserveAVGroup = layersDialog.preservePanel.add( 'group', undefined );
			layersDialog.preserveAVGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			layersDialog.preserveAV = layersDialog.preserveAVGroup.add( 'checkbox', [20, 30, 210, 50], 'Audio/Video Layers' );
			layersDialog.preserveAV.value = initPreserveAV;
			layersDialog.preserveAV.enabled = !initPreserveUnselected;
			layersDialog.preserveAV.size = layerCheckBoxSize;
			layersDialog.preserveAV.helpTip = 'Render the Audio/Video layers with each of the selected layers.';
			layersDialog.preserveAdjustments = layersDialog.preserveAVGroup.add( 'checkbox', [210, 30, 370, 50], 'Adjustment Layers' );
			layersDialog.preserveAdjustments.value = initPreserveAdjustments;
			layersDialog.preserveAdjustments.enabled = !initPreserveUnselected;
			layersDialog.preserveAdjustments.size = layerCheckBoxSize;
			layersDialog.preserveAdjustments.helpTip = 'Render the Adjustment layers with each of the selected layers.';
			
			// Optional panel.
			layersDialog.optionalPanel = layersDialog.add( 'panel', undefined, 'Optional Settings' );
			layersDialog.parseLayerNamesGroup = layersDialog.optionalPanel.add( 'group', undefined );
			layersDialog.parseLayerNamesGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			layersDialog.parseLayerNamesLabel = layersDialog.parseLayerNamesGroup.add( 'statictext', undefined, 'Layer Name Parsing' )
			layersDialog.parseLayerNamesLabel.size = layerLabelSize;
			layersDialog.parseLayerNamesLabel.helpTip = 'Allows you to specify how the layer names should be formatted. You can then grab parts of the formatting and stick them in either the output name or the subfolder format box with square brackets. So, for example, if you are naming your layers something like "ops024_a_diff", you could put "<graphic>_<layer>_<pass>" in this box. Then in the subfoler box, you could put "[graphic]\\[layer]\\v001\\[pass]", which would give you "ops024\\a\\v001\\diff" as the subfolder structure.';
			layersDialog.parseLayerNames = layersDialog.parseLayerNamesGroup.add( 'edittext', undefined, initLayerNameParse )
			layersDialog.parseLayerNames.size = layerTextSize;
			
			// Output settings to use for the comps (needed since we're not grabbing stuff already in the queue)
			layersDialog.outputPanel = layersDialog.add( 'panel', undefined, 'Output Settings' );
			
			layersDialog.renderSettingsGroup = layersDialog.outputPanel.add( 'group', undefined );
			layersDialog.renderSettingsGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			layersDialog.renderSettingsLabel = layersDialog.renderSettingsGroup.add( 'statictext', undefined, 'Render Settings' );
			layersDialog.renderSettingsLabel.size = layerLabelSize;
			layersDialog.renderSettingsLabel.helpTip = 'Select which render settings to use.';
			layersDialog.renderSettings = layersDialog.renderSettingsGroup.add( 'dropdownlist', undefined );
			layersDialog.renderSettings.size = layerComboSize;
			
			layersDialog.outputModuleGroup = layersDialog.outputPanel.add( 'group', undefined );
			layersDialog.outputModuleGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			layersDialog.outputModuleLabel = layersDialog.outputModuleGroup.add( 'statictext', undefined, 'Output Module' );
			layersDialog.outputModuleLabel.size = layerLabelSize;
			layersDialog.outputModuleLabel.helpTip = 'Select which output module to use.';
			layersDialog.outputModule = layersDialog.outputModuleGroup.add( 'dropdownlist', undefined );
			layersDialog.outputModule.size = layerComboSize;
			
			layersDialog.outputFormatGroup = layersDialog.outputPanel.add( 'group', undefined );
			layersDialog.outputFormatGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			layersDialog.outputFormatLabel = layersDialog.outputFormatGroup.add( 'statictext', undefined, 'Output Format' );
			layersDialog.outputFormatLabel.size = layerLabelSize;
			layersDialog.outputFormatLabel.helpTip = 'Specify how the output file name should be formatted.';
			layersDialog.outputFormat = layersDialog.outputFormatGroup.add( 'edittext', undefined, initOutputFormat );
			layersDialog.outputFormat.size = layerTextSize;
			
			layersDialog.outputFolderGroup = layersDialog.outputPanel.add( 'group', undefined );
			layersDialog.outputFolderGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			layersDialog.outputFolderLabel = layersDialog.outputFolderGroup.add( 'statictext', undefined, 'Output Folder' );
			layersDialog.outputFolderLabel.size = layerLabelSize;
			layersDialog.outputFolderLabel.helpTip = 'Specify where the output files should be rendered to.';
			layersDialog.outputFolder = layersDialog.outputFolderGroup.add( 'edittext', undefined, initOutputFolder );
			layersDialog.outputFolder.size = layerBrowseTextSize;
			layersDialog.browseButton = layersDialog.outputFolderGroup.add( 'button', undefined, '...' );
			layersDialog.browseButton.size = layerButtonSize;
			layersDialog.browseButton.onClick = function()
			{
				var origValue = layersDialog.outputFolder.text;
				var newValue = callDeadlineCommand( "-selectdirectory \"" + origValue + "\"" ).replace( "\n", "" ).replace( "\r", "" );
				if( newValue != "" )
					layersDialog.outputFolder.text = newValue;
				
				//var outFolder = Folder.selectDialog();
				//if ( outFolder != null )
					//layersDialog.outputFolder.text = outFolder.fsName;
			}
			
			layersDialog.useSubfoldersGroup = layersDialog.outputPanel.add( 'group', undefined );
			layersDialog.useSubfoldersGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			layersDialog.useSubfolders = layersDialog.useSubfoldersGroup.add( 'checkbox', undefined, 'Use Subfolders' );
			layersDialog.useSubfolders.value = initUseSubfolders;
			layersDialog.useSubfolders.size = layerLabelSize;
			layersDialog.useSubfolders.helpTip = ' Enable this to render each layer to its own subfolder. If this is enabled, you must also specify the subfolder format.';
			layersDialog.useSubfolders.onClick = function()
			{
				layersDialog.subfolderFormat.enabled = layersDialog.useSubfolders.value;
			}
			layersDialog.subfolderFormat = layersDialog.useSubfoldersGroup.add( 'edittext', undefined, initSubfolderFormat );
			layersDialog.subfolderFormat.enabled = initUseSubfolders;
			layersDialog.subfolderFormat.size = layerTextSize;
			
			//need to grab the values from the dropdown list (make a temp addition to render queue and grab from there)
			var rqItem = app.project.renderQueue.items.add( app.project.activeItem );
			
			for( var i=0; i < rqItem.templates.length; i++ )
			{
				if ( rqItem.templates[i].substring(0, 7) != '_HIDDEN' )
					layersDialog.renderSettings.add( "item", rqItem.templates[i] );
			}
			var item = layersDialog.renderSettings.find( initRenderSettings );
			if (  item != null )
				layersDialog.renderSettings.selection = item;
			else if( rqItem.templates.length > 0 )
			{
				var item = layersDialog.renderSettings.find( rqItem.templates[0] );
				if (  item != null )
					layersDialog.renderSettings.selection = item;
			}
		
			//available output modules
			var outMod = rqItem.outputModule(1);
			for( var i=0; i < outMod.templates.length; i++ )
			{
				if ( outMod.templates[i].substring(0, 7) != '_HIDDEN' )
					layersDialog.outputModule.add( "item", outMod.templates[i] );
			}
			item = layersDialog.outputModule.find( initOutputModule );
			if (  item != null )
				layersDialog.outputModule.selection = item;
			else if( outMod.templates.length > 0 )
			{
				item = layersDialog.outputModule.find( outMod.templates[0] );
				if (  item != null )
					layersDialog.outputModule.selection = item;
			}
			
			rqItem.remove();
			
			// button group
			layersDialog.buttonGroup = layersDialog.add( 'group', undefined );
			layersDialog.buttonGroup.alignment = [ScriptUI.Alignment.FILL, ScriptUI.Alignment.TOP];
			//layersDialog.buttonLabel = layersDialog.buttonGroup.add( 'statictext', undefined, '' );
			//layersDialog.buttonLabel.size = [262, 20];
			layersDialog.progressBar = layersDialog.buttonGroup.add( 'progressbar', undefined, '' );
			layersDialog.progressBar.size = [262, 20];
			layersDialog.progressBar.value = 0;
			
			//submit button - goes through the selected layers and submits them
			layersDialog.submitButton = layersDialog.buttonGroup.add( 'button', undefined, 'Submit' );
			layersDialog.submitButton.onClick = function()
			{
				results = "";
				errors = "";
				
				if( layersDialog.renderSettings.selection == null )
					errors += "Please select an entry for the Render Settings.\n";
				
				if( layersDialog.outputModule.selection == null )
					errors += "Please select an entry for the Output Module.\n";
				
				if( errors != "" )
				{
					errors += "\nPlease fix these errors before submitting your job to Deadline.";
					alert( errors );
					return;
				}
				
				//Grabs the layer parsing string if it's there
				var parsingRegexs = new Array()
				parseString = layersDialog.parseLayerNames.text;
				parseString = parseString.replace( /([\(\)\[\]\{\}\.\*\+\?\|\/\\])/g, '\\$1' );//replace special regex chars with their escaped equivalents
				regexp = /<(.*?)>/;
				
				while ( parseString.match( regexp ) !== null )
				{
					var tempString = parseString;
					var varName = RegExp.$1;
					
					replaceRegex = new RegExp( "<" + varName + ">", "ig" );
					tempString = tempString.replace( replaceRegex, "(.*?)" );
					tempString = tempString.replace( /<.*?>/g, ".*?" );
					parsingRegexs[varName] = "^" + tempString + "$";
					
					parseString = parseString.replace( replaceRegex, ".*?");
				}
				
				//create a duplicate comp, so we don't accidentally mess with settings
				var duplicateComp = activeComp.duplicate();
				
				var renderCam = layersDialog.preserveCamera.value;
				var renderLights = layersDialog.preserveLights.value;
				var renderAdjustments = layersDialog.preserveAdjustments.value;
				var renderAV = layersDialog.preserveAV.value;
				var renderUnselected = layersDialog.preserveUnselected.value;
				var topCam = true;
				var invalidCharLayers = "";
				
				duplicateComp.name = activeComp.name;
				
				//go through all the layers in the active comp and disable the ones we're not ALWAYS rendering
				for ( var i=1; i <= duplicateComp.layers.length; i++ )
				{
					var currLayer = duplicateComp.layers[i];

					if ( activeComp.layers[i].selected )
						currLayer.selected = true;
					
					//if( currLayer("Camera Options") != null && renderCam && topCam ) //only topmost camera layer is rendered (if option is specified)
					if( currLayer.matchName == "ADBE Camera Layer" && renderCam && topCam ) //only topmost camera layer is rendered (if option is specified)
					{
						topCam = false;
						//do nothing else, since we want this layer enabled
					}
					else
					{
						//figure out if this is an unselected layer we are going to render
						alwaysRender = renderUnselected; //always render if unselected and option specified
						//alwaysRender = alwaysRender || (currLayer("Light Options") != null && renderLights); //always render if light layer and option specified
						alwaysRender = alwaysRender || (currLayer.matchName == "ADBE Light Layer" && renderLights); //always render if light layer and option specified
						alwaysRender = alwaysRender || (currLayer.adjustmentLayer && renderAdjustments); //always render if adjustment layer and option specified
						alwaysRender = alwaysRender || ((currLayer.hasVideo || currLayer.hasAudio) && renderAV); //always render if AV layer and option specified
						
						if ( currLayer.selected || !alwaysRender ) //unless one of the above conditions were met (or if layer is selected), disable layer
						{
							currLayer.enabled = false;
							currLayer.audioEnabled = false;
							
							fixedLayerName = currLayer.name.replace( /([\*\?\|:\"<>\/\\%£])/g, '_' ); //replace invalid path characters with an underscore
								
							if(fixedLayerName != currLayer.name)
								invalidCharLayers = invalidCharLayers + currLayer.name + "\n";
						}
					}
				}
				
				if( invalidCharLayers.length == 0 || confirm("The following layers contain invalid path characters:\n\n" + invalidCharLayers + "\nThe following are considered invalid characters: *, ?, |, :, \", <, >, /, \\, %, £\nIf you chose to continue, invalid characters in the output path will be replaced by an underscore '_'. \nContinue?"))
				{
					var restoreProjectPath = false;
					var oldProjectPath = projectPath;
					
					// See if we need to save the current scene as an aepx file first.
					if( dialog.exportAsXml.value && projectPath.indexOf( ".aep", projectPath.length - 4 ) != -1 )
					{
						app.project.save( File( projectPath.substring( 0, projectPath.length - 4 ) + ".aepx" ) );
						projectPath = app.project.file.fsName;
						restoreProjectPath = true;
					}
					
					layersDialog.progressBar.value = 0;
					
					var submitCount = 0;
					var selectedRenderSettings = layersDialog.renderSettings.selection;
					var selectedOutputModule = layersDialog.outputModule.selection;
					
					//go through selected layers and render them one at a time
					for ( var i=0; i < duplicateComp.selectedLayers.length; i++ )
					{
						layersDialog.progressBar.value = ((i+1)*100) / (duplicateComp.selectedLayers.length+1);
						
						var currLayer = duplicateComp.selectedLayers[i];
						
						//if it's already enabled, it means we're always rendering the layer, so skip it (unless it's the last one and we haven't submitted anything yet)
						if ( !currLayer.enabled || ( submitCount == 0 && i == duplicateComp.selectedLayers.length ) ) 
						{
							currLayer.enabled = true;
							if ( currLayer.hasAudio )
								currLayer.audioEnabled = true;
							
							var parsedTokens = new Array();
							var layerName = currLayer.name;
							for ( var varName in parsingRegexs )
							{
								parsingRE = new RegExp( parsingRegexs[varName], "i" );
								if ( !parsingRE.test( layerName ) )
								{
									alert( "The layer name \"" + layerName + "\" does not match the parsing string.\nParsing will not be performed for this layer name." );
									break;
								}
								else
								{
									parsedTokens[varName] = RegExp.$1;
								}
							}
							
							var rqItem = app.project.renderQueue.items.add( duplicateComp );
							rqItem.applyTemplate( selectedRenderSettings );
							
							var outMod = rqItem.outputModule( 1 );
							outMod.applyTemplate( selectedOutputModule );
							
							var outputFolder = trim( layersDialog.outputFolder.text );
							// \ / : * ? " < > |
							var fixedLayerName = currLayer.name.replace( /([\*\?\|:\"<>\/\\%£])/g, '_' ); //replace invalid path characters with an underscore
							
							if ( layersDialog.useSubfolders.value )
							{	
								outputFolder = outputFolder + "/" + trim( layersDialog.subfolderFormat.text );
								outputFolder = outputFolder.replace( "\[layerName\]", trim( fixedLayerName ) );
								
								for( var varName in parsedTokens )
									outputFolder = outputFolder.replace( "\[" + varName + "\]", trim( parsedTokens[varName] ) );
								//alert(outputFolder);
								//set the folder as the file for the output module temporarily - this makes it replace the [compName], etc. templates.
								//the dummy extension is added, since AE will automatically add an extension if one isn't provided.
								outMod.file = new Folder( outputFolder + "._DUMMY_" );
								outputFolder = outMod.file.fsName;
								outputFolder = outputFolder.replace( "._DUMMY_", "" );
								
								//creates the subfolder
								subFolder = new Folder( outputFolder );
								subFolder.create();
							}
							
							var outputFormat = layersDialog.outputFormat.text;
							outputFormat = outputFormat.replace( "\[layerName\]", fixedLayerName );
							for( var varName in parsedTokens )
								outputFormat  = outputFormat.replace( "\[" + varName + "\]", parsedTokens[varName] );
							
							outMod.file = new File( outputFolder + "/" + outputFormat );
							
							//need to save project between every pass, since we're submitting the scene file (otherwise it'll just render the same thing each time)
							app.project.save( app.project.file );
							
							//SubmitComp( rqItem, true, activeComp.name + "_" + currLayer.name );
							SubmitComp( app.project.file.fsName, rqItem, true, activeComp.name + "_" + fixedLayerName );
							submitCount++;
							
							rqItem.remove();
							
							currLayer.enabled = false;
							currLayer.audioEnabled = false;
						}
					}
					
					layersDialog.progressBar.value = 100;
					
					// Restore the original project path if necessary.
					if( restoreProjectPath )
					{
						app.project.save( app.project.file );
						app.open( File( oldProjectPath ) )
					}
				}
				
				//remove the duplicate comp, and save project again
				duplicateComp.remove();
				app.project.save( app.project.file );
				
				if( results.length > 0 )
					alert( results );
			}
			
			//close button - saves current settings as defaults in the .ini file
			layersDialog.closeButton = layersDialog.buttonGroup.add( 'button', undefined, 'Close' );
			layersDialog.closeButton.onClick = function()
			{
				setIniSetting( "Layers_PreserveCamera", toBooleanString( layersDialog.preserveCamera.value ) );
				setIniSetting( "Layers_PreserveLights", toBooleanString( layersDialog.preserveLights.value ) );
				setIniSetting( "Layers_PreserveAdjustments", toBooleanString( layersDialog.preserveAdjustments.value ) );
				setIniSetting( "Layers_PreserveAV", toBooleanString( layersDialog.preserveAV.value ) );
				setIniSetting( "Layers_PreserveUnselected", toBooleanString( layersDialog.preserveUnselected.value ) );
				
				if ( layersDialog.renderSettings.selection != undefined )
					setIniSetting( "Layers_RenderSettings", layersDialog.renderSettings.selection.toString() );

				if ( layersDialog.outputModule.selection != undefined )
					setIniSetting( "Layers_OutputModule", layersDialog.outputModule.selection.toString() );
					
				setIniSetting( "Layers_OutputFolder", layersDialog.outputFolder.text );
				setIniSetting( "Layers_OutputFormat", layersDialog.outputFormat.text );
				setIniSetting( "Layers_UseSubfolders", toBooleanString( layersDialog.useSubfolders.value ) );
				setIniSetting( "Layers_SubfolderFormat", layersDialog.subfolderFormat.text );
				setIniSetting( "Layers_NameParsing", layersDialog.parseLayerNames.text);
				
				layersDialog.close();
			}
			
			layersDialog.show();
		}
	}


	function GetQueuedCompCount()
	{
		var count = 0;
		for( i = 1; i <= app.project.renderQueue.numItems; ++i )
		{
			if( app.project.renderQueue.item( i ).status == RQItemStatus.QUEUED )
				count = count + 1;
		}
		return count;
	}
	
	function IsMovieFormat( extension )
	{
		var movieFormat = false;
		if( extension != null )
		{
			var cleanExtension = extension.toLowerCase();
			// These formats are all the ones included in DFusion, as well
			// as all the formats in AE that don't contain [#####].
			if( cleanExtension == "vdr" || cleanExtension == "wav" || cleanExtension == "dvs" ||
				cleanExtension == "fb"  || cleanExtension == "omf" || cleanExtension == "omfi"||
				cleanExtension == "stm" || cleanExtension == "tar" || cleanExtension == "vpr" ||
				cleanExtension == "gif" || cleanExtension == "img" || cleanExtension == "flc" ||
				cleanExtension == "flm" || cleanExtension == "mp3" || cleanExtension == "mov" ||
				cleanExtension == "rm"  || cleanExtension == "avi" || cleanExtension == "wmv" ||
				cleanExtension == "mpg" || cleanExtension == "m4a" || cleanExtension == "mpeg" )
			{
				movieFormat = true;
			}
		}
		return movieFormat;
	}
	
	function Floor( x )
	{
		return ( x - ( x % 1 ) );
	}
	
	function deadlineStringToArray( str )
	{
		str = str.replace( "\r", "" );
		var tempArray = str.split( '\n' );
		var array;
		
		if( tempArray.length > 0 )
		{
			array = new Array( tempArray.length - 1 );
		
			// Only loop to second last item in tempArray, because the last item is always empty.
			for( var i = 0; i < tempArray.length - 1; i ++ )
				array[i] = tempArray[i].replace( "\n", "" ).replace( "\r", "" );
		}
		else
			array = new Array( 0 );
		
		return array;
	}
	
	function isLocal( path )
	{
		if( path.length >= 2 )
		{
			var drive = path.substring( 0, 1 ).toLowerCase();
			if( drive == "c" || drive == "d" || drive == "e" )
				return true;
		}
		
		return false;
	}
	
	function setSliderValue( text, min, max, slider )
	{
		var intValue = parseInt( text );
		var clampedValue = clampValue( intValue, min, max );
		if( intValue != clampedValue )
			this.text = clampedValue + ""
		slider.value = clampedValue;
	}
	
	function clampValue( value, minValue, maxValue )
	{
		//alert( value + '' );
		if( isNaN( value ) || value < minValue )
			return minValue;
		if( value > maxValue )
			return maxValue;
		//return value;
		//alert( Math.round( value ) + '' );
		return Math.round( value );
	}
	
	function toBooleanString( value )
	{
		if( value )
			return "true";
		else
			return "false";
	}
	
	function parseBool( value )
	{
		value = value.toLowerCase();
		if( value == "1" || value == "t" || value == "true" )
			return true;
		else
			return false;
	}
	
	function trim( stringToTrim )
	{
		return stringToTrim.replace( /^\s+|\s+$/g, "" );
	}
	
	function replaceAll( str, searchStr, replaceStr )
	{
		var strReplaceAll = str;
		var intIndexOfMatch = strReplaceAll.indexOf( searchStr );
		while (intIndexOfMatch != -1)
		{
			strReplaceAll = strReplaceAll.replace( searchStr, replaceStr );
			intIndexOfMatch = strReplaceAll.indexOf( searchStr );
		}
		return strReplaceAll;
	}
	
	// Sets the global function above so that deadlinecommand only gets called once
	// to get the settings directory.
	function getIniFile()
	{
		if( AfterEffectsIniFilename == "" )
		{
			var prefix = callDeadlineCommand("GetSettingsDirectory");
			prefix = prefix.replace("\n","");
			prefix = prefix.replace("\r","");
			
			if (system.osName == "MacOS")
				AfterEffectsIniFilename = prefix + "//ae_submission.ini";
			else
				AfterEffectsIniFilename = prefix + "\\ae_submission.ini";
		}
		
		return AfterEffectsIniFilename;
	}   
	
	function getIniSetting( key, defaultValue )
	{
		var value = defaultValue;
		var filename;
		
		filename = getIniFile();
		iniFile = File( filename);
		if( iniFile.exists )
		{
			iniFile.open( 'r' );
			while( ! iniFile.eof )
			{
				var line = iniFile.readln();
				var index = line.indexOf( "=" );
				if( index > 0 )
				{
					var currKey = line.substring( 0, index );
					if( currKey == key )
					{
						value = line.substring( index + 1 );
						break;
					}
				}
			}
			iniFile.close();
		}
		
		return value;
	}
	
	function setIniSetting( key, value )
	{
		var iniFileContentsString = "";
		var filename;
	
		filename = getIniFile();
		
		iniFile = File( filename );
		if( iniFile.exists )
		{
			iniFile.open( 'r' );
			iniFileContentsString = iniFile.read() + "\n";
			iniFile.close();
		}

				
		var iniFileContents = deadlineStringToArray( iniFileContentsString );

		newIniFile = File( filename );
		newIniFile.open( 'w' );
		for( var i = 0; i < iniFileContents.length; i ++ )
		{
			var line = iniFileContents[i];
			if( line.length > 0 )
			{
				var index = line.indexOf( "=" );
				if( index > 0 )
				{
					var currKey = line.substring( 0, index );
					if( currKey != key )
						newIniFile.writeln( line );
				}
			}
		}
				
		newIniFile.writeln( key + "=" + value );
		newIniFile.close();
	}
} 