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
BASE_URL = 'http://www.kidswb.com/video'
BASE = 'http://www.kidswb.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows=tree.find('div',attrs={'id':'channelCarousel'})
    if shows:
        shows=shows.findAll('a')
        db_shows = []
        for show in shows:
            name = show.find('img')['alt'].strip()
            url = show['title']
            if db==True:
                db_shows.append((name, 'thewbkids', 'fullepisodes', url))
            else:
                common.addShow(name, 'thewbkids', 'fullepisodes', url)
        if db==True:
            return db_shows
        else:
            common.setView('tvshows')

def fullepisodes(url=common.args.url):
    url = 'http://www.kidswb.com/video/playlists?pid=channel&chan='+url
    data = common.getURL(url)
    html = demjson.decode(data)['list_html']
    tree=BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES).find('ul',attrs={'id':'videoList_ul'})
    if tree:
        videos = tree.findAll('li',recursive=False)
        for video in videos:
            infoLabels={}
            vid_id = video['id'][6:]
            thumb=video.find('img')['src']
            infoLabels['Title'] = video.find('span',attrs={'id':'vidtitle_'+vid_id}).string
            infoLabels['TVShowTitle'] = video.find('p',attrs={'class':'vidtitle'}).contents[1]
            infoLabels['Plot'] = video.find('p',attrs={'id':'viddesc_'+vid_id}).string
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(vid_id)+'"'
            u += '&mode="thewbkids"'
            u += '&sitemode="play"'
            common.addVideo(u,infoLabels['Title'],thumb,infoLabels=infoLabels)
        common.setView('episodes')

def play(url=common.args.url):
    jsonurl = 'http://metaframe.digitalsmiths.tv/v2/WBtv/assets/'+url+'/partner/11?format=json'
    data = common.getURL(jsonurl)
    rtmp = demjson.decode(data)['videos']['limelight700']['uri']
    rtmpsplit = rtmp.split('mp4:')
    rtmp = rtmpsplit[0]+' playpath=mp4:'+rtmpsplit[1]
    item = xbmcgui.ListItem(path=rtmp)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)