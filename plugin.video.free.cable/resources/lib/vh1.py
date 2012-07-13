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

pluginhandle=int(sys.argv[1])

BASE_URL = 'http://www.vh1.com/video/browse/shows.jhtml'
BASE = 'http://www.vh1.com'

blacklist = [   "14th Annual Critics' Choice Awards (2009)",
                '2009 Hip Hop Honors',
                '2010 Hip Hop Honors',
                "Critics' Choice Movie Awards (2010)",
                "Critics' Choice Movie Awards (2011)",
                'DIVAS (2010)',
                'Do Something Awards 2010',
                'Do Something Awards 2011',
                'Front Row',
                'Movies That Rock!',
                'Pop Up Video',
                'Posted',
                'Rock Honors: The Who',
                'Stand Up To Cancer',
                'VH1 Big In 2006 Awards',
                'VH1 Divas (2009)',
                'VH1 Divas Celebrates Soul',
                'VH1 Pop Up Video'
                ]

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    url = 'http://www.vh1.com/shows/all_vh1_shows.jhtml'
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #print tree.prettify()
    shows=tree.find('div',attrs={'id':'azshows'}).findAll('a')
    goodshows = []
    novideos = []
    failedshows = []
    for show in shows:
        name = show.string
        if name in blacklist:
            continue
        url = show['href']
        if BASE not in url:
            url = BASE + url
        common.addDirectory(name,'vh1','showsubcats',url)

def showsubcats(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #print tree.prettify()
    subs=tree.find(attrs={'class':'group-a'}).findAll('a')
    for sub in subs:
        name = sub.string
        url = sub['href']
        if BASE not in url:
            url = BASE + url
        if name == None:
            name = sub.contents[-1]
        if 'Episodes' in name or 'Clips' in name or 'Peeks' in name or 'Watch' in name or 'Video' in name:
            if 'id=' in url:
                u = sys.argv[0]
                u += '?url="'+urllib.quote_plus(url)+'"'
                u += '&mode="vh1"'
                u += '&sitemode="playurl"'
                item=xbmcgui.ListItem(name)
                item.setInfo( type="Video", infoLabels={ "Title":name })
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)
            else:
                common.addDirectory(name,'vh1','videos',url)

