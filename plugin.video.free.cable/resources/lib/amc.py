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
import demjson
import pyamf

from pyamf import remoting, amf3, util

import resources.lib._common as common

pluginhandle = int(sys.argv[1])
BASE_URL = 'http://www.amctv.com/videos'
BASE = 'http://www.amctv.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows=tree.find('select',attrs={'id':'rb-video-browser-show'}).findAll('option',attrs={'title':True})
    db_shows = []
    for show in shows:
        name = show.string.encode('utf-8')
        url = show['value']
        if db==True:
            db_shows.append((name,'amc','showcats',url))
        else:
            common.addShow(name, 'amc', 'showcats', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')
        
def showcats():
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    video_types=tree.find('select',attrs={'id':'rb-video-browser-content_type'}).findAll('option')
    shows=tree.find('select',attrs={'id':'rb-video-browser-show'}).findAll('option')#,attrs={'title':True})
    db_shows = []
    for show in shows:
        if show['value'] == common.args.url:
            cats = show['title'].replace('[','').replace(']','').replace('"','').split(',')
            for type in video_types:
                if type['value'] in cats:
                    name = type.string
                    url = 'rb-video-browser-num_items=100'
                    url += '&module_id_base=rb-video-browser'
                    url += '&rb-video-browser-show='+show['value']
                    url += '&rb-video-browser-content_type='+type['value']
                    common.addDirectory(name, 'amc', 'videos', url)
    common.setView('seasons')

def videos():
    url = 'http://www.amctv.com/index.php'
    values = {'video_browser_action':'filter',
              'params[type]':'all',
              'params[filter]':common.args.url,
              'params[page]':'1',
              'params[post_id]':'71306',      
              'module_id_base':'rb-video-browser'}
    data = common.getURL( url , values)
    data = demjson.decode(data)['html']['date']
    items = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES).findAll('li')
    for item in items:
        link = item.find('a')
        img = link.find('img')
        url = link['href']
        name = img['title']
        plot = img['alt'].replace('/n',' ')
        thumb = img['src']
        print item.prettify()
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="amc"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     #"Season":season,
                     #"Episode":episode,
                     "Plot":plot,
                     #"TVShowTitle":common.args.name
                     }
        common.addVideo(u,name,thumb,infoLabels=infoLabels)
    common.setView('episodes')


def play(url=common.args.url):
   swfUrl = 'http://admin.brightcove.com/viewer/us20120228.1146/federatedVideoUI/BrightcovePlayer.swf'
   
   data = common.getURL(url)
   exp_id,key = re.compile('BrightcoveHTML5PlayerChange\.init\(".+?", "(.+?)", "(.+?)"\);').findall(data)[0]
   content_id = re.compile('videoPlayer" value="(.+?)"').findall(data)[0]
   
   renditions = get_episode_info(key, content_id, url, exp_id)['programmedContent']['videoPlayer']['mediaDTO']['renditions']
   print renditions
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
   const = 'de7ada8734d5a3b7ea1ee34fef266d6050fe6e3a'
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
        
