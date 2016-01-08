Copy the [NIM_CONNECTOR_ROOT]/plugins/Houdini/install/MainMenuCommon.xml file to the $HOUDINI_PATH (The default path is $HOME/houdiniX.x )

In the $HOUDINI_PATH edit the houdini.env file to include the line:
NIM_CONNECTOR_ROOT = "[NIM_CONNECTOR ROOT]"

Replacing the [NIM_CONNECTOR ROOT] - the one in brackets with the path to the NIM Connectors.

For example:
NIM_CONNECTOR_ROOT = "I:/VAULT/modules/nim"