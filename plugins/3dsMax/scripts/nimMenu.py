#****************************************************************************
#
# Filename: 3dsMax/nimMenu.py
# Version:  v1.0.3.151215
#
# Copyright (c) 2015 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
#
# ****************************************************************************
import MaxPlus
import os,sys

nim3dsMaxScriptPath = os.path.dirname(os.path.realpath(__file__))
nim3dsMaxScriptPath = nim3dsMaxScriptPath.replace('\\','/')
nimScriptPath = nim3dsMaxScriptPath.rstrip('/plugins/3dsMax/scripts')
print "NIM Script Path: %s" % nimScriptPath

#sys.path.append('[NIM_CONNECTOR_ROOT]')
sys.path.append(nimScriptPath)
import nim_core.UI as nimUI
import nim_core.nim_api as nimAPI
import nim_core.nim_file as nimFile

reload(nimUI)
reload(nimAPI)
reload(nimFile)

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
        
        if nimReload._IsValidWrapper():
            print "Created nimReload"
        else:
            print "Failed to create nimReload"
        mb.AddItem(nimReload)
        
        menu = mb.Create(MaxPlus.MenuManager.GetMainMenu())
        #print 'menu created', menu.Title 
    else:
        print 'The menu ', name, ' already exists'

def getLastMenuItem(menu = MaxPlus.MenuManager.GetMainMenu()):
    return list(menu.Items)[-1]
    
def testLastItem(text):
    assert(getLastMenuItem().Title  == text)

def main():
    print "Removing any previously left 'menu items'"
    MaxPlus.MenuManager.UnregisterMenu(u"NIM")
    
    print "Creating a new menu"
    testLastItem(u"&Help")
    outputMenu(MaxPlus.MenuManager.GetMainMenu(), False)
    
    print "Creating a new menu"
    createNimMenu(u"NIM")
    outputMenu(MaxPlus.MenuManager.GetMainMenu(), False)
    testLastItem(u"NIM")
    

if __name__ == '__main__':
    main()