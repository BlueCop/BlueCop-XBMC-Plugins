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

whitelist = ['Awesome VH1 Moments',
             'Big In 06',
             #'Bonus Clips',
             'Concert For Diana',
             'Confessions of a Teen Idol',
             #'Episode Sneak Peeks',
             'Fab Life',
             'Flavor Of Love',
             'Freestyle59',
             #'Full Episodes',
             'Hip Hop Honors',
             'Home Purchasing Club',
             'I Love Money',
             'I Love The',
             'Music Videos',
             'Pop Culture Dictionary',
             'Rock Honors',
             'Scream Queens',
             #'Show Clips',
             'Storytellers',
             'The Bachelor',
             "The Critics' Choice Awards",
             'The Greatest',
             'The Misadventures of Bob Paparazzo',
             'The Pickup Artist',
             'The White Rapper Show',
             'VH1 News',
             'VH1 Specials',
             'Web Junk',
             'World Series Of Pop Culture']

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    sub=tree.find('div',attrs={'id':'video_channel_container'})
    menu=sub.findAll(attrs={'class':'video_browse_container1'})
    db_shows = []
    for item in menu:
        link = item.find(attrs={'class':'video_browse_link_head'}).find('a')
        name = link.string
        url = BASE + link['href']
        if name in whitelist:
            if db==True:
                db_shows.append((name,'vh1','videos',url))
            else:
                common.addDirectory(name,'vh1','videos',url)

    pagintation=sub.find('div',attrs={'style':True}).find('div',attrs={'style':True}).findAll('a',attrs={'class':'pagi_link'})
    for page in pagintation:
        if 'Next' in page.string:
            continue
        url = BASE_URL + page['href']
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        sub=tree.find('div',attrs={'id':'video_channel_container'})
        menu=sub.findAll(attrs={'class':'video_browse_container1'})
        for item in menu:
            link = item.find(attrs={'class':'video_browse_link_head'}).find('a')
            name = link.string
            url = BASE + link['href']
            if name in whitelist:
                if db==True:
                    db_shows.append((name,'vh1','videos',url))
                else:
                    common.addDirectory(name,'vh1','videos',url)
    if db==False:
        common.addDirectory('Basketball Wives','vh1','videos','http://www.vh1.com/video/browse/index.jhtml?id=basketball_wives')
        common.addDirectory('Behind the Music','vh1','videos','http://www.vh1.com/video/browse/index.jhtml?id=6759')
        common.addDirectory('Celebrity Rehab','vh1','videos','http://www.vh1.com/video/browse/index.jhtml?id=celebrity_rehab_with_dr_drew')
        common.addDirectory('Mob Wives','vh1','videos','http://www.vh1.com/video/browse/index.jhtml?id=36088')
        common.addDirectory('Single Ladies','vh1','videos','http://www.vh1.com/video/browse/index.jhtml?id=34960')
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    elif db==True:
        db_shows.append(('Basketball Wives','vh1','videos','http://www.vh1.com/video/browse/index.jhtml?id=basketball_wives'))
        db_shows.append(('Behind the Music','vh1','videos','http://www.vh1.com/video/browse/index.jhtml?id=6759'))
        db_shows.append(('Celebrity Rehab','vh1','videos','http://www.vh1.com/video/browse/index.jhtml?id=celebrity_rehab_with_dr_drew'))
        db_shows.append(('Mob Wives','vh1','videos','http://www.vh1.com/video/browse/index.jhtml?id=36088'))
        db_shows.append(('Single Ladies','vh1','videos','http://www.vh1.com/video/browse/index.jhtml?id=34960'))
        return db_shows

def videos(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    sub=tree.find('div',attrs={'id':'video_channel_container'})
    videoset=sub.findAll(attrs={'class':'video_browse_container'})
    addvideos(videoset)
    pagintation=sub.find('div',attrs={'style':True}).find('div',attrs={'style':True}).findAll('a',attrs={'class':'pagi_link'})
    for page in pagintation:
        if 'Next' in page.string:
            purl = url.split('?')[0] + page['href']
            videos(purl)

    
def addvideos(videoset):    
    for video in videoset:
        thumb = video.find('img')['src']
        link = video.find(attrs={'class':'video_browse_link_head'}).find('a')
        name = link.string
        url = BASE + link['href']
        #airDate = video['mainposted']
        #description = video['maincontent']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="vh1"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 #"Season":season,
                                                 #"Episode":episode,
                                                 #"Plot":description,
                                                 #"premiered":airDate
                                                 #"Duration":duration,
                                                 "TVShowTitle":common.args.name
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

def play(uri=common.args.url):
    data = common.getURL(uri)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    uri = tree.find('link',attrs={'rel':'video_src'})['href'].split('/')[-1]
    configurl = 'http://www.vh1.com/player/embed/AS3/configuration.jhtml?uri='+uri
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
