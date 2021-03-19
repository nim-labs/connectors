# NIM NukeStudio Connector

try:
	import sys
	import hiero.core
	
	#UPDATE [NIM_CONNECTOR_ROOT] with the path to your NIM Connectors root folder
	nim_root = '[NIM_CONNECTOR_ROOT]' 
	
	sys.path.append(nim_root)
	try:
		if int(hiero.core.env['VersionMajor']) >= 10:
			HieroVersionMajor = int(hiero.core.env['VersionMajor'])
			HieroVersionMinor = int(hiero.core.env['VersionMinor'])
			if HieroVersionMajor == 10 and HieroVersionMinor < 5:
				# Loading NIM Hiero Connector for Hiero 10.0vX
				sys.path.append(nim_root+'/plugins/Nuke/v10/Python/Startup/nim_hiero_connector')
				hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v10/Python/Startup/nim_hiero_connector')
			elif HieroVersionMajor == 10 and HieroVersionMinor >= 5:
				# Loading NIM Hiero Connector for Hiero 10.5vX
				sys.path.append(nim_root+'/plugins/Nuke/v10.5/Python/Startup/nim_hiero_connector')
				hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v10.5/Python/Startup/nim_hiero_connector')
			elif HieroVersionMajor == 11 and HieroVersionMinor < 3:
				# Loading NIM Hiero Connector for Hiero 11.0vX
				sys.path.append(nim_root+'/plugins/Nuke/v11/Python/Startup/nim_hiero_connector')
				hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v11/Python/Startup/nim_hiero_connector')
			elif HieroVersionMajor == 11 and HieroVersionMinor >= 3:
				# Loading NIM Hiero Connector for Hiero 11.3vX
				sys.path.append(nim_root+'/plugins/Nuke/v11.3/Python/Startup/nim_hiero_connector')
				hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v11.3/Python/Startup/nim_hiero_connector')
			elif HieroVersionMajor == 12 and HieroVersionMinor == 0:
				# Loading NIM Hiero Connector for Hiero 12.0vX
				sys.path.append(nim_root+'/plugins/Nuke/v12.0/Python/Startup/nim_hiero_connector')
				hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v12.0/Python/Startup/nim_hiero_connector')
			elif HieroVersionMajor == 12 and HieroVersionMinor >= 1:
				# Loading NIM Hiero Connector for Hiero 12.1vX
				sys.path.append(nim_root+'/plugins/Nuke/v12.1/Python/Startup/nim_hiero_connector')
				hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v12.1/Python/Startup/nim_hiero_connector')
			elif HieroVersionMajor == 13 and HieroVersionMinor >= 0:
				# Loading NIM menu for NukeStudio 13.0vX
				sys.path.append(nim_root+'/plugins/Nuke/v13.0/Python/Startup')
				hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v13.0/Python/Startup')
			else:
				# Loading NIM menu for NukeStudio 13.0vX
				sys.path.append(nim_root+'/plugins/Nuke/v13.0/Python/Startup/nim_hiero_connector')
				hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v13.0/Python/Startup/nim_hiero_connector')
	except:
		# Loading NIM Hiero Connector for Hiero 9.XvX
		sys.path.append(nim_root+'/plugins/Nuke/v09/Python/Startup/nim_hiero_connector')
		hiero.core.addPluginPath(nim_root+'/plugins/Nuke/v09/Python/Startup/nim_hiero_connector')

	if HieroVersionMajor >= 13 :	
		try :
			from nim_hiero_connector import main
			from nim_hiero_connector.core.nimHieroConnector import *
			from nim_hiero_connector.core.nimHieroExport import *
			from nim_hiero_connector.core.nimShotProcessor import *
			from nim_hiero_connector.core.nimShotProcessorUI import *
			from nim_hiero_connector.core.nimProcessorUI import *
			# NIM Loaded
		except ImportError as error:
			# print("Failed to load NIM Connector", error)
			pass

	else :
		from nimNukeStudioMenu import *
		from nimHieroConnector import *
		from nimHieroExport import *
		from nimShotProcessor import *
		from nimShotProcessorUI import *
		from nimProcessorUI import *
except:
	# print("Could not load NIM Connector:", sys.exc_info()[0])
	pass

# END NIM NukeStudio Connector
