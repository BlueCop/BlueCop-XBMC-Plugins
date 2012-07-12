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
BASE_URL = 'http://abcfamily.go.com/watch'
BASE = 'http://abcfamily.go.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'class':'networkGroup'}).findAll('div',recursive=False)
    db_shows = []
    for item in menu:
        link = item.find('a')
        name = link['title']
        url = link['page']
        description = link['desc']
        thumb = item.find('img')['src']
        if db==True:
            db_shows.append((name,'abcfamily','showcats',url))
        else:
            common.addShow(name, 'abcfamily', 'showcats', url) #, thumb, thumb, description)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def showcats(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    cats=tree.findAll(attrs={'class' : re.compile('(.+?)videoCollectionModule moduleWide ')})
    for cat in cats:
        name = cat.find('div',attrs={'class' : 'twocolumnheader'}).find('h3').string.title()
        common.addDirectory(name, 'abcfamily', 'videos', url) 
    common.setView('seasons')

def videos(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    cats=tree.findAll(attrs={'class' : re.compile('(.+?)videoCollectionModule moduleWide ')})
    for cat in cats:
        catname = cat.find('div',attrs={'class' : 'twocolumnheader'}).find('h3').string.title()
        if catname == common.args.name:
            episodes = cat.findAll(attrs={'class' : 'fullgallery'})
            if len(episodes) > 0:
                for video in episodes:
                    url = video.find('a')['href']
                    thumb = video.find('img')['src']
                    name = video.find('img')['alt']
                    description = video.contents[8].strip() 
                    seasonepisode = video.contents[6].strip().split('|')
                    season = int(seasonepisode[0].replace('Season','').strip())
                    episode = int(seasonepisode[1].replace('Episode','').strip())
                    displayname = '%sx%s - %s' % (str(season),str(episode),name)
                    u = sys.argv[0]
                    u += '?url="'+urllib.quote_plus(url)+'"'
                    u += '&mode="abcfamily"'
                    u += '&sitemode="play"'
                    infoLabels={ "Title":name,
                                 "Season":season,
                                 "Episode":episode,
                                 "Plot":description
                                 #"premiered":airDate,
                                 #"Duration":duration,
                                 #"TVShowTitle":tvshow
                                 }
                    common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
            else:
                videos = cat.findAll(attrs={'class' : 'shortgallery'})
                for video in videos:
                    url = BASE + video.find('a')['href']
                    try:
                        thumb = video.find('img')['src']
                    except:
                        try:
                            thumb = video.find('image')['src']
                        except:
                            print 'no thumb'
                            thumb = ''
                    name = video.find(attrs={'class' : 'shortvideoTitle'}).find('a').string
                    if name == None:
                        name = video.find(attrs={'class' : 'shortvideoTitle'}).find('abbr')['title']
                    description = video.find(attrs={'class' : 'shortvideoDesc'}).string.strip()
                    try:
                        seasonepisode = video.find(attrs={'class' : 'videoSeasonInfo'}).string.strip().split('|')
                        season = int(seasonepisode[0].replace('Season','').strip())
                        episode = int(seasonepisode[1].replace('Episode','').strip())
                        displayname = '%sx%s - %s' % (str(season),str(episode),name)
                    except:
                        season = 0
                        episode = 0
                        displayname = name
                    u = sys.argv[0]
                    u += '?url="'+urllib.quote_plus(url)+'"'
                    u += '&mode="abcfamily"'
                    u += '&sitemode="play"'
                    infoLabels={ "Title":name,
                                 "Season":season,
                                 "Episode":episode,
                                 "Plot":description
                                 #"premiered":airDate,
                                 #"Duration":duration,
                                 #"TVShowTitle":tvshow
                                 }
                    common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def play(url=common.args.url):
    vid= re.compile('(VD\d*)').findall(url)[0]
    rtmpdata = 'http://cdn.abc.go.com/vp2/ws/s/contents/2002/utils/video/mov/17496/9024/%s/432?v=05040017_1' % vid
    data = common.getURL(rtmpdata)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    hosts = tree.findAll('host')
    for host in hosts:
        if 'Akamai' in host['name']:
            rtmp = 'rtmpe://%s/%s' % (host['url'], host['app'])
    filenames = tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality'])
    for filename in filenames:
        if filename['src'] <> '':
            bitrate = int(filename['bitrate'])
            if bitrate > hbitrate and bitrate <= sbitrate:
                hbitrate = bitrate
                playpath = filename['src']
                
    swfUrl = 'http://ll.static.abc.com/m/vp2/prod/flash/VP2_05040017_0_1254.swf'
    rtmpurl = rtmp+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    item = xbmcgui.ListItem(path=rtmpurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
