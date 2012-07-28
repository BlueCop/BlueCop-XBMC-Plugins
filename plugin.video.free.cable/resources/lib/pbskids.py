import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

import demjson
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from pyamf.remoting.client import RemotingService
import resources.lib._common as common

pluginhandle = int (sys.argv[1])
BASE_URL = 'http://pbs.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=6HSLquMebdOkNaEygDWyPOIbkPAnQ0_C&startIndex=1&endIndex=50&query=customText|CategoryType|Show&query=CustomBoolean|isPreschool|true&query=HasReleases&field=fullTitle&field=description&field=customData'

BASE = 'http://pbskids.org'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    data = common.getURL(BASE_URL)
    shows = demjson.decode(data)['items']
    db_shows = []
    for item in shows:
        url = item['fullTitle']
        name = item['fullTitle']
        if db==True:
            db_shows.append((name,'pbskids','episodes',url))
        else:
            common.addShow(name, 'pbskids', 'episodes', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')
    
def episodes(showname = common.args.url):
    url = 'http://pbs.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=6HSLquMebdOkNaEygDWyPOIbkPAnQ0_C'
    url += '&startIndex=1&endIndex=250&sortField=airdate&sortDescending=true&query=Categories|'+showname.replace(' ','%20')
    url += '&field=title&field=categories&field=airdate&field=expirationDate&field=length&field=description&field=language&field=thumbnailURL&field=URL&field=PID&contentCustomField=IsClip&contentCustomField=RelatedContentIDs&contentCustomField=RelatedContentIDs_Spanish&contentCustomField=Related_Activities&contentCustomField=Series_URL&contentCustomField=TV_Rating&contentCustomField=Production_NOLA&contentCustomField=Series_Title&contentCustomField=IsGame_header&contentCustomField=Episode_Title&query=CustomBoolean|isPreschool|true&param=affiliate|PBS%20KIDS%20NATIONAL&param=player|PreKplayer'
    data = common.getURL(url)
    videos = demjson.decode(data)['items']
    for video in videos:
        infoLabels={}
        thumb=video['thumbnailURL']
        url=video['URL']
        infoLabels['Title']=video['title']
        infoLabels['Plot']=video['description']
        infoLabels['TVShowTitle']=video['categories'][0] 
        infoLabels['Duration']=str(int(video['length'])/1000)
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="pbskids"'
        u += '&sitemode="play"'
        common.addVideo(u,infoLabels['Title'],thumb,infoLabels=infoLabels)
    common.setView('episodes')

#Get SMIL url and play video
def play():
    smilurl=common.args.url+'&format=SMIL'
    data = common.getURL(smilurl)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print tree.prettify()
    base = tree.find('meta')
    if base:
        base = base['base']
        if 'rtmp://' in base:
            playpath=tree.find('ref')['src']
            if '.mp4' in playpath:
                playpath = 'mp4:'+playpath
            else:
                playpath = playpath.replace('.flv','')
            finalurl = base+' playpath='+playpath
        elif 'http://' in base:
            playpath=tree.find('ref')['src']
            finalurl = base+playpath
    else:
        finalurl=tree.find('ref')['src']
    item = xbmcgui.ListItem(path=finalurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)