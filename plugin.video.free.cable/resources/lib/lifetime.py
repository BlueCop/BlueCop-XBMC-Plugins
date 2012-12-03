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

import binascii
import time
import hmac
try:
    import hashlib.sha1 as sha1
except:
    import sha as sha1

pluginhandle = int(sys.argv[1])
showlist= 'http://www.mylifetime.com/video'

def masterlist():
    return shows(db=True)

def rootlist():
    data = common.getURL(showlist)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu = tree.find('div',attrs={'id':'accordion','class':'view-content'}).findAll('h3')
    for item in menu:
        name = item.find('a',attrs={'href':'#'}).string
        common.addDirectory(name, 'lifetime', 'shows', name )
    common.addDirectory('Full Movies', 'lifetime', 'movies', '')
    common.setView('seasons')

def shows(url=common.args.url,db=False):
    data = common.getURL(showlist)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu = tree.find('div',attrs={'id':'accordion','class':'view-content'}).findAll('h3')
    names = []
    for item in menu:
        name = item.find('a',attrs={'href':'#'}).string
        names.append(name)
    if db == False:
        marker = names.index(url)
    elif db == True:
        marker = names.index('Current Shows')
    menu = tree.find('div',attrs={'id':'accordion','class':'view-content'})
    shows = menu.findAll('div',recursive=False)[marker].findAll('li')
    dbshows = []
    for show in shows:
        showdata = show.findAll(attrs={'class':'field-content'})
        name = showdata[0].a.string
        showid = showdata[1].string
        if db == False:
            if 'Movies' in common.args.name:
                common.addDirectory(name, 'lifetime', 'showroot', showid)
            else:
                common.addShow(name, 'lifetime', 'showroot', showid)
        elif db == True:
            dbshows.append((name, 'lifetime', 'showroot', showid))
    if db == True:
        return dbshows
    else:
        common.setView('tvshows')
        
def showroot(showid=common.args.url):
    common.addDirectory('Episodes', 'lifetime', 'episodes', showid )
    common.addDirectory('Clips', 'lifetime', 'clips', showid )
    common.setView('seasons')

def episodes(showid=common.args.url):
    url = 'http://www.mylifetime.com/d6/views/ajax'
    url += '?show_code='+urllib.quote_plus(showid)
    url += '&premium%5B%5D=0'
    url += '&ajax_pager_field=0'
    url += '&most_filter=mr'
    url += '&view_name=video_watch_full_episodes_assoc'
    url += '&view_display_id=block_1'
    url += '&view_args='
    url += '&view_path=watch-full-episodes-online'
    url += '&view_base_path=null'
    url += '&view_dom_id=video-watch-full-episodes-assoc-block-1'
    url += '&pager_element=0'
    processEpisodes(url)
    #processEpisodes(url.replace('&premium%5B%5D=0','&premium%5B%5D=1'))
    common.setView('episodes')
        
def movies(showid=common.args.url):
    url = 'http://www.mylifetime.com/d6/views/ajax'
    #url += '?js=1&page=1'
    url += '?view_name=video_watch_full_movies_assoc'
    url += '&view_display_id=block_1'
    url += '&view_args='
    url += '&view_path=watch-full-movies-online'
    url += '&view_base_path=null'
    url += '&view_dom_id=video-watch-full-movies-assoc-block-1'
    url += '&pager_element=1'
    processMovies(url)
    common.setView('episodes')

def clips(showid=common.args.url):
    url = 'http://www.mylifetime.com/d6/views/ajax'
    url += '?js=1&page=1'
    url += '&field_length_value_many_to_one%5B%5D=Clip'
    url += '&show_code='+urllib.quote_plus(showid)
    url += '&ajax_pager_field=0'
    url += '&most_filter=mr'
    url += '&view_name=video_homepage_video_list'
    url += '&view_display_id=block_1'
    url += '&view_args='
    url += '&view_path=video'
    url += '&view_base_path=null'
    url += '&view_dom_id=video-homepage-video-list-block-1'
    url += '&pager_element=0'
    processEpisodes(url)
    common.setView('episodes')

def processEpisodes(url):
    data = common.getURL(url)
    remove = re.compile('<script.*?script>', re.DOTALL)
    data = re.sub(remove, '', data)
    remove = re.compile('<\\!--.*?-->', re.DOTALL)
    data = re.sub(remove, '', data)
    htmldata = demjson.decode(data)['display']
    remove = re.compile('"<div.*?div>"')
    htmldata = re.sub(remove, '""', htmldata)
    tree=BeautifulSoup(htmldata, convertEntities=BeautifulSoup.HTML_ENTITIES)
    print tree.prettify()
    episodes = tree.findAll('div',attrs={'class':re.compile('video-image-wrapper video')})
    if len(episodes) == 0:
        return False
    for episode in episodes:
        print episode.prettify()
        url = episode.find('a')['href']
        name = episode.find('img')['title']
        thumb = episode.find('img')['src']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="lifetime"'
        u += '&sitemode="playepisode"'
        infoLabels={ "Title":name,
                    "TVShowTitle":common.args.name}
        common.addVideo(u,name,thumb,infoLabels=infoLabels)
    return True

