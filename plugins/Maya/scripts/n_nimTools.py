#****************************************************************************
#
# Filename: Maya/n_nimTools.py
# Version:  v2.0.0.160511
#
# Copyright (c) 2016 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ****************************************************************************


import maya.cmds as mc
import maya.mel as mm
import urllib, urllib2
import json
import os.path
from os.path import expanduser


def getNimData(query, item_1=None, item_2=None):
    '''Querys mySQL server and returns decoded json array'''
    
    ''' TODO: CHECK IF FILE EXSITS AND IF NOT OPEN ALERT '''
    userHome = expanduser("~")
    if userHome.endswith('Documents'):
        userHome = userHome[:-9]
    nimPrefsFile = os.path.join(userHome,'.nim','prefs.nim')
    nimPrefs = {}
    with open(nimPrefsFile) as prefsFile:
        for line in prefsFile:
            name, var = line.partition("=")[::2]
            var = var.rstrip(' \r\n')
            nimPrefs[name.strip()] = var
    prefsFile.close()
    #nim_URL = nimPrefs["NimURL"]
    nim_URL = nimPrefs["NIM_URL"]
    #print ("nimURL: %s", nim_URL)
    
    if query == 'getShotInfo':
        sqlCmd = {'q':query,'ID':item_1,'userID':item_2}
        
    elif query == 'getTaskInfo':
        sqlCmd = {'q':query,'class':item_1,'itemID':item_2}
    
    elif query == 'getUserFullName':
        sqlCmd = {'q':query,'u':item_1}
        
    else:
        print ("No Query Found")
        return
    
    actionURL = nim_URL+urllib.urlencode(sqlCmd)		#actionURL = self.nim_URL+'q=getShows&ID='+jobID
    #print actionURL
    f = urllib2.urlopen(actionURL)
    result = json.loads( f.read(), object_hook=_decode_dict )
    f.close()
    return result


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
           key = key.encode('utf-8')
        if isinstance(value, unicode):
           value = value.encode('utf-8')
        elif isinstance(value, list):
           value = _decode_list(value)
        elif isinstance(value, dict):
           value = _decode_dict(value)
        rv[key] = value
    return rv


def getListValue(data, item, key):
    '''returns the value'''
    value = data[item][key]
    return value


def selectMenuItemAnn(optionMenu, menuAnn):
    '''Select menu item by annotation'''
    try:
        if mc.optionMenu(optionMenu, query=True, numberOfItems=True) > 0:
            selected_menuItems = mc.optionMenu(optionMenu, query=True, itemListLong=True)
            
            try:
                if len(selected_menuItems) > 0:
                    #print('Num Menu Items: '+str(len(selected_menuItems)))
                    i = 1
                    for item in selected_menuItems:
                        menuItemText = mc.menuItem(item, query=True, ann=True)
                        if menuAnn == menuItemText:
                                #print('menuItem Found: '+str(i))
                                mc.optionMenu(optionMenu, edit=True, sl=int(i))
                                #print('itemIndex: '+str(i)+'selected')
                                break
                        else:
                            i = i+1
                else:
                    return None
            except:
                pass
        else:
            return None
    except:
        pass