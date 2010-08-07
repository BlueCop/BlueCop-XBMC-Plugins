import xbmcplugin
import xbmcgui
import xbmc

import common
import urllib,urllib2
import sys
import re
import os

class Main:

    def __init__( self ):
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        if common.args.mode == 'Shows':
            self.LISTSHOWS('all')
        elif common.args.mode == 'ShowsPrimetime':
            self.LISTSHOWS('primetime')
        elif common.args.mode == 'ShowsDaytime':
            self.LISTSHOWS('daytime')
        elif common.args.mode == 'ShowsLate':
            self.LISTSHOWS('late')
        elif common.args.mode == 'ShowsClassics':
            self.LISTSHOWS('classics')
        elif common.args.mode == 'ShowsSpecials':
            self.LISTSHOWS('specials')

    def LISTSHOWS(self,cat):
        url = common.ALL_SHOWS_URL
        link=common.getHTML(url)
        match=re.compile('<a href="(.+?)" class="shows" target="_parent">(.+?)<').findall(link)
        for url,name in match:
                thumb = "http://www.cbs.com" + url + "images/common/show_logo.gif"
                #Clean names
                name = name.replace("<br>"," ").replace("&reg","").replace('&trade;','')
                #Ignore badshow links & showids
                if "http://" in url:
                        pass
                elif "/daytime/" == url:
                        pass
                elif "/primetime/survivor/fantasy/" == url:
                        pass                       
                else:
                        #Fix late show showid & thumb
                        if "/latenight/lateshow/" == url:
                                url = "/late_show/"
                                thumb = "http://www.cbs.com" + url + "images/common/show_logo.gif"
                        #Fix crimetime thumb        
                        elif "/crimetime/" == url:
                                thumb = "http://www.cbs.com" + url + "images/common/show_logo.png"
                        #Fix 48 Hours and Victorias Secret thumb
                        elif "/primetime/48_hours/" == url or "/specials/victorias_secret/" == url:
                                thumb = "http://www.cbs.com" + url + "images/common/show_logo.jpg"
                        elif "/primetime/big_brother/housecalls/" == url:
                                thumb = "http://www.cbs.com" + "/primetime/big_brother/" + "images/common/show_logo.gif"
                        #Blank icons for unavailable
                        elif "/primetime/flashpoint/" == url or "/primetime/game_show_in_my_head/" == url or "/specials/grammys/lincoln/" == url:
                                thumb = xbmc.translatePath(os.path.join(common.imagepath,url.replace('/','') + ".png"))

                        #Plot cache file
                        plotfile = xbmc.translatePath(os.path.join(common.cachepath,url.replace('/','') + ".txt"))
                        #Check for show info cache file
                        if os.path.isfile(plotfile):
                            f = open(plotfile , 'r')
                            plot = f.read()
                            f.close()
                        #No Plot
                        else:
                            plot = 'No Plot Information Available'
                        #All Categories
                        if cat == "all":
                            common.addDirectory(name,url,'List',thumb,thumb,plot)
                        #Selected Categories
                        elif cat in url:
                            common.addDirectory(name,url,'List',thumb,thumb,plot)

        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ))
