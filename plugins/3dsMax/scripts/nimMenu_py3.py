#****************************************************************************
#
# Filename:     3dsMax/nimMenu.py
# Version:      7.0.2.241007
# Compatible:   3dsMax 2022 and higher
#               Includes support for 3dsMax 2025+
#
# Copyright (c) 2014-2024 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
#
# ****************************************************************************

from pymxs import runtime as rt
import os,sys,re,traceback
import importlib

nim3dsMaxScriptPath = os.path.dirname(os.path.realpath(__file__))
nim3dsMaxScriptPath = nim3dsMaxScriptPath.replace('\\','/')
nimScriptPath = re.sub(r"\/plugins/3dsMax/scripts$", "", nim3dsMaxScriptPath)
print("NIM Script Path: %s" % nimScriptPath)

sys.path.append(nimScriptPath)
import nim_core.UI as nimUI
import nim_core.nim_api as nimAPI
import nim_core.nim_file as nimFile
import nim_core.nim_win as nimWin

importlib.reload(nimUI)
importlib.reload(nimAPI)
importlib.reload(nimFile)
importlib.reload(nimWin)

def outputMenuItem(item, recurse = True, indent = ''):
    text = item.GetTitle() 
    print(indent, text if text else "----")
    if item.HasSubMenu and recurse:
        outputMenu(item.SubMenu, recurse, indent + '   ')
    
def outputMenu(menu, recurse = True, indent = ''):
    for i in menu.Items:
        outputMenuItem(i, recurse, indent)

def openFileAction():
    nimUI.mk('FILE')
    print('NIM: openFileAction')

def importFileAction():
    nimUI.mk('LOAD', _import=True )
    print('NIM: importFileAction')

def referenceFileAction():
    nimUI.mk('LOAD', ref=True)
    print('NIM: referenceFileAction')

def saveFileAction():
    nimUI.mk('SAVE')
    print('NIM: saveFileAction')

def saveSelectedAction():
    nimUI.mk( mode='SAVE', _export=True )
    print('NIM: saveSelectedAction')

def versionUpAction():
    nimAPI.versionUp()
    print('NIM: versionUpAction')

def publishAction():
    nimUI.mk('PUB')
    print('NIM: publishAction')

def changeUserAction():
    print('NIM: changeUserAction')
    try:
        nimWin.userInfo()
    except Exception as e :
        print('Sorry, there was a problem choosing NIM user...')
        print('    %s' % traceback.print_exc())
    return
    
def reloadScriptsAction():
    nimFile.scripts_reload()
    print('NIM: reloadScriptsAction')



def add_to_main_menu_bar(menu):
    main_menu = rt.menuMan.GetMainMenuBar()
    sub_menu_index = main_menu.numItems() - 1
    sub_menu_item = rt.menuMan.createSubMenuItem('-', menu)
    main_menu.addItem(sub_menu_item, sub_menu_index)
    rt.menuMan.updateMenuBar()


def add_to_menu(menu, title, func):
    macro_name = func.replace('()', '')
    # category, macroName, tooltip, text, function
    t = rt.macros.new('nim', macro_name, 'NIM Connectors', '', func)
    # macro_name, category
    menu_action = rt.menuMan.createActionItem(macro_name, 'nim')
    menu_action.setUseCustomTitle(True)
    menu_action.setTitle(title)
    menu.addItem(menu_action, -1)

def add_separator(menu):
    sep = rt.menuMan.createSeparatorItem()
    menu.addItem(sep, -1)

def add_func_to_global(var, func):
    rt.execute('global ' + var)
    rt.globalVars.set(var, func)


