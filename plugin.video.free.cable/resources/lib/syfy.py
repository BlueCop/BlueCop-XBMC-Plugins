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

BASE_URL = 'http://www.syfy.com/rewind/'
BASE = 'http://www.syfy.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    data = re.compile('<!-- show listing -->(.*?)<!-- end show listing -->',re.DOTALL).findall(data)[0]
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    categories=tree.find(attrs={'id' : 'show_boxes'}).findAll('div',recursive=False)
    db_shows = []
    for item in categories:
        name = item.string
        url = BASE_URL + item.find('a')['href']
        name = item.find('a').find('img')['alt']
        thumb = BASE_URL + item.find('a').find('img')['src']
        if db==True:
            db_shows.append((name,'syfy','episodes',url))
        else:
            common.addDirectory(name, 'syfy', 'episodes', url, thumb)
    if db==True:
        return db_shows

def episodes(url = common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    data = common.getURL(url)
    data = re.compile('<div id="show_video_container">(.*?)<div class="dropshadow_bottom">',re.DOTALL).findall(data)[0]
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodes=tree.find(attrs={'id' : 'video_list'}).findAll('a')
    for episode in episodes:
        url = episode['id']
        thumb = episode.find('img')['src']
        namedata = episode.find(attrs={'class' : 'title'})
        name = namedata.contents[1].strip()
        try:
            seasonepisode = namedata.contents[0].split('Episode ')[1].split('<')[0].strip()
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
            displayname = name
            season = 0
            episode = 0
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="syfy"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 "Season":season,
                                                 "Episode":episode,
                                                 #"Plot":description,
                                                 #"premiered":airDate,
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
            referer='http://video.nbcuni.com/outlet/extensions/inext_video_player/video_player_extension.swf',
            user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
        )
    ClipAll_service = gw.getService('getClipInfo.getClipAll')
    geo  ="US"
    num1 = "www.syfy.com"
    num2 = "-1"
    response = ClipAll_service(vid,geo,num1,num2)
    url = 'http://video.nbcuni.com/' + response['clipurl']
    return url


def getrtmp():
    gw = RemotingService(url='http://video.nbcuni.com/amfphp/gateway.php',
            referer='http://video.nbcuni.com/outlet/extensions/inext_video_player/video_player_extension.swf',
            user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
        )
    ClipAll_service = gw.getService('getConfigInfo.getConfigAll')
    num1 = "19102"
    response = ClipAll_service(num1)
    rtmphost= response['akamaiHostName']
    app = response['akamaiAppName']
    identurl = 'http://'+rtmphost+'/fcs/ident'
    ident = common.getURL(identurl)
    ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
    rtmpurl = 'rtmpe://'+ip+':1935/'+app+'?_fcs_vhost='+rtmphost
    return str(rtmpurl)

def getswfUrl():
    swfUrl = "http://video.nbcuni.com/outlet/extensions/inext_video_player/video_player_extension.swf?4.7"
    return swfUrl
