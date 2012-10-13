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

BASE_URL = 'http://www.mtv.com/ontv/all/'
BASE = 'http://www.mtv.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    shows = []
    multishow = {}
    
    # Grab Current Shows
    data = common.getURL('http://www.mtv.com/ontv/all/current.jhtml')
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows,multishow = grabShowlist(tree,shows,multishow)

    # Grab Current Shows MTV2
    data = common.getURL('http://www.mtv.com/ontv/all/currentMtv2.jhtml')
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows,multishow = grabShowlist(tree,shows,multishow)
     
    # Process Full Show List
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows,multishow = grabShowlist(tree,shows,multishow)
    pagintation=tree.find(attrs={'class':'pagintation'}).findAll('a')
    for page in pagintation:
        if 'Next' in page.string:
            continue
        url = BASE_URL + page['href']
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        shows,multishow = grabShowlist(tree,shows,multishow)
    
    # Grab Popular Shows
    popularShows = tree.find('div',attrs={'id':'shows-grid','class':'grid'}).find('ul').findAll('a')
    for item in popularShows:
        name = item.string
        if 'All Shows' not in name:
            url = BASE + item['href']
            cleanname = name.split(' (Season')[0]
            if cleanname in multishow.keys():
                multishow[cleanname]=True
            else:
                multishow[cleanname]=False
                shows.append((cleanname,url))
            
    db_shows=[]
    for name,url in shows:
        mode = 'showsub'
        db_shows.append((name, 'mtv', mode, url))
    if db==True:
        return db_shows
    else:
        for name, mode, submode, url in db_shows:
            common.addShow(name,mode,submode,url)
        common.setView('tvshows')
            
def grabShowlist(tree,shows,multishow):
    menu=tree.find('ol',attrs={'class':'lst '}).findAll('a')
    for item in menu:
        name = item.contents[2]
        url = BASE + item['href']
        cleanname = name.split(' (Season')[0]
        #if '(Season' in name:
        #    season = int(name.split(' (Season')[1]).replace(')',''))
        if cleanname in multishow.keys():
            multishow[cleanname]=True
        else:
            multishow[cleanname]=False
            shows.append((cleanname,url))
    return (shows,multishow)

def showsub():
    showname=common.args.name
    if 'series.jhtml' in common.args.url:
        videos_url = common.args.url.replace('series.jhtml','video.jhtml')
    elif common.args.url.endswith('/'):
        redirect_url = common.args.url+'video.jhtml'
        videos_url = common.getRedirect(redirect_url).replace('series.jhtml','video.jhtml')
    else:
        videos_url = common.args.url
    data = common.getURL(videos_url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    seasonmenu=tree.find('select',attrs={'id':'videolist_id'})
    if seasonmenu:
        seasons = seasonmenu.findAll('option')
        for season in seasons:
            url = BASE + season['value']
            name = season.string
            common.addDirectory(name,'mtv','seasonOptions',url)
        common.setView('seasons')
    else:
        seasonOptions(videos_url+'?filter=')

def seasonOptions(url=common.args.url):
    #options=[]
    #vidmenu=tree.findAll('li',attrs={'class':re.compile('itemList-subItem')})
    #for item in menu:
    #    link = item.find('a')
    #    name = link.contents[2]
    #    url = BASE + link['href']
    #    if '?' in url:
    #        parameters = '?'+url.split('?')[1]
    #        options.append((name,parameters))
    common.addDirectory('All Videos','mtv','videos',url)
    common.addDirectory('Full Episodes','mtv','videos',url+'fulleps')
    common.addDirectory('Bonus Clips','mtv','videos',url+'bonusclips')
    common.addDirectory('After Shows','mtv','videos',url+'aftershows')
    common.addDirectory('Sneak Peeks','mtv','videos',url+'sneakpeeks')
    common.setView('seasons')

def videos(url=common.args.url,tree=False):
    if not tree:
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos=tree.find('ol',attrs={'id':'vid_mod_1'})
    if videos:
        videos=videos.findAll('li',attrs={'id':re.compile('vidlist')})    
        for video in videos:
            thumb = BASE + video.find('img')['src']
            name = video['maintitle']
            url = BASE + video['mainurl']
            uri = video['mainuri']
            if uri == '':
                uri = url
            airDate = video['mainposted']
            description = video['maincontent']
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(uri)+'"'
            u += '&mode="mtv"'
            u += '&sitemode="play"'
            infoLabels={ "Title":name,
                         #"Season":season,
                         #"Episode":episode,
                         "Plot":description,
                         "premiered":airDate
                         #"Duration":duration,
                         #"TVShowTitle":common.args.name
                         }
            common.addVideo(u,name,thumb,infoLabels=infoLabels)
    common.setView('episodes')
    
def play(uri = common.args.url,referer='http://www.mtv.com'):
    mtvn = 'http://media.mtvnservices.com/'+uri 
    swfUrl = common.getRedirect(mtvn,referer=referer)
    configurl = urllib.unquote_plus(swfUrl.split('CONFIG_URL=')[1].split('&')[0]).strip()
    #configurl = configurl.split('/config.xml?')[0]+'/context4/config.xml?'+configurl.split('/config.xml?')[1]
    configxml = common.getURL(configurl,referer=mtvn)
    tree=BeautifulStoneSoup(configxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    feed = tree.find('feed')
    #try:
    mrssurl = feed.string.replace('{uri}',uri).replace('&amp;','&')
    mrssxml = common.getURL(mrssurl)
    mrsstree = BeautifulStoneSoup(mrssxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    #except:
    #    mrsstree = feed
    segmenturls = mrsstree.findAll('media:content')
    stacked_url = 'stack://'
    for segment in segmenturls:
        surl = segment['url']#+'&acceptMethods=fms,hdn1,hds'
        videos = common.getURL(surl)
        videos = BeautifulStoneSoup(videos, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('rendition')
        hbitrate = -1
        sbitrate = int(common.settings['quality'])
        for video in videos:
            bitrate = int(video['bitrate'])
            if bitrate > hbitrate and bitrate <= sbitrate:
                hbitrate = bitrate
                rtmpdata = video.find('src').string
                rtmpurl = rtmpdata + " swfurl=" + swfUrl.split('?')[0] +" pageUrl=" + referer + " swfvfy=true"
        stacked_url += rtmpurl.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(path=stacked_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def playurl(url = common.args.url):
    #BROKEN
    data=common.getURL(url)
    #try:
    #    uri = re.compile('<meta content="http://(.+?)" itemprop="embedURL"/>').findall(data)[0]
    #except:
    #    uri=re.compile("\= '(.+?)';").findall(data)[0]
    playuri(uri,referer=url)
