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
from BeautifulSoup import BeautifulStoneSoup
import resources.lib._common as common
from pyamf import remoting

pluginhandle=int(sys.argv[1])

BASE_URL = 'http://www.fxnetworks.com/episodes.php'
BASE = 'http://www.fxnetworks.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find('ul', attrs={'class':'shows'}).findAll('li',recursive=False)
    db_shows = []
    for item in menu:
        try:
            url = item.find(attrs={'class':'action watch-episodes'})['href']
            #url = url.replace('/fod/play.php?sh=','/fod/').replace('/watch/','/fod/')   
            thumb = BASE+'/'+item.find('img')['src']
            showname = item.find(attrs={'class':'content'})('h2')[0].string
            if db==True:
                db_shows.append((showname,'fx','show',url))
            else:
                common.addShow(showname, 'fx', 'show', url)#, thumb)
        except:
            print 'no watch episode action'
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')
    
def show(url=common.args.url):
    common.addDirectory('Full Episodes', 'fx', 'episodes', url)
    common.addDirectory('Clips & Extras', 'fx', 'clip', url)
    common.setView('seasons')

def clips(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    extras=tree.findAll('div', attrs={'id':'row2','class':'videoExtras'})
    for extra in extras:
        videos=extra.findAll('div',attrs={'id':True,'class':'episodeListing'})
        addvideos(videos)
    common.setView('episodes')
    
def episodes(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos=tree.find('div', attrs={'id':'row1','class':'fullEpisodes'}).findAll('div',attrs={'id':True,'class':'episodeListing'})
    addvideos(videos)
    common.setView('episodes')

def addvideos(videos):
    for video in videos:
        link = video.find('a', attrs={'class':'thumbnailLink'})
        url = 'http://vod.fxnetworks.com'+link['href']
        thumb = link.find('img')['src']
        title = video.find('a', attrs={'class':'thumbnailLinkText'}).string
        seasonNum = video.find('p', attrs={'class':'seasonNum'}).string
        name = seasonNum+' '+title
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="fx"'
        u += '&sitemode="play"'
        infoLabels={ "Title":title}
        common.addVideo(u,name,thumb,infoLabels=infoLabels)

def play():
    videoPlayer = int(common.args.url.split('/')[-1])
    const = 'cd687d9fa9f678adbdccc61fe50233e43e61164e'
    playerID = 640594657001
    publisherID = 67398584001
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
    conn.request("POST", "/services/messagebroker/amf?playerKey=AQ~~,AAAAD7FExsE~,dWW_A2fca-0o0T8SJiLGfd39phbKu16R", str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    print response
    return response  

