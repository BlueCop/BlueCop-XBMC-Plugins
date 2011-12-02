import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from pyamf import amf3
import resources.lib._common as common

pluginhandle = int (sys.argv[1])

BASE_URL = 'http://www.bravotv.com/full-episodes'
BASE = 'http://www.bravotv.com'

FULL_FEED = 'http://videoservices.nbcuni.com/player/feeds?networkId=1781&networkName=bravo&eTag=bravofullep'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(FULL_FEED)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    items=tree.findAll('item')
    names = []
    for item in items:
        name = item.find('media:subtitle').string
        if name not in names:
            names.append(name)
    if db == False:
        for name in names:
            common.addDirectory(name, 'bravo', 'show', name)
    elif db == True:
        dbshows=[]
        for name in names:
            dbshows.append((name, 'bravo', 'show', name))
        return dbshows

def show(showname=common.args.url):
    data = common.getURL(FULL_FEED)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    items=tree.findAll('item')
    print tree.prettify()
    names = []
    for item in items:
        sname = item.find('media:subtitle').string
        if sname == showname:
            name = item.find('description').string
            try:name = name.split('-')[1].strip()
            except: name = item.find('description').string
            videoid = item.find('link').string
            thumb = item.find('media:thumbnail').string
            seasonepisode = item.find('title').string.replace('Season','').split('Episode')
            try:season = int(seasonepisode[0])
            except:season = 0
            try:episode = int(seasonepisode[1])
            except:episode = 0
            duration = item.find('media:content')['duration']
            airDate = item.find('pubdate').string.split(' ')[0]
            if season <> 0 or episode <> 0:
                displayname = '%sx%s - %s' % (str(season),str(episode),name)
            else:
                displayname = name
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(videoid)+'"'
            u += '&mode="bravo"'
            u += '&sitemode="play"'
            item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":name,
                                                     "Season":season,
                                                     "Episode":episode,
                                                     #"Plot":description,
                                                     "premiered":airDate,
                                                     "Duration":duration,
                                                     "TVShowTitle":common.args.name
                                                     })
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

def play(videoid=common.args.url):
    config = 'http://videoservices.nbcuni.com/player/config?configId=13012&version=2&clear=true'
    data = common.getURL(config)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    appname = tree.find('akamaiappname').string
    rtmphost = tree.find('akamaihostname').string
    netstore = tree.find('akamainetstorage').string
    vurl = 'http://videoservices.nbcuni.com/player/clip'
    vurl+= '?domainReq=www%2Ebravotv%2Ecom&clipId='+videoid+'&geoIP=US'
    data = common.getURL(vurl)
    context = amf3.Context()
    decoded = amf3.Decoder(data, context).readElement()
    clipurl = netstore+decoded['clipurl']
    swfUrl = 'http://video.nbcuni.com/outlet/extensions/inext_video_player/video_player_extension.swf'
    data = common.getURL(clipurl)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    items=tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality']) * 1024
    for item in items:
        bitrate = int(item['system-bitrate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            playpath = item['src']
            if '.mp4' in playpath:
                playpath = 'mp4:'+playpath
            else:
                playpath = playpath.replace('.flv','')
            finalurl = 'rtmpe://'+rtmphost+'/'+appname+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    item = xbmcgui.ListItem(path=finalurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    