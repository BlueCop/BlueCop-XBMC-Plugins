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

import zlib
from StringIO import StringIO
import hmac
import hashlib
import base64
from flvlib.scripts import onEdge_flv

from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import demjson

import resources.lib._common as common

pluginhandle = int(sys.argv[1])
BASE_URL = 'http://video.nationalgeographic.com/video/national-geographic-channel/full-episodes/'
#BASE_URL = 'http://video.nationalgeographic.com/video/national-geographic-channel/shows/'
SPECIALS_BASE_URL = 'http://video.nationalgeographic.com/video/national-geographic-channel/specials-1/'
BASE = 'http://video.nationalgeographic.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    for url in (BASE_URL,):
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        shows=tree.findAll('div',attrs={'class':'natgeov-cat-group'})
        db_shows=[]
        for show in shows:
            name = show.find('h3').contents[0].split('(')[0].strip()
            url = BASE + show.find('a')['href']
            if db==True:
                db_shows.append((name, 'natgeo', 'showsub', url))
            else:
                common.addShow(name, 'natgeo', 'showsub', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def showsub():
    if common.args.url.endswith('-1'):
        common.addDirectory('Full Episodes', 'natgeo' , 'episodes', common.args.url[:-2])
    common.addDirectory('All Videos', 'natgeo', 'episodes', common.args.url)
    common.setView('seasons')


def episodes(url = common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    addVideos(tree)
    pagedata = re.compile('new Paginator\((.+?),(.+?)\)').findall(data)
    if pagedata:
        total   = int(pagedata[0][0])
        current = int(pagedata[0][1])
        if total > 1:
            for page in range(1,total):
                data = common.getURL(url+'/'+str(page)+'/')
                tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
                addVideos(tree)
    common.setView('episodes')

def addVideos(tree):
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
        infoLabels={ "Title":name,
                     "Duration":duration,
                     #"Season":season,
                     #"Episode":episode,
                     #"Plot":str(plot),
                     "TVShowTitle":showname
                     }
        common.addVideo(u,name,thumb,infoLabels=infoLabels)

def randomstring(N):
    return ''.join(random.choice(string.ascii_uppercase) for x in range(N))

def play(url = common.args.url):
    videoname = url.split('/')[-2]
    smil = 'http://video.nationalgeographic.com/video/player/data/xml/%s.smil' % videoname
    data = common.getURL(smil)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print tree.prettify()
    base = tree.find('meta',attrs={'name':'httpBase'})['content']
    filepath = tree.find('video')['src']
    final = base + filepath
    
    VIDb64 = base64.encodestring(final).replace('\n','')
    swfUrl = 'http://images.nationalgeographic.com/wpf/sites/video/swf/ngplayer_v2.2.swf'
    SWFb64 = base64.encodestring(swfUrl).replace('\n','')
    proxyUrl = 'http://127.0.0.1:64653/secureconne/%s/%s' % (VIDb64,SWFb64)
    item = xbmcgui.ListItem(path=proxyUrl)
    item.setProperty('mimetype', 'video/x-flv') 
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

    