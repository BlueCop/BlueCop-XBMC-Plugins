import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import httplib
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson
import resources.lib._common as common

import pyamf
from pyamf import remoting, amf3, util

pluginhandle = int (sys.argv[1])

BASE_URL = 'http://marvel.com/connect/dynamic_list?id=video_index&type=video&sort_order=alpha_asc'
BASE = 'http://marvel.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    db_shows = []
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows=tree.findAll('li')
    for show in shows:
        show=show.find('a')
        url = BASE+show['href']+'?limit=100'
        showname = show.string.rsplit(' ',1)[0].strip()
        if db==True:
            db_shows.append((showname, 'marvel', 'show', url))
        else:
            common.addShow(showname, 'marvel', 'show', url)    
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')
        
def show(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos=tree.find('ul',attrs={'id':'browse_results'}).findAll('li',recursive=False)
    for video in videos:
        infoLabels={}
        link=video.find('a')
        thumb=video.find('img')['src']
        url=BASE+link['href']
        infoLabels['Title']=link['title']
        #infoLabels['premiered']=video.find('p',attrs={'class':'browse_result_sale grid-hidden'})
        infoLabels['Plot']=video.find('div',attrs={'class':'browse_result_description'}).string.strip()
        infoLabels['TVShowTitle']=common.args.name
        try:infoLabels['Duration']=video.find('span',attrs={'class':'duration'}).string.strip('()')
        except:pass
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="marvel"'
        u += '&sitemode="play"'
        common.addVideo(u,infoLabels['Title'],thumb,infoLabels=infoLabels)
    common.setView('episodes')
    
def play(url=common.args.url):
    swfUrl = 'http://admin.brightcove.com/viewer/us20110809.1526/federatedVideoUI/BrightcovePlayer.swf'
    
    data = common.getURL(url)
    key = re.compile('<param name="playerKey" value="(.+?)" />').findall(data)[0]
    content_id = re.compile('<param name="@videoPlayer" value="(.+?)" />').findall(data)[0]
    exp_id = re.compile('<param name="playerID" value="(.+?)" />').findall(data)[0]
    
    renditions = get_episode_info(key, content_id, url, exp_id)['programmedContent']['videoPlayer']['mediaDTO']['renditions']
    rtmp = ''
    hi_res = 0
    selected_video = None
    for video in renditions:
        if(int(video['size'])>hi_res):
            selected_video = video
            hi_res = int(video['size'])
    
    link = selected_video['defaultURL']
    item = xbmcgui.ListItem(path=link)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def get_episode_info(key, content_id, url, exp_id):
    conn = httplib.HTTPConnection("c.brightcove.com")
    envelope = build_amf_request(key, content_id, url, exp_id)
    conn.request("POST", "/services/messagebroker/amf?playerKey="+key, str(remoting.encode(envelope).read()),{'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    return response

class ViewerExperienceRequest(object):
    def __init__(self, URL, contentOverrides, experienceId, playerKey, TTLToken=''):
        self.TTLToken = TTLToken
        self.URL = URL
        self.deliveryType = float(0)
        self.contentOverrides = contentOverrides
        self.experienceId = experienceId
        self.playerKey = playerKey

class ContentOverride(object):
    def __init__(self, contentId, contentType=0, target='videoPlayer'):
        self.contentType = contentType
        self.contentId = contentId
        self.target = target
        self.contentIds = None
        self.contentRefId = None
        self.contentRefIds = None
        self.contentType = 0
        self.featureId = float(0)
        self.featuredRefId = None

def build_amf_request(key, content_id, url, exp_id):
    print 'ContentId:'+content_id
    print 'ExperienceId:'+exp_id
    print 'URL:'+url
    const = '4c1b306cc23230173e7dfc04e68329d3c0c354cb'
    pyamf.register_class(ViewerExperienceRequest, 'com.brightcove.experience.ViewerExperienceRequest')
    pyamf.register_class(ContentOverride, 'com.brightcove.experience.ContentOverride')
    content_override = ContentOverride(int(content_id))
    viewer_exp_req = ViewerExperienceRequest(url, [content_override], int(exp_id), key)
    
    env = remoting.Envelope(amfVersion=3)
    env.bodies.append(
       (
          "/1",
          remoting.Request(
             target="com.brightcove.experience.ExperienceRuntimeFacade.getDataForExperience",
             body=[const, viewer_exp_req],
             envelope=env
          )
       )
    )
    return env
