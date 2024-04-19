
# Hook called when the application is fully initialized after a project is loaded.
# project_name: the project that was loaded -- String
def app_initialized(project_name):
    pass


# Hook called when the application is exiting.
# info: Information about the current executable -- dictionary
#
#    Keys:
#
#    homeDirectory: [String]
#       Home directory of the started executable.
#       Example: /opt/Autodesk/flame_2016.1.2
#
#    version: [String]
#       Decorated version string of the started executable.
#       Example: Using the previous example, version == "2016.1.2"
#
#    versionMajor: [String]
#       Major version of the started executable.
#       Example: Using the previous example, versionMajor == "2016"
#
#    versionMinor: [String]
#       Minor version of the started executable.
#       Example: Using the previous example, versionMinor == "1"
#
#    versionPatch: [String]
#       Patch version of the started executable.
#       Example: Using the previous example, versionPatch == "2"
#
#   versionStamp: [String]
#        Stamp version of the started executable.
#        Example: versionStamp == "185" (Not visible on homeDirectory path)
#
#    configPath: [String]
#       Path to the loaded config file.
#       Example: Using the previous example, default is /opt/Autodesk/flame_2016.1.2/cfg/init.cfg
def app_exited(info):
    pass


# Hook called when a new user is loaded in the application.
# info: Information about the user switching -- dictionary
#
#    Keys:
#
#    userName: [String]
#       Loaded user's userName
#
#    context: [String]
#       Context of the user change
#           context == "splash" if userChanged is triggered from the splash screen
#           context == "settings" if userChanged is triggered from the settings
def user_changed(info):
    pass


# Hook called when a sequence finishes rendering (even if unsuccessful).
# module_name : Name of the rendering module -- String.
# sequence_name : Name of the rendered sequence -- String.
# elapsed_time_in_seconds : number of seconds used to render -- Float
def render_ended(module_name, sequence_name, elapsed_time_in_seconds):
    pass


# Hook called when a sequence finishes playback (even if unsuccessful).
# sequence_name : Name of the rendered sequence -- String.
# fps : FPS -- Float
# debug_info: Debugging Playback Information -- Dict
def playback_ended(sequence_name, fps, debug_info):
    pass


# Hook called when the user changes the video preview device. The following
# values are read from the init.cfg VideoPreviewDevice keyword.
# description : Description of the video preview device -- String
#               (ex : "1920x1080@5994i_free")
# width : Width of the preview device -- Integer.
# height : Height of the preview device -- Integer.
# bit_depth : Bit depth of the preview device -- Integer.
# rate_string : Rate of the preview device -- String.
#               (ex : "6000i")
# sync_string : Sync source of the preview device -- String.
#              (ex : "freesync")
def preview_window_config_changed(
    description, width, height, bit_depth, rate_string, sync_string
):
    pass


# Hook called when starting the application and when switching project
# This value will be used as default for the rename shotname dialog
#
# project: [String]
#    Usually called with current project.
#
# Ex: if project == "project_name":
#         return "<track>_<segment>_project"
#     return "<track>_<segment>_global"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def timeline_default_shot_name(project, *args, **kwargs):
    pass


# Hook called when starting the application and when switching project
# This value will be used as default for the marker name
#
# project: [String]
#    Usually called with current project.
#
# Ex: if project == "project_name":
#         return "<user>_<time>_project"
#     return "<user>_<time>_global"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def timeline_default_marker_name(project, *args, **kwargs):
    pass


# Hook called when starting the application and when switching project
# This value will be used as default for the marker comment
#
# project: [String]
#    Usually called with current project.
#
# Ex: if project == "project_name":
#         return "<user>_<time>_project"
#     return "<user>_<time>_global"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def timeline_default_marker_comment(project, *args, **kwargs):
    pass


# Hook called when starting the application and when switching project
# This value will be used as default for the segment marker name
#
# project: [String]
#    Usually called with current project.
#
# Ex: if project == "project_name":
#         return "<user>_<time>_project"
#     return "<user>_<time>_global"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def timeline_default_segment_marker_name(project, *args, **kwargs):
    pass


# Hook called when starting the application and when switching project
# This value will be used as default for the segment marker comment
#
# project: [String]
#    Usually called with current project.
#
# Ex: if project == "project_name":
#         return "<user>_<time>_project"
#     return "<user>_<time>_global"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def timeline_default_segment_marker_comment(project, *args, **kwargs):
    pass


# Hook called when starting the application and when switching project
# This value will be used as default name for gap bfx.
#
# project: [String]
#    Usually called with current project.
#
# Ex: if project == "project_name":
#         return "<track>_<segment>_project"
#     return "<track>_<segment>_global"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def timeline_default_gap_bfx_name(project, *args, **kwargs):
    pass


# Hook called when starting the application and when switching project
# This value will be used as default for the reference name
#
# project: [String]
#    Usually called with current project.
#
# Ex: if project == "project_name":
#         return "<user>_<time>_project"
#     return "<user>_<time>_global"
#
# :note: This method can be implemented only once.
#        First instance found will be used
#
def default_reference_name(project, *args, **kwargs):
    pass

