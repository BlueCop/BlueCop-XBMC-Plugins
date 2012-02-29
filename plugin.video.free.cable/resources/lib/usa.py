import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

import demjson
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from pyamf.remoting.client import RemotingService
import resources.lib._common as common

pluginhandle = int (sys.argv[1])
BASE_URL = 'http://feed.theplatform.com/f/OyMl-B/PleQEkKucpUm/categories?form=json&fields=order,title,fullTitle,label,:smallBannerUrl,:largeBannerUrl&fileFields=duration,url,width,height&sort=order'
BASE = 'http://www.usanetwork.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    data = common.getURL(BASE_URL)
    shows = demjson.decode(data)['entries']
    db_shows = []
    for item in shows:
        print item
        url = item['plcategory$fullTitle']
        name = item['title']
        if db==True:
            db_shows.append((name,'usa','episodes',url))
        else:
            common.addDirectory(name, 'usa', 'episodes', url)
    if db==True:
        return db_shows

def episodes(fullname = common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    url = 'http://feed.theplatform.com/f/OyMl-B/Y3vAV4MxgwlM'
    url += '?form=json'
    url += '&fields=guid,title,description,categories,content,:fullEpisode,defaultThumbnailUrl'
    url += '&fileFields=duration,url,width,height'
    url += '&count=true'
    url += '&byCategories='+urllib.quote_plus(fullname)
    url += '&byCustomValue={fullEpisode}{true}'
    data = common.getURL(url)
    episodes = demjson.decode(data)['entries']
    for episode in episodes:
        print episode
        name = episode['title']
        description = episode['description']
        thumb= episode['plmedia$defaultThumbnailUrl']
        duration=str(int(episode['media$content'][0]['plfile$duration']))
        url=episode['media$content'][0]['plfile$url']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="usa"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 #"Season":season,
                                                 #"Episode":episode,
                                                 "Plot":description,
                                                 #"premiered":airDate,
                                                 "Duration":duration,
                                                 "TVShowTitle":common.args.name
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

#Get SMIL url and play video
def play():
    smilurl=common.args.url
    swfUrl = 'http://www.usanetwork.com/videos/pdk/swf/flvPlayer.swf'
    data = common.getURL(smilurl)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    print tree.prettify()
    rtmpbase = tree.find('meta')
    if rtmpbase:
        rtmpbase = rtmpbase['base']
        items=tree.find('switch').findAll('video')
        hbitrate = -1
        sbitrate = int(common.settings['quality']) * 1024
        for item in items:
            bitrate = int(item['system-bitrate'])
            if bitrate > hbitrate and bitrate <= sbitrate:
                hbitrate = bitrate
                playpath = item['src']
                if '.mp4' in playpath:
                    playpath = 'mp4:'+playpath
                else:
                    playpath = playpath.replace('.flv','')
                finalurl = rtmpbase+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    else:
        items=tree.find('switch').findAll('video')
        hbitrate = -1
        sbitrate = int(common.settings['quality']) * 1024
        for item in items:
            bitrate = int(item['system-bitrate'])
            if bitrate > hbitrate and bitrate <= sbitrate:
                hbitrate = bitrate
                finalurl = item['src']
    item = xbmcgui.ListItem(path=finalurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
