import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import sys
import os

import demjson

import resources.lib._common as common

pluginhandle = int(sys.argv[1])
BASE_URL = 'https://s3.amazonaws.com/ddp-digitaria-public/public/cache/endpoint_pushes/852/feed.json'
BASE = 'http://tv.gsn.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    items = demjson.decode(data)['media']['items']
    shows = []
    for item in items:
        name = item['title'].split('Season')[0].strip()
        if name not in shows:
            shows.append(name)
    for show in shows:
        common.addDirectory(show, 'gsn', 'episodes', show.replace("'",''))

def episodes(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    data = common.getURL(BASE_URL)
    items = demjson.decode(data)['media']['items']
    for item in items:
        name = item['title']
        if common.args.url in name.replace("'",''):
            season = int(name.split('Season')[1].split('Episode')[0].strip())
            episode = int(name.split('Episode')[1].strip())
            name = name.split('Season')[0].strip()+' %sx%s' % (str(season),str(episode))
            plot = item['description']
            thumb = item['thumbnail_url']
            #url = item['url']
            urls = item['conversions']
            url = urls[len(urls)-1]['streaming_url']
            item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":name,
                                                     #"Duration":duration
                                                     "Season":season,
                                                     "Episode":episode,
                                                     "Plot":plot,
                                                     "TVShowTitle":name
                                                     })
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle,url=url,listitem=item,isFolder=False)