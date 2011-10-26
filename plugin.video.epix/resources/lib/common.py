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

def getURL( url , useCookie=False):
    print 'getURL: '+url
    if useCookie and os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17')]
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
    liz.setProperty('fanart_image',fanart)
    liz.setProperty('IsPlayable', 'true')
    if cm:
        liz.addContextMenuItems( cm , replaceItems=True )
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=False,totalItems=totalItems)
    
def login():
    providers = { '8':'Charter Communications',
                  '7':'Cox Communications',
                  '10':'DISH Network',
                  '9':'Mediacom',
                  '14':'Suddenlink',
                  '1':'Verizon FiOS'}
    types = ['Epix','8','7','10','9','14','1']
    logintype = types[int(addon.getSetting("logintype"))]
    if logintype == 'Epix':
        epixlogin()
    else:
        cablelogin(logintype)

def cablelogin(selected):
    if os.path.isfile(COOKIEFILE):
        if addon.getSetting("clearcookies") == 'true':
            os.remove(COOKIEFILE)
        else:
            return
    data = getURL('http://www.epixhd.com/epx/ajax/chooseMSO/?mso_id='+selected)
    jsondata = demjson.decode(data)
    tree = BeautifulStoneSoup(jsondata['content'], convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    try:
        signinUrl = tree.find('iframe')['src']
        provider =  tree.find('iframe')['class']
    except:
        signinUrl = re.compile('<script language="javascript">self.parent.location="(.*?)";').findall(jsondata['content'])[0]
        provider = 'cox'
    br = mechanize.Browser()  
    br.set_handle_robots(False)
    br.set_cookiejar(cj)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17')]  
    sign_in = br.open(signinUrl)
    if provider == 'charter':
        br.select_form(name="f")  
        br["username"] = addon.getSetting("login_name")
        br["password"] = addon.getSetting("login_pass")
        br["zipcode"] = addon.getSetting("zipcode")
    elif provider == 'cox':
        br.select_form(name="LoginPage")  
        br["username"] = addon.getSetting("login_name")
        br["password"] = addon.getSetting("login_pass")
    elif provider == 'dish':
        br.select_form(name="f")  
        br["username"] = addon.getSetting("login_name")
        br["password"] = addon.getSetting("login_pass")
    elif provider == 'mediacom':
        br.select_form(name="f")  
        br["username"] = addon.getSetting("login_name")
        br["password"] = addon.getSetting("login_pass")
    elif provider == 'suddenlink':
        br.select_form(name="f")  
        br["username"] = addon.getSetting("login_name")
        br["password"] = addon.getSetting("login_pass")
    elif provider == 'verizon':
        br.select_form(name="loginpage")
        br["IDToken1"] = addon.getSetting("login_name")
        br["IDToken2"] = addon.getSetting("login_pass")
    br.submit()
    br.select_form(nr=0)
    response = br.submit()
    data = response.read()
    redirect = 'http://www.epixhd.com' + re.compile('self.parent.location="(.*?)"').findall(data)[0]
    print getURL(redirect) 
    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)

def epixlogin():
    if os.path.isfile(COOKIEFILE):
        if addon.getSetting("clearcookies") == 'true':
            os.remove(COOKIEFILE)
        else:
            return
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

