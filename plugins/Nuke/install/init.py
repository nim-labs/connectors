#NIM Nuke Connector

#UPDATE [NIM_CONNECTOR_ROOT] with the path to your NIM Connectors root folder
nim_root = '[NIM_CONNECTOR_ROOT]'

nuke.pluginAddPath(nim_root)
NukeVersionMajor = int(nuke.env['NukeVersionMajor'])
NukeVersionMinor = int(nuke.env['NukeVersionMinor'])

if NukeVersionMajor < 10:
	# Loading NIM for Nuke 9.XvX and lower
	nuke.pluginAddPath(nim_root+'/plugins/Nuke/v09')
	nuke.pluginAddPath(nim_root+'/plugins/Nuke/v09/gizmos')
else:
	if NukeVersionMajor == 10 and NukeVersionMinor < 5:
		# Loading NIM for Nuke 10.0vX
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v10')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v10/gizmos')
	elif NukeVersionMajor == 10 and NukeVersionMinor >= 5:
		# Loading NIM for Nuke 10.5vX
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v10.5')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v10.5/gizmos')
	elif NukeVersionMajor == 11 and NukeVersionMinor < 3:
		# Loading NIM for Nuke 11.0vX
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v11')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v11/gizmos')
	elif NukeVersionMajor == 11 and NukeVersionMinor >= 3:
		# Loading NIM for Nuke 11.3vX
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v11.3')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v11.3/gizmos')
	elif NukeVersionMajor == 12 and NukeVersionMinor == 0:
		# Loading NIM for Nuke 12.0vX
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v12.0')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v12.0/gizmos')
	elif NukeVersionMajor == 12 and NukeVersionMinor >= 1:
		# Loading NIM for Nuke 12.1vX
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v12.1')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v12.1/gizmos')
	elif NukeVersionMajor == 13 and NukeVersionMinor <= 1:
		# Loading NIM for Nuke 13.0vX
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v13.0')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v13.0/gizmos')
	elif NukeVersionMajor == 13 and NukeVersionMinor >= 2:
		# Loading NIM for Nuke 13.0vX
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v13.2')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v13.2/gizmos')
	else:
		# Loading NIM for Nuke 13.0vX
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v13.2')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v13.2/gizmos')

# END NIM Nuke Connector