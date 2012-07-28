
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
    data = common.getURL(BASE)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows = tree.find('div',attrs={'class' : 'footer-groups-middle'}).findAll('a')
    for show in shows:
        if len(show.contents) > 1:
            name = show.contents[0]+show.contents[2]
        else:
            name = show.string
        if name:
            url = BASE+show['href']
            if name.endswith(' Videos'):
                name = name.replace(' Videos','')
                if db==True:
                    db_shows.append((name,'hub','videos',url))
                else:
                    common.addShow(name, 'hub', 'videos',url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def videos(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('section',attrs={'class' : re.compile('content-item.+?')})
    for video in videos:
        infoLabels={}
        url   = BASE+video.find('a')['href']
        thumb = BASE+video.find('img')['src']
        infoLabels['Title'] = video.find('b',attrs={'class':'content-item-subtitle'}).string
        infoLabels['TVShowTitle'] = str(video.find('b',attrs={'class':'content-item-brand'}).string)
        infoLabels['Plot'] = str(video.find('span',attrs={'class':'content-item-short-description'}).string) 
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="hub"'
        u += '&sitemode="play"'
        common.addVideo(u,infoLabels['Title'],thumb,infoLabels=infoLabels)
    common.setView('episodes')

def play():
    # get our id number here since it's not accessable from the overview page and we don't want to kill the processor
    #data = common.getURL(common.args.url)
    #tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #id=tree.findAll('script')[-1].string.split('brightcove_mediaId =')[1].split(';')[0].strip()
    id = common.args.url.split('/watch/')[1].split('/')[0]
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
