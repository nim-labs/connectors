
Below are 2 sets of instructions for NukeStudio and Nuke.  
If you are using NukeStudio and Nuke you only need to do the NukeStudio installation.


NukeStudio Installation:
	
	STEP 1 - Copy (2) init.py files:

		NukeStudio uses two init.py files to create the various UI integrations.
		The default paths for these files are in the following locations:

		.nuke Folder Location

			Windows: [DRIVE]:/Users/[USERNAME]/.nuke
			OSX: ~/.nuke
			Linux: ~/.nuke
		
		Startup Folder Location

			Windows: [DRIVE]:/Users/[USERNAME]/.nuke/Python/Startup
			OSX: ~/.nuke/Python/Startup
			Linux: ~/.nuke/Python/Startup

		Copy the file [NIM_CONNECTOR_ROOT]/plugins/Nuke/install/init.py to your .nuke folder location

		Copy the file [NIM_CONNECTOR_ROOT]/plugins/Nuke/install/Python/Startup/init.py to your .nuke/Python/Startup folder location



	STEP 2 - Edit (2) init.py files:

		Edit the .nuke/init.py and .nuke/Python/Startup/init.py files to update the [NIM_CONNECTOR_ROOT] with the proper path to your studios NIM connector folder.

			** NOTE: Be sure to use forward slashes “/” for all directory separators in the path

		If you have an init.py file already at either location, copy the contents of the corresponding init.py file to the end of the existing file, updating the paths as instructed.

			** NOTE: If you do not see the .nuke folder, either you have not run NukeStudio or Nuke for the first time or you may need to enable viewing of hidden files.

		If a .nuke/Python/Startup directory does exist you can manually make the needed folder structure in the correct location.



	STEP 3 - Export Presets:
		NIM ships with a default export template for the NIM: Process as Shots export processor.

		To install copy the folder [NIM_CONNECTOR_ROOT]/plugins/Nuke/vX.X/TaskPresets to your local .nuke folder location.

		Windows: [DRIVE]:/Users/[USERNAME]/.nuke/TaskPresets
		OSX: ~/.nuke/TaskPresets
		Linux: ~/.nuke/TaskPresets

			** NOTE: As of NukeStudio 10.5 there is a new preset format.  
					 Please copy the TaskPresets folder from the correspoding Nuke version.


Nuke Installation:

	STEP 1 - Copy (1) init.py files:

		NukeStudio uses two init.py files to create the various UI integrations.
		The default paths for these files are in the following locations:

		.nuke Folder Location

			Windows: [DRIVE]:/Users/[USERNAME]/.nuke
			OSX: ~/.nuke
			Linux: ~/.nuke
		
		Startup Folder Location

			Windows: [DRIVE]:/Users/[USERNAME]/.nuke/Python/Startup
			OSX: ~/.nuke/Python/Startup
			Linux: ~/.nuke/Python/Startup

		Copy the file [NIM_CONNECTOR_ROOT]/plugins/Nuke/install/init.py to your .nuke folder location



	STEP 2 - Edit (1) init.py files:

		Edit the .nuke/init.py and .nuke/Python/Startup/init.py files to update the [NIM_CONNECTOR_ROOT] with the proper path to your studios NIM connector folder.

			** NOTE: Be sure to use forward slashes “/” for all directory separators in the path

		If you have an existing init.py file, copy the contents of the corresponding init.py file to the end of the existing file, updating the paths as instructed.

			** NOTE: If you do not see the .nuke folder, either you have not run Nuke for the first time or you may need to enable viewing of hidden files.