#!/usr/bin/python

import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime,base64,sys
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import random
import resources.lib._common as common
pluginhandle = int(sys.argv[1])

BASEURL = 'http://www.history.com/shows'
H2URL = 'http://www.history.com/shows/h2'
BASE = 'http://www.history.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    db_shows = []
    data = common.getURL(BASEURL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    showpages = tree.findAll(attrs={'class':'watch more'}) 
    for show in showpages:
        url = show['href']
        name = url.split('/')[2].replace('-',' ').title()
        url = BASE + url
        if db==True:
            db_shows.append((name,'history','showcats',url))
        else:
            common.addDirectory(name, 'history', 'showcats', url)
    data = common.getURL(H2URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    showpages = tree.findAll(attrs={'class':'watch more'})
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
            url = link['href']
            if BASE not in url:
                url = BASE + url
            name = link.string
            common.addDirectory(name, 'history', 'videos', url)
    except:
        videos()

def videos(url=common.args.url):
    link = common.getURL(url)
    mrssData = re.compile('mrssData += +"(.+)"').findall(link)[0];
    mrssData = urllib2.unquote(base64.decodestring(mrssData))
    tree=BeautifulStoneSoup(mrssData,convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print tree.prettify()
    items = tree.findAll('item')
    for item in items:
        title = item.title.contents[0]
        plot  = item.description.contents[0]
        thumb = item.findAll('media:thumbnail')[0]['url']
        duration = item.findAll('media:content')[0]['duration']
        smil = item.findAll('media:text')[5].contents[0]
        smil = smil.replace('smilUrl=','')
        #episode_list.append((title, image, duration, plot, smil))
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(smil)+'"'
        u += '&mode="history"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(title, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":title,
                                                 #"Season":season,
                                                 #"Episode":episode,
                                                 "Plot":plot,
                                                 #"premiered":airdate,
                                                 "Duration":duration,
                                                 #"TVShowTitle":common.args.name
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

def play():
    sig = common.getURL('http://www.history.com/components/get-signed-signature?url='+re.compile('/s/(.+)\?').findall(common.args.url)[0]+'&cache=889')
    url = common.args.url+'&sig='+sig
    link = common.getURL(url)
    tree=BeautifulStoneSoup(link, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print tree.prettify()
    base = tree.find('meta')['base']
    videos = tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality']) * 1000
    for video in videos:
        try:bitrate = int(video['system-bitrate'])
        except:bitrate = int(video['systembitrate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            filename = video['src'].replace('.mp4','').replace('.flv','')
    swfUrl = 'http://www.history.com/flash/VideoPlayer.swf'
    auth = filename.split('?')[1]
    filename = filename.split('?')[0]
    finalurl = base+'?'+auth+' swfurl='+swfUrl+' swfvfy=true playpath='+filename
    item = xbmcgui.ListItem(path=finalurl)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)



	       
