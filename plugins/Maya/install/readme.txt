Step 1 - Install the NIM module:

	Copy the [NIM_CONNECTOR_ROOT]/plugins/Maya/install/nim.mod file to your module path.

	The default locations for ``MAYA_MODULE_PATH` are: (Examples shown for Maya 2016)

	Windows:

		[DRIVE]:/Users/[USERNAME]/My Documents/maya/2016/modules
		[DRIVE]:/Users/[USERNAME]/My Documents/maya/modules
		C:/Program Files/Common Files/Autodesk Shared/Modules/maya/2016
		C:/Program Files/Common Files/Autodesk Shared/Modules/maya
		[MAYA INSTALLATION DIRECTORY]/modules

	OSX & Linux:

		$MAYA_APP_DIR/maya/2016/modules
		$MAYA_APP_DIR/maya/modules
		/usr/autodesk/modules/maya/2016
		/usr/autodesk/modules/maya
			OSX MAYA_APP_DIR = ~<username>/Library/Preferences/Autodesk/maya
			LINUX MAYA_APP_DIR = ~<username>/maya

	Edit the nim.mod file and replace [NIM_CONNECTOR_ROOT] with the full path to the NIM Connector root folder.


Step 2 - Install/Update userSetup.mel:

	Maya’s userSetup.mel file can be found in the following locations:
		Windows: [DRIVE]:/Users/[USERNAME]/My Documents/maya/scripts
		OSX: /Users/[USERNAME]/Library/Preferences/Autodesk/maya/scripts
		Linux: /home/[USERNAME]/maya/scripts

	If you do not have a userSetup.mel, copy the file [NIM_CONNECTOR_ROOT]/plugins/Maya/setup/userSetup.mel to your maya/scripts location.

	If you have an existing userSetup.mel file, add the following line to the end of the userSetup.mel to invoke the NIM menu at startup:
		n_nimMenu;
		