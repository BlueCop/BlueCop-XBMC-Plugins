#!/usr/bin/env python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import cookielib
import mechanize
import demjson
import sys
import urllib
import urllib2
import re
import os.path
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc

print sys.argv
addon = xbmcaddon.Addon('plugin.video.epix')
pluginpath = addon.getAddonInfo('path')

pluginhandle = int(sys.argv[1])

COOKIEFILE = os.path.join(xbmc.translatePath(pluginpath),'resources','cache','cookies.lwp')

BASE_URL = 'http://www.epixhd.com'
cj = cookielib.LWPCookieJar()

class _Info:
    def __init__( self, *args, **kwargs ):
        print "common.args"
        print kwargs
        self.__dict__.update( kwargs )

exec "args = _Info(%s)" % (urllib.unquote_plus(sys.argv[2][1:].replace("&", ", ").replace('"',"\"")) , )

def getURL( url , host='www.amazon.com',useCookie=False):
    print 'getURL: '+url
    if useCookie and os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17'),
                         ('Host', host)]
    usock = opener.open(url)
    response = usock.read()
    usock.close()
    #cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    return response

def addDir(name, mode, sitemode, url='', thumb='', fanart='', infoLabels=False, totalItems=0, cm=False):
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+mode+'"'
    u += '&sitemode="'+sitemode+'"'
    u += '&name="'+urllib.quote_plus(name)+'"'
    item=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumb)
    item.setProperty('fanart_image',fanart)
    if not infoLabels:
        infoLabels={ "Title": name}
    if cm:
        item.addContextMenuItems( cm, replaceItems=True  )
    item.setInfo( type="Video", infoLabels=infoLabels)
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=item,isFolder=True,totalItems=totalItems)

def addVideo(name,url,poster='',fanart='',infoLabels=False,totalItems=0,cm=False,traileronly=False):
    if not infoLabels:
        infoLabels={ "Title": name}
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="play"'
    u += '&name="'+urllib.quote_plus(name)+'"'
    u += '&sitemode="PLAYVIDEO"'
    liz=xbmcgui.ListItem(name, thumbnailImage=poster)
    liz.setInfo( type="Video", infoLabels=infoLabels)
    liz.setProperty('fanart_image',poster)
    liz.setProperty('IsPlayable', 'true')
    if cm:
        liz.addContextMenuItems( cm , replaceItems=True )
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=False,totalItems=totalItems)     

def login():
    if os.path.isfile(COOKIEFILE):
        os.remove(COOKIEFILE)
    loginurl = 'https://secure.epixhd.com/epx/ajax/user/login/'
    loginurl += '?jsoncallback=jQuery00000000000000000000_0000000000000'
    loginurl += '&user_email='+addon.getSetting("login_name")
    loginurl += '&user_password='+addon.getSetting("login_pass")
    loginurl += '&temp_password=Password'
    data = getURL(loginurl).split('(')[1].split(')')[0]
    jsondata = demjson.decode(data)
    auth = 'http://www.epixhd.com/epx/ajax/user/auth/?otk='+jsondata['otk']
    print getURL(auth)
    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)

