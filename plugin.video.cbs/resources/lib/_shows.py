import xbmcplugin
import xbmcgui
import xbmc

import common
import urllib,urllib2
import sys
import re
import os
from BeautifulSoup import BeautifulSoup

class Main:

    def __init__( self ):
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        data = common.getHTML(common.BASE_URL)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        menu=tree.find(attrs={'id' : 'navigation'})
        catgories=menu.findAll(attrs={'class' : 'head'})
        for item in catgories:
            if item.string == common.args.name:
                marker = catgories.index(item)
                shows = menu.findAll('ul')[marker].findAll('a')
                for show in shows:
                    name = show.string.encode('utf-8')
                    series = show['onclick'].replace("set_show(this,'",'').replace("');",'').encode('utf-8')
                    common.addDirectory(name,'showlist','Videos',series)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ))
