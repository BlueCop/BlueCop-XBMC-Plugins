import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
from pyamf.remoting.client import RemotingService
import resources.lib._common as common

pluginhandle = int (sys.argv[1])

BASE_URL = 'http://www.nbc.com/Video/library/'
BASE = 'http://www.nbc.com'

def masterlist():
    common.args.name = 'Show Library'
    return shows(BASE_URL, db=True)

def checkurl(url):
    #Add base url checks
    return url

def rootlist():
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'class' : 'scet-gallery-nav'})
    categories=menu.findAll('h3')
    for item in categories:
        name = item.string
        if name == 'Previews & Specials' or name == 'All Videos' or name == 'Webisodes':
            continue
        common.addDirectory(name, 'nbc', 'shows', BASE_URL)

def showroot(url = common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'class' : 'scet-gallery-nav'})
    categories=menu.findAll('h3')
    for item in categories:
        name = item.string    
        if name == 'All Videos':
            continue
        common.addDirectory(name, 'nbc', 'showsub', url)

def showsub(url = common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    if common.args.name == 'Full Episodes' or common.args.name == 'Webisodes':
        sitemode='fullepisodes'
    else:
        sitemode='listvideos'
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'class' : 'scet-gallery-nav'})
    categories=menu.findAll('h3')
    for category in categories:
        if common.args.name == category.string:
            marker = categories.index(category)
    items = menu.findAll('ul')[marker].findAll('a')
    for item in items:
        name = item.string
        url = BASE + item['href']
        common.addDirectory(name, 'nbc', sitemode, url)
        
def shows(url = common.args.url, db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'class' : 'scet-gallery-nav'})
    categories=menu.findAll('h3')
    for category in categories:
        if common.args.name == category.string:
            marker = categories.index(category)
    items = menu.findAll('ul')[marker].findAll('a')
    db_shows = []
    if len(items) == 1:
        url = BASE + items[0]['href']
        shows2(url)
    for item in items:
        name = item.string
        url = item['href']
        if db==True:
            db_shows.append((name,'nbc','showroot',url))
        else:
            common.addDirectory(name, 'nbc', 'showroot', url)
    if db==True:
        return db_shows

def shows2(url):
    if common.args.name == 'Full Episodes':
        sitemode='fullepisodes'
    else:
        sitemode='listvideos'
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    items=tree.find(attrs={'id' : 'header-video-clips'})
    items=items.findAll('a')
    for item in items:
        name = item['title']
        itemurl = item['href']
        if BASE not in itemurl:
            if itemurl[0] == '/':
                itemurl = BASE + itemurl
            else:
                itemurl = url + itemurl
        thumb = item.find('img')['src']
        common.addDirectory(name, 'nbc', sitemode, itemurl, thumb)

def listvideos (url = common.args.url,trypages=True):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    if trypages == True:
        try:
            firstpage = tree.find(attrs={'class':'nbcu_pager_page nbcu_pager_active'})
            pages = tree.findAll(attrs={'class':'nbcu_pager_page'})
            pages.insert(0,firstpage)
            for page in pages:
                url = BASE + page['href']
                listvideos(url,False)
            return
        except:
            print 'Single Page'
    items=tree.find(attrs={'id' : 'header-video-clips'})
    items=items.findAll(attrs={'class':'img-wrap'})
    for item in items:
        url = BASE + item['href']
        name = item['title']
        thumb = item.find('img')['src']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="nbc"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 "TVShowTitle":common.args.name
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)
        
