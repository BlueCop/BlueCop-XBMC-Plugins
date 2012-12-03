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

BASE_URL = 'http://www.comedycentral.com'

def rootlist(db=False):
    data = common.getURL(BASE_URL)
    data = unicode(data, 'utf-8', errors='ignore')
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find('li',attrs={'class':'nav_item_3'}).findAll('a')
    db_shows = []
    for item in menu:
        name = item.string
        url = item['href']
        if 'http://' not in url:
            url = BASE_URL+url 
        if name <> 'Episodes':
            if name == 'South Park':
                mode = 'sp_seasons'
            elif name <> 'The Daily Show with Jon Stewart' and name <> 'The Colbert Report':
                mode = 'ccepisodes'
            else:
                mode = 'episodes'
            if db==True:
                db_shows.append((name,'comedy',mode,url))
            else:
                common.addShow(name,'comedy',mode,url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def ccepisodes(url=common.args.url):
    data = common.getURL(url)
    try:
        showcase=re.compile("var episodeShowcaseLlink = '(.+?)';").findall(data)[0]
        keepGoing=True
    except:
        keepGoing=False
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="comedy"'
        u += '&sitemode="playurl"'
        common.addVideo(u,"Play Episode")
    current=1
    while keepGoing:
        showcase_url = BASE_URL+showcase+'?currentPage='+str(current)
        data = common.getURL(showcase_url)
        videos=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES).findAll('div',attrs={'itemtype':'http://schema.org/TVEpisode'})
        for video in videos:
            infoLabels={}
            url=video.find('meta',attrs={'itemprop':'url'})['content']
            thumb=video.find('meta',attrs={'itemprop':'image'})['content']
            infoLabels['Title']=video.find('meta',attrs={'itemprop':'name'})['content']
            infoLabels['Plot']=video.find('meta',attrs={'itemprop':'description'})['content']
            infoLabels['premiered']=common.formatDate(video.find('meta',attrs={'itemprop':'datePublished'})['content'],'%b %d, %Y')
            seasonEpisode = video.find('div',attrs={'class':'video_meta'}).string.split('|')[0].split('-')
            infoLabels['Season'] = int(seasonEpisode[0].replace('Season','').strip())
            if 'Special' not in seasonEpisode[1]:
                episode = seasonEpisode[1].replace('Episode','').strip()
                if len(episode) > 2:
                    episode = episode[-2:]
                infoLabels['Episode'] = int(episode)
            else:
                infoLabels['Episode'] = 0
            if infoLabels['Season'] <> 0 or infoLabels['Episode'] <> 0:
                displayname = '%sx%s - %s' % (infoLabels['Season'],str(infoLabels['Episode']),infoLabels['Title'])
            else:
                displayname = infoLabels['Title']
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="comedy"'
            u += '&sitemode="playurl"'
            common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
        if len(videos) < 5:
            keepGoing=False
        current+=1
    common.setView('episodes')
                
def episodes(url=common.args.url):
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
                airDate = common.formatDate(airDate,'%m/%d/%y')
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
                u += '&sitemode="playurl"'
                infoLabels={ "Title":name,
                             "Season":season,
                             "Episode":episode,
                             "Plot":description,
                             "premiered":airDate,
                             #"Duration":duration,
                             "TVShowTitle":common.args.name
                             }
                common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
        else:
            eurl = item['id']
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
                airDate = common.formatDate(airDate,'%m/%d/%y')
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
                u += '&sitemode="playurl"'
                infoLabels={ "Title":name,
                             "Season":season,
                             "Episode":episode,
                             "Plot":description,
                             "premiered":airDate,
                             #"Duration":duration,
                             "TVShowTitle":common.args.name
                             }
                common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def sp_seasons(url=common.args.url):
    for sn in range(1,17):
        sn = str(sn)
        name = 'Season '+sn
        url = sn
        common.addDirectory(name,'comedy','sp_episodes',url)
    common.setView('seasons')

def sp_episodes():
    import demjson
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)
    url = 'http://www.southparkstudios.com/feeds/full-episode/carousel/'+common.args.url+'/dc400305-d548-4c30-8f05-0f27dc7e0d5c'
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
        infoLabels={ "Title": title,
                    "Season":season,
                    "Episode":episode,
                    "premiered":date,
                    "Plot":description,
                    "TVShowTitle":"South Park"
                    }
        common.addVideo(u,title,thumbnail,infoLabels=infoLabels)
    common.setView('episodes')

def sp_play():
    uri =  'mgid:cms:content:southparkstudios.com:'+common.args.url
    playuri(uri,referer='http://www.southparkstudios.com/full-episodes')

def playuri(uri = common.args.url,referer='http://www.comedycentral.com'):
    mp4_url = "http://mtvnmobile.vo.llnwd.net/kip0/_pxn=0+_pxK=18639+_pxE=/44620/mtvnorigin"
    mtvn = 'http://media.mtvnservices.com/'+uri 
    swfUrl = common.getRedirect(mtvn,referer=referer)
    configurl = urllib.unquote_plus(swfUrl.split('CONFIG_URL=')[1].split('&')[0]).strip()
    configxml = common.getURL(configurl)
    tree=BeautifulStoneSoup(configxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    mrssurl = tree.find('feed').string.replace('{uri}',uri).replace('&amp;','&')
    mrssxml = common.getURL(mrssurl)
    tree=BeautifulStoneSoup(mrssxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    segmenturls = tree.findAll('media:content')
    stacked_url = 'stack://'
    for segment in segmenturls:
        surl = segment['url']
        videos = common.getURL(surl)
        videos = BeautifulStoneSoup(videos, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('rendition')
        hbitrate = -1
        sbitrate = int(common.settings['quality'])
        for video in videos:
            bitrate = int(video['bitrate'])
            if bitrate > hbitrate and bitrate <= sbitrate:
                hbitrate = bitrate
                rtmpdata = video.find('src').string
                if 'viacomspstrm' in rtmpdata:
                    rtmpurl = mp4_url+rtmpdata.split('viacomspstrm')[2]
                elif 'viacomccstrm' in rtmpdata:
                    rtmpurl = mp4_url+rtmpdata.split('viacomccstrm')[2]
                #app = rtmpdata.split('://')[1].split('/')[1]
                #rtmpdata = rtmpdata.split('/'+app+'/')
                #rtmp = rtmpdata[0]
                #playpath = rtmpdata[1]
                #f '.mp4' in playpath:
                #    playpath = 'mp4:'+playpath.replace('.mp4','')
                #else:
                #    playpath = playpath.replace('.flv','')
                #rtmpurl = rtmp+'/'+app+ ' playpath='+playpath + " swfurl=" + swfUrl.split('?')[0] +" pageUrl=" + referer + " swfvfy=true"
                #print rtmpurl
        stacked_url += rtmpurl.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(path=stacked_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def playurl(url = common.args.url):
    data=common.getURL(url)
    try:
        uri=re.compile('var url = "http://media.mtvnservices.com/(.+?)";').findall(data)[0]
    except:
        try:
            uri=re.compile('<param name="movie" value="http://media.mtvnservices.com/(.+?)"').findall(data)[0]
        except:
            uri=re.compile('data-mgid="(.+?)"').findall(data)[0]
    playuri(uri,referer=url)
