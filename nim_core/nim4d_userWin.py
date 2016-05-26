#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim4d_userWin.py
# Version:  v2.0.0.160511
#
# Copyright (c) 2016 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  General Imports :
import ntpath, os, platform, re, sys
#  C4D Imports :
import c4d
from c4d import bitmaps, gui, plugins
#  NIM Imports :
import nim as Nim
import nim_api as Api
import nim_c4d as C
import nim_file as F
import nim_prefs as Prefs
import nim_print as P
import nim_win as Win

#  Variables :
version='v2.0.0'
winTitle='NIM_'+version+' - '
_os=platform.system().lower()
nim_plugin_ID=1032427

#  START - Get User dialog, for setting the Username :
class GetUser( gui.GeDialog ) :
    
    def __init__( self ) :
        'Instantiates a dictionary containing all ID numbers needed for the dialog.'
        self.usr=''
        self.usrIDs={}
        self.IDs={ 'grp1': 1000, 'grp2': 1001, 'txt': 1002, 'combo': 1003, 'btn': 1004, 'initial': 1010 }
        return
    
    
    def CreateLayout( self ) :
        'Creates the UI elements.'
        combo_num=self.IDs['initial']
        cur_user=F.get_user()
        nimURL=Prefs.get_url()
        P.info('CreateLayout - nimURL: %s' % nimURL)
        usrList=Api.get_userList( url=nimURL )
        
        #  Text and Combo Box :
        self.GroupBegin( self.IDs['grp1'], c4d.BFH_SCALEFIT, cols=1, rows=2 )
        self.GroupBegin( self.IDs['grp2'], c4d.BFH_SCALEFIT, cols=2, rows=1 )
        self.AddStaticText( self.IDs['txt'], c4d.BFH_SCALE, initw=95, name='User :' )
        self.AddComboBox( self.IDs['combo'], c4d.BFH_SCALEFIT, initw=250 )
        self.GroupEnd()
        self.AddButton( self.IDs['btn'], c4d.BFH_SCALEFIT, name='Set User' )
        self.GroupEnd()
        
        #  Populate Combo Box :
        for u in usrList :
            self.AddChild( self.IDs['combo'], combo_num, u['username'] )
            #  Save dictionary of ID numbers :
            self.usrIDs[str(combo_num)]=u['username']
            
            #  Try to auto-set to current Username, from ENV Vars :
            if cur_user==u['username'] :
                pass
            
            combo_num+=1
        
        return True
    
    
    def Command( self, id, msg ) :
        'Updates the user setting.'
        #  Set Username :
        if id==self.IDs['combo'] :
            num=self.GetLong( id )
            for menuID in self.usrIDs :
                if int(menuID)==num :
                    self.usr=self.usrIDs[menuID]
                    break
            print 'User set to "%s"' % self.usr
        
        if id==self.IDs['btn'] :
            #  Check User ID :
            url=Prefs.get_url()
            if url : userID=Api.get( sqlCmd={ 'q': 'getUserID', 'u': self.usr }, debug=False, nimURL=url )
            else : userID=Api.get( sqlCmd={ 'q': 'getUserID', 'u': self.usr }, debug=False )
            #  Update Preferences :
            if userID : Prefs.set_userInfo( userID, self.usr )
            self.Close()
        
        return True
    
    def get_user( self ) :
        'Returns the user name specified.'
        return self.usr

#  END - Get User Dialog.

#  END.

