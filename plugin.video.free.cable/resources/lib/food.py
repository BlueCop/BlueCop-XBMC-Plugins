import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson
import resources.lib._common as common

pluginhandle = int (sys.argv[1])

BASE_URL = 'http://www.foodnetwork.com/food-network-full-episodes/videos/index.html'
BASE = 'http://www.foodnetwork.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    items=tree.find(attrs={'class':'playlists'}).findAll('a')
    for item in items:
        name = item.string.split('-')[0].strip()
        url = BASE+item['href'].replace('channel-video/json/','feeds/channel-video/').replace(',00.json','_RA,00.json')
        common.addDirectory(name, 'food', 'show', url)
        
def show(url=common.args.url):
    data = common.getURL(url)
    videos = demjson.decode(data.split(' = ')[1])[0]['videos']
    for video in videos:
        if 'Season' in common.args.name:
            season = int(common.args.name.split('Season')[1])
            showname = common.args.name.split('Season')[0]
        else:
            showname = common.args.name
            season = 0
        #episode = int(video['number'])
        name = video['label']
        duration = video['length']
        thumb = video['thumbnailURL']
        description = video['description']
        airDate = video['delvStartDt']
        playpath = video['videoURL'].replace('http://wms.scrippsnetworks.com','').replace('.wmv','')
        url = 'rtmp://flash.scrippsnetworks.com:1935/ondemand?ovpfv=1.1'
        url+= ' swfUrl=http://common.scrippsnetworks.com/common/snap/snap-3.0.3.swf playpath='+playpath
        displayname = name
        item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 "Season":season,
                                                 #"Episode":episode,
                                                 "Plot":description,
                                                 "premiered":airDate,
                                                 "Duration":duration,
                                                 "TVShowTitle":showname
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=url,listitem=item,isFolder=False)