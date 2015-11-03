# NIM NukeStudio Connector
try:
	import sys
	import hiero.core
	
	sys.path.append('[NIM_CONNECTOR_ROOT]')
	sys.path.append('[NIM_CONNECTOR_ROOT]/plugins/Nuke/Python/Startup/nim_hiero_connector')
	hiero.core.addPluginPath('[NIM_CONNECTOR_ROOT]/plugins/Nuke/Python/Startup/nim_hiero_connector')
	
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