def main():

    maxVersion = rt.maxversion()
    print("3dsMax Version: %s" % maxVersion)
    #<Array<#(22000, 55, 0, 22, 2, 0, 2126, 2020, ".2 Update ")>>

    if maxVersion[7] >= 2025:
        print("Building NIM menu")

        try:
            # ------------- Define plugin actions --------------------
            # Create a macroscript that executes our plugin specific code
            # (this macroscript defines an action that can be used as an Action menu item)
            rt.macros.new(
                "NIM",                                      # Category for the macro script
                "Open",                                     # Name of the macro script
                "Open a file using the NIM connector",      # Tooltip text for the action
                "Open",                                     # Text displayed in the menu
                "openFileAction()"                          # Function to execute when this action is triggered
            )

            rt.macros.new(
                "NIM",                                      # Category for the macro script
                "Import",                                   # Name of the macro script
                "Import a file using the NIM connector",    # Tooltip text for the action
                "Import",                                   # Text displayed in the menu
                "importFileAction()"                        # Function to execute when this action is triggered
            )

            rt.macros.new(
                "NIM",                                          # Category for the macro script
                "Reference",                                    # Name of the macro script
                "Reference a file using the NIM connector",     # Tooltip text for the action
                "Reference",                                    # Text displayed in the menu
                "referenceFileAction()"                         # Function to execute when this action is triggered
            )

            rt.macros.new(
                "NIM",                                                                  # Category for the macro script
                "SaveAs",                                                               # Name of the macro script
                "Save a file to a new or exiting basename using the NIM connector",     # Tooltip text for the action
                "Save As",                                                              # Text displayed in the menu
                "saveFileAction()"                                                      # Function to execute when this action is triggered
            )

            rt.macros.new(
                "NIM",                                                                                  # Category for the macro script
                "ExportSelected",                                                                       # Name of the macro script
                "Export the selected items to a new or exiting basename using the NIM connector",       # Tooltip text for the action
                "Export Selected",                                                                      # Text displayed in the menu
                "saveSelectedAction()"                                                                  # Function to execute when this action is triggered
            )

            rt.macros.new(
                "NIM",                                                      # Category for the macro script
                "VersionUp",                                                # Name of the macro script
                "Version up the current file using the NIM connector",      # Tooltip text for the action
                "Version Up",                                               # Text displayed in the menu
                "versionUpAction()"                                         # Function to execute when this action is triggered
            )

            rt.macros.new(
                "NIM",                                                  # Category for the macro script
                "Publish",                                              # Name of the macro script
                "Publish the current file using the NIM connector",     # Tooltip text for the action
                "Publish",                                              # Text displayed in the menu
                "publishAction()"                                       # Function to execute when this action is triggered
            )

            rt.macros.new(
                "NIM",                                  # Category for the macro script
                "ChangeUser",                           # Name of the macro script
                "Change the current NIM user",     # Tooltip text for the action
                "Change User",                          # Text displayed in the menu
                "changeUserAction()"                    # Function to execute when this action is triggered
            )

            rt.macros.new(
                "NIM",                          # Category for the macro script
                "ReloadScripts",                # Name of the macro script
                "Reload the NIM menu scripts",  # Tooltip text for the action
                "Reload Scripts",               # Text displayed in the menu
                "reloadScriptsAction()"         # Function to execute when this action is triggered
            )

            # Expose this function to the maxscript global namespace
            rt.openFileAction = openFileAction
            rt.importFileAction = importFileAction
            rt.referenceFileAction = referenceFileAction
            rt.saveFileAction = saveFileAction
            rt.saveSelectedAction = saveSelectedAction
            rt.versionUpAction = versionUpAction
            rt.publishAction = publishAction
            rt.changeUserAction = changeUserAction
            rt.reloadScriptsAction = reloadScriptsAction

            # ------------- Menu Creation Callback --------------------
            # This callback is called every time the menu structure is newly evaluated, such as on 3ds Max startup or when the menu preset changes
            def menucallback():
                """Register the menu and its items.
                This callback is registered on the "cuiRegistermenus" event of 3dsMax and
                is typically called in he startup of 3dsMax.
                """
                menumgr = rt.callbacks.notificationparam()
                mainmenubar = menumgr.mainmenubar

                # Create a new submenu at the end of the 3dsMax main menu bar
                # To place the menu at a specific position, use the 'beforeID' parameter with the GUID of the succeeding menu item
                # Note, that every menu item in the menu system needs a persistent Guid for identification and referencing
                submenu = mainmenubar.createsubmenu("129ca045-a4f6-4baf-90be-2205640e9800","NIM")

                # Add the macroscript actions to the submenu
                # Note the action identifier created from the macroscripts name and category
                macroscriptTableid = 647394
                submenu.createaction("2a2f952e-2edb-4bd3-b28d-a9c3c04d4e14",
                    macroscriptTableid, "Open`NIM")

                submenu.createaction("ebb35072-3ad0-4e3a-a0ed-4cadb313af45",
                    macroscriptTableid, "Import`NIM")
                
                submenu.createaction("1df470fb-7492-4e0a-98dc-b907dce186f0",
                    macroscriptTableid, "Reference`NIM")
                
                submenu.createSeparator("a9eb8598-e86c-4bbe-8c12-6a08b895bed5")
                
                submenu.createaction("ec90aac0-1911-428e-8a47-28ccf89f670d",
                    macroscriptTableid, "SaveAs`NIM")
                
                submenu.createaction("4ef6b5db-a183-4a83-bbb9-b5e8ea31647b",
                    macroscriptTableid, "ExportSelected`NIM")
                
                submenu.createSeparator("c6c7619c-01e9-438d-8184-e08646726abc")
                
                submenu.createaction("5ad4f625-aee8-4f13-9bcb-8796a7f6563f",
                    macroscriptTableid, "VersionUp`NIM")
                
                submenu.createaction("c60fd04d-71af-4560-9d84-e50030d0c9e8",
                    macroscriptTableid, "Publish`NIM")
                
                submenu.createSeparator("44b50fc4-22c7-48aa-8768-8ee708d4be98")
                
                submenu.createaction("12f47b9c-2c9a-49f8-9b57-b6d7c43381ed",
                    macroscriptTableid, "ChangeUser`NIM")
                
                submenu.createaction("adc0d21b-740d-4b5b-889a-f705a81939b7",
                    macroscriptTableid, "ReloadScripts`NIM")

            # Make sure menucallback is called on cuiRegisterMenus events
            # so that it can register menus at the appropriate moment
            NIM_MENU_SCRIPT = rt.name("nimMenu")
            rt.callbacks.removescripts(id=NIM_MENU_SCRIPT)
            rt.callbacks.addscript(rt.name("cuiRegisterMenus"), menucallback, id=NIM_MENU_SCRIPT)


        except Exception as e :
            print( "Failed to create NIM menu" )
            print( "    %s" % traceback.print_exc() )

    else:
        try:
            print("Building NIM menu")

            while rt.menuMan.findMenu('NIM'):
                rt.menuMan.unRegisterMenu(rt.menuMan.findMenu('NIM'))
            while rt.menuMan.findMenu('NIM Settings'):
                rt.menuMan.unRegisterMenu(rt.menuMan.findMenu('NIM Settings'))

            add_func_to_global('nim_openFileAction', openFileAction)
            add_func_to_global('nim_importFileAction', importFileAction)
            add_func_to_global('nim_referenceFileAction', referenceFileAction)
            add_func_to_global('nim_saveFileAction', saveFileAction)
            add_func_to_global('nim_saveSelectedAction', saveSelectedAction)
            add_func_to_global('nim_versionUpAction', versionUpAction)
            add_func_to_global('nim_publishAction', publishAction)
            add_func_to_global('nim_changeUserActionn', changeUserAction)
            add_func_to_global('nim_reloadScriptsAction', reloadScriptsAction)

            mainMenuBar = rt.menuMan.getMainMenuBar()
            nimMenu = rt.menuMan.createMenu("NIM")
            add_to_main_menu_bar(nimMenu)
            add_to_menu(nimMenu, 'Open', 'nim_openFileAction()')
            add_to_menu(nimMenu, 'Import', 'nim_importFileAction()')
            add_to_menu(nimMenu, 'Reference', 'nim_referenceFileAction()')
            add_separator(nimMenu)
            add_to_menu(nimMenu, 'Save As', 'nim_saveFileAction()')
            add_to_menu(nimMenu, 'Export Selected', 'nim_saveSelectedAction()')
            add_separator(nimMenu)
            add_to_menu(nimMenu, 'Version Up', 'nim_versionUpAction()')
            add_to_menu(nimMenu, 'Publish', 'nim_publishAction()')
            add_separator(nimMenu)
            add_to_menu(nimMenu, 'Change User', 'nim_changeUserActionn()')
            add_to_menu(nimMenu, 'Reload Scripts', 'nim_reloadScriptsAction()')
            add_separator(nimMenu)
            
            print( "NIM Menu Created" )

        except Exception as e :
            print( "Failed to create NIM menu" )
            print( "    %s" % traceback.print_exc() )
        

if __name__ == '__main__':
    main()