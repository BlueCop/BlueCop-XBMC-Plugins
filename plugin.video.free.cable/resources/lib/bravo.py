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
BASE_URL = 'http://feed.theplatform.com/f/PHSl-B/hOMhFl_Iu3_G/?&form=json'
BASE = 'http://www.bravotv.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    data = common.getURL(BASE_URL)
    shows = demjson.decode(data)['entries']
    db_shows = []
    dupes = []
    for item in shows:
        name = item['pl1$show'][0]
        if name not in dupes:
            if db==True:
                db_shows.append((name,'bravo','episodes',name))
            else:
                common.addShow(name, 'bravo', 'episodes', name)
            dupes.append(name)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')
        
def episodes():
    process('http://feed.theplatform.com/f/PHSl-B/hOMhFl_Iu3_G?')
    common.setView('episodes')

def process(urlBase, fullname = common.args.url):
    url = urlBase
    url += '&form=json'
    #url += '&fields=guid,title,description,categories,content,defaultThumbnailUrl'#,:fullEpisode
    url += '&fileFields=duration,url,width,height'
    url += '&count=true'
    #url += '&byCategories='+urllib.quote_plus(fullname)
    #url += '&byCustomValue={fullEpisode}{false}'
    data = common.getURL(url)
    episodes = demjson.decode(data)['entries']
    for episode in episodes:
        if fullname == episode['pl1$show'][0]:
            name = episode['description'].split('-')[1].strip()
            showname = episode['pl1$subtitle']
            description = episode['description']
            thumb= episode['plmedia$defaultThumbnailUrl']
            season = episode['pl1$season'][0]
            episodeNum = episode['pl1$episode'][0]
            duration=str(int(episode['media$content'][0]['plfile$duration']))
            url=episode['media$content'][0]['plfile$url']
            airDate = common.formatDate(epoch=episode['pubDate']/1000)
            displayname = '%sx%s - %s' % (str(season),str(episodeNum),name)
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="bravo"'
            u += '&sitemode="play"'
            infoLabels={ "Title":name,
                         "Season":season,
                         "Episode":episodeNum,
                         "Plot":description,
                         "premiered":airDate,
                         "Duration":duration,
                         "TVShowTitle":showname
                         }
            common.addVideo(u,displayname,thumb,infoLabels=infoLabels)

#Get SMIL url and play video
def play():
    smilurl=common.args.url
    swfUrl = 'http://www.bravotv.com/_tp/pdk/swf/flvPlayer.swf'
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
