#****************************************************************************
#
# Filename:     3dsMax/nimMenu.py
# Version:      5.0.1.210608
# Compatible:   3dsMax 2022 and higher
#
# Copyright (c) 2014-2021 NIM Labs LLC
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
    try:
        print("Rebuilding NIM menu items")

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