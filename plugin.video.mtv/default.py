#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import string, os, re, time, datetime, math, time, unicodedata, types
import threading

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson

#import mechanize

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

pluginhandle = int(sys.argv[1])
xbmcplugin.setContent(pluginhandle, 'musicvideos')

addon = xbmcaddon.Addon('plugin.video.mtv')
pluginpath = addon.getAddonInfo('path')
datapath = xbmc.translatePath('special://profile/addon_data/plugin.video.mtv/')
if not os.path.exists(datapath):
    os.makedirs(datapath)
#cachepath = xbmc.translatePath(addon.getSetting('cache-folder'))

FAVFILESQL = os.path.join(datapath,'favs.sqlite')

VIDEOCACHE = os.path.join(datapath,'cache.json')

BASE = 'http://www.mtv.com'

fanart = os.path.join(pluginpath,'fanart.jpg')
vicon = os.path.join(pluginpath,'icon.png')
#maxperpage=(int(addon.getSetting('perpage'))+1)*25

# Root listing

def listCategories():
    addDir('Favorite Artists',     '', 'favArtists')
    addDir('Popular Artists'  , 'http://www.mtv.com/music/artists/most_popular.jhtml', 'listArtists')
    addDir('Artist Picks'     , 'http://www.mtv.com/music/artists/', 'listArtists')
    addDir('Artists A-Z',       '', 'listArtistAZ')
    xbmcplugin.endOfDirectory(pluginhandle)

def listArtistAZ():
    url = 'http://www.mtv.com/music/artists/browse.jhtml?chars='
    alphabet=set(string.ascii_lowercase)
    for letter in alphabet:
        addDir(letter.upper(), url+str(letter), 'listArtists')
    addDir('#', url+'.', 'listArtists')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle)

def listArtists():
    url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    links = tree.find('div',attrs={'class':'group-b'}).findAll('a')
    for link in links:
        img = link.find('img')
        thumb = img['src'].split('?')[0]
        name = img['alt'].encode('utf-8')
        url = BASE + link['href']
        id = thumb.split(':')[-1]
        cm = []
        u='plugin://plugin.video.youtube/?path=/root/search&feed=search&search='+urllib.quote_plus(name)+'&'
        cm.append( ('YouTube %s' % name, "Container.Update(%s)" % u) )
        u=sys.argv[0]+"?id="+urllib.quote_plus(id)+"&name="+urllib.quote_plus(name)+"&image="+urllib.quote_plus(thumb)+"&mode="+urllib.quote_plus('addfavArtistdb')
        cm.append( ('Favorite %s' % name, "XBMC.RunPlugin(%s)" % u) )
        addDir(name,   id,      'listArtistRoot', iconimage=thumb, cm=cm)
    xbmcplugin.endOfDirectory(pluginhandle)
    setView() 

def listArtistRoot():
    url = 'http://www.mtvmusicmeter.com/sitewide/dataservices/meter/videos/?id='+params['url']
    data = getURL(url)
    SaveFile(VIDEOCACHE, data)
    videos = demjson.decode(data)['videos']
    total = len(videos)
    types = []
    for video in videos:
        videoType = video['videoTypeGrouping_facet'].replace('_',' ').title()
        if videoType not in types:
            types.append(videoType)
    for type in types:
        addDir(type,params['url'], 'listArtistVideos', iconimage=params['artistimage'])
    addDir('All Videos',            params['url'], 'listArtistVideos', iconimage=params['artistimage'])
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle)

def listArtistVideos():   
    #url = 'http://www.mtvmusicmeter.com/sitewide/dataservices/meter/videos/?id='+params['url']
    #data = getURL(url)
    data = OpenFile(VIDEOCACHE)
    videos = demjson.decode(data)['videos']
    total = len(videos)
    for video in videos:
        videoType = video['videoTypeGrouping_facet'].replace('_',' ').title()
        if videoType == params['name'] or 'All Videos' == params['name']:
            mtvID = video['id']
            title = video['title_t'].replace('&amp;','&')
            artist = video['artist_t']
            image = 'http://images1.mtv.com/uri/mgid:uma:video:mtv.com:'+mtvID
            displayname = title#+' (%s)' % videoType
            u = sys.argv[0]
            u += '?url='+urllib.quote_plus(mtvID)
            u += '&mode='+urllib.quote_plus('playVideo')
            item=xbmcgui.ListItem(displayname, iconImage=image, thumbnailImage=image)
            item.setProperty('fanart_image',params['artistimage'])
            item.setInfo( type="Video",infoLabels={ "Title":title,
                                                    "Studio":videoType,
                                                    "Artist":artist,
                                                    "Album":artist})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False,totalItems=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView()
    
# Play Video
def playVideo():
    uri = 'mgid:uma:video:mtvmusic.com:%s' % params['url']
    vid = params['url']
    mediaurl = 'http://services.mtvmusic.com/player/embed/includes/media-gen.jhtml'
    mediaurl += '?uri=%s&vid=%s&type=network&ref={ref}&bug=' % (uri,vid)
    if addon.getSetting('us_proxy_enable') == 'true':
        proxy=True
    else:
        proxy=False
    videos = getURL(mediaurl,proxy=proxy)
    videos = BeautifulStoneSoup(videos, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('rendition')
    hbitrate = -1
    sbitrate = int(10000000)
    for video in videos:
        bitrate = int(video['bitrate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            rtmpdata = video.find('src').string
            swfUrl = "http://media.mtvnservices.com/player/prime/mediaplayerprime.1.12.1.swf"
            rtmpurl = rtmpdata + " swfurl=" + swfUrl + " swfvfy=true"
    item = xbmcgui.ListItem(path=rtmpurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

# Common
def addDir(name, url, mode, plot='', iconimage=vicon ,folder=True,total=0,page=1,cm=False):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+'&name='+urllib.quote_plus(name)
    if iconimage <> vicon:
        u+='&artistimage='+urllib.quote_plus(iconimage)
    item=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if iconimage <> vicon:
        item.setProperty('fanart_image',iconimage)
    item.setInfo( type="Video", infoLabels={ "Title":name,
                                             "plot":plot
                                           })
    if cm:
        item.addContextMenuItems( cm )
    return xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=folder,totalItems=total)

def setView(override=False):
    confluence_views = [50,500,511]
    if addon.getSetting('viewenable') == 'true':
        if override:
            view = str(override)
        else:
            view=int(addon.getSetting('defaultview'))
            view = str(confluence_views[view])
        xbmc.executebuiltin("Container.SetViewMode("+view+")")

def getURL( url , postdata=False, alert=True, proxy=False):
    try:
        print 'MTV --> common :: getURL :: url = '+url
        if proxy:
            us_proxy = 'http://' + addon.getSetting('us_proxy') + ':' + addon.getSetting('us_proxy_port')
            proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
            if addon.getSetting('us_proxy_pass') <> '' and addon.getSetting('us_proxy_user') <> '':
                print 'Using authenticated proxy: ' + us_proxy
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, us_proxy, addon.getSetting('us_proxy_user'), addon.getSetting('us_proxy_pass'))
                proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
            else:
                print 'Using proxy: ' + us_proxy
                opener = urllib2.build_opener(proxy_handler)
        else:
            opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0')]
        if postdata:
            usock=opener.open(url,postdata)
        else:
            usock=opener.open(url)
        response=usock.read()
        usock.close()
        return response
    except urllib2.URLError, e:
        print 'Error reason: ', e
        heading = 'Error'
        message = e
        duration = 10000
        if alert:
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
        return False

def favArtists():
    xbmcplugin.setContent(pluginhandle, 'artists')
    createArtistdb()
    db = sqlite.connect(FAVFILESQL)
    db.text_factory = str
    c = db.cursor()
    for artist in c.execute('select distinct * from artists'):
        artist_id = artist[0]
        artist_name = artist[1]
        artist_image = artist[2]
        video_count = artist[3]
        cm = []
        u='plugin://plugin.video.youtube/?path=/root/search&feed=search&search='+urllib.quote_plus(artist_name)+'&'
        cm.append( ('YouTube %s' % artist_name, "Container.Update(%s)" % u) )
        u=sys.argv[0]+"?id="+urllib.quote_plus(artist_id)+"&mode="+urllib.quote_plus('removefavArtists')
        cm.append( ('Remove %s' % artist_name, "XBMC.RunPlugin(%s)" % u) )
        addDir(artist_name, artist_id, 'listArtistRoot', iconimage=artist_image, cm=cm)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView()
    c.close()

def createArtistdb():
    if not os.path.isfile(FAVFILESQL):
        db = sqlite.connect(FAVFILESQL)
        db.text_factory = str
        c = db.cursor()
        c.execute('''CREATE TABLE artists(
                     id TEXT,
                     name TEXT,
                     image TEXT,
                     count INTEGER,
                     PRIMARY KEY(id)
                     );''')
        db.commit()
        c.close()

def addfavArtistdb():
    id = params['id']
    name = params['name']
    image = params['image']
    createArtistdb()
    db = sqlite.connect(FAVFILESQL)
    db.text_factory = str
    c = db.cursor()
    c.execute('insert or ignore into artists values (?,?,?,?)', [id,name,image,0])
    db.commit()
    c.close()
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Added Artist', 5000) )
 
def removefavArtists():
    db = sqlite.connect(FAVFILESQL)
    db.text_factory = str
    c = db.cursor()
    c.execute('delete from artists where id = (?)', (params['id'],) )
    db.commit()
    c.close()
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Deleted Artist', 5000) )
    #xbmc.executebuiltin("Container.Refresh()")
    
def deletefavArtists():
    db = sqlite.connect(FAVFILESQL)
    db.text_factory = str
    c = db.cursor()
    c.execute('delete from artists')
    db.commit()
    c.close()
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Deleted Favorite Artists', 10000) )

def SaveFile(path, data):
    file = open(path,'w')
    file.write(data)
    file.close()

def OpenFile(path):
    file = open(path, 'r')
    contents=file.read()
    file.close()
    return contents

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=urllib.unquote_plus(splitparams[1])                                        
    return param

params=get_params()
try:
    mode=params["mode"]
except:
    mode=None
print "Mode: "+str(mode)
print "Parameters: "+str(params)

if mode==None:
    listCategories()
else:
    exec '%s()' % mode
