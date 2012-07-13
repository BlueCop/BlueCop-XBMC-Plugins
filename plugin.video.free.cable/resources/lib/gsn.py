import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import sys
import os
import re

import demjson
from BeautifulSoup import BeautifulSoup

import resources.lib._common as common

pluginhandle = int(sys.argv[1])
#BASE_URL = 'https://s3.amazonaws.com/ddp-digitaria-public/public/cache/endpoint_pushes/852/feed.json'
BASE = 'http://gsntv.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(BASE)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows=tree.find('ul',attrs={'class':'sub-menu sub-menu-1'}).findAll('a')
    db_shows = []
    for show in shows:
        print show.prettify()
        url = BASE+show['href']+'videos/'
        name = show.find('span').string
        if db==True:
            db_shows.append((name, 'gsn', 'show', url))
        else:
            common.addShow(name, 'gsn', 'show', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def show():
    data = common.getURL(common.args.url)
    full = re.compile('f:"(.*?)",').findall(data)
    clip = re.compile('c:"(.*?)",').findall(data)
    if len(full) > 0:
        if full[0] <> '':
            common.addDirectory('Full Episodes', 'gsn', 'episodes', full[0])
    if len(clip) > 0:
        if clip[0] <> '':
            common.addDirectory('Clips', 'gsn', 'episodes', clip[0])
    common.setView('seasons')

def episodes():
    data = common.getURL(common.args.url)
    items = demjson.decode(data)['media']['items']
    for item in items:
        name = item['title'].encode('utf-8')
        try:
            season = int(name.split('Season')[1].split('Episode')[0].strip())
            episode = int(name.split('Episode')[1].strip())
            name = name.split('Season')[0].strip()+' %sx%s' % (str(season),str(episode))
        except:
            season = 0
            episode = 0
        try:plot = item['description'].encode('utf-8')
        except:plot = item['description'][0].encode('utf-8')
        thumb = item['thumbnail_url']
        #url = item['url']
        urls = item['conversions']
        url = urls[len(urls)-1]['streaming_url']
        infoLabels={ "Title":name,
                     #"Duration":duration
                     "Season":season,
                     "Episode":episode,
                     "Plot":plot,
                     "TVShowTitle":name
                     }
        common.addVideo(url,name,thumb,infoLabels=infoLabels)
    common.setView('episodes')