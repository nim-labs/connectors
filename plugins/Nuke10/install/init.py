'''
nuke.pluginAddPath('[NIM_CONNECTOR_ROOT]')
nuke.pluginAddPath('[NIM_CONNECTOR_ROOT]/plugins/Nuke')
nuke.pluginAddPath('[NIM_CONNECTOR_ROOT]/plugins/Nuke/gizmos')
'''

nim_root = '[NIM_CONNECTOR_ROOT]'
nuke.pluginAddPath(nim_root)
if int(nuke.env['NukeVersionMajor']) < 10:
	print "Loading NIM for Nuke 9.XvX and lower"
	nuke.pluginAddPath(nim_root+'/plugins/Nuke')
	nuke.pluginAddPath(nim_root+'/plugins/Nuke/gizmos')
else:
	print "Loading NIM for Nuke 10.XvX"
	nuke.pluginAddPath(nim_root+'/plugins/Nuke10')
	nuke.pluginAddPath(nim_root+'/plugins/Nuke10/gizmos')