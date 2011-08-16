import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re
import httplib

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import resources.lib._common as common
from pyamf import remoting

pluginhandle = int(sys.argv[1])

BASEURL = 'http://www.aetv.com/videos/display.jsp'
BASE = 'http://www.aetv.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASEURL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'av-list1','class':'all-videos_unordered'}).findAll('a')
    db_shows = []
    for item in menu:
        name = item.string.encode('utf-8')
        url = item['href']
        if 'http://' not in item['href']:
            url = BASE + url
        if db==True:
            db_shows.append((name,'aetv','episodes',url))
        else:
            common.addDirectory(name, 'aetv', 'episodes', url)
    if db==True:
        db_shows.append(('Breakout Kings','aetv','episodes','http://www.aetv.com/breakout-kings/video/'))
    else:
        common.addDirectory('Breakout Kings', 'aetv', 'episodes', 'http://www.aetv.com/breakout-kings/video/')
    if db==True:
        return db_shows

def episodes(url=common.args.url):
    data = common.getURL(url)
    playerID = int(re.compile('bcpid=(.+?)&bclid').findall(data)[0])
    configurl = BASE + re.compile('baseURL=(.+?)&baseDIR').findall(data)[0] + '/categories.xml'
    id_data = common.getURL(configurl)
    categories=BeautifulStoneSoup(id_data, convertEntities=BeautifulStoneSoup.XML_ENTITIES).findAll('category')
    for category in categories:
        try: name = category.find('title').contents[1].strip()
        except: name = category.find('title').contents[0].strip()
        refids = category.findAll('refid')
        showstring=''
        for refid in refids:
            showstring += refid.string+'<strings>'
        common.addDirectory(name, 'aetv', 'showsub', str(playerID)+'<split>'+showstring)

def showsub():
    urldata=common.args.url.split('<split>')
    playerID = int(urldata[0])
    showstrings = urldata[1].split('<strings>')
    for showstring in showstrings:
        if showstring <> '':
            addvideos(playerID, showstring)
    
def addvideos(playerID, showstring):    
    const = '1ce592dc1e35e815f66ae86d01057451c807a9cb'
    try:
        for item in get_clip_info(const, playerID, showstring)['videoDTOs']:
            name = item['displayName'].encode('utf-8')
            thumb = item['videoStillURL']
            airDate = str(item['publishedDate']).encode('utf-8')
            description = item['shortDescription'].encode('utf-8')
            try: season = int(item['customFields']['seasonnumber'])
            except: season = 0
            try: episode = int(item['customFields']['episodenumber'])
            except: episode = 0
            try: showtitle = item['customFields']['seriesname']
            except: showtitle = common.args.name
            if season <> 0 or episode <> 0:
                displayname = '%sx%s - %s' % (str(season),str(episode),name)
            else:
                displayname = name
            if len(item['renditions']) <> 0:
                url = choosertmp(item['renditions'])
            else:
                url = processrtmp(item['FLVFullLengthURL'])
            item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":name,
                                                     "Season":season,
                                                     "Episode":episode,
                                                     "Plot":description,
                                                     "premiered":airDate,
                                                     #"Duration":duration,
                                                     "TVShowTitle":showtitle
                                                     })
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle,url=url,listitem=item,isFolder=False)
    except:
        print 'Vidoe loading failure'

def choosertmp(renditions):
    hbitrate = -1
    sbitrate = int(common.settings['quality']) * 1024
    for item in renditions:
        bitrate = int(item['encodingRate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            url = item['defaultURL']
    return processrtmp(url)

def processrtmp(urldata):
    auth = urldata.split('?')[1]
    urldata = urldata.split('&')
    rtmp = urldata[0]+'?'+auth
    playpath = urldata[1].split('?')[0]+'?'+auth
    swfUrl = 'http://admin.brightcove.com/viewer/us1.25.03.01.2011-05-12131832/federatedVideo/BrightcovePlayer.swf'
    rtmpurl = rtmp+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    return rtmpurl

def build_amf_request(const, playerID, showstring):
    env = remoting.Envelope(amfVersion=3)
    env.bodies.append(
        (
            "/1", 
            remoting.Request(
                target="com.brightcove.player.runtime.PlayerMediaFacade.findPagingMediaCollectionByReferenceId", 
                body=[const, playerID, showstring, 0, 50, 1119255093],
                envelope=env
            )
        )
    )
    return env

def get_clip_info(const, playerID, showstring):
    conn = httplib.HTTPConnection("c.brightcove.com")
    envelope = build_amf_request(const, playerID, showstring)
    conn.request("POST", "/services/messagebroker/amf?playerId="+str(playerID), str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    return response  
