#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import string, os, re, time, datetime, math, time, unicodedata, types
import threading

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson

import mechanize

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

pluginhandle = int(sys.argv[1])
xbmcplugin.setContent(pluginhandle, 'musicvideos')

addon = xbmcaddon.Addon('plugin.video.mtv')
pluginpath = addon.getAddonInfo('path')
datapath = xbmc.translatePath('special://profile/addon_data/plugin.video.mtv/')
#cachepath = xbmc.translatePath(addon.getSetting('cache-folder'))

BASE = 'http://www.mtv.com'

fanart = os.path.join(pluginpath,'fanart.jpg')
vicon = os.path.join(pluginpath,'icon.png')
maxperpage=(int(addon.getSetting('perpage'))+1)*25

# Root listing

def listCategories():
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
        name = img['alt']
        url = BASE + link['href']
        id = thumb.split(':')[-1]
        addDir(name,   id,      'listArtistVideos', iconimage=thumb)
    xbmcplugin.endOfDirectory(pluginhandle)   

def listArtistVideos():   
    url = 'http://www.mtvmusicmeter.com/sitewide/dataservices/meter/videos/?id='+params['url']
    data = getURL(url)
    videos = demjson.decode(data)['videos']
    total = len(videos)
    for video in videos:
        mtvID = video['id']
        title = video['title_t']
        artist = video['artist_t']
        u = sys.argv[0]
        u += '?url='+urllib.quote_plus(mtvID)
        u += '&mode='+urllib.quote_plus('playVideo')
        displayname = artist+' - '+title
        item=xbmcgui.ListItem(displayname)
        item.setInfo( type="Video",infoLabels={ "Title":title,
                                                "Artist":artist})
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False,totalItems=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    
# Play Video
def playVideo():
    uri = 'mgid:uma:video:mtvmusic.com:%s' % params['url']
    configurl = 'http://media.mtvnservices.com/pmt/e1/players/mgid:uma:video:mtvmusic.com:/context10/context1/config.xml'
    configurl += '?uri=%s' % uri
    configurl += '&type=network&ref=www.mtv.com&geo=US&group=music&network=cable&device=Other'
    configxml = getURL(configurl)
    tree=BeautifulStoneSoup(configxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    mrssurl = tree.find('feed').string.replace('{uri}',uri).replace('&amp;','&').replace('{type}','network')
    mrssxml = getURL(mrssurl)
    tree=BeautifulStoneSoup(mrssxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    segmenturls = tree.findAll('media:content')
    stacked_url = 'stack://'
    for segment in segmenturls:
        surl = segment['url']
        videos = getURL(surl)
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
        stacked_url += rtmpurl.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(path=stacked_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

# Common
def addDir(name, url, mode, plot='', iconimage=vicon ,folder=True,total=0,page=1,cm=False):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+'&page='+str(page)
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

def getURL( url , postdata=False, alert=True):
    try:
        print 'MTV --> common :: getURL :: url = '+url
        #proxy = 'http://localhost:8888'
        #proxy_handler = urllib2.ProxyHandler({'http':proxy})
        #opener = urllib2.build_opener(proxy_handler)
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
