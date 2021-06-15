/* 
	Edit the following line and replace [NIM_CONNECTOR_ROOT] 
	with the full path to the NIM Connector root folder.
	
	For example: 
		connector_path = "C:/Vault/NIM_Connectors"
*/

connector_path = "[NIM_CONNECTOR_ROOT]"


/* **************************************************
	DO NOT EDIT BELOW THIS LINE
*************************************************** */

py3 = connector_path+"/plugins/3dsMax/scripts/nimMenu_py3.py"
py2 = connector_path+"/plugins/3dsMax/scripts/nimMenu_py2.py"

sys = python.import "sys"
pythonVersion = sys.version_info.major

if pythonVersion >= 3 
then (
	print("Python3 environment found.")
	python.ExecuteFile py3
)
else (
	print("Python2 environment found.")
	python.ExecuteFile py2
)