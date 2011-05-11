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
        menu=tree.find(attrs={'id' : 'videoContent'})
        categories=menu.findAll('div', attrs={'id' : True}, recursive=False)
        for item in categories:
            if item['id'] == common.args.url:
                shows = item.findAll(attrs={'id' : 'show_block_interior'})
                for show in shows:
                    name = show.find('img')['alt'].encode('utf-8')
                    thumbnail = common.BASE_URL + show.find('img')['src']
                    url = common.BASE + show.find('a')['href'].encode('utf-8')
                    common.addDirectory(name, url,'Videos',thumb=thumbnail)
                break
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ))
