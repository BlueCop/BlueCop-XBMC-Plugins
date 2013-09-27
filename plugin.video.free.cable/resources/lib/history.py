#!/usr/bin/python

import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime,base64,sys
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import random
import resources.lib._common as common
import demjson

import binascii
import time
import hmac
try:
    import hashlib.sha1 as sha1
except:
    import sha as sha1

pluginhandle = int(sys.argv[1])

BASEURL = 'http://www.history.com/shows'
H2URL = 'http://www.history.com/shows/h2'
BASE = 'http://www.history.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    db_shows = []
    data = common.getURL(BASEURL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    showpages = tree.findAll(attrs={'class':'watch more'}) 
    for show in showpages:
        url = show['href']
        name = url.split('/')[2].replace('-',' ').title()
        url = BASE + url
        if db==True:
            db_shows.append((name,'history','showcats',url))
        else:
            common.addShow(name, 'history', 'showcats', url)
    data = common.getURL(H2URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    showpages = tree.findAll(attrs={'class':'watch more'})
    for show in showpages:
        url = show['href']
        name = url.split('/')[2].replace('-',' ').title()
        url = BASE + url
        if db==True:
            db_shows.append((name,'history','showcats',url))
        else:
            common.addShow(name, 'history', 'showcats', url)
    if db==True:
        return db_shows    
    else:
        common.setView('tvshows')

def showcats(url=common.args.url):
    data = common.getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    colume1 = tree.find(attrs={'class':'col col-1'})
    try:
        cats = colume1.find(attrs={'class':'parent videos'}).findAll(attrs={'class':'clearfix'})
        for cat in cats:
            link = cat.find('a')
            url = link['href']
            if BASE not in url:
                url = BASE + url
            name = link.string
            common.addDirectory(name, 'history', 'videos', url)
        common.setView('seasons')
    except:
        videos()
        
def videos(url=common.args.url):
    print "DEBUG VIDEOES",url
    print "sart of signin"
    #signed_url = sign_url(common.args.url)
    #print signed_url
    #link = common.getURL(signed_url)
    #print "L",link
    data = common.getURL(url)
   # print "DARA",data
    jsonData = re.compile('var playlist = (.+);').findall(data)[0];
    #print "jdata",jsonData
    json = demjson.decode(jsonData)
    print "JSON",json
    for item in json:
        premium = item['premium']
        if premium == 'false':
           title = item['display']['title'].strip()
           plot  = item['display']['description'].strip()
           thumb = item['display']['thumbUrl']
           #print "T",thumb
           duration = item['display']['duration']
           smil = item['videoURLs']['releaseURL']
           #print "vidurls",item['videoURLs']
           #print "SMIL",smil
           u = sys.argv[0]
           u += '?url="'+urllib.quote_plus(smil)+'"'
           u += '&mode="history"'
           u += '&sitemode="play"'
           infoLabels={ "Title":title,
                        #"Season":season,
                        #"Episode":episode,
                        "Plot":plot,
                        #"premiered":airdate,
                        "Duration":duration,
                        #"TVShowTitle":common.args.name
                        }
           common.addVideo(u,title,thumb,infoLabels=infoLabels)
    common.setView('episodes')
    
def videosHTML(url=common.args.url):
    print "Using html"
    data = common.getURL(url)
    tree=BeautifulSoup(data,convertEntities=BeautifulSoup.HTML_ENTITIES)
    items = tree.find('ul',attrs={'class':'media-thumbs media-thumbs-videos clearfix'}).findAll('li')
    for item in items:
        title = item.find('a').string.strip()
        plot  = item.findAll('p')[1].string
        thumb = item['style'].split('url(')[1].replace(')','')
        duration = item.find('span').string.strip('()')
        url = BASE+ item.find('a')['href']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="history"'
        u += '&sitemode="play"'
        infoLabels={ "Title":title,
                     #"Season":season,
                     #"Episode":episode,
                     "Plot":plot,
                     #"premiered":airdate,
                     "Duration":duration,
                     #"TVShowTitle":common.args.name
                     }
        common.addVideo(u,title,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def videosRSS(url=common.args.url):
    link = common.getURL(url)
    mrssData = re.compile('mrssData += +"(.+)"').findall(link)[0];
    mrssData = urllib2.unquote(base64.decodestring(mrssData))
    tree=BeautifulStoneSoup(mrssData,convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print tree.prettify()
    items = tree.findAll('item')
    for item in items:
        title = item.title.contents[0]
        plot  = item.description.contents[0]
        thumb = item.findAll('media:thumbnail')[0]['url']
        duration = item.findAll('media:content')[0]['duration']
        smil = item.findAll('media:text')[5].contents[0]
        smil = smil.replace('smilUrl=','')
        #episode_list.append((title, image, duration, plot, smil))
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(smil)+'"'
        u += '&mode="history"'
        u += '&sitemode="play"'
        infoLabels={ "Title":title,
                     #"Season":season,
                     #"Episode":episode,
                     "Plot":plot,
                     #"premiered":airdate,
                     "Duration":duration,
                     #"TVShowTitle":common.args.name
                     }
        common.addVideo(u,title,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def playOLD():
    sig = common.getURL('http://www.history.com/components/get-signed-signature?url='+re.compile('/s/(.+)\?').findall(common.args.url)[0]+'&cache=889')
    url = common.args.url+'&sig='+sig
    link = common.getURL(url)
    tree=BeautifulStoneSoup(link, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    base = tree.find('meta')['base']
    videos = tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality']) * 1000
    for video in videos:
        try:bitrate = int(video['system-bitrate'])
        except:bitrate = int(video['systembitrate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            filename = video['src'].replace('.mp4','').replace('.flv','')
    swfUrl = 'http://www.history.com/flash/VideoPlayer.swf'
    auth = filename.split('?')[1]
    filename = filename.split('?')[0]
    finalurl = base+'?'+auth+' swfurl='+swfUrl+' swfvfy=true playpath='+filename
    item = xbmcgui.ListItem(path=finalurl)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def play():
    if (common.settings['enableproxy'] == 'true'):proxy = True
    else:proxy = False
    signed_url = sign_url(common.args.url)
    #get auth
    #token=getAUTH(aifp,window,tokentype,vid,filename)
    print "proxy",proxy
    link = common.getURL(signed_url,proxy=proxy)
    
    print "**",link
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
            if '.mp4' in video['src']:
                filename = 'mp4:'+filename #slices 08052013
   
    swfUrl = 'http://www.history.com/flash/VideoPlayer.swf'
    #swfUrl='http://servicesaetn-a.akamaihd.net/video/pdk/swf/flvPlayer.swf'
    auth = filename.split('?')[1]
    filename = filename.split('?')[0]
    finalurl = base+'?'+auth+' swfurl='+swfUrl+' swfvfy=true playpath='+filename
    item = xbmcgui.ListItem(path=finalurl)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def sign_url(url):
    #slices - changed ro use url
    #http://www.tbs.com/processors/cvp/token.jsp
    sig=common.getURL('http://www.history.com/components/get-signed-signature?url='+re.compile('/s/(.+)\?').findall(url)[0])
    #hmac_key = 'crazyjava'
    #http://link.theplatform.com/s/xc6n8B/Uk9Iewei0eId/tracker.log?type=qos&ver=2&d=1367950641769&rid0=28489795528&t0=Ancient%20Aliens%3A%20The%20Time%20Travelers&tc0=1&lp0=0&lt0=3&pb0=100&pp0=0&pr0=0&nocache=1367950646788
    #http://link.theplatform.com/s/xc6n8B/Uk9Iewei0eId?mbr=true&sig=005189478ac93e8e252247688d9fe43e80a0ceabf57e46df32733363723374&metafile=true&assetTypes=medium%5Fvideo%5Fs3&switch=rtmp&format=SMIL&Tracking=true&Embedded=true
    #SEC_HEX = '733363723374' #'s3cr3t'
    #expiration = get_expiration()
    #print expiration
    #path = url.split('http://link.theplatform.com/s/')[1]
    #sign_data = binascii.unhexlify('00'+expiration+binascii.hexlify(path).lower())
    #print "Sign data",sign_data
    #sig = hmac.new(hmac_key, sign_data, sha1)
    #sigHEX = sig.hexdigest()
    #signature = '00' + expiration + sigHEX + SEC_HEX
    finalUrl = url+'&sig='+sig+'&format=SMIL&Tracking=true&Embedded=true&mbr=true&auth=daEbfbTdjaccacMd9aHd_ccdLbad6cjdSdg-brIOlw-cOW-ooHzv'
    print "fu",finalUrl
    return finalUrl

def get_expiration(auth_length = 600):
    current_time = time.mktime(time.gmtime())+auth_length
    expiration = ('%0.2X' % current_time).lower()
    return expiration