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

BASE_URL = 'http://www.comedycentral.com/'

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'class':'full-episodes'}).findAll('li')
    db_shows = []
    for item in menu:
        item = item.find('a')
        name = item.string
        url = item['href']
        if name == 'South Park':
            mode = 'sp_seasons'
        else:
            mode = 'episodes'
        if db==True:
            db_shows.append((name,'comedy',mode,url))
        else:
            common.addDirectory(name,'comedy',mode,url)
    if db==True:
        return db_shows

def episodes(url=common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.findAll(attrs={'id':True,'class':True,'href':'#'})
    for item in menu:
        if 'http://www.colbertnation.com' in common.args.url:
            eurl='http://www.colbertnation.com'+item['id']
            data = common.getURL(eurl)
            tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES) 
            episodes=tree.findAll(attrs={'class':'module showcase_item'})
            selected = tree.find(attrs={'class':'module showcase_item selected'})
            if selected <> None:
                episodes.insert(0,selected)
            for episode in episodes:
                thumb = episode.find('img')['src'].split('?')[0]
                name = episode.find(attrs={'class':'title'}).find('a').string.encode('utf8')
                url = episode.find(attrs={'class':'title'}).find('a')['href']
                airDate = episode.find(attrs={'class':'date'}).string.replace('Aired: ','')
                try: description = episode.find(attrs={'class':'description'}).string.encode('utf8')
                except: description = ''
                seasonepisode = episode.find(attrs={'class':'number'}).string.replace('Episode ','')
                if len(seasonepisode) == 5:
                    season = int(seasonepisode[:2])
                    episode = int(seasonepisode[-3:])
                elif len(seasonepisode) == 4:
                    season = int(seasonepisode[:2])
                    episode = int(seasonepisode[-2:])
                elif len(seasonepisode) == 3:
                    season = int(seasonepisode[:1])
                    episode = int(seasonepisode[-2:])
                else:
                    season = 0
                    episode = 0
                if season <> 0 or episode <> 0:
                    displayname = '%sx%s - %s' % (str(season),str(episode),name)
                else:
                    displayname = name
                u = sys.argv[0]
                u += '?url="'+urllib.quote_plus(url)+'"'
                u += '&mode="comedy"'
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
        else:
            eurl = item['id'].replace('www.comedycentral.com','www.thedailyshow.com')
            data = common.getURL(eurl)
            tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES) 
            episodes=tree.findAll(attrs={'class':'moreEpisodesContainer'})
            selected = tree.find(attrs={'class':'moreEpisodesContainer-selected'})
            if selected <> None:
                episodes.insert(0,selected)
            for episode in episodes:
                thumb = episode.find('img')['src'].split('?')[0]
                name = episode.find(attrs={'class':'moreEpisodesTitle'}).find('a').string.encode('utf8')
                url = episode.find(attrs={'class':'moreEpisodesTitle'}).find('a')['href']
                airDate = episode.find(attrs={'class':'moreEpisodesAirDate'}).find(attrs={'class':'date'}).string.replace('Aired: ','')
                try: description = episode.find(attrs={'class':'description'}).string.encode('utf8')
                except: description = ''
                seasonepisode = episode.find(attrs={'class':'moreEpisodesNumber'}).find(attrs={'class':'id'}).string.replace('Episode ','')
                if len(seasonepisode) == 5:
                    season = int(seasonepisode[:2])
                    episode = int(seasonepisode[-3:])
                elif len(seasonepisode) == 4:
                    season = int(seasonepisode[:2])
                    episode = int(seasonepisode[-2:])
                elif len(seasonepisode) == 3:
                    season = int(seasonepisode[:1])
                    episode = int(seasonepisode[-2:])
                else:
                    season = 0
                    episode = 0
                if season <> 0 or episode <> 0:
                    displayname = '%sx%s - %s' % (str(season),str(episode),name)
                else:
                    displayname = name
                u = sys.argv[0]
                u += '?url="'+urllib.quote_plus(url)+'"'
                u += '&mode="comedy"'
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

def sp_seasons(url=common.args.url):
    xbmcplugin.setContent(pluginhandle, 'seasons')
    for sn in range(1,16):
        sn = str(sn)
        name = 'Season '+sn
        url = sn
        common.addDirectory(name,'comedy','sp_episodes',url)

def sp_episodes():
    import demjson
    xbmcplugin.setContent(pluginhandle, 'episodes')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)
    url = 'http://www.southparkstudios.com/feeds/full-episode/carousel/'+common.args.url+'/342853'
    json = common.getURL(url)
    episodes = demjson.decode(json)['season']['episode']
    for episode in episodes:
        title = episode['title']
        description = episode['description'].encode('ascii', 'ignore')
        thumbnail = episode['thumbnail'].replace('width=55','')
        episodeid = episode['id']
        senumber = episode['episodenumber']
        date = episode['airdate'].replace('.','-')
        seasonnumber = senumber[:-2]
        episodenumber = senumber[len(seasonnumber):]
        try:
            season = int(seasonnumber)
            episode = int(episodenumber)
        except:
            season = 0
            episode = 0
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(episodeid)+'"'
        u += '&mode="comedy"'
        u += '&sitemode="sp_play"'
        liz=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": title,
                                                "Season":season,
                                                "Episode":episode,
                                                "premiered":date,
                                                "Plot":description,
                                                "TVShowTitle":"South Park"
                                                })
        liz.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)

def sp_play():
    url =  'http://www.southparkstudios.com/feeds/video-player/mrss/mgid%3Acms%3Acontent%3Asouthparkstudios.com%3A'+common.args.url
    play(url)
        

def play(rssurl=False):
    if rssurl == False:
        data = common.getURL(common.args.url)
        uri=re.compile('<param name="movie" value="http://media.mtvnservices.com/(.+?)"').findall(data)[0]
        rssurl = 'http://shadow.comedycentral.com/feeds/video_player/mrss/?uri='+uri        
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
    swfurl = "http://media.mtvnservices.com/player/prime/mediaplayerprime.1.9.2.swf"
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
