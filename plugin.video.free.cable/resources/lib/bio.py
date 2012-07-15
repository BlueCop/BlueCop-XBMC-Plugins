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
BASE_URL = 'http://www.biography.com/videos'
BASE = 'http://www.biography.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    items=tree.find('ul',attrs={'class':'left-col-menu video-landing clearfix'}).findAll('li',attrs={'class':True})
    db_shows = []
    for item in items:
        if item['class'] == 'mainItem expanded' or item['class'] == 'mainItem ':
            if item.find('span').string == 'Shows':
                sub=item.find('ul')
                if sub <> None:
                    subcats=sub.findAll('li')
                    for cat in subcats:
                        link = cat.find('a')
                        name = link.find('span').string
                        url = link['href']
                        if db==True:
                            db_shows.append((name, 'bio', 'videos', url))
                        else:
                            common.addShow(name, 'bio', 'videos', url)
            else:
                link = item.find('a')
                name = link.find('span').string
                url = link['href']
                common.addDirectory(name, 'bio', 'videos', url)
                sub=item.find('ul')
                if sub <> None:
                    subcats=sub.findAll('li')
                    for cat in subcats:
                        link = cat.find('a')
                        name = link.find('span').string
                        url = link['href']
                        if db==True:
                            pass
                            #db_shows.append((name, 'bio', 'videos', url))
                        else:
                            common.addDirectory(name, 'bio', 'videos', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')
                      
def videos(url=common.args.url):
    url = BASE+url+'?page-number=1&pagination-type=all&pagination-sort-by=most-recent&pagination-per-page=100'
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos=tree.find('ul',attrs={'class':'video-group-list five-columns'}).findAll('li',recursive=False)
    for video in videos:
        link = video.find('p').find('a')
        name = link.string.strip()
        url = BASE + link['href']
        thumb = video.find('img')['src']
        duration = video.find('span',attrs={'class':'video-duration'}).string.strip().replace('(','').replace(')','')
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="bio"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     "Duration":duration}
        common.addVideo(u,name,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def play(url=common.args.url):
    swfUrl = 'http://admin.brightcove.com/viewer/us20120228.1146/federatedVideoUI/BrightcovePlayer.swf'
    
    data = common.getURL(url)
    exp_id,content_id = re.compile('embedPlayer\("(.+?)", "(.+?)",').findall(data)[0]
    key = exp_id
    
    renditions = get_episode_info(key, content_id, url, exp_id)['programmedContent']['videoPlayer']['mediaDTO']['renditions']
    rtmp = ''
    hi_res = 0
    selected_video = None
    for video in renditions:
        if(int(video['size'])>hi_res):
            selected_video = video
            hi_res = int(video['size'])
    rtmpdata = selected_video['defaultURL'].split('&mp4:')
    rtmp = rtmpdata[0]+' playpath=mp4:'+rtmpdata[1]
    rtmp += ' pageUrl='+url
    
    item = xbmcgui.ListItem(path=rtmp)
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
   const = '5e953dada6862ed388075b269a11253eb52a15c4'
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