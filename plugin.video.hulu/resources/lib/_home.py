import xbmc
import xbmcplugin
from xbmcgui import Dialog

import common
import os
import sys

from BeautifulSoup import BeautifulStoneSoup

class Main:
    def __init__( self ):
        self.addMainHomeItems()
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )
    
    def addMainHomeItems( self ):
        if common.settings['enable_login']=='true':
            try:
                common.login()
            except:
                print 'Hulu Login Failure'
        html=common.getFEED(common.BASE_MENU_URL)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        menuitems=tree.findAll('item')
        for item in menuitems:
            display=item.find('display').string
            items_url='http://m.hulu.com'+item.find('items_url').string
            cmtype=item.find('cmtype').string
            fanart = 'http://assets.huluim.com/companies/key_art_hulu.jpg'
            if cmtype == 'None' or display == 'Help' or display == 'Profiles' or display == 'Now Playing':
                continue
            elif display == 'TV':
                thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"tv_icon.png"))
                plot = "A listing of all the Television Shows currently available on Hulu.com"
            elif display == 'Movies':
                thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"movie_icon.png"))
                plot = "A listing of all the Movies currently available on Hulu.com"
            elif display == 'Search':
                thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"search_icon.png"))
                plot = "Search content currently available on Hulu.com"
            else:
                thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon.png"))
                plot = ''
            common.addDirectory(display,items_url,cmtype,thumbnail,thumbnail,fanart=fanart,plot=plot,page='1',perpage='25')
