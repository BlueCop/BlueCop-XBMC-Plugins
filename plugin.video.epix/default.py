#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
        EPIX
"""
#main imports
import xbmcplugin
import xbmc
import xbmcgui
import xbmcaddon
import sys
import resources.lib.common as common
import urllib

pluginhandle = common.pluginhandle

#plugin constants
__plugin__ = "EPIX"
__authors__ = "BlueCop"
__credits__ = ""
__version__ = "0.0.1"


print "\n\n\n\n\n\n\n====================EPIX START====================\n\n\n\n\n\n"

def modes( ):
    if sys.argv[2]=='':
        #common.login()
        common.addDir('Alphabetical','listmovie','LIST_ALPHA')
        common.addDir('Genre','listmovie','LIST_GENRE')
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        exec 'import resources.lib.%s as sitemodule' % common.args.mode
        exec 'sitemodule.%s()' % common.args.sitemode

modes ( )
sys.modules.clear()