def fullepisodes (url = common.args.url,trypages=True):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:
        if trypages == True:
            try:
                firstpage = tree.find(attrs={'class':'nbcu_pager_page nbcu_pager_active'})
                pages = tree.findAll(attrs={'class':'nbcu_pager_page'})
                pages.insert(0,firstpage)
                for page in pages:
                    url = BASE + page['href']
                    fullepisodes(url,False)
                return
            except:
                print 'Single Page'
        items=tree.find(attrs={'id' : 'header-video-clips'})
        items=items.findAll(attrs={'class' : 'list_full_detail_horiz'})
        for item in items:
            link = item.find('a')
            url = BASE + link['href']
            name = link['title']
            thumb = link.find('img')['src']
            description = item.find(attrs={'class' : 'list_full_des'}).contents[0].contents[0]
            airDate = item.find(attrs={'class' : 'list_full_det_time'}).contents[0].contents[1].strip()
            try:
                seasonepisode = item.find(attrs={'class' : 'list_full_det_title'})('a')[0].string.split(':')[0].split('. ')[1]
                if 3 == len(seasonepisode):
                    season = int(seasonepisode[:1])
                    episode = int(seasonepisode[-2:])
                elif 4 == len(seasonepisode):
                    season = int(seasonepisode[:2])
                    episode = int(seasonepisode[-2:])
                if season <> 0 or episode <> 0:
                    displayname = '%sx%s - %s' % (str(season),str(episode),name)
            except:
                print 'season/episode metadata failed'
                season = 0
                episode = 0
                displayname = name
    
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="nbc"'
            u += '&sitemode="play"'
            item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":name,
                                                     "Season":season,
                                                     "Episode":episode,
                                                     "Plot":description,
                                                     "premiered":airDate,
                                                     #"Duration":duration,
                                                     "TVShowTitle":common.args.name
                                                     })
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)
    except:
        items=tree.findAll(attrs={'class' : 'thumb-block '})
        for item in items:
            url = BASE + item.find('a')['href']
            name = item.find(attrs={'class' : 'title'}).string
            thumb = item.find('img')['src']
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="nbc"'
            u += '&sitemode="play"'
            item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":name
                                                     #"premiered":airDate,
                                                     #"Duration":duration,
                                                     #"TVShowTitle":common.args.name
                                                     })
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)            

#Get SMIL url and play video
def play():
    vid=re.compile('/(\d+)/').findall(common.args.url)[0]
    smilurl = getsmil(vid)
    rtmpurl = getrtmp()
    swfUrl = getswfUrl()
    data = common.getURL(smilurl)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    items=tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality']) * 1024
    for item in items:
        bitrate = int(item['system-bitrate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            playpath = item['src']
            if '.mp4' in playpath:
                playpath = 'mp4:'+playpath
            else:
                playpath = playpath.replace('.flv','')
            finalurl = rtmpurl+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    item = xbmcgui.ListItem(path=finalurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def getsmil(vid):
    gw = RemotingService(url='http://video.nbcuni.com/amfphp/gateway.php',
            referer='http://www.nbc.com/assets/video/3-0/swf/NBCVideoApp.swf',
            user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
        )
    ClipAll_service = gw.getService('getClipInfo.getClipAll')
    geo  ="US"
    num1 = "632"
    num2 = "-1"
    response = ClipAll_service(vid,geo,num1,num2)
    url = 'http://video.nbcuni.com/' + response['clipurl']
    return url


def getrtmp():
    gw = RemotingService(url='http://video.nbcuni.com/amfphp/gateway.php',
            referer='http://www.nbc.com/assets/video/3-0/swf/NBCVideoApp.swf',
            user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
        )
    ClipAll_service = gw.getService('getConfigInfo.getConfigAll')
    num1 = "17010"
    response = ClipAll_service(num1)
    rtmphost= response['akamaiHostName']
    app = response['akamaiAppName']
    identurl = 'http://'+rtmphost+'/fcs/ident'
    ident = common.getURL(identurl)
    ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
    rtmpurl = 'rtmp://'+ip+':1935/'+app+'?_fcs_vhost='+rtmphost
    return str(rtmpurl)

def getswfUrl():
    swfUrl = "http://www.nbc.com/assets/video/4-0/swf/core/video_player_extension.swf?4.5.5"
    return swfUrl
