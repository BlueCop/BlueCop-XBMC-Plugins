#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re
import httplib
import base64
import random
import binascii
import time
import hmac
try:
    import hashlib.sha1 as sha1
except:
    import sha as sha1


from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import resources.lib._common as common
from pyamf import remoting

pluginhandle = int(sys.argv[1])

BASEURL = 'http://www.aetv.com/videos/display.jsp'
SHOWSURL = 'http://www.aetv.com/allshows.jsp'
BASE = 'http://www.aetv.com'

def masterlist():
    return showlist(db=True)

def rootlist(db=False):
    common.addDirectory('Shows'    , 'aetv', 'showlist', '')
    common.addDirectory('Lifestyle', 'aetv', 'lifesytlelist', 'season_url')
    common.addDirectory('Classic'  , 'aetv', 'classiclist', 'season_url')

def lifesytlelist():
    droplist('/lifestyle/')

def classiclist():
    droplist('/classic/')
    
def droplist(homedir):
    url  = 'http://www.aetv.com/minisite/videoajx.jsp'
    url += '?homedir='+homedir
    url += '&pfilter=ALL%20VIDEOS'
    url += '&sfilter=All%20Categories'
    url += '&seriesfilter=ALL%20SERIES'
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows = tree.find('div',attrs={'id':'series_filter'}).findAll('li',attrs={'class':None})
    for show in shows:
        name = show.find('a').string
        url  = 'http://www.aetv.com/minisite/videoajx.jsp'
        url += '?homedir='+homedir
        url += '&seriesfilter='+name.replace(' ','%20')
        common.addShow(name, 'aetv', 'show_primary_filter', url)

