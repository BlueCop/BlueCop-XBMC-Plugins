import xbmc
import xbmcplugin
import xbmcgui

import common
import os
import sys

from BeautifulSoup import BeautifulSoup

pluginhandle = int (sys.argv[1])

class Main:
    def __init__( self ):
        self.addMainHomeItems()
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )

   
    def addMainHomeItems( self ):
        tvicon = xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png"))
        #Video lists
        common.addDirectory('Most Popular','popular','Videos')
        common.addDirectory('Latest Videos','latest','Videos')
        common.addDirectory('Full Episodes','fullep','Videos')
        #Show types
        data = common.getHTML(common.BASE_URL)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        categories=tree.findAll(attrs={'class' : 'head'})
        for item in categories:
            name = item.string
            common.addDirectory(name,mode="Shows")
