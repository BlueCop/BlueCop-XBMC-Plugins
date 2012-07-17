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
BASE_URL = 'http://video.nationalgeographic.com/video/nat-geo-wild/shows-1/'
SPECIALS_BASE_URL = 'http://video.nationalgeographic.com/video/nat-geo-wild/specials-2/'
BASE = 'http://video.nationalgeographic.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    for url in (BASE_URL,SPECIALS_BASE_URL):
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        shows=tree.findAll('div',attrs={'class':'natgeov-cat-group'})
        db_shows=[]
        for show in shows:
            name = show.find('h3').contents[0].split('(')[0].strip()
            url = BASE + show.find('a')['href']
            if db==True:
                db_shows.append((name, 'natgeowild', 'showsub', url))
            else:
                common.addShow(name, 'natgeowild', 'showsub', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def showsub():
    episodes()
    #if not common.args.url.endswith('-1'):
    #    common.addDirectory('Full Episodes', 'natgeowild' , 'episodes', common.args.url+'-1')
    #common.addDirectory('All Videos', 'natgeowild', 'episodes', common.args.url)
    #common.setView('seasons')

def episodes(url=common.args.url):
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
        u += '&mode="natgeowild"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     "Duration":duration,
                     #"Season":season,
                     #"Episode":episode,
                     #"Plot":str(plot),
                     "TVShowTitle":showname
                     }
        common.addVideo(u,name,thumb,infoLabels=infoLabels)
    common.setView('episodes')
        
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