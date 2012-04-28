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

addon = xbmcaddon.Addon('plugin.video.baeble')
pluginpath = addon.getAddonInfo('path')
datapath = xbmc.translatePath('special://profile/addon_data/plugin.video.baeble/')
if not os.path.exists(datapath):
    os.makedirs(datapath)
#cachepath = xbmc.translatePath(addon.getSetting('cache-folder'))

VIDEOSSQL = os.path.join(pluginpath,'videos.sqlite')

BASE = 'http://www.baeblemusic.com'

fanart = os.path.join(pluginpath,'fanart.jpg')
vicon = os.path.join(pluginpath,'icon.png')
#maxperpage=(int(addon.getSetting('perpage'))+1)*25

# Root listing

def listCategories():
    addDir('Videos',           '', 'AllVideos')
    addDir('Sessions',         '', 'AllSessions')
    addDir('Concerts',         '', 'AllConcerts')
    addDir('Interviews',       '', 'AllInterviews')
    addDir('Artists',          '', 'AllArtists')
    #addDir('Scan Artists',     '', 'scanArtistdb')
    xbmcplugin.endOfDirectory(pluginhandle)

def AllArtists():
    createMusicdb()
    db = sqlite.connect(VIDEOSSQL)
    db.text_factory = str
    c = db.cursor()
    for artist in c.execute('select distinct artist,image from videos'):
        image = artist[1]
        artist = artist[0]
        addDir(artist,     artist, 'ListArtistVideos',iconimage=image)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView()
    c.close()

def ListArtistVideos():
    createMusicdb()
    db = sqlite.connect(VIDEOSSQL)
    db.text_factory = str
    c = db.cursor()
    for video in c.execute('select distinct * from videos where artist = (?)', (params['url'],)):
        video_id = video[0]
        artist = video[1]
        title = video[2]
        type = video[3]
        image = video[4]
        url = video[5].replace(' ','_')
        published = video[6]
        favor = video[7]
        displayname = artist+' - '+title
        item=xbmcgui.ListItem(displayname, iconImage=image, thumbnailImage=image)
        item.setProperty('fanart_image',image)
        item.setInfo( type="Video",infoLabels={ "Title":displayname,
                                                "Artist":artist,
                                                "Album":artist})
        item.setProperty('IsPlayable', 'true')
        item.setProperty('mimetype', 'video/mp4')
        xbmcplugin.addDirectoryItem(pluginhandle,url=url,listitem=item,isFolder=False)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView()
    c.close()
    
def AllInterviews():
    AllVideos(type='interview')

def AllSessions():
    AllVideos(type='Session')
    
def AllConcerts():
    AllVideos(type='concert')

def AllVideos(type='musicvideo'):
    createMusicdb()
    db = sqlite.connect(VIDEOSSQL)
    db.text_factory = str
    c = db.cursor()
    for video in c.execute('select distinct * from videos where type = (?)', (type,)):
        video_id = video[0]
        artist = video[1]
        title = video[2]
        type = video[3]
        image = video[4]
        url = video[5].replace(' ','_')
        published = video[6]
        favor = video[7]
        displayname = artist+' - '+title
        item=xbmcgui.ListItem(displayname, iconImage=image, thumbnailImage=image)
        item.setProperty('fanart_image',image)
        item.setInfo( type="Video",infoLabels={ "Title":displayname,
                                                "Artist":artist,
                                                "Album":artist})
        item.setProperty('IsPlayable', 'true')
        item.setProperty('mimetype', 'video/mp4')
        xbmcplugin.addDirectoryItem(pluginhandle,url=url,listitem=item,isFolder=False)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView()
    c.close()
    

def createMusicdb():
    if not os.path.isfile(VIDEOSSQL):
        db = sqlite.connect(VIDEOSSQL)
        db.text_factory = str
        c = db.cursor()
        c.execute('''CREATE TABLE videos(
                     id INTEGER,
                     artist TEXT,
                     title TEXT,
                     type TEXT,
                     image TEXT,
                     media TEXT,
                     published TEXT,
                     favor BOOLEAN,
                     PRIMARY KEY(id,type)
                     );''')
        db.commit()
        c.close()

def scanArtistdb():
    createMusicdb()
    uri = 'http://www.baeblemusic.com/setlists/miscVideos/%s.txt'
    #uri = 'http://www.baeblemusic.com/setlists/concerts/%s.txt'
    db = sqlite.connect(VIDEOSSQL)
    db.text_factory = str
    c = db.cursor()
    failed = []
    for i in range(1,2109):
        url = uri % str(i)
        data = getURL(url,alert=False)
        if data and data <> '}':
            video = demjson.decode(data)['Video Data'][0]
            id = video['id']
            type = video['videoType']
            if 'guestapt' == type:
                type = 'Session'
            print id,type
            #'interview'
            #'musicvideo'
            #'guestapt'
            #'concert'
            if '<br/>' in video['title']:
                title = video['title'].split('<br/>')[0]
                artist = video['title'].split('<br/>')[1]
            elif 'with' in video['title']:
                title = video['title'].split('with')[0].strip()
                artist = video['title'].split('with')[1].strip()
            elif 'live at' in video['title']:
                title = 'Live at '+video['title'].split('live at')[1].strip()
                artist = video['title'].split('live at')[0].strip()
            else:
                title = video['title']
                artist = type.title()
            thumb = video['thumbnail'].replace('-150','-498')
            media = video['url'].replace(' ','_')
            published = video['published']
            #published = time.strptime(video['published'][:-6], '%a, %d %b %Y %H:%M:%S')
            c.execute('insert into videos values (?,?,?,?,?,?,?,?)', [id,artist,title,type,thumb,media,published,False])
            db.commit()
        else:
            failed.append(i)
    c.close()
    print failed

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
        print 'baeble --> common :: getURL :: url = '+url
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
