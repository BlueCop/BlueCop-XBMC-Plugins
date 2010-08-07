import xbmc
import xbmcplugin
from xbmcgui import Dialog

import common
import os
import sys

pluginhandle = int (sys.argv[1])

class Main:
    def __init__( self ):
        self.addMainHomeItems()
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )

   
    def addMainHomeItems( self ):
        namecount = 0
        if (xbmcplugin.getSetting(pluginhandle,'recent') == '0') or (xbmcplugin.getSetting(pluginhandle,'recent') == '2'):
            namecount += 1
            common.addDirectory(str(namecount) + ". Latest Videos",
                                common.ALL_RECENT_URL,
                                "Latest",
                                xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                                xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                                plot = "Latest Videos Added to CBS.com")
        if (xbmcplugin.getSetting(pluginhandle,'popular') == '0') or (xbmcplugin.getSetting(pluginhandle,'popular') == '2'):
            namecount += 1
            common.addDirectory(str(namecount) + ". Most Popular",
                                common.ALL_POPULAR_URL,
                                "Popular",
                                xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                                xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                                plot = "Most Popular Episodes and Clips from CBS.com")
        namecount += 1
        common.addDirectory(str(namecount) + ". All Shows",
                            common.ALL_SHOWS_URL,
                            "Shows",
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            plot = "")
        namecount += 1
        common.addDirectory(str(namecount) + ". Primetime",
                            common.ALL_SHOWS_URL,
                            "ShowsPrimetime",
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            plot = "")
        namecount += 1
        common.addDirectory(str(namecount) + ". Daytime",
                            common.ALL_SHOWS_URL,
                            "ShowsDaytime",
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            plot = "")
        namecount += 1
        common.addDirectory(str(namecount) + ". Late Night",
                            common.ALL_SHOWS_URL,
                            "ShowsLate",
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            plot = "")
        namecount += 1
        common.addDirectory(str(namecount) + ". TV Classics",
                            common.ALL_SHOWS_URL,
                            "ShowsClassics",
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            plot = "")
        namecount += 1
        common.addDirectory(str(namecount) + ". Specials",
                            common.ALL_SHOWS_URL,
                            "ShowsSpecials",
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png")),
                            plot = "")
        if (xbmcplugin.getSetting(pluginhandle,'hdcat') == 'true'):
            namecount += 1
            common.addDirectory(str(namecount) + ". HD Videos",
                                common.HDVIDEOS_URL,
                                "HD",
                                xbmc.translatePath(os.path.join(common.imagepath,"hd_icon.png")),
                                xbmc.translatePath(os.path.join(common.imagepath,"hd_icon.png")),
                                plot = "")
