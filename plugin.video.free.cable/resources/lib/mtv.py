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
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find('ol',attrs={'class':'lst '}).findAll('a')
    db_shows = []
    multiseason = []
    db_shows.append(('Beavis and Butthead','mtv','showsub','http://www.mtv.com/shows/beavis_and_butthead/series.jhtml'))
    db_shows.append(('Real World: San Diego','mtv','showsub','http://www.mtv.com/shows/real_world/san_diego/series.jhtml'))
    for item in menu:
        name = item.contents[2]
        if ' (Season' in name:
            name = name.split(' (Season')[0]
            mode = 'seasons'
            if name in multiseason:
                continue
            else:
                multiseason.append(name)
        else:
            mode = 'showsub'
        url = BASE + item['href']
        db_shows.append((name,'mtv',mode,url))
    pagintation=tree.find(attrs={'class':'pagintation'}).findAll('a')
    for page in pagintation:
        if 'Next' in page.string:
            continue
        url = BASE_URL + page['href']
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        menu=tree.find('ol',attrs={'class':'lst '}).findAll('a')
        for item in menu:
            name = item.contents[2]
            if ' (Season' in name:
                name = name.split(' (Season')[0]
                mode = 'seasons'
                if name in multiseason:
                    continue
                else:
                    multiseason.append(name)
            else:
                mode = 'showsub'
            url = BASE + item['href']
            db_shows.append((name,'mtv',mode,url))           
    if db==True:
        return db_shows
    else:
        for name, mode, submode, url in db_shows:
            common.addDirectory(name,mode,submode,url)

def seasons():
    showname=common.args.name
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find('ol',attrs={'class':'lst '}).findAll('a')
    for item in menu:
        name = item.contents[2].replace("'",'')
        if showname in name:
            try: name = name.split(' (')[1].replace(')','')
            except: name = name
            url = BASE + item['href']
            common.addDirectory(name,'mtv','showsub',url)
    pagintation=tree.find(attrs={'class':'pagintation'}).findAll('a')
    for page in pagintation:
        if 'Next' in page.string:
            continue
        url = BASE_URL + page['href']
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        menu=tree.find('ol',attrs={'class':'lst '}).findAll('a')
        for item in menu:
            name = item.contents[2].replace("'",'')
            if showname in name:
                try: name = name.split(' (')[1].replace(')','')
                except: name = name
                url = BASE + item['href']
                common.addDirectory(name,'mtv','showsub',url)

def showsub(url=common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.findAll('li',attrs={'class':re.compile('itemList-subItem')})
    if len(menu) == 0:
        url = url.replace('series.jhtml','video.jhtml')
        videos(url)
    elif len(menu) == 1:
        url = BASE + menu[0].find('a')['href']
        videos(url)
    else:
        for item in menu:
            link = item.find('a')
            name = link.contents[2]
            url = BASE + link['href']
            common.addDirectory(name,'mtv','videos',url)

def videos(url=common.args.url):
    try:
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        videos=tree.find('ol',attrs={'id':'vid_mod_1'}).findAll('li',attrs={'id':re.compile('vidlist')})    
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
            item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":name,
                                                     #"Season":season,
                                                     #"Episode":episode,
                                                     "Plot":description,
                                                     "premiered":airDate
                                                     #"Duration":duration,
                                                     #"TVShowTitle":common.args.name
                                                     })
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)
    except:
        print 'videos failed'

def play(uri=common.args.url):
    if 'http://' in uri:
        data = common.getURL(uri)
        tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        uri = tree.find('meta',attrs={'name':'mtvn_uri'})['content']
        url = 'http://www.mtv.com/player/includes/mediaGen.jhtml?uri='+uri
        stacked_url = grabrtmp(url)
    else:
        rssurl = 'http://www.mtv.com/player/embed/AS3/fullepisode/rss/?id='+uri.split(':')[-1]+'&uri='+uri+'&instance=fullepisode'
        data = common.getURL(rssurl)
        tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        mcurls=tree.findAll('media:content')
        stacked_url = 'stack://'
        for mcurl in mcurls:
            rtmp = grabrtmp(mcurl['url'].split('&')[0])
            stacked_url += rtmp.replace(',',',,')+' , '
        stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(path=stacked_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
     

def grabrtmp(url):
    swfurl = "http://media.mtvnservices.com/player/release/?v=4.5.3"
    data = common.getURL(url)
    bitrates = re.compile('bitrate="(.+?)"').findall(data)
    rtmps = re.compile('<src>rtmp(.+?)</src>').findall(data)
    mbitrate = -1
    lbitrate = 0
    for rtmp in rtmps:
        marker = rtmps.index(rtmp)
        bitrate = int(bitrates[marker])
        if bitrate == 0:
            continue
        elif bitrate > mbitrate:
            mbitrate = bitrate
            furl = 'rtmp'+ rtmp + " swfurl=" + swfurl + " swfvfy=true"
    return furl