def processMovies(url):
    data = common.getURL(url)
    remove = re.compile('<script.*?script>', re.DOTALL)
    data = re.sub(remove, '', data)
    remove = re.compile('<\\!--.*?-->', re.DOTALL)
    data = re.sub(remove, '', data)
    htmldata = demjson.decode(data)['display']
    remove = re.compile('"<div.*?div>"')
    htmldata = re.sub(remove, '""', htmldata)
    tree=BeautifulSoup(htmldata, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #print tree.prettify()
    episodes = tree.findAll('div',attrs={'class':re.compile('video-image-wrapper video')})
    if len(episodes) == 0:
        return False
    for episode in episodes:
        print episode.prettify()
        url = episode.find('a')['href']
        try:    name = episode.find('b').string
        except: name = episode.find('img')['title']
        thumb = episode.find('img')['src']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="lifetime"'
        u += '&sitemode="playepisode"'
        infoLabels={ "Title":name,
                    "TVShowTitle":common.args.name}
        common.addVideo(u,name,thumb,infoLabels=infoLabels)
    return True
    
def playepisode(url=common.args.url):
    data = common.getURL(url)
    path = url.split('mylifetime.com/')[1].split('?')[0]
    jsonData = re.compile('Drupal\.settings\.video, (.+)\);').findall(data)[0]
    json = demjson.decode(jsonData)
    for item in json['cached_videos']:
        if item['path'] == path:
            smil_url = item['pdk_flash_url'].split('?')[0]
    #smil_url = json['cached_videos'][0]['pdk_flash_url'].split('?')[0]
    signed_url = sign_url(smil_url)
    link = common.getURL(signed_url)
    tree=BeautifulStoneSoup(link, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    base = tree.find('meta')['base']
    videos = tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality']) * 1000
    for video in videos:
        try:bitrate = int(video['system-bitrate'])
        except:
            try:bitrate = int(video['systembitrate'])
            except: bitrate = 1
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            filename = video['src'].replace('.mp4','').replace('.flv','')
    swfUrl = 'http://www.mylifetime.com/shows/sites/all/libraries/pdk_player/pdk/swf/flvPlayer.swf'
    auth = filename.split('?')[1]
    filename = filename.split('?')[0]
    finalurl = base+'?'+auth+' swfurl='+swfUrl+' swfvfy=true playpath='+filename
    item = xbmcgui.ListItem(path=finalurl)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def sign_url(url):
    hmac_key = 'crazyjava'
    SEC_HEX = '733363723374' #'s3cr3t'
    expiration = get_expiration()
    path = url.split('http://link.theplatform.com/s/')[1]
    sign_data = binascii.unhexlify('00'+expiration+binascii.hexlify(path).lower())
    sig = hmac.new(hmac_key, sign_data, sha1)
    sigHEX = sig.hexdigest()
    signature = '00' + expiration + sigHEX + SEC_HEX
    finalUrl = url+'?sig='+signature+'&format=SMIL&Tracking=true&Embedded=true&mbr=true'
    return finalUrl

def get_expiration(auth_length = 600):
    current_time = time.mktime(time.gmtime())+auth_length
    expiration = ('%0.2X' % current_time).lower()
    return expiration
    
### OLD BRIGHTCOVE CODE
    
def playepisodeOLD(url=common.args.url):
    swfUrl = 'http://admin.brightcove.com/viewer/us20110809.1526/federatedVideoUI/BrightcovePlayer.swf'
    
    data = common.getURL(url)
    key = re.compile('"player_key":"(.+?)","').findall(data)[0]
    try:content_id = re.compile('"defaultVideoID":"(.+?)","').findall(data)[0]
    except:content_id = re.compile('"video_id":"(.+?)","').findall(data)[0]
    exp_id = re.compile('"player_id":"(.+?)","').findall(data)[0]
    
    renditions = get_episode_info(key, content_id, url, exp_id)['programmedContent']['videoPlayer']['mediaDTO']['renditions']
    rtmp = ''
    hi_res = 0
    selected_video = None
    for video in renditions:
        print video
        if(int(video['size'])>hi_res):
            selected_video = video
            hi_res = int(video['size'])
    
    rtmp = selected_video['defaultURL']
    refactor = re.compile('^(.+?ondemand)/&(.+?)(\?.+)$').findall(rtmp)[0]
    mpvideo = re.compile('_(\d+)_').findall(refactor[1])[0]
    publishId = re.compile('mp4:(\d+?)/').findall(refactor[1])
    if(len(publishId)==0):
        publishId = re.compile('^(\d+?)').findall(refactor[1])[0]
    else:
        publishId = publishId[0]
    
    rtmp = refactor[0]+refactor[2]+' playpath='+refactor[1]+refactor[2]+'&videoId='+mpvideo+'&lineUpId=&pubId='+publishId+'&playerId='+exp_id+'&affiliatedId='
    rtmp += ' pageUrl='+url
    
    item = xbmcgui.ListItem(path=rtmp)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def get_episode_info(key, content_id, url, exp_id):
    conn = httplib.HTTPConnection("c.brightcove.com")
    envelope = build_amf_request(key, content_id, url, exp_id)
    conn.request("POST", "/services/messagebroker/amf?playerKey="+key, str(remoting.encode(envelope).read()),{'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    print response
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
    const = '686a10e2a34ec3ea6af8f2f1c41788804e0480cb'
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
    
    
    
    