def videos(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #print tree.prettify()
    subs=tree.find(attrs={'class':'group-b'})
    try:finalsubs = subs.find(attrs={'class':'video-list'}).findAll('tr',attrs={'class':True})
    except:finalsubs = subs.find(attrs={'id':"vid_mod_1"}).findAll(attrs={'itemscope':True})
    for sub in finalsubs:
        print sub
        sub = sub.find('a')
        name = sub.string
        url = sub['href']
        if BASE not in url:
            url = BASE + url
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="vh1"'
        u += '&sitemode="playurl"'
        item=xbmcgui.ListItem(name)
        item.setInfo( type="Video", infoLabels={ "Title":name })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

def playuri(uri = common.args.url,referer='http://www.tvland.com'):
    mtvn = 'http://media.mtvnservices.com/'+uri 
    swfUrl = common.getRedirect(mtvn,referer=referer)
    configurl = urllib.unquote_plus(swfUrl.split('CONFIG_URL=')[1].split('&')[0])
    configxml = common.getURL(configurl)
    tree=BeautifulStoneSoup(configxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    feed = tree.find('player').find('feed')
    try:
        mrssurl = feed.string.replace('{uri}',uri).replace('&amp;','&')
        mrssxml = common.getURL(feedurl)
        mrsstree = BeautifulStoneSoup(feeddata, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    except:
        mrsstree = feed
    segmenturls = tree.findAll('media:content')
    stacked_url = 'stack://'
    for segment in segmenturls:
        surl = segment['url']
        videos = common.getURL(surl)
        videos = BeautifulStoneSoup(videos, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('rendition')
        hbitrate = -1
        sbitrate = int(common.settings['quality'])
        for video in videos:
            bitrate = int(video['bitrate'])
            if bitrate > hbitrate and bitrate <= sbitrate:
                hbitrate = bitrate
                rtmpdata = video.find('src').string
                
                protocall = rtmpdata.split('://')[0]
                host = rtmpdata.split('://')[1].split('/')[0]
                app = rtmpdata.split('://')[1].split('/')[1]
                playpath = rtmpdata.split(app+'/')[1]
                if '.mp4' in playpath:
                    playpath = 'mp4:'+playpath#.replace('.mp4','')
                else:
                    playpath = playpath#.replace('.flv','')
                rtmpurl = 'rtmpe://'+host+':1935/'+app
                rtmpurl += ' playpath=' + playpath + " swfurl=" + swfUrl.split('?')[0] +" pageUrl=" + referer + " swfvfy=true"
                
                #app = rtmpdata.split('://')[1].split('/')[1]
                #rtmpdata = rtmpdata.split(app)
                #rtmp = rtmpdata[0]
                #playpath = rtmpdata[1]
                #if '.mp4' in playpath:
                #    playpath = 'mp4:'+playpath.replace('.mp4','')
                #else:
                #    playpath = playpath.replace('.flv','')
                #swfUrl = "http://media.mtvnservices.com/player/prime/mediaplayerprime.1.6.0.swf"
                #rtmpurl = rtmpdata + " swfurl=" + swfUrl.split('?')[0] +" pageUrl=" + referer + " swfvfy=true"
        stacked_url += rtmpurl.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    print stacked_url
    item = xbmcgui.ListItem(path=stacked_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def playurl(url = common.args.url):
    data = common.getURL(url)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    uri = tree.find('link',attrs={'rel':'video_src'})['href'].split('/')[-1]
    playuri(uri,referer=url)


def playold(uri=common.args.url):
    data = common.getURL(uri)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    uri = tree.find('link',attrs={'rel':'video_src'})['href'].split('/')[-1]
    configurl  = 'http://www.vh1.com/player/embed/AS3/configuration.jhtml?uri='+uri
    configurl += '&type=network&ref=www.vh1.com&geo=US&&device=Other&ver=prime'
    data = common.getURL(configurl)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    feed = tree.find('player').find('feed')
    try:
        feedurl = feed.string
        feeddata = common.getURL(feedurl)
        feeddata = BeautifulStoneSoup(feeddata, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    except:
        feeddata = feed
    segmenturls=feeddata.findAll('media:content')
    stacked_url = 'stack://'
    for segment in segmenturls:
        surl = segment['url']
        rtmp = grabrtmp(surl)
        stacked_url += rtmp.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(path=stacked_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)    

def grabrtmp(url):
    uri = url.split('uri=')[1].split('&')[0]
    videos = common.getURL(url)
    videos = BeautifulStoneSoup(videos, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('rendition')
    hbitrate = -1
    sbitrate = int(common.settings['quality'])
    for video in videos:
        bitrate = int(video['bitrate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            rtmpdata = video.find('src').string
            protocall = rtmpdata.split('://')[0]
            host = rtmpdata.split('://')[1].split('/')[0]
            app = rtmpdata.split('://')[1].split('/')[1]
            playpath = rtmpdata.split(app+'/')[1]
            if '.mp4' in playpath:
                playpath = 'mp4:'+playpath#.replace('.mp4','')
            else:
                playpath = playpath#.replace('.flv','')
            swfUrl = "http://media.mtvnservices.com/player/prime/mediaplayerprime.1.8.5.swf?uri="+uri
            rtmpurl = 'rtmpe://'+host+':1935/'+app
            #rtmpurl += ' conn=O:1 conn=NB:0:0 conn=NS:1:'+playpath+' conn=O:0'
            rtmpurl += ' playpath=' + playpath + ' swfurl=' + swfUrl + ' swfvfy=1'
            # -C O:1 -C NB:0:0 -C NS:1:mp4:gsp.vhonecomstor/vh1.com/shows/celebrity_rehab_5/vh_cr_51_rt242902_clip_s1_640x480_1600_m30.mp4 -C O:0
            
    print rtmpurl
    return rtmpurl
