import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re
import time

from BeautifulSoup import BeautifulSoup
from pyamf.remoting.client import RemotingService
import resources.lib._common as common

pluginhandle = int (sys.argv[1])

BASE_URL = 'http://www.nbc.com/video/library/full-episodes/'
BASE = 'http://www.nbc.com'

def masterlist():
    return shows(BASE_URL,'Show Library', db=True)

def rootlist():
    shows(BASE_URL,'Show Library')

def shows(url = common.args.url, choosenCat='Show Library', db=False):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'class' : 'scet-gallery-nav'})
    categories=menu.findAll('h3')
    for category in categories:
        if choosenCat == category.string:
            marker = categories.index(category)
    items = menu.findAll('ul')[marker].findAll('a')
    db_shows = []
    dupecheck = []
    #            ('Revolution','nbc','showroot','http://www.nbc.com/revolution/video/nobodys-fault-but-mine/1425158/'),
    #            ('Chicago Fire','nbc','showroot','http://www.nbc.com/chicago-fire/video/categories/season-1/1416546/')]
    #common.addShow('Revolution','nbc','showroot','http://www.nbc.com/revolution/video/nobodys-fault-but-mine/1425158/')
    #common.addShow('Chicago Fire','nbc','showroot','http://www.nbc.com/chicago-fire/video/categories/season-1/1416546/')
    for item in items:
        name = item.string
        url = item['href']
        #if db==True:
        db_shows.append((name,'nbc','showroot',url))
        dupecheck.append(name)
        #else:
        #    common.addShow(name, 'nbc', 'showroot', url)
    
    items = tree.findAll('ul',attrs={'class':'scet_th_list'})
    for list in items:
        for item in list.findAll('li',recursive=False):
            link = item.find('a')
            name = link['title']
            url = link['href']
            if name not in dupecheck:
                db_shows.append((name,'nbc','showroot',url))
                dupecheck.append(name)

    if not db:
        for show in db_shows:
            common.addShow(show[0], 'nbc', 'showroot', show[3])

    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def showroot(url = common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'shows')
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    sets=tree.find('div',attrs={'id' : 'scet-categories'}).findAll('div',attrs={'class' : 'scet-cat-group'})
    for set in sets:
        set_title = set.find('h5').string.lower()
        if set_title == 'all videos':
            continue
        elif set_title == 'full episodes' or set_title == 'webisodes':
            mode = 'showsubFullEpisode'
        else:
            mode = 'showsubClips'
        for link in set.findAll('a'):
            name = link.string.strip()
            url = BASE+link['href'].split('?')[0]+'?view=detail'
            common.addDirectory(name, 'nbc', mode, url)
    common.setView('seasons')

def showsubFullEpisode(url = common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    titledata=tree.find('h3',attrs={'class' : 'scet-browse-heading'}).string.split(':')
    showname = titledata[0].strip()
    try:season = int(titledata[1].replace('Season','').strip())
    except: season = 0
    videos=tree.find('div',attrs={'class' : 'scet-browse-group detail-full-episodes-view'}).findAll('div',attrs={'class' : 'thumb-block'})
    for video in videos:
        #print video.prettify()
        url = BASE + video.find('a')['href']
        thumb = video.find('img')['src'].replace('w=131&h=74','w=446&h=248')
        name = video.find('div',attrs={'class' : 'title'}).string.strip()
        description = video.find('p',attrs={'class' : 'description'}).find('span').string
        airDateData = video.find('div',attrs={'class' : 'air-date'}).string.split(':')[1].strip()
        airDate = time.strftime('%Y-%d-%m', time.strptime(airDateData, '%m/%d/%y') )
        year = int(time.strftime('%Y', time.strptime(airDateData, '%m/%d/%y') ))
        date = time.strftime('%d.%m.%Y', time.strptime(airDateData, '%m/%d/%y') )
        duration = video.find('div',attrs={'class' : 'runtime'}).string.split(':',1)[1].strip()
        mpaa = video.find('div',attrs={'class' : 'meta rating'}).string
        if mpaa == None:
            mpaa=''
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="nbc"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     "Season":season,
                     "MPAA":mpaa,
                     #"Episode":episode,
                     "Plot":description,
                     "date'":date,
                     "aired":airDate,
                     "year":year,
                     "Duration":duration,
                     "TVShowTitle":showname
                     }
        common.addVideo(u,name,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def showsubClips(url = common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos=tree.find('div',attrs={'class' : 'scet-browse-group detail-short-clips-view '}).findAll('div',attrs={'class' : 'thumb-block '})
    for video in videos:
        #print video.prettify()
        url = BASE + video.find('a')['href']
        thumb = video.find('img')['src'].replace('w=131&h=74','w=446&h=248')
        name = video.find('div',attrs={'class' : 'title'}).string.strip()
        showname = video.find('div',attrs={'class' : 'type'}).string.strip()
        description = video.find('p',attrs={'class' : 'description'}).find('span').string
        duration = video.find('div',attrs={'class' : 'runtime'}).string.split(':',1)[1].strip()
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="nbc"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     #"Season":season,
                     #"Episode":episode,
                     "Plot":description,
                     #"premiered":airDate,
                     "Duration":duration,
                     "TVShowTitle":showname
                     }
        common.addVideo(u,name,thumb,infoLabels=infoLabels)
    common.setView('episodes')

#Get SMIL url and play video
def play():
    vid=common.args.url.strip('/').split('/')[-1]
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
    url  = 'http://videoservices.nbcuni.com/player/clip?clear=true&domainReq=www.nbc.com&geoIP=US'
    url += '&clipId='+vid
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    url = 'http://video.nbcuni.com/' + tree.find('clipurl').string
    return url

def getrtmp():
    rtmphost = 'cp37307.edgefcs.net'
    app = 'ondemand'
    identurl = 'http://'+rtmphost+'/fcs/ident'
    ident = common.getURL(identurl)
    ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
    rtmpurl = 'rtmp://'+ip+':1935/'+app+'?_fcs_vhost='+rtmphost
    return str(rtmpurl)

def getsmilOLD(vid):
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

def getrtmpOLD():
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
    swfUrl = "http://video.nbcuni.com/core/6.6.1/OSMFPlayer.swf"
    return swfUrl
