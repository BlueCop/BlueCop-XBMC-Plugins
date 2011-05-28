import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from pyamf.remoting.client import RemotingService
import resources.lib._common as common

pluginhandle = int (sys.argv[1])

BASE_URL = 'http://video.usanetwork.com/'
BASE = 'http://video.usanetwork.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    categories=tree.find(attrs={'id' : 'find_it_branch_Full_Episodes'}).find(attrs={'class' : 'find_it_shows'}).findAll('a')
    db_shows = []
    for item in categories:
        name = item.string
        url = item['href']
        if db==True:
            db_shows.append((name,'usa','episodes',url,None,None,None))
        else:
            common.addDirectory(name, 'usa', 'episodes', url)
    if db==True:
        return db_shows

def episodes(url = common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    data = common.getURL(url)
    rssurl = re.compile('var _rssURL = "(.+?)";').findall(data)[0].replace('%26','&')
    data = common.getURL(rssurl)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    menu=tree.findAll('item')
    for item in menu:
        namedata = item('title')[0].string.encode('utf-8').title().split(':')
        try:
            name = namedata[1].strip()
            seasonepisode = namedata[0]
            if 3 == len(seasonepisode):
                season = int(seasonepisode[:1])
                episode = int(seasonepisode[-2:])
            elif 4 == len(seasonepisode):
                season = int(seasonepisode[:2])
                episode = int(seasonepisode[-2:])
            if season <> 0 or episode <> 0:
                displayname = '%sx%s - %s' % (str(season),str(episode),name)
        except:
            print 'no season data'
            name = namedata[0].strip()
            displayname = name
            season = 0
            episode = 0
        url = item('link')[0].string
        thumb = item('media:thumbnail')[0].string
        airDate = item('pubdate')[0].string.split('T')[0]
        description = item('description')[0].string
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="usa"'
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
        
#Get SMIL url and play video
def play():
    vid=common.args.url
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
            referer='http://livepassdl.conviva.com/ver/2.27.0.43059/LivePassModuleMain.swf',
            user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
        )
    ClipAll_service = gw.getService('getClipInfo.getClipAll')
    geo  ="inside"
    num1 = "www.usanetwork.com"
    num2 = "-1"
    response = ClipAll_service(vid,geo,num1,num2)
    url = 'http://video.nbcuni.com/' + response['clipurl']
    return url


def getrtmp():
    gw = RemotingService(url='http://video.nbcuni.com/amfphp/gateway.php',
            referer='http://livepassdl.conviva.com/ver/2.27.0.43059/LivePassModuleMain.swf',
            user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
        )
    ClipAll_service = gw.getService('getConfigInfo.getConfigAll')
    num1 = "23012"
    response = ClipAll_service(num1)
    rtmphost= response['akamaiHostName']
    app = response['akamaiAppName']
    identurl = 'http://'+rtmphost+'/fcs/ident'
    ident = common.getURL(identurl)
    ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
    rtmpurl = 'rtmp://'+ip+':1935/'+app+'?_fcs_vhost='+rtmphost
    return str(rtmpurl)

def getswfUrl():
    swfUrl = "http://www.usanetwork.com/[[IMPORT]]/livepassdl.conviva.com/ver/2.27.0.43059/LivePassModuleMain.swf"
    return swfUrl
