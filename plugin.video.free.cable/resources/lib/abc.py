import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import resources.lib._common as common

pluginhandle = int(sys.argv[1])
showlist= 'http://cdn.abc.go.com/vp2/ws-supt/s/syndication/2000/rss/001/001/-1/-1/-1/-1/-1/-1'

def masterlist():
    rootlist()

def rootlist():
    data = common.getURL(showlist)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    menu=tree.findAll('item')
    for item in menu:
        name = item('title')[0].string.encode('utf-8')
        url = item('link')[0].string
        thumb = item('image')[0].string
        common.addDirectory(name, 'abc', 'showcats', url , thumb)

def showcats(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    video_rss = menu=tree.find(attrs={'type' : 'application/rss+xml'})['href']
    data = common.getURL(video_rss)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    menu=tree.findAll('item')
    for item in menu:
        namedata = item('title')[0].string.encode('utf-8').split(' Full Episode - ')
        name = namedata[0]
        season = int(namedata[1].split(' - ')[0].split(' | ')[1].replace('s',''))
        episode = int(namedata[1].split(' - ')[0].split(' | ')[0].replace('e',''))
        tvshow = namedata[1].split(' - ')[1] 
        url = item('link')[0].string
        thumb = item('image')[0].string
        airDate = item('pubdate')[0].string.split('T')[0]
        descriptiondata = re.compile('<p>(.+?)</p>').findall(item('description')[0].string)[0].split('<br>')
        description = descriptiondata[0]
        duration = descriptiondata[-2].replace('Duration: ','')
        displayname = '%sx%s - %s' % (str(season),str(episode),name)
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="abc"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 "Season":season,
                                                 "Episode":episode,
                                                 "Plot":description,
                                                 "premiered":airDate,
                                                 "Duration":duration,
                                                 "TVShowTitle":tvshow
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)
        
def play(url=common.args.url):
    vid=url.split('/')[-2]
    rtmpdata = 'http://cdn.abc.go.com/vp2/ws/s/contents/2003/utils/video/mov/13/9024/%s/432?v=06000007_3' % vid
    data = common.getURL(rtmpdata)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    hosts = tree.findAll('host')
    for host in hosts:
        if host['name'] == 'L3':
            rtmp = 'rtmp://%s/%s' % (host['url'], host['app'])
    filenames = tree.findAll('video')
    hbitrate = -1
    for filename in filenames:
        if filename['src'] <> '':
            bitrate = int(filename['bitrate'])
            if bitrate > hbitrate:
                hbitrate = bitrate
                playpath = filename['src']
                
    swfUrl = 'http://livepassdl.conviva.com/ver/2.27.0.42841/LivePassModuleMain.swf'
    rtmpurl = rtmp+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    item = xbmcgui.ListItem(path=rtmpurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
