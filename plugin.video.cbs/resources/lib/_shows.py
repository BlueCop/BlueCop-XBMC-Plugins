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
        #<a href="?showname=primetime/48_hours#video">48 Hours Mystery</a>
        #match=re.compile('<a href="\?showname=(.+?)\#video">(.+?)</a>').findall(link)
        for url,name in match:
                #thumb = "http://www.cbs.com" + url + "images/common/show_logo.gif"
                #Clean names
                url = '/'+url.replace('&showtype=classics','')+'/'
                name = name.replace("<br>"," ").replace("&reg;","").replace('&trade;','').replace('&amp;','&')
                #Ignore badshow links & showids
                if "http://" in url:
                        pass
                elif "/daytime/" == url:
                        pass                 
                else:
                        #All Categories
                        if cat == "all":
                            common.addDirectory(name,url,'List')
                        #Selected Categories
                        elif cat in url:
                            common.addDirectory(name,url,'List')

        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ))
