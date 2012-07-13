import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import httplib
import sys
import os
import re
import binascii
import time

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import resources.lib._common as common
from pyamf import remoting
import demjson

import hmac
try:
    import hashlib.sha1 as sha1
except:
    import sha as sha1

pluginhandle=int(sys.argv[1])

BASE_URL = 'http://www.fox.com/full-episodes/'
BASE = 'http://www.fox.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'fullEpisodesListing'}).findAll(attrs={'class' : 'showInfo'})
    db_shows = []
    for item in menu:
        name = item.find('h3').string
        url = BASE + item.findAll('a')[1]['href']+'/full-episodes/'
        if db==True:
            db_shows.append((name,'fox','episodes',url))
        else:
            common.addShow(name, 'fox', 'episodes', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')
        
def episodes(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'fullEpisodesList'}).findAll(attrs={'data-video-id':True})
    for item in menu:
        videoObject = demjson.decode(item.find('script',attrs={'class':'videoObject','type':'application/json'}).string)
        thumb = videoObject['videoStillURL']
        url = videoObject['videoURL']
        
        videoid = str(item['data-video-id']).encode('utf-8')
        name = item.find(attrs={'class':'episodeName'}).find('a').string
        duration = item.find(attrs={'class':'episodeName'}).contents[2].string.replace('(','').replace(')','')
        episodenumber = item.find(attrs={'class':'episodeNumber'}).contents[1].split('/')
        season = int(episodenumber[0])
        episode = int(episodenumber[1])
        description = item.find(attrs={'class':'description'}).string
        airDate = item.find(attrs={'class':'airDate'}).string
        displayname = '%sx%s - %s' % (str(season),str(episode),name)
        
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="fox"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     "Season":season,
                     "Episode":episode,
                     "Plot":description,
                     "premiered":airDate,
                     "Duration":duration,
                     "TVShowTitle":common.args.name
                     }
        common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def FOXsig(smil_url):
    relative_path = smil_url.split('theplatform.com/s/')[1].split('?')[0]
    sha1_key = "#100FoxLock"
    secret_name = "FoxKey"
    final_sig = '00' #00 or 10 for parameter signing
    final_sig += str(hex(int(time.time()+60))).split('x')[1]
    hmacdata = final_sig+relative_path
    final_sig += binascii.hexlify(hmac.new(sha1_key, hmacdata, sha1).digest())
    final_sig += binascii.hexlify(secret_name)
    return final_sig

def play():
    smil_url = common.args.url
    smil_url += '&format=SMIL&Tracking=true&Embedded=true'
    smil_url += 'sig='+FOXsig(smil_url)
    data = common.getURL(smil_url)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    filenames = tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality'])
    for filename in filenames:
        bitrate = int(filename['system-bitrate'])/1024
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            final_url = filename['src']
    item = xbmcgui.ListItem(path=final_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)    

def play_old():
    videoPlayer = int(common.args.url)
    const = '17e0633e86a5bc4dd47877ce3e556304d0a3e7ca'
    playerID = 644436256001
    publisherID = 51296410001
    rtmpdata = get_clip_info(const, playerID, videoPlayer, publisherID)
    print rtmpdata
    rtmpdata = rtmpdata['renditions']
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

