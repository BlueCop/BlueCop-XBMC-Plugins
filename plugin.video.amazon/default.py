"""
        AMAZON
"""
#main imports
import xbmcplugin
import xbmc
import xbmcgui
import sys
import resources.lib.common as common
import urllib

pluginhandle = common.pluginhandle

#plugin constants
__plugin__ = "AMAZON"
__authors__ = "BlueCop"
__credits__ = ""
__version__ = "0.2.8"


print "\n\n\n\n\n\n\n====================AMAZON START====================\n\n\n\n\n\n"

def modes( ):
    if sys.argv[2]=='':
        common.mechanizeLogin()
        updatemovie = []  
        updatemovie.append( ('Full Movie Refresh', 'XBMC.RunPlugin(%s?mode="movie"&sitemode="addMoviesdb")' % ( sys.argv[0] ) ) )
        updatemovie.append( ('Update New Movies',  'XBMC.RunPlugin(%s?mode="movie"&sitemode="addNewMoviesdb")' % ( sys.argv[0] ) ) )
        common.addDir('Movies','listmovie','LIST_MOVIE_ROOT', cm=updatemovie)
        updatetv = [] 
        updatetv.append( ('Full Television Refresh', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="addTVdb")' % ( sys.argv[0] ) ) )
        updatetv.append( ('Update New Television',   'XBMC.RunPlugin(%s?mode="tv"&sitemode="addNewTVdb")' % ( sys.argv[0] ) ) )
        updatetv.append( ('Scan TVDB',   'XBMC.RunPlugin(%s?mode="tv"&sitemode="scanTVDBshows")' % ( sys.argv[0] ) ) )
        updatetv.append( ('Fix HD Shows',   'XBMC.RunPlugin(%s?mode="tv"&sitemode="fixHDshows")' % ( sys.argv[0] ) ) )
        updatetv.append( ('Fix Genres',   'XBMC.RunPlugin(%s?mode="tv"&sitemode="fixGenres")' % ( sys.argv[0] ) ) )
        updatetv.append( ('Fix Years',   'XBMC.RunPlugin(%s?mode="tv"&sitemode="fixYears")' % ( sys.argv[0] ) ) )
        common.addDir('Television','listtv','LIST_TV_ROOT', cm=updatetv)
        if xbmcplugin.getSetting(pluginhandle,'enablelibrary') == 'true':
            common.addDir('My Library','library','LIBRARY_ROOT')
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        exec 'import resources.lib.%s as sitemodule' % common.args.mode
        exec 'sitemodule.%s()' % common.args.sitemode

modes ( )
sys.modules.clear()
