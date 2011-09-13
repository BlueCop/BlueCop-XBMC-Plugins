import xbmc
import xbmcplugin
from xbmcgui import Dialog
import urllib
import common
import os
import sys

from BeautifulSoup import BeautifulStoneSoup

class Main:
    def __init__( self ):
        self.addMainHomeItems()
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )
    
    def addMainHomeItems( self ):
        #DISABLED WEBSITE LOGIN
        #if common.settings['enable_login']=='true':
        #    if not os.path.isfile(common.COOKIEFILE):
        #        common.login_cookie()


        html=common.getFEED(common.BASE_MENU_URL)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        menuitems=tree.findAll('item')
        fanart = common.hulu_fanart
        for item in menuitems:
            display=item.find('display').string
            items_url='http://m.hulu.com'+item.find('items_url').string
            cmtype=item.find('cmtype').string
            thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon.png"))
            if cmtype == 'None' or display == 'Help' or display == 'Profiles' or display == 'Now Playing':
                continue
            elif display =='Popular':
                thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon_popular.jpg"))
            elif display =='Recently Added':
                thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon_recently_added.jpg"))        
            elif display == 'TV':
                thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon_tv.jpg"))
            elif display == 'Movies':
                thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon_movies.jpg"))
            elif display == 'Search':
                thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon_search.jpg"))
            common.addDirectory(display,items_url,cmtype,thumbnail,thumbnail,fanart=fanart,page='1',perpage='25')
        if common.settings['enable_login']=='true':
            #try:
            if not os.path.isfile(common.QUEUETOKEN):
                common.login_queue()
            thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon_queue.jpg"))
            cm = [ ('Add Queue to Library', "XBMC.RunPlugin(%s?mode='updatexbmclibrary')" % ( sys.argv[0] ) ) ]
            common.addDirectory('Queue'         ,'http://m.hulu.com/menu/hd_user_queue'          , 'Queue'         ,thumbnail,thumbnail,fanart=fanart,page='1',perpage='2000',cm=cm)
            thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon_subscriptions.jpg"))
            cm = [ ('Add Subscriptions to Library', "XBMC.RunPlugin(%s?mode='xbmclibrary')" % ( sys.argv[0] ) ) ]
            common.addDirectory('Subscriptions' ,'http://m.hulu.com/menu/hd_user_subscriptions'  , 'Subscriptions' ,thumbnail,thumbnail,fanart=fanart,page='1',perpage='2000',cm=cm)
            thumbnail = xbmc.translatePath(os.path.join(common.imagepath,"icon_history.jpg"))
            common.addDirectory('History'       ,'http://m.hulu.com/menu/hd_user_history'        , 'History'       ,thumbnail,thumbnail,fanart=fanart,page='1',perpage='2000')
            #except:
            #    print 'Hulu Queue Failure'
