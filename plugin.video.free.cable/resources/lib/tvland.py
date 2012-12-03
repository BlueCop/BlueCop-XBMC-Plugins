
import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, sys, os, time
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import resources.lib._common as common

BASE = 'http://www.tvland.com/full-episodes'
pluginhandle = int(sys.argv[1])

def masterlist():
    return rootlist(db=True)
        
def rootlist(db=False):
    data = common.getURL(BASE)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    categories=tree.find('div',attrs={'class' : 'showsList'}).findAll('a')
    db_shows = []
    for show in categories:
        url = show['href']
        name = show.contents[0].strip()
        #if name == 'Hot in Cleveland':
        #    mode = 'hic_episodes'
        #else:
        mode = 'episodes'
        if db==True:
            db_shows.append((name,'tvland',mode,url))
        else:
            common.addShow(name, 'tvland', mode, url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def episodes(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodes=tree.findAll(attrs={'class' : 'episodeContainer'})
    for episode in episodes:
        seasonepisode = episode.find(attrs={'class' : 'episodeIdentifier'}).string.split('#')[1]
        airDate = episode.find(attrs={'class' : 'episodeAirDate'}).contents[1].strip()
        description = episode.find(attrs={'class' : 'episodeDescription'}).contents[0].strip()
        try:
            duration = episode.find(attrs={'class' : 'episodeDuration'}).string.replace(')','').replace('(','')
        except:
            duration = ''
        episodeTitle = episode.find(attrs={'class' : 'episodeTitle'}).find('a')
        name = episodeTitle.string
        url = episodeTitle['href']
        thumb = episode.find(attrs={'class' : 'episodeImage'}).find('img')['src'].split('?')[0]
        try:
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
        u += '&mode="tvland"'
        u += '&sitemode="playurl"'
        infoLabels={ "Title":name,
                     "Season":season,
                     "Episode":episode,
                     "Plot":description,
                     "premiered":airDate,
                     "Duration":duration,
                     "TVShowTitle":common.args.name
                     }
        common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def hic_episodes():
    epoch = str(int(time.mktime(time.gmtime())*1000))
    s1url = 'http://www.tvland.com/fragments/search_results/related_episodes_seasons?_='+epoch+'&showId=25573&seasonId=41909&episodeId=43520'
    s2url = 'http://www.tvland.com/fragments/search_results/related_episodes_seasons?_='+epoch+'&showId=25573&seasonId=27283&episodeId=43520'
    s3url = 'http://www.tvland.com/fragments/search_results/related_episodes_seasons?_='+epoch+'&showId=25573&seasonId=44996&episodeId=46849'
    #episodes(s1url)
    episodes(s2url)
    episodes(s3url)
    common.setView('episodes')
    
def playuri(uri = common.args.url,referer='http://www.tvland.com'):
    mp4_url = "http://mtvnmobile.vo.llnwd.net/kip0/_pxn=0+_pxK=18639+_pxE=/44620/mtvnorigin"
    mtvn = 'http://media.mtvnservices.com/'+uri 
    swfUrl = common.getRedirect(mtvn,referer=referer)
    configurl = urllib.unquote_plus(swfUrl.split('CONFIG_URL=')[1].split('&')[0])
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
                rtmpurl = mp4_url+rtmpdata.split('e20')[1]
                #app = rtmpdata.split('://')[1].split('/')[1]
                #rtmpdata = rtmpdata.split(app)
                #rtmp = rtmpdata[0]
                #playpath = rtmpdata[1]
                #if '.mp4' in playpath:
                #    playpath = 'mp4:'+playpath.replace('.mp4','')
                #else:
                #    playpath = playpath.replace('.flv','')
                #rtmpurl = rtmp + app +" playpath=" + playpath + " swfurl=" + swfUrl + " swfvfy=true"
        stacked_url += rtmpurl.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(path=stacked_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def playurl(url = common.args.url):
    data=common.getURL(url)
    #tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #uri = tree.find('param',attrs={'name':'movie'})['value'].split('://')[1].split('/')[1]
    uri = re.compile('"http://media.mtvnservices.com/(.*?)",').findall(data)[0]
    playuri(uri,referer=url)


