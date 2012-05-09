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

addon = xbmcaddon.Addon('plugin.video.videolecture.net')
pluginpath = addon.getAddonInfo('path')
datapath = xbmc.translatePath('special://profile/addon_data/plugin.video.videolecture.net/')
if not os.path.exists(datapath):
    os.makedirs(datapath)
#cachepath = xbmc.translatePath(addon.getSetting('cache-folder'))

#VIDEOSSQL = os.path.join(pluginpath,'videos.sqlite')

BASE = 'http://videolectures.net'

fanart = os.path.join(pluginpath,'fanart.jpg')
vicon = os.path.join(pluginpath,'icon.png')
#maxperpage=(int(addon.getSetting('perpage'))+1)*25

# Root listing

def listRoot():
    addDir('Categories',       '', 'listCategories')
    #addDir('Categories Old',       'http://videolectures.net/', 'listCategoriesOLD')
    addDir('Search',           '', 'searchVideos')
    xbmcplugin.endOfDirectory(pluginhandle)

def listCategories():
    params['name']='Videos'
    listCatRootID(id='1')

def listCategoriesOLD(url=False):
    if not url:
        url = params['url']
    data = getURL(url)
    if data:
        tree=BeautifulSoup(data.replace('&nbsp;',' '), convertEntities=BeautifulSoup.HTML_ENTITIES)
        items = tree.find('ul',attrs={'class':'categories'}).findAll('li')
        for item in items:
            link = item.find('a')
            name=link.string.encode('utf-8')
            url=BASE+link['href']
            id = link['id'].replace('cat=','')
            total = item.contents[1].encode('utf-8').strip()
            display = name+total
            addDir(display,     id, 'listCatRootID')
            #addDir(display,     url, 'listCatRootURL')
        xbmcplugin.endOfDirectory(pluginhandle)

def listCatRootURL(url=False):
    if not url:
        url = params['url']
    data = getURL(url)
    if data:
        id = re.compile("query\+='&cid=(.+?)';").findall(data)[0]
        listCatRootID(id)

def listCatRootID(id=False):
    if not id:
        id = params['url']
    subcatUrl = 'http://videolectures.net/site/ajax/drilldown/counts/?cid='+id
    data = getURL(subcatUrl)
    if data:
        tree=BeautifulSoup(data.replace('&nbsp;',' '), convertEntities=BeautifulSoup.HTML_ENTITIES)
        itemTable = tree.find('div',attrs={'id':'drilldown_categories'})
        if itemTable:
            items = itemTable.findAll('span')
            addDir('All '+params['name'],     id, 'listCatVideosID')
            for item in items:
                link = item.find('a')
                name=link.string.encode('utf-8').strip()
                url=BASE+link['href']
                total = item.contents[2].encode('utf-8').strip()
                display = name+' '+total
                addDir(display,     url, 'listCatRootURL')
            xbmcplugin.endOfDirectory(pluginhandle)
        else:
            listCatVideosID(id)

def listCatVideosID(id=False,page=False,width=5):
    if not id:
        id = params['url']
    if not page:
        page = int(params['page'])
    videoUrl = 'http://videolectures.net/site/ajax/drilldown/'
    videoUrl += '?cid='+id
    videoUrl += '&w='+str(width)
    videoUrl += '&p='+str(page)
    data = getURL(videoUrl)
    if data:
        tree=BeautifulSoup(data.replace('&nbsp;',' '), convertEntities=BeautifulSoup.HTML_ENTITIES)
        itemTable = tree.find('div',attrs={'id':'drilldown_thumblist'})
        if 'javascript:go_to_page(' in data:
            current,last = re.compile("Page (.+?) of (.+?)\n").findall(data)[0]
            if current <> last:
                next = int(current)+1
                addDir('Next Page ('+str(next)+' of '+last+')', id, 'listCatVideosID', page=next)
                #addDir('Last Page ('+last+')', id, 'listCatVideosID', page=int(last))
        items = itemTable.findAll('div',attrs={'class':'evt_thumb'})
        for item in items:
            link = item.find('a')
            url = BASE+link['href']
            name = link.find('b').string.encode('utf-8').strip()
            thumb = item.find('img')['src']
            addDir(name,     url, 'ListEventVideos', iconimage=thumb)
        listVideos4Tree(itemTable)
    xbmcplugin.endOfDirectory(pluginhandle)

def ListEventVideos(url=False):
    if not url:
        url = params['url']
    data = getURL(url)
    if data:
        tree=BeautifulSoup(data.replace('&nbsp;',' '), convertEntities=BeautifulSoup.HTML_ENTITIES)
        listVideos4Tree(tree)
    xbmcplugin.endOfDirectory(pluginhandle)

def listVideos4Tree(tree):
    items = tree.findAll('div',attrs={'class':'lec_thumb'})
    for item in items:
        link = item.find('a')
        url = BASE+link['href']
        name = link.find('span',attrs={'class':'thumb_ext'}).string.encode('utf-8').strip()
        thumb = item.find('div',attrs={'class':'lec_thumb_img'})['style'].split("background:url('")[1].split("')")[0]
        try:
            author = item.find('div',attrs={'class':'author'}).find('span',attrs={'class':'thumb_ext'}).string.encode('utf-8').strip()
            display = name+' ('+author+')'
        except:display = name  
        addDir(display,     url, 'playVideo', iconimage=thumb ,playable=True)

def searchVideos():
    keyb = xbmc.Keyboard('', 'Search '+mode)
    keyb.doModal()
    if keyb.isConfirmed():
        search = urllib.quote_plus(keyb.getText())
        surl = 'http://videolectures.net/site/ajax/drilldown/?q='+search+'&cid=1&w=5'
        ListEventVideos(surl)

def playVideo(url=False):
    if not url:
        url = params['url']
    data = getURL(url)
    rtmp = re.compile('clip.netConnectionUrl = "(.+?)";').findall(data)[0]
    playpath = re.compile('clip.url = "(.+?)";').findall(data)[0]
    final = rtmp +' playpath='+playpath
    item = xbmcgui.ListItem(path=final)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

# Common
def addDir(name, url, mode, plot='', iconimage=vicon ,folder=True,total=0,page=1,cm=False,playable=False):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+'&name='+urllib.quote_plus(name)+'&page='+urllib.quote_plus(str(page))
    if iconimage <> vicon:
        u+='&iconimage='+urllib.quote_plus(iconimage)
    item=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    #if iconimage <> vicon:
    #    item.setProperty('fanart_image',iconimage)
    item.setInfo( type="Video", infoLabels={ "Title":name,
                                             "plot":plot
                                           })
    if playable:
        item.setProperty('IsPlayable', 'true')
        folder=False
    if cm:
        item.addContextMenuItems( cm )
    return xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,totalItems=total,isFolder=folder)

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
        print 'VIDEOLECTURES --> common :: getURL :: url = '+url
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
    param={}
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
    listRoot()
else:
    exec '%s()' % mode
