"""
        FREE CABLE
"""
#main imports
import xbmcplugin
import xbmc
import xbmcgui
import sys
import resources.lib._common as common
import urllib

pluginhandle = int (sys.argv[1])

#plugin constants
__plugin__ = "FREE CABLE"
__authors__ = "BlueCop"
__credits__ = ""
__version__ = "0.0.6"


print "\n\n\n\n\n\n\nstart of FREE CABLE plugin\n\n\n\n\n\n"

def modes( ):
    if sys.argv[2]=='':
        #Plug-in Root List
        common.addDirectory(' All Shows','Masterlist')
        for name , network in common.site_dict.iteritems():
            common.addDirectory(name, network, 'rootlist')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory( pluginhandle )
    elif common.args.mode is 'Masterlist':
        xbmcplugin.setContent(int(sys.argv[1]), 'TVShows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        shows = common.load_db()
        for tvdb_id, name, mode, sitemode, url, description, poster, fanart, aired, genre, rating in shows:
            common.addDirectory(name.encode('utf8'), mode, sitemode, url, poster, fanart, description, aired, genre)
        xbmcplugin.endOfDirectory(pluginhandle)
    elif common.args.mode in common.site_dict.values():
        exec 'import resources.lib.%s as sitemodule' % common.args.mode
        exec 'sitemodule.%s()' % common.args.sitemode
        if not common.args.sitemode.startswith('play'):
            xbmcplugin.endOfDirectory( pluginhandle )

modes ( )
sys.modules.clear()
