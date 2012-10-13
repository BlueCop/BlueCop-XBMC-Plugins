import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re
import httplib
import base64
import random

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
    data = common.getURL(BASEURL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'av-list1','class':'all-videos_unordered'}).findAll('a')
    db_shows = []
    blackListShows = ["Kirstie Alley's Big Life"]
    subListShows = ['Cold Case Files',
                    'Confessions of a Matchmaker',
                    'CSI Miami',
                    'Inked',
                    'Random 1',
                    'SWAT - Dallas, Detroit, KC',
                    'Sons of Hollywood',
                    'Jacked: Auto Theft Task Force',
                    'The Two Coreys']
    newListShows = ['Airline','Extreme Paranormal','Flight 93','King of Cars']
    for name in newListShows:
        url = 'http://www.aetv.com/videos/classic/?bcpid=65056640001&bclid=1747275989'
        if db==True:
            db_shows.append((name, 'aetv', 'show_cats_filter', url))
        else:
            common.addShow(name, 'aetv', 'show_cats_filter', url)
    for item in menu:
        name = item.string.encode('utf-8')
        url = item['href']
        if 'http://' not in item['href']:
            url = BASE + url
        if 'aetv.com/longmire/' in url:
            url+='video/'
        if name in subListShows:
            mode = 'show_cats_filter'
        elif name in blackListShows:
            continue
        else:
            mode = 'show_cats'
            
        if db==True:
            db_shows.append((name, 'aetv', mode, url))
        else:
            common.addShow(name, 'aetv', mode, url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def show_cats_filter():
    if common.args.name == 'SWAT - Dallas, Detroit, KC':
        common.args.name = 'S.W.A.T.'
    elif common.args.name == 'CSI Miami':
        common.args.name = 'CSI: Miami'
    show_cats(filter=True)

def show_cats(url=common.args.url,filter=False):
    data = common.getURL(url)
    try:
        if 'bcpid=' in url:
            playerID = url.split('bcpid=')[1].split('&')[0]
        else:
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
            if filter and common.args.name == name:
                showsub(str(playerID)+'<split>'+showstring)
                break
            elif not filter:
                common.addDirectory(name, 'aetv', 'showsub', str(playerID)+'<split>'+showstring)
            common.setView('seasons')
    except:
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        homedir = tree.find('div',attrs={'id':'video_home_dir','style':'display : none'}).string
        #homedir = re.compile('<div id="video_home_dir" style="display : none">(.+?)</div>').findall(data)[0]
        series_url  = 'http://www.aetv.com/minisite/videoajx.jsp'
        series_url += '?homedir='+homedir
        full_series_url = series_url+'&pfilter=FULL%20EPISODES'
        clips_series_url = series_url+'&pfilter=CLIPS'
        common.addDirectory('Full Episodes', 'aetv', 'showseasonThePlatform', full_series_url)
        common.addDirectory('Clips', 'aetv', 'showseasonThePlatform', clips_series_url)
        common.setView('seasons')

def showseasonThePlatform(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    seasons = tree.findAll('div',attrs={'class':'fake-select inactive'})[1].findAll('li',attrs={'class':None})
    if len(seasons) > 0:
        for season in seasons:
            link = season.find('a')
            season_url = url+'&sfilter='+link.string.strip().replace(' ','%20')
            common.addDirectory(link.string, 'aetv', 'showsubThePlatform', season_url)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        common.setView('seasons')
    else:
        showsubThePlatform(tree=tree)
    

def showsubThePlatform(url=common.args.url,tree=False):
    if not tree:
        data = common.getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos=tree.findAll('li',attrs={'class':'selected'})
    try:season = int(tree.findAll('li',attrs={'class':'selected'})[1].find('a').string.replace('Season ',''))
    except:season = 0
    videos=tree.findAll('div',attrs={'class':'video_playlist-item'})
    for video in videos:
        infoLabels={'Season':season}
        video_details = video.find('div',attrs={'class':'video_details'})
        infoLabels['Title'] = video_details.find('p',attrs={'class':'video_details-title'}).string.encode('utf-8')
        thumb = video.find('img')['src']
        url = video.find('a')['onclick'].split(",'")[1].split("'")[0]
        infoLabels['Plot'] = video_details.find('p',attrs={'class':'video_details-synopsis'}).string.encode('utf-8')
        displayname=infoLabels['Title']
        for p in video_details.findAll('p',attrs={'class':None}):
            if p.find('span'):
                infoLabels['Duration'] = p.find('span').string
            else:
                if 'Premiere Date: ' in p.string:
                    infoLabels['premiered'] = p.string.replace('Premiere Date: ','')
                elif 'Episode: ' in p.string:
                    try:
                        infoLabels['Episode'] = int(p.string.replace('Episode: ',''))
                        if infoLabels['Season'] <> 0:
                            displayname = '%sx%s - %s' % (str(infoLabels['Season']),str(infoLabels['Episode']),infoLabels['Title'])
                        else:
                            displayname = str(infoLabels['Episode'])+' - '+infoLabels['Title']
                    except:
                        infoLabels['Episode'] = 0
                        displayname = infoLabels['Title']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="aetv"'
        u += '&sitemode="playThePlatform"'
        common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def playThePlatform():
    data = common.getURL(common.args.url)
    #mrss = urllib.unquote_plus(base64.b64decode(re.compile('{ mrss: "(.+?)",').findall(data)[0]))
    mrss = urllib.unquote_plus(base64.b64decode(re.compile('"mrss=(.+?)&').findall(data)[0]))
    smil_url = re.compile('<media:text>smilUrl=(.+?)</media:text>').findall(mrss)[0]
    signUrl  = 'http://www.history.com/components/get-signed-signature'
    signUrl += '?url='+smil_url.split('/s/')[1].split('?')[0]
    signUrl += '&cache='+str(random.randint(100, 999))
    sig = str(common.getURL(signUrl))
    smil_url += '&sig='+sig
    data = common.getURL(smil_url)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    rtmp_base = tree.find('meta')['base']
    filenames = tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality'])
    for filename in filenames:
        bitrate = int(filename['system-bitrate'])/1024
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            playpath = filename['src']
    swfUrl = 'http://www.aetv.com/js/minisite4g/VideoPlayer.swf'
    rtmpurl = rtmp_base+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    item = xbmcgui.ListItem(path=rtmpurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def showsub(url=common.args.url):
    urldata=url.split('<split>')
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
            infoLabels={ "Title":name,
                         "Season":season,
                         "Episode":episode,
                         "Plot":description,
                         "premiered":airDate,
                         #"Duration":duration,
                         "TVShowTitle":showtitle
                         }
            common.addVideo(url,displayname,thumb,infoLabels=infoLabels)
        common.setView('episodes')
    except:
        print 'Video loading failure'

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
