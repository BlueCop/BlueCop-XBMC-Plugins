import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import httplib
import sys
import os
import re
import random
import string

from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import demjson

import resources.lib._common as common

pluginhandle = int(sys.argv[1])
BASE_URL = 'http://video.nationalgeographic.com/video/national-geographic-channel/full-episodes/'
BASE = 'http://video.nationalgeographic.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows=tree.findAll('div',attrs={'class':'natgeov-cat-group'})
    for show in shows:
        name = show.find('h3').contents[0].split('(')[0].strip()
        url = BASE + show.find('a')['href']
        common.addDirectory(name, 'natgeo', 'episodes', url)

def episodes():
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    url = common.args.url
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodes=tree.find('ul',attrs={'class':'grid cf'}).findAll('li',recursive=False)
    showname = tree.find('h3',attrs={'id':'natgeov-section-title'}).contents[0]
    for episode in episodes:
        vidthumb = episode.find('div',attrs={'class':'vidthumb'})
        name = vidthumb.find('a')['title']
        thumb = BASE + vidthumb.find('img')['src']
        duration = vidthumb.find('span',attrs={'class':'vidtimestamp'}).string
        url = BASE + vidthumb.find('a')['href']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="natgeo"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 "Duration":duration,
                                                 #"Season":season,
                                                 #"Episode":episode,
                                                 #"Plot":str(plot),
                                                 "TVShowTitle":showname
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

def randomstring(N):
    return ''.join(random.choice(string.ascii_uppercase) for x in range(N))

def play(url = common.args.url):
    videoname = url.split('/')[-2]
    smil = 'http://video.nationalgeographic.com/video/player/data/xml/%s.smil' % videoname
    data = common.getURL(smil)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    base = tree.find('meta',attrs={'name':'httpBase'})['content']
    filepath = tree.find('video')['src']
    final = base + filepath+'?v=1.2.17&fp=MAC%2011,1,102,62'+'&r='+randomstring(5)+'&g='+randomstring(12)
    item = xbmcgui.ListItem(path=final)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)