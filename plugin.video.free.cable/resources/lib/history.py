#!/usr/bin/python

import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime,base64,sys
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import resources.lib._common as common
pluginhandle = int(sys.argv[1])

BASEURL = 'http://www.history.com/shows'
BASE = 'http://www.history.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    data = common.getURL(BASEURL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    showpages = tree.findAll(attrs={'class':'watch more'})
    db_shows = []
    for show in showpages:
        url = show['href']
        name = url.split('/')[2].replace('-',' ').title()
        url = BASE + url
        if db==True:
            db_shows.append((name,'history','showcats',url))
        else:
            common.addDirectory(name, 'history', 'showcats', url)
    if db==True:
        return db_shows    

def showcats(url=common.args.url):
    data = common.getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    colume1 = tree.find(attrs={'class':'col col-1'})
    try:
        cats = colume1.find(attrs={'class':'parent videos'}).findAll(attrs={'class':'clearfix'})
        for cat in cats:
            link = cat.find('a')
            url = BASE + link['href']
            name = link.string
            common.addDirectory(name, 'history', 'videos', url)
    except:
        videos()

def videos(url=common.args.url):
    data = common.getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.find(attrs={'class':'col col-7 col-last'}).find('ul').findAll('li',attrs={'style':True}, recursive=False)
    for video in videos:
        name = video.find('strong').string
        url = video['style'].split('url(')[1].replace(')','')
        thumb = url
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="history"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 #"Season":season,
                                                 #"Episode":episode,
                                                 #"Plot":description,
                                                 #"premiered":airdate,
                                                 #"Duration":duration,
                                                 #"TVShowTitle":common.args.name
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)
    
def play():
    path = re.compile('^(.+)/(.+?)/').findall(common.args.url)[0]
    url = path[0] + '/' + path[1] + '/' + path[1] + '.smil'
    link = common.getURL(url)
    tree=BeautifulStoneSoup(link, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    base = tree.find('meta')['base']
    videos = tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality']) * 1000
    for video in videos:
        bitrate = int(video['system-bitrate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            filename = video['src'].replace('.mp4','').replace('.flv','')
    swfUrl = 'http://www.history.com/flash/VideoPlayer.swf'
    finalurl = base+getAuth()+' swfurl='+swfUrl+' swfvfy=true playpath='+filename
    item = xbmcgui.ListItem(path=finalurl)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def getAuth():
    link = common.getURL('http://www.history.com/videos/categories_parent?name=secureflash/')
    auth = base64.decodestring(re.compile('<description>(.+?)</description>').findall(link)[0])
    aifp = re.compile('<category>(.+?)</category>').findall(link)[0]
    return '?ovpfv=2.1.4&auth='+auth+'&aifp='+aifp+'&slist=secureflash/'



	       
