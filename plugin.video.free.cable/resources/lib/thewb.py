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
BASE_URL = 'http://www.thewb.com/shows/full-episodes'
BASE = 'http://www.thewb.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    if (common.settings['enableproxy'] == 'true'):proxy = True
    else:proxy = False
    data = common.getURL(BASE_URL,proxy=proxy)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows=tree.find('div',attrs={'id':'show-directory'}).findAll('li')
    db_shows = []
    for show in shows:
        link=show.find('a')
        name = link.contents[0].strip()
        url = BASE+link['href']
        if db==True:
            db_shows.append((name, 'thewb', 'fullepisodes', url))
        else:
            common.addShow(name, 'thewb', 'fullepisodes', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def fullepisodes(url=common.args.url):
    if (common.settings['enableproxy'] == 'true'):proxy = True
    else:proxy = False
    data = common.getURL(url,proxy=proxy)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodes=tree.find('div',attrs={'id':'full_ep_car'}).findAll('div',attrs={'id':True,'class':True})
    for episode in episodes:
        links=episode.findAll('a')
        url=BASE+links[1]['href']
        showname = links[1].find('strong').string
        name = links[0].find('img')['title'].replace(showname,'').strip().encode('utf-8')
        thumb=links[0].find('img')['src']
        plot=episode.findAll('p')[1].string
        try:
            seasonEpisode = episode.find('span',attrs={'class':'type'}).string
            seasonSplit = seasonEpisode.split(': Ep. ')
            season = int(seasonSplit[0].replace('Season','').strip())
            episodeSplit = seasonSplit[1].split(' ')
            episode = int(episodeSplit[0])
            duration = episodeSplit[1].replace('(','').replace(')','').strip()
            displayname = '%sx%s - %s' % (str(season),str(episode),name)
        except:
            season = 0
            episode = 0
            duration = ''
            displayname = name
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="thewb"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     "Duration":duration,
                     "Season":season,
                     "Episode":episode,
                     "Plot":plot,
                     "TVShowTitle":showname
                     }
        common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def play(url=common.args.url):
    jsonurl = 'http://metaframe.digitalsmiths.tv/v2/WBtv/assets/'+url.split('/')[-1]+'/partner/146?format=json'
    if (common.settings['enableproxy'] == 'true'):proxy = True
    else:proxy = False
    data = common.getURL(jsonurl,proxy=proxy)
    rtmp = demjson.decode(data)['videos']['limelight700']['uri']
    rtmpsplit = rtmp.split('mp4:')
    rtmp = rtmpsplit[0]+' playpath=mp4:'+rtmpsplit[1]
    item = xbmcgui.ListItem(path=rtmp)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)