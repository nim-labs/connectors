'''
# NIM NukeStudio Connector
try:
	import sys
	import hiero.core
	
	sys.path.append('I:/VAULT/modules/nim_dev')
	sys.path.append('I:/VAULT/modules/nim_dev/plugins/Nuke/Python/Startup/nim_hiero_connector')
	hiero.core.addPluginPath('I:/VAULT/modules/nim_dev/plugins/Nuke/Python/Startup/nim_hiero_connector')
	
	from nimNukeStudioMenu import *
	from nimHieroConnector import *
	from nimHieroExport import *
	from nimShotProcessor import *
	from nimShotProcessorUI import *
	from nimProcessorUI import *
except:
	pass
# END NIM NukeStudio Connector
'''