
import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, sys, os, time
import httplib

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import resources.lib._common as common
from pyamf import remoting

BASE_URL = 'http://www.hubworld.com/videos/episodes'
BASE = 'http://www.hubworld.com'

pluginhandle = int(sys.argv[1])

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(BASE_URL)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodes = tree.findAll(attrs={'class' : 'float-left item'})

    found = []
    for episode in episodes:
        showid = episode.find('a')['href'].split('shows/')[1].split('/videos')[0]
        if showid not in found:
            found.append(showid)
    print found

    for showid in found:
        show = shows[showids.index(showid)]
        name = show[0]
        url = show[1]
        thumb = show[2]
        if db==True:
            db_shows.append((name,'hub','episodes',BASE + url,None,thumb,None))
        else:
            common.addDirectory(name, 'hub', 'episodes', BASE + url, thumb)

    # add on a Movies category
    if db==True:
        db_shows.append(('Movies','hub','episodes','movies',None,None,None))
    else:
        common.addDirectory('Movies', 'hub', 'episodes', 'movies')

    if db==True:
        return db_shows

def episodes(url=common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    if url == '':
        return
    if url == 'movies':
        data = common.getURL('http://www.hubworld.com/videos/movies')
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        movies = tree.findAll('div',attrs={'class' : 'float-left item'})
        for movie in movies:
            movietitle = movie.find('div', attrs={'class' : 'desc'}).string.strip().encode('utf-8')
            thumb = BASE + movie.find(attrs={'class' : 'thumbnail'})['thumbnailsrc']
            description = movie.find(attrs={'class' : 'hr'}).findAll('div')[1].string.strip().encode('utf-8')
            url = BASE + movie.find('a')['href']
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="hub"'
            u += '&sitemode="play"'
            item=xbmcgui.ListItem(movietitle, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":movietitle,
                                                     "Season":0,
                                                     "Episode":0,
                                                     "Plot":description,
                                                     "premiered":'',
                                                     "Duration":'',
                                                     "TVShowTitle":''
                                                     })
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)
    else:
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        # [0] is the position of the episodes block, I really hope they don't change this
        try:
            episodes=tree.findAll(attrs={'class' : 'landing-carousel-content carousel'})[0].find('div',attrs={'class' : 'container'}).findAll('div',attrs={'class' : 'clear-after item'})
        except:
            episodes = []
        for episode in episodes:
            seasonepisode = int(episode.find(attrs={'class' : 'float-left thumbnail'})['thumbnailsrc'].split('-ep')[1].split('-')[0])
            season = 0

            airDate = ''
            description = episode.find(attrs={'class' : 'hr'}).findAll('div')[1].string.strip()
            duration = ''
            try:
                episodeTitle = episode.find(attrs={'style' : 'overflow: hidden; height: 64px;'}).string.encode('utf-8').split(':')[1].strip()
            except:
                episodeTitle = episode.find(attrs={'style' : 'overflow: hidden; height: 64px;'}).string.encode('utf-8').strip()
            name = episodeTitle
            displayname = name
            url = BASE + episode.find('a')['href']
            thumb = BASE + episode.find(attrs={'class' : 'float-left thumbnail'})['thumbnailsrc']

            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="hub"'
            u += '&sitemode="play"'
            item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":name,
                                                     "Season":season,
                                                     "Episode":seasonepisode,
                                                     "Plot":description,
                                                     "premiered":airDate,
                                                     "Duration":duration,
                                                     "TVShowTitle":common.args.name
                                                     })
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

def play():
    # get our id number here since it's not accessable from the overview page and we don't want to kill the processor
    data = common.getURL(common.args.url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    id=tree.findAll('script')[-1].string.split('brightcove_mediaId =')[1].split(';')[0].strip()

    # ok, back to buisness
    videoPlayer = int(id)

    # no idea what 'const' is supposed to do...
    const = '17e0633e86a5bc4dd47877ce3e556304d0a3e7ca'
    playerID = 802565678001
    publisherID = 90719631001
    rtmpdata = get_clip_info(const, playerID, videoPlayer, publisherID)['renditions']
    hbitrate = -1
    sbitrate = int(common.settings['quality']) * 1024
    for item in rtmpdata:
        bitrate = int(item['encodingRate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            urldata = item['defaultURL']
            # no auth required
            #auth = urldata.split('?')[1]
            urldata = urldata.split('&')
            rtmp = urldata[0]
            playpath = urldata[1]
    swfUrl = 'http://admin.brightcove.com/viewer/us1.25.03.01.2011-05-12131832/federatedVideo/BrightcovePlayer.swf'
    rtmpurl = rtmp+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    item = xbmcgui.ListItem(path=rtmpurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def build_amf_request(const, playerID, videoPlayer, publisherID):
    env = remoting.Envelope(amfVersion=3)
    env.bodies.append(
        (
            "/1",
            remoting.Request(
                target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById",
                body=[const, playerID, videoPlayer, publisherID],
                envelope=env
            )
        )
    )
    return env

def get_clip_info(const, playerID, videoPlayer, publisherID):
    conn = httplib.HTTPConnection("c.brightcove.com")
    envelope = build_amf_request(const, playerID, videoPlayer, publisherID)
    conn.request("POST", "/services/messagebroker/amf?playerKey=AQ~~,AAAAFR9Ptpk~,qrsh31CHJoFjltWH9CfvxE3UxqGVBf9B", str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    return response
