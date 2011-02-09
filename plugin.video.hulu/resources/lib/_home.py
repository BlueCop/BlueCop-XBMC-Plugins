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
                if not os.path.isfile(common.COOKIEFILE):
                    common.login_cookie()
            except:
                print 'Hulu Login Failure'

        html=common.getFEED(common.BASE_MENU_URL)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        menuitems=tree.findAll('item')
        fanart = 'http://assets.huluim.com/companies/key_art_hulu.jpg'
        for item in menuitems:
            display=item.find('display').string
            items_url='http://m.hulu.com'+item.find('items_url').string
            cmtype=item.find('cmtype').string
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
        if common.settings['enable_login']=='true':
            try:
                if not os.path.isfile(common.QUEUETOKEN):
                    common.login_queue()
                thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon.png"))
                common.addDirectory('Queue'         ,'http://m.hulu.com/menu/hd_user_queue'          , 'Queue'         ,thumbnail,thumbnail,fanart=fanart,page='1',perpage='2000')
                common.addDirectory('Subscriptions' ,'http://m.hulu.com/menu/hd_user_subscriptions'  , 'Subscriptions' ,thumbnail,thumbnail,fanart=fanart,page='1',perpage='2000')
                common.addDirectory('History'       ,'http://m.hulu.com/menu/hd_user_history'        , 'History'       ,thumbnail,thumbnail,fanart=fanart,page='1',perpage='2000')
            except:
                print 'Hulu Queue Failure'
