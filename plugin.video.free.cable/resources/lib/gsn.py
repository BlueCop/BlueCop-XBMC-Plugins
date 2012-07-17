import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import sys
import os
import re
import types

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
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    for item in items:
        infoLabels={}
        name = item['title'].encode('utf-8')
        try:
            infoLabels['Season'] = int(name.split('Season')[1].split('Episode')[0].strip())
            infoLabels['Episode'] = int(name.split('Episode')[1].strip())
            name = name.split('Season')[0].strip()
        except:
            name = name.split('Season')[0].strip()
        thumb = item['thumbnail_url']
        #url = item['url']
        urls = item['conversions']
        url = urls[len(urls)-1]['streaming_url']
        infoLabels['Title']=name
        infoLabels['TVShowTitle']=name
        for field in item['custom_fields']:
            if field['slug'] == 'season-number':
                infoLabels['Season']=int(field['values'][0])
            elif field['slug'] == 'episode-number':
                infoLabels['Episode']=int(field['values'][0])
            elif field['slug'] == 'rating':
                infoLabels['MPAA']=field['values'][0]
        
        if isinstance(item['description'], types.ListType):
            infoLabels['Plot'] = item['description'][0].encode('utf-8')
        else:
            infoLabels['Plot'] = item['description'].encode('utf-8')
        
        if infoLabels.has_key('Episode') and infoLabels.has_key('Season'):
            displayname = '%sx%s - %s' % (str(infoLabels['Season']),str(infoLabels['Episode']),name)
        elif infoLabels.has_key('Episode'):
            displayname = '%s. - %s' % (str(infoLabels['Episode']),name)
        elif infoLabels.has_key('Season'):    
            displayname = 'S%s - %s' % (str(infoLabels['Season']),name)
        else:
            displayname=name
        infoLabels['Title']=displayname
        common.addVideo(url,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')