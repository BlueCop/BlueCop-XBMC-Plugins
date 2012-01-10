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

BASE_URL = 'http://www.oxygen.com/full-episodes/'
BASE = 'http://www.oxygen.com'

#SHOW_FEED = 'http://www.oxygen.com/full-episodes/media/full-episodes/oxygenShows.xml'
SHOW_FEED = 'http://www.oxygen.com/full-episodes/xml/showConfig.xml'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(SHOW_FEED)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    items=tree.findAll('show')
    for item in items:
        name = item.find('showname').string
        url = item.find('rssurl').string
        thumb = item.find('thumbnail').string
        common.addDirectory(name, 'oxygen', 'show', url, thumb=thumb)

def show(feed=common.args.url):
    data = common.getURL(feed)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    items=tree.findAll('item')
    for item in items:
        name = item.find('title').string#.split('-')[1].strip()
        description = item.find('description').string
        videoid = item.find('link').string
        thumb = item.find('media:thumbnail').string
        #seasonepisode = item.find('title').string.replace('Season','').split('Episode')
        #season = int(seasonepisode[0])
        #episode = int(seasonepisode[1])
        duration = item.find('media:content')['duration']
        airDate = item.find('pubdate').string.split(' ')[0]
        #if season <> 0 or episode <> 0:
        #    displayname = '%sx%s - %s' % (str(season),str(episode),name)
        #else:
        displayname = name
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(videoid)+'"'
        u += '&mode="oxygen"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 #"Season":season,
                                                 #"Episode":episode,
                                                 "Plot":description,
                                                 "premiered":airDate,
                                                 "Duration":duration,
                                                 "TVShowTitle":common.args.name
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

def play(videoid=common.args.url):
    config = 'http://videoservices.nbcuni.com/player/config?configId=27006&version=2&clear=true'
    data = common.getURL(config)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    appname = tree.find('akamaiappname').string
    rtmphost = tree.find('akamaihostname').string
    netstore = tree.find('akamainetstorage').string
    vurl = 'http://videoservices.nbcuni.com/player/clip'
    vurl+= '?geoIP=US&domainReq=www%2Eoxygen%2Ecom&clipId='+videoid
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
    