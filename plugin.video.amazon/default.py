#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
        AMAZON
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
__plugin__ = "AMAZON"
__authors__ = "BlueCop"
__credits__ = ""
__version__ = "0.5.0"


print "\n\n\n\n\n\n\n====================AMAZON START====================\n\n\n\n\n\n"

def modes( ):
    if sys.argv[2]=='':
        #common.mechanizeLogin()
        common.addDir('Watchlist','library','WATCHLIST_ROOT')
        if common.addon.getSetting('enablelibrary') == 'true':
            common.addDir('Purchases & Rentals','library','LIBRARY_ROOT')
        common.addDir('Featured Movies','appfeed','APP_LEVEL2','2,2')
        common.addDir('Featured Television','appfeed','APP_LEVEL2','3,2')

        updatemovie = []
        updatemovie.append( ('Export Movie Favorites to Library',   'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="xbmclibrary"&sitemode="LIST_MOVIES")' ) )
        updatemovie.append( ('Full Movie Refresh(DB)', 'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="movies"&sitemode="addMoviesdb")' ) )
        common.addDir('Movies','listmovie','LIST_MOVIE_ROOT', cm=updatemovie)

        updatetv = []
        updatetv.append( ('Export TV Favorites to Library',   'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="xbmclibrary"&sitemode="LIST_TVSHOWS")' ) )
        updatetv.append( ('Full Television Refresh(DB)', 'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="tv"&sitemode="addTVdb")' ) )
        #updatetv.append( ('Scan TVDB(DB)',   'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="tv"&sitemode="scanTVDBshows")' ) )]
        common.addDir('Television','listtv','LIST_TV_ROOT', cm=updatetv)

        common.addDir('Search Prime','appfeed','SEARCH_PRIME','')
        #OLD SEARCH
        #common.addDir('Search Prime','searchprime','SEARCH_PRIME','http://www.amazon.com/s?ie=UTF8&field-is_prime_benefit=1&rh=n%3A2858778011%2Ck%3A')

        #TESTS
        #common.addDir('Categories Testing','appfeed','APP_ROOT')
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        exec 'import resources.lib.%s as sitemodule' % common.args.mode
        exec 'sitemodule.%s()' % common.args.sitemode

modes ( )
sys.modules.clear()
