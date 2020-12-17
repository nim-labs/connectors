
NIM Studio Management - NIM Connectors :

	The NIM Connectors are designed to be a flexible set of plugins and core API functions for users to integrate their applications with the NIM Studio Mangement platform. The connectors require a NIM VM to be installed for use.  

	More information about NIM and a free 30 day trial can be found at:
	https://nim-labs.com


	The Connector API consists of a suite of functions to communicate with a NIM server, retrieve and store data, and can be used to easily save, publish and version up files, navigate NIM managed project structures, upload review items, and more. 

	Full Connector API documentation can be found at:
	https://nim-labs.com/docs/NIM/html/api_python.html


	The plugins are application specific plugins and scripts to automate tasks inside of the targeted DCC applications. NIM comes with connectors for major DCC applications and renderfarm integration. The NIM Connectors in 3rd party DCC applications support many file management features including basic functionality such as open, import, save, and save as operations. These features extend to advanced options including referencing, timeline export, and more depending upon the application. The NIM Connectors support automatic version control, pre-determined naming conventions, and loading of published files. Renderfarm support enables automatic logging of renders, dailies generation and uploading to NIM.

	Full documentation for the NIM Connector plugins can be found at:
	https://nim-labs.com/docs/NIM/html/index.html#connectors


	In addition to the pre-built connectors, custom connectors can be created using the NIM API directly or by expanding upon the exsting core functionality.


	The connector directory structure is separated into 4 main folders:
		css - CSS used to style connector UI elements
		img - Images used by the connector UI
		nim_core - Shared function library and API used across connectors
		plugins - Application specific plugins and scripts





