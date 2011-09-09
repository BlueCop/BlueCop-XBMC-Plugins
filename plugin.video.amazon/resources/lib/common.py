#!/usr/bin/env python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import cookielib
import mechanize
#import operator
import sys
import urllib
import urllib2
import re
import os.path
import xbmcplugin
import xbmcgui
import addoncompat

pluginhandle = int(sys.argv[1])

COOKIEFILE = os.path.join(os.getcwd().replace(';', ''),'resources','cache','cookies.lwp')

BASE_URL = 'http://www.amazon.com'

class _Info:
    def __init__( self, *args, **kwargs ):
        print "common.args"
        print kwargs
        self.__dict__.update( kwargs )

exec "args = _Info(%s)" % (urllib.unquote_plus(sys.argv[2][1:].replace("&", ", ").replace('"','\'')) , )


def getURL( url , host='www.amazon.com',useCookie=False):
    print 'getURL: '+url
    cj = cookielib.LWPCookieJar()
    if useCookie and os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17'),
                         ('Host', host)]
    usock = opener.open(url)
    response = usock.read()
    usock.close()
    return response

def addDir(name, mode, sitemode, url='', thumb='', fanart='', infoLabels=False, totalItems=0, cm=False):
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+mode+'"'
    u += '&sitemode="'+sitemode+'"'
    u += '&name="'+urllib.quote_plus(name.replace("'",'"'))+'"'
    if fanart == '':
        try:fanart = args.fanart
        except:fanart = os.path.join(os.getcwd().replace(';', ''),'fanart.jpg')
    else:u += '&fanart="'+urllib.quote_plus(fanart)+'"'
    if thumb == '':
        try:thumb = args.thumb
        except:thumb = os.path.join(os.getcwd().replace(';', ''),'icon.png')
    else:u += '&thumb="'+urllib.quote_plus(thumb)+'"'
    item=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumb)
    item.setProperty('fanart_image',fanart)
    if not infoLabels:
        infoLabels={ "Title": name}
    if cm:
        item.addContextMenuItems( cm )
    item.setInfo( type="Video", infoLabels=infoLabels)
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=item,isFolder=True,totalItems=totalItems)

def addVideo(name,url,poster='',fanart='',infoLabels=False,totalItems=0,cm=False,traileronly=False):
    if not infoLabels:
        infoLabels={ "Title": name}
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="play"'
    u += '&name="'+urllib.quote_plus(name.replace("'",'"'))+'"'
    utrailer = u+'&sitemode="PLAYTRAILER"'
    if traileronly:
        u += '&sitemode="PLAYTRAILER_RESOLVE"'        
    else:
        u += '&sitemode="PLAYVIDEO"'
    infoLabels['Trailer']=utrailer
    liz=xbmcgui.ListItem(name, thumbnailImage=poster)
    liz.setInfo( type="Video", infoLabels=infoLabels)
    liz.setProperty('fanart_image',fanart)
    liz.setProperty('IsPlayable', 'true')
    if cm:
        liz.addContextMenuItems( cm )
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=False,totalItems=totalItems)     

def mechanizeLogin():
    if os.path.isfile(COOKIEFILE):
        os.remove(COOKIEFILE)
    cj = cookielib.LWPCookieJar()
    br = mechanize.Browser()  
    br.set_handle_robots(False)
    br.set_cookiejar(cj)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17')]  
    sign_in = br.open("http://www.amazon.com/gp/flex/sign-out.html")   
    br.select_form(name="sign-in")  
    br["email"] = xbmcplugin.getSetting(pluginhandle,"login_name")
    br["password"] = xbmcplugin.getSetting(pluginhandle,"login_pass")
    logged_in = br.submit()  
    error_str = "The e-mail address and password you entered do not match any accounts on record."  
    if error_str in logged_in.read():
        xbmcgui.Dialog().ok('Login Error',error_str)
        print error_str
    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)