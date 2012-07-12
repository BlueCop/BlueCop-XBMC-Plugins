"""
        FREE CABLE
"""
#main imports
import xbmcplugin
import xbmc
import xbmcgui
import sys
import os
import resources.lib._common as common
import urllib

pluginhandle = int (sys.argv[1])

#plugin constants
__plugin__ = "FREE CABLE"
__authors__ = "BlueCop"
__credits__ = ""
__version__ = "0.3.1"


print "\n\n\n\n\n\n\nstart of FREE CABLE plugin\n\n\n\n\n\n"

def modes( ):
    if sys.argv[2]=='':
        #Plug-in Root List
        common.addDirectory(' Favorite Shows','Favorlist','NoUrl',thumb=common.fav_icon)
        common.addDirectory(' All Shows','Masterlist','NoUrl',thumb=common.all_icon)
        for network, name  in common.site_dict.iteritems():
            station_icon = os.path.join(common.imagepath,network+'.png')
            if common.addoncompat.get_setting(network) == 'true':
                common.addDirectory(name, network, 'rootlist',thumb=station_icon,fanart=common.plugin_fanart)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory( pluginhandle )
        common.setView()
    elif common.args.mode == 'Masterlist':
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        common.load_showlist()
        common.setView('tvshows')
        xbmcplugin.endOfDirectory(pluginhandle)
    elif common.args.mode == 'Favorlist':   
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        common.load_showlist(favored=True)
        common.setView('tvshows')
        xbmcplugin.endOfDirectory(pluginhandle)
    elif common.args.mode == 'common':
        exec 'common.%s()' % common.args.sitemode
    elif common.args.mode in common.site_dict.keys():
        exec 'import resources.lib.%s as sitemodule' % common.args.mode
        exec 'sitemodule.%s()' % common.args.sitemode
        if not common.args.sitemode.startswith('play'):
            xbmcplugin.endOfDirectory( pluginhandle )

modes ( )
sys.modules.clear()
