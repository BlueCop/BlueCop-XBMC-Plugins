import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import httplib
import sys
import os
import re

from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import demjson

import resources.lib._common as common

pluginhandle = int(sys.argv[1])
BASE_URL = 'http://www.nick.com/videos/full-episode-videos'
BASE = 'http://www.nick.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows=tree.findAll('div',attrs={'class':'filter-content-more'})[3].findAll('li')
    for show in shows:
        name = show.find('span',attrs={'class':'filter-name'}).string
        url = show['data-value']
        common.addDirectory(name, 'nick', 'episodes', url)        

def episodes():
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    url = 'http://www.nick.com/ajax/videos/full-episode-videos'
    url += '?sort=date+desc&start=0&viewType=videoContentList&rows=25&artist=&show='+common.args.url+'&f_type=&f_contenttype='
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodes=tree.findAll('article')
    for episode in episodes:
        name = episode.find('p',attrs={'class':'short-title'}).string
        showname = episode.find('p',attrs={'class':'show-name'}).string
        plot = episode.find('p',attrs={'class':'description'}).string
        thumb = episode.find('img',attrs={'class':'thumbnail'})['src']
        dataid = episode['data-id']
        url = BASE + episode.find('a')['href']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="nick"'
        u += '&sitemode="playvideo"'
        item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 #"Duration":duration,
                                                 #"Season":season,
                                                 #"Episode":episode,
                                                 "Plot":str(plot),
                                                 "TVShowTitle":showname
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

def play(uri = common.args.url):
    configurl = 'http://media.mtvnservices.com/pmt/e1/players/mgid:cms:episode:nick.com:/context1/config.xml'
    configurl += '?uri=%s&type=network&ref=www.nick.com&geo=US&group=kids&' % uri
    configxml = common.getURL(configurl)
    tree=BeautifulStoneSoup(configxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    mrssurl = tree.find('feed').string.replace('{uri}',uri).replace('&amp;','&').replace('{type}','network')
    mrssxml = common.getURL(mrssurl)
    tree=BeautifulStoneSoup(mrssxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    segmenturls = tree.findAll('media:content')
    stacked_url = 'stack://'
    for segment in segmenturls:
        surl = segment['url']
        videos = common.getURL(surl)
        videos = BeautifulStoneSoup(videos, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('rendition')
        hbitrate = -1
        sbitrate = int(common.settings['quality'])
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

def playvideo(url = common.args.url):
    data=common.getURL(url)
    uri=re.compile('uri:"(.+?)",').findall(data)[0]
    play(uri)