def show_primary_filter(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    primary_filter = tree.find('div',attrs={'id':'primary_filter'})
    if primary_filter:
        filters = primary_filter.findAll('li',attrs={'class':None})
        if len(filters) > 1:
            for filter in filters:
                link = filter.find('a')
                item_url = url + '&pfilter='+link.string.strip().replace(' ','%20')
                common.addDirectory(link.string.title(), 'aetv', 'show_secondary_filter', item_url)
        else:
            showsubThePlatform(url.replace(' ','%20'),tree=tree)
    else:
        showsubThePlatform(url.replace(' ','%20'),tree=tree)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    common.setView('seasons')

def show_secondary_filter(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    second_filter = tree.find('div',attrs={'id':'secondary_filter'})
    if second_filter:
        filters = second_filter.findAll('li')
        if len(filters) > 1:
            for filter in filters:
                link = filter.find('a')
                if link.string == 'All Categories':
                    item_url = url
                else:
                    item_url = url + '&sfilter='+link.string.strip().replace(' ','%20')
                common.addDirectory(link.string.title(), 'aetv', 'showsubThePlatform', item_url)
        else:
            showsubThePlatform(url.replace(' ','%20'),tree=tree)
    else:
        showsubThePlatform(url.replace(' ','%20'),tree=tree)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    common.setView('seasons')
    
def showlist(db=False):
    data = common.getURL(BASEURL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'av-list1','class':'all-videos_unordered'}).findAll('a')
    db_shows = []
    blackListShows = ["Kirstie Alley's Big Life","The Sopranos®","Coma"]
    for item in menu:
        name = item.string.encode('utf-8')
        url = item['href']
        if 'http://' not in item['href']:
            url = BASE + url
        if name in blackListShows:
            continue

        if db==True:
            db_shows.append((name, 'aetv', 'show_cats', url))
        else:
            common.addShow(name, 'aetv', 'show_cats', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def show_cats(url=common.args.url):
    data = common.getURL(url.replace(' ','%20'))
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    homedir = tree.find('div',attrs={'id':'video_home_dir','style':'display : none'}).string
    series_base  = 'http://www.aetv.com/minisite/videoajx.jsp'
    series_base += '?homedir='+homedir
    #full_series_url = series_url+'&pfilter=FULL%20EPISODES'
    #clips_series_url = series_url+'&pfilter=CLIPS'
    if homedir == '/lifestyle/' or homedir == '/classic/':
        series = url.split('=')[-1].replace(' ','%20')
        series_url = series_base + '&seriesfilter='+series
    else:
        series_url = series_base
    data = common.getURL(series_url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    seasons = tree.find('div',attrs={'id':'primary_filter'}).findAll('li',attrs={'class':None})
    if len(seasons) > 0:
        for season in seasons:
            link = season.find('a')
            if '?' in series_base:
                season_url = series_base + '&pfilter='+link.string.strip().replace(' ','%20')
            else:
                season_url = series_base + '?pfilter='+link.string.strip().replace(' ','%20')
            if homedir == '/lifestyle/' or homedir == '/classic/':
                series = url.split('=')[-1].replace(' ','%20')
                season_url += '&seriesfilter='+series
            common.addDirectory(link.string.title(), 'aetv', 'showseasonThePlatform', season_url)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        common.setView('seasons')
    else:
        showseasonThePlatform(url.replace(' ','%20'),tree=tree)
    common.setView('seasons')

def showseasonThePlatform(url=common.args.url,tree=False):
    if not tree:
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    seasons = tree.find('div',attrs={'id':'secondary_filter'}).findAll('li')
    if len(seasons) > 1:
        for season in seasons:
            link = season.find('a')
            if link.string == 'All Categories':
                season_url = url
            else:
                season_url = url+'&sfilter='+link.string.strip().replace(' ','%20')
            common.addDirectory(link.string, 'aetv', 'showsubThePlatform', season_url)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        common.setView('seasons')
    else:
        showsubThePlatform(url.replace(' ','%20'),tree=tree)
    

def showsubThePlatform(url=common.args.url,tree=False):
    if not tree:
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos=tree.findAll('li',attrs={'class':'selected'})
    try:season = int(tree.findAll('li',attrs={'class':'selected'})[1].find('a').string.replace('Season ',''))
    except:season = 0
    videos=tree.findAll('div',attrs={'class':'video_playlist-item'})
    for video in videos:
        infoLabels={'Season':season}
        video_details = video.find('div',attrs={'class':'video_details'})
        infoLabels['Title'] = video_details.find('p',attrs={'class':'video_details-title'}).string.encode('utf-8')
        thumb = video.find('img')['realsrc']
        if 'http://' not in thumb:
            thumb = BASE + thumb
        url = 'http'+video.find('a')['onclick'].split("'http")[1].split("'")[0]
        infoLabels['Plot'] = video_details.find('p',attrs={'class':'video_details-synopsis'}).string.encode('utf-8')
        displayname=infoLabels['Title']
        for p in video_details.findAll('p',attrs={'class':None}):
            if p.find('span'):
                infoLabels['Duration'] = p.find('span').string
            else:
                if 'Premiere Date: ' in p.string:
                    infoLabels['premiered'] = p.string.replace('Premiere Date: ','')
                elif 'Episode: ' in p.string:
                    try:
                        infoLabels['Episode'] = int(p.string.replace('Episode: ',''))
                        if infoLabels['Season'] <> 0:
                            displayname = '%sx%s - %s' % (str(infoLabels['Season']),str(infoLabels['Episode']),infoLabels['Title'])
                        else:
                            displayname = str(infoLabels['Episode'])+' - '+infoLabels['Title']
                    except:
                        infoLabels['Episode'] = 0
                        displayname = infoLabels['Title']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="aetv"'
        u += '&sitemode="playThePlatform"'
        common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def playThePlatform():
    data = common.getURL(common.args.url)
    #mrss = urllib.unquote_plus(base64.b64decode(re.compile('{ mrss: "(.+?)",').findall(data)[0]))
    try:mrss = urllib.unquote_plus(base64.b64decode(re.compile('{ mrss: "(.+?)",').findall(data)[0]))
    except:mrss = urllib.unquote_plus(base64.b64decode(re.compile('"mrss=(.+?)&').findall(data)[0]))
    tree=BeautifulStoneSoup(mrss, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    for item in tree.findAll('item'):
        link = item.find('link').string
        if link == common.args.url:
            smil_url = item.find('media:text',text=re.compile('smilUrl=')).string.split('smilUrl=')[1]
    #smil_url = re.compile('<media:text>smilUrl=(.+?)</media:text>').findall(mrss)[0]
    #signUrl  = 'http://www.history.com/components/get-signed-signature'
    #signUrl += '?url='+smil_url.split('/s/')[1].split('?')[0]
    #signUrl += '&cache='+str(random.randint(100, 999))
    #sig = str(common.getURL(signUrl))
    sig = sign_url(smil_url)
    smil_url += '&sig='+sig
    data = common.getURL(smil_url)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    rtmp_base = tree.find('meta')['base']
    filenames = tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality'])
    for filename in filenames:
        bitrate = int(filename['system-bitrate'])/1024
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            playpath = filename['src']
    swfUrl = 'http://www.aetv.com/js/minisite4g/VideoPlayer.swf'
    rtmpurl = rtmp_base+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    item = xbmcgui.ListItem(path=rtmpurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def sign_url(url):
    hmac_key = 'crazyjava'
    SEC_HEX = '733363723374' #'s3cr3t'
    expiration = get_expiration()
    path = url.split('http://link.theplatform.com/s/')[1].split('?')[0]
    sign_data = binascii.unhexlify('00'+expiration+binascii.hexlify(path).lower())
    sig = hmac.new(hmac_key, sign_data, sha1)
    sigHEX = sig.hexdigest()
    signature = '00' + expiration + sigHEX + SEC_HEX
    #finalUrl = url+'?sig='+signature+'&format=SMIL&Tracking=true&Embedded=true&mbr=true'
    return signature

def get_expiration(auth_length = 600):
    current_time = time.mktime(time.gmtime())+auth_length
    expiration = ('%0.2X' % current_time).lower()
    return expiration
