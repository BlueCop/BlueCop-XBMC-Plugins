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
import pyamf

from pyamf import remoting, amf3, util

import resources.lib._common as common

pluginhandle = int(sys.argv[1])
BASE_URL = 'http://nicktoons.nick.com/ajax/videos/all-videos/?sort=date+desc&start=0&page=1&viewType=collectionAll&type=fullEpisodeItem'
BASE = 'http://nicktoons.nick.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    print tree.prettify()
    shows=tree.find('select',attrs={'id':'dropdown-by-show'}).findAll('option')
    for show in shows:
        name = show.string
        if name <> 'All Shows':
            url = show['value']
            common.addDirectory(name, 'nicktoons', 'episodes', url)        

def episodes():
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    url = 'http://nicktoons.nick.com/ajax/videos/all-videos/'+common.args.url
    url += '?sort=date+desc&start=0&page=1&viewType=collectionAll&type=fullEpisodeItem'
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodes=tree.find('ul',attrs={'class':'large-grid-list clearfix'}).findAll('li',recursive=False)
    for episode in episodes:
        h4link=episode.find('h4').find('a')
        name = h4link.string
        url = BASE + h4link['href']
        thumb = episode.find('img')['src'].split('?')[0]
        plot = episode.find('p',attrs={'class':'description text-small color-light'}).string
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="nicktoons"'
        u += '&sitemode="playvideo"'
        item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 #"Duration":duration,
                                                 "Season":0,
                                                 "Episode":0,
                                                 "Plot":str(plot),
                                                 "TVShowTitle":common.args.name
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

def play(uri = common.args.url):
    configurl = 'http://media.mtvnservices.com/pmt/e1/players/mgid:cms:episode:nicktoons.com:/context1/config.xml'
    configurl += '?uri=%s&type=network&ref=nicktoons.nick.com&geo=US&group=kids&' % uri
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