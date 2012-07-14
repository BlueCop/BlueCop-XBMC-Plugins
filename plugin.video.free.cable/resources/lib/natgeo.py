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
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows=tree.findAll('div',attrs={'class':'natgeov-cat-group'})
    db_shows=[]
    for show in shows:
        name = show.find('h3').contents[0].split('(')[0].strip()
        url = BASE + show.find('a')['href']
        if db==True:
            db_shows.append((name, 'natgeo', 'episodes', url))
        else:
            common.addShow(name, 'natgeo', 'episodes', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def episodes():
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
    'http://channelhd-f.akamaihd.net/control/channel/feed/362/225.flv_0_0@1?cmd=sendingNewToken&v=2.7.6+'+'&r='+randomstring(5)+'&g='+randomstring(12)
    smil = 'http://video.nationalgeographic.com/video/player/data/xml/%s.smil' % videoname
    data = common.getURL(smil)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    base = tree.find('meta',attrs={'name':'httpBase'})['content']
    filepath = tree.find('video')['src']
    final = base + filepath+'?v=1.2.17&fp=MAC%2011,1,102,62'+'&r='+randomstring(5)+'&g='+randomstring(12)
    finalControl = base + filepath.replace('/feed/','/control/')+'_0_0@1?cmd=sendingNewToken&v=2.7.6'+'&r='+randomstring(5)+'&g='+randomstring(12)
    common.getURL(smil)
    item = xbmcgui.ListItem(path=final)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    xbmc.sleep(10000)
    if xbmc.Player().isPlaying():
        data = common.getURL(finalControl)
    
    
def getURLTOKEN( url , values = None ,proxy = False, referer=False):
    try:
        if proxy == True:
            us_proxy = 'http://' + addoncompat.get_setting('us_proxy') + ':' + addoncompat.get_setting('us_proxy_port')
            print 'Using proxy: ' + us_proxy
            proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        print 'FREE CABLE --> common :: getURL :: url = '+url
        if values == None:
            req = urllib2.Request(url)
        else:
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data)
        if referer:
            req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:13.0) Gecko/20100101 Firefox/13.0.1')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.HTTPError, error:
        print 'Error reason: ', error
        return error.read()
    else:
        return link
    