import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import httplib
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
import resources.lib._common as common
from pyamf import remoting

pluginhandle=int(sys.argv[1])

BASE_URL = 'http://www.fox.com/full-episodes/'
BASE = 'http://www.fox.com'

def masterlist():
    rootlist()

def rootlist():
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'fullEpisodesListing'}).findAll(attrs={'class' : 'showInfo'})
    for item in menu:
        showname = item.find('h3').string
        url = BASE + item.findAll('a')[1]['href']
        common.addDirectory(showname, 'fox', 'episodes', url)

def episodes(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'fullEpisodesList'}).findAll(attrs={'data-video-id':True})
    for item in menu:
        videoid = str(item['data-video-id']).encode('utf-8')
        name = item.find(attrs={'class':'episodeName'}).find('a').string
        duration = item.find(attrs={'class':'episodeName'}).contents[2].string.replace('(','').replace(')','')
        episodenumber = item.find(attrs={'class':'episodeNumber'}).contents[1].split('/')
        season = int(episodenumber[0])
        episode = int(episodenumber[1])
        description = item.find(attrs={'class':'description'}).string
        airDate = item.find(attrs={'class':'airDate'}).string
        displayname = '%sx%s - %s' % (str(season),str(episode),name)
        thumb = ''
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(videoid)+'"'
        u += '&mode="fox"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 "Season":season,
                                                 "Episode":episode,
                                                 "Plot":description,
                                                 "premiered":airDate,
                                                 "Duration":duration,
                                                 "TVShowTitle":common.args.name
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)


def play():
    videoPlayer = int(common.args.url)
    const = '17e0633e86a5bc4dd47877ce3e556304d0a3e7ca'
    playerID = 644436256001
    publisherID = 51296410001
    rtmpdata = get_clip_info(const, playerID, videoPlayer, publisherID)['renditions']
    hbitrate = -1
    sbitrate = int(common.settings['quality']) * 1024
    for item in rtmpdata:
        bitrate = int(item['encodingRate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            urldata = item['defaultURL']
            auth = urldata.split('?')[1]
            urldata = urldata.split('&')
            rtmp = urldata[0]+'?'+auth
            playpath = urldata[1].split('?')[0]+'?'+auth
    swfUrl = 'http://admin.brightcove.com/viewer/us1.25.03.01.2011-05-12131832/federatedVideo/BrightcovePlayer.swf'
    rtmpurl = rtmp+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    item = xbmcgui.ListItem(path=rtmpurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
       
def build_amf_request(const, playerID, videoPlayer, publisherID):
    env = remoting.Envelope(amfVersion=3)
    env.bodies.append(
        (
            "/1", 
            remoting.Request(
                target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById", 
                body=[const, playerID, videoPlayer, publisherID],
                envelope=env
            )
        )
    )
    return env

def get_clip_info(const, playerID, videoPlayer, publisherID):
    conn = httplib.HTTPConnection("c.brightcove.com")
    envelope = build_amf_request(const, playerID, videoPlayer, publisherID)
    conn.request("POST", "/services/messagebroker/amf?playerKey=AQ~~,AAAAC_GBGZE~,q40QbnxHunHkwKuAvWxESNjERBgcAQY8", str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    return response  

