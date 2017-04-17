#NIM Nuke Connector

#UPDATE [NIM_CONNECTOR_ROOT] with the path to your NIM Connectors root folder
nim_root = '[NIM_CONNECTOR_ROOT]'

nuke.pluginAddPath(nim_root)
NukeVersionMajor = int(nuke.env['NukeVersionMajor'])
NukeVersionMinor = int(nuke.env['NukeVersionMinor'])

if NukeVersionMajor < 10:
	print "Loading NIM for Nuke 9.XvX and lower"
	nuke.pluginAddPath(nim_root+'/plugins/Nuke/v09')
	nuke.pluginAddPath(nim_root+'/plugins/Nuke/v09/gizmos')
else:
	if NukeVersionMajor == 10 and NukeVersionMinor == 0:
		print "Loading NIM for Nuke 10.0vX"
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v10')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v10/gizmos')
	else:
		print "Loading NIM for Nuke 10.5vX"
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v10.5')
		nuke.pluginAddPath(nim_root+'/plugins/Nuke/v10.5/gizmos')

# END NIM Nuke Connector