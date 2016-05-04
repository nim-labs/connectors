# NIM NukeStudio Connector

try:
	import sys
	import hiero.core
	
	#UPDATE [NIM_CONNECTOR_ROOT] with the path to your NIM Connectors root folder
	nim_root = '[NIM_CONNECTOR_ROOT]' 
	
	sys.path.append(nim_root)
	try:
		if int(hiero.core.env['VersionMajor']) >= 10:
			print "Loading NIM Hiero Connector for Hiero 10.XvX"
			sys.path.append(nim_root+'/plugins/Nuke/v10/Python/Startup/nim_hiero_connector')
			hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v10/Python/Startup/nim_hiero_connector')
	except:
		print "Loading NIM Hiero Connector for Hiero 9.XvX"
		sys.path.append(nim_root+'/plugins/Nuke/v09/Python/Startup/nim_hiero_connector')
		hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v09/Python/Startup/nim_hiero_connector')

	from nimNukeStudioMenu import *
	from nimHieroConnector import *
	from nimHieroExport import *
	from nimShotProcessor import *
	from nimShotProcessorUI import *
	from nimProcessorUI import *
except:
	print "Could not load NIM Connector:", sys.exc_info()[0]
	pass

# END NIM NukeStudio Connector
