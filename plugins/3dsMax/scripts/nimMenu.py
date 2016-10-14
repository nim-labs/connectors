#****************************************************************************
#
# Filename: 3dsMax/nimMenu.py
# Version:  2.5.0.161013
#
# Copyright (c) 2016 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
#
# ****************************************************************************
import MaxPlus
import os,sys,re

nim3dsMaxScriptPath = os.path.dirname(os.path.realpath(__file__))
nim3dsMaxScriptPath = nim3dsMaxScriptPath.replace('\\','/')
nimScriptPath = re.sub(r"\/plugins/3dsMax/scripts$", "", nim3dsMaxScriptPath)
print "NIM Script Path: %s" % nimScriptPath

sys.path.append(nimScriptPath)
import nim_core.UI as nimUI
import nim_core.nim_api as nimAPI
import nim_core.nim_file as nimFile
import nim_core.nim_win as nimWin

reload(nimUI)
reload(nimAPI)
reload(nimFile)
reload(nimWin)

def outputMenuItem(item, recurse = True, indent = ''):
    text = item.GetTitle() 
    print indent, text if text else "----"
    if item.HasSubMenu and recurse:
        outputMenu(item.SubMenu, recurse, indent + '   ')
    
def outputMenu(menu, recurse = True, indent = ''):
    for i in menu.Items:
        outputMenuItem(i, recurse, indent)

def openFileAction():
    nimUI.mk('FILE')
    print 'NIM: openFileAction'

def importFileAction():
    nimUI.mk('LOAD', _import=True )
    print 'NIM: importFileAction'

def refereceFileAction():
    nimUI.mk('LOAD', ref=True)
    print 'NIM: refereceFileAction'

def saveFileAction():
    nimUI.mk('SAVE')
    print 'NIM: saveFileAction'

def saveSelectedAction():
    nimUI.mk( mode='SAVE', _export=True )
    print 'NIM: saveSelectedAction'

def versionUpAction():
    nimAPI.versionUp()
    print 'NIM: versionUpAction'

def publishAction():
    nimUI.mk('PUB')
    print 'NIM: publishAction'

def changeUserAction():
    print 'NIM: changeUserAction'
    try:
        nimWin.userInfo()
    except Exception, e :
        print 'Sorry, there was a problem choosing NIM user...'
        print '    %s' % traceback.print_exc()
    return
    
def reloadScriptsAction():
    nimFile.scripts_reload()
    print 'NIM: reloadScriptsAction'

nimOpen = MaxPlus.ActionFactory.Create('Open File', 'Open', openFileAction)
nimImport = MaxPlus.ActionFactory.Create('Import File', 'Import', importFileAction)
nimReference = MaxPlus.ActionFactory.Create('Reference File', 'Reference', refereceFileAction)
nimSaveAs = MaxPlus.ActionFactory.Create('Save As', 'Save As', saveFileAction)
nimExportSelected = MaxPlus.ActionFactory.Create('Export Selected', 'Export Selected', saveSelectedAction)
nimVersionUp = MaxPlus.ActionFactory.Create('Version Up', 'Version Up', versionUpAction)
nimPublish = MaxPlus.ActionFactory.Create('Publish File', 'Publish', publishAction)
nimChangeUser = MaxPlus.ActionFactory.Create('Change User', 'Change User', changeUserAction)
nimReload = MaxPlus.ActionFactory.Create('Reload Scripts', 'Reload Scripts', reloadScriptsAction)

def createNimMenu(name):
    if not MaxPlus.MenuManager.MenuExists(name):
        mb = MaxPlus.MenuBuilder(name)

        if nimOpen._IsValidWrapper():
            print "Created nimOpen"
        else:
            print "Failed to create nimOpen"
        mb.AddItem(nimOpen)
        
        if nimImport._IsValidWrapper():
            print "Created nimImport"
        else:
            print "Failed to create nimImport"
        mb.AddItem(nimImport)

        if nimReference._IsValidWrapper():
            print "Created nimReference"
        else:
            print "Failed to create nimReference"
        mb.AddItem(nimReference)
        
        mb.AddSeparator()

        if nimSaveAs._IsValidWrapper():
            print "Created nimSaveAs"
        else:
            print "Failed to create nimSaveAs"
        mb.AddItem(nimSaveAs)

        if nimExportSelected._IsValidWrapper():
            print "Created nimExportSelected"
        else:
            print "Failed to create nimExportSelected"
        mb.AddItem(nimExportSelected)
       
        mb.AddSeparator()
       
        if nimVersionUp._IsValidWrapper():
            print "Created nimVersionUp"
        else:
            print "Failed to create nimVersionUp"
        mb.AddItem(nimVersionUp)
        
        if nimPublish._IsValidWrapper():
            print "Created nimPublish"
        else:
            print "Failed to create nimPublish"
        mb.AddItem(nimPublish)
        
        mb.AddSeparator()
        
        if nimChangeUser._IsValidWrapper():
            print "Created nimChangeUser"
        else:
            print "Failed to create nimChangeUser"
        #mb.AddItem(nimChangeUser)

        if nimReload._IsValidWrapper():
            print "Created nimReload"
        else:
            print "Failed to create nimReload"
        #mb.AddItem(nimReload)
        
        menu = mb.Create(MaxPlus.MenuManager.GetMainMenu())
        
        if not MaxPlus.MenuManager.MenuExists(u"NIM Settings"):
            subMenu = MaxPlus.MenuBuilder(u"NIM Settings")
            subMenu.AddItem(nimChangeUser)
            subMenu.AddItem(nimReload)
            nimSubMenu = subMenu.Create(menu)

        #print 'menu created', menu.Title 
    else:
        print 'The menu ', name, ' already exists'

def main():
    try:
        print "Removing any previously left 'menu items'"
        MaxPlus.MenuManager.UnregisterMenu(u"NIM")
        MaxPlus.MenuManager.UnregisterMenu(u"NIM Settings")

        print "Reading current NIM menu"
        outputMenu(MaxPlus.MenuManager.GetMainMenu(), False)

        print "Creating the NIM menu"
        createNimMenu(u"NIM")
        outputMenu(MaxPlus.MenuManager.GetMainMenu(), False)
    except:
        print "Failed to create NIM menu"
        

if __name__ == '__main__':
    main()