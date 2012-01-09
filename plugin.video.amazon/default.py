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
__version__ = "0.3.2"


print "\n\n\n\n\n\n\n====================AMAZON START====================\n\n\n\n\n\n"

def modes( ):
    if sys.argv[2]=='':
        common.mechanizeLogin()
        updatemovie = []
        updatemovie.append( ('Export Movie Favorites to Library',   'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="xbmclibrary"&sitemode="LIST_MOVIES")' ) )
        updatemovie.append( ('Full Movie Refresh(DB)', 'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="movies"&sitemode="addMoviesdb")' ) )
        updatemovie.append( ('Recent Movies Refresh(DB)',  'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="movies"&sitemode="addNewMoviesdb")' ) )
        common.addDir('Movies','listmovie','LIST_MOVIE_ROOT', cm=updatemovie)
        updatetv = []
        updatetv.append( ('Export TV Favorites to Library',   'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="xbmclibrary"&sitemode="LIST_TVSHOWS")' ) )
        updatetv.append( ('Full Television Refresh(DB)', 'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="tv"&sitemode="addTVdb")' ) )
        #updatetv.append( ('Update New Television',   'XBMC.RunPlugin(%s?mode="tv"&sitemode="addNewTVdb")' % ( sys.argv[0] ) ) )
        updatetv.append( ('Scan TVDB(DB)',   'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="tv"&sitemode="scanTVDBshows")' ) )
        updatetv.append( ('Delete User Database',   'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="tv"&sitemode="deleteUserDatabase")' ) )
        updatetv.append( ('Delete Backup Database',   'XBMC.RunPlugin(plugin://plugin.video.amazon/?mode="tv"&sitemode="deleteBackupDatabase")' ) )
        #updatetv.append( ('Fix HD Shows',   'XBMC.RunPlugin(%s?mode="tv"&sitemode="fixHDshows")' % ( sys.argv[0] ) ) )
        #updatetv.append( ('Fix Genres',   'XBMC.RunPlugin(%s?mode="tv"&sitemode="fixGenres")' % ( sys.argv[0] ) ) )
        #updatetv.append( ('Fix Years',   'XBMC.RunPlugin(%s?mode="tv"&sitemode="fixYears")' % ( sys.argv[0] ) ) )
        common.addDir('Television','listtv','LIST_TV_ROOT', cm=updatetv)
        common.addDir('Search Prime','searchprime','SEARCH_PRIME','http://www.amazon.com/s?ie=UTF8&field-is_prime_benefit=1&rh=n%3A2858778011%2Ck%3A')
        if common.addon.getSetting('enablelibrary') == 'true':
            common.addDir('My Library','library','LIBRARY_ROOT')
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        exec 'import resources.lib.%s as sitemodule' % common.args.mode
        exec 'sitemodule.%s()' % common.args.sitemode

modes ( )
sys.modules.clear()
