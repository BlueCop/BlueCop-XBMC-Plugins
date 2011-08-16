
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
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)

    showids = [
        'atomic-betty',
        'batman-beyond',
        'batman',
        'conan-the-adventurer',
        'cosmic-quantum-ray',
        'dan-vs',
        'deltora-quest',
        'dennis-and-gnasher',
        'endurance',
        'family-game-night',
        'fraggle-rock',
        'a-real-american-hero',
        'renegades',
        'grossology',
        'hubworld-show',
        'jem-and-the-holograms',
        'kenny-the-shark',
        'meerkat-manor',
        'men-in-black-the-series',
        'friendship-is-magic',
        'pictureka',
        'pound-puppies',
        'the-haunting-hour',
        'at-blake-holsey-high',
        'berry-bitty-adventures',
        'journey-to-fearless',
        'twisted-whiskers-show',
        'prime',
        'energon',
        'generation-1',
        'truth-or-scare',
        'tutenstein',
        'where-on-earth-is-carmen-sandiego'
    ]
    # title, url, thumb
    shows = [
        ['Atomic Betty','/atomic-betty/shows/atomic-betty','http://www.hubworld.com/hubworld/img/shows/atomic-betty/abett-show-thumb-112x82.jpg'],
        ['Batman Beyond','/batman-beyond/shows/batman-beyond','http://www.hubworld.com/hubworld/img/shows/batman-beyond/gallery/batman-gallery1-thumb-112x82.jpg'],
        ['Batman','/batman/shows/batman','http://www.hubworld.com/hubworld/img/shows/batman-adam-west/gallery/BAW_Gallery_112x82_08.jpg'],
        ['Conan the Adventurer','/conan-the-adventurer/shows/conan-the-adventurer','http://www.hubworld.com/hubworld/img/shows/conan-the-adventurer/conan-sm-thumb-112x82.jpg'],
        ['Cosmic Quantum Ray','/cosmic-quantum-ray/shows/cosmic-quantum-ray','http://www.hubworld.com/hubworld/img/shows/cosmic-quantum-ray/cqr-show-thumb-112x82.jpg'],
        ['Dan Vs.','/dan-vs/shows/dan-vs','http://www.hubworld.com/hubworld/img/shows/danvs/danv-show-thumb-112x82.jpg'],
        ['Deltora Quest','/deltora-quest/shows/deltora-quest','http://www.hubworld.com/hubworld/img/shows/deltora-quest/dquest-show-thumb-112x82.jpg'],
        ['Dennis and Gnasher','/dennis-and-gnasher/shows/dennis-and-gnasher','http://www.hubworld.com/hubworld/img/shows/dennis-gnasher/dgnas-show-thumb-112x82.jpg'],
        ['Endurance','/endurance/shows/endurance','http://www.hubworld.com/hubworld/img/shows/endurance/gallery/En_112x82_01.jpg'],
        ['Family Game Night','/family-game-night/shows/family-game-night','http://www.hubworld.com/hubworld/img/shows/family-game-night/fgn-show-thumb-112x82.jpg'],
        ['Fraggle Rock','/fraggle-rock/shows/fraggle-rock','http://www.hubworld.com/hubworld/img/shows/fraggle-rock/frock-show-thumb-112x82.jpg'],
        ['G.I. Joe: A Real American Hero','/gi-joe/shows/a-real-american-hero','http://www.hubworld.com/hubworld/gi-joe/gi-joe-RAH_112x82_Thumb_Storm_Shadow_02.jpg'],
        ['G.I. Joe: Renegades','/gi-joe/shows/renegades','http://www.hubworld.com/hubworld/img/shows/gi-joe/giren-show-thumb-112x82.jpg'],
        ['Grossology','/grossology/shows/grossology','http://www.hubworld.com/hubworld/img/shows/grossology/gallery/Gross_Gallery_112x82_07.jpg'],
        ['Hubworld The Show','/the-hub/shows/hubworld-show','http://www.hubworld.com/hubworld/img/shows/hubworld/HW_Gallery_112x82_03.jpg'],
        ['Jem and the Holograms','/jem-and-the-holograms/shows/jem-and-the-holograms','http://www.hubworld.com/hubworld/img/shows/jem-and-the-holograms/jem-sm-thumb-112x82.jpg'],
        ['Kenny the Shark','/kenny-the-shark/shows/kenny-the-shark','http://www.hubworld.com/hubworld/img/shows/kenny-the-shark/kts-image-gallery/KTS_Gallery_112x82_15.jpg'],
        ['Meerkat Manor','/meerkat-manor/shows/meerkat-manor','http://www.hubworld.com/hubworld/img/shows/meerkat-manor/meerkt-show-thumb-112x82.jpg'],
        ['Men in Black: The Series','/men-in-black/shows/men-in-black-the-series','http://www.hubworld.com/hubworld/img/shows/men-in-black/gallery/mib-gallery7-thumb-112x82.jpg'],
        ['My Little Pony: Friendship is Magic','/my-little-pony/shows/friendship-is-magic','http://www.hubworld.com/hubworld/img/shows/my-little-pony/mlp-show-thumb-112x82.jpg'],
        ['Pictureka!','/pictureka/shows/pictureka','http://www.hubworld.com/hubworld/img/shows/pictureka/pict-show-thumb-112x82.jpg'],
        ['Pound Puppies','/pound-puppies/shows/pound-puppies','http://www.hubworld.com/hubworld/img/shows/poundpuppies/ppup-show-thumb-112x82.jpg'],
        ['R.L. Stine\'s The Haunting Hour','/rl-stine/shows/the-haunting-hour','http://www.hubworld.com/hubworld/img/thumbnail/rstine-video-sneakpeek-thumb-112x82.jpg'],
        ['Strange Days at Blake Holsey High','/strange-days/shows/at-blake-holsey-high','http://www.hubworld.com/hubworld/img/shows/strange-days/sbh-show-thumb-112x82.jpg'],
        ['Strawberry Shortcake\'s Berry Bitty Adventures','/strawberry-shortcakes/shows/berry-bitty-adventures','http://www.hubworld.com/hubworld/img/shows/strawberry-shortcake/ssbba-show-thumb-112x82.jpg'],
        ['Taylor Swift Journey to Fearless','/taylor-swift/shows/journey-to-fearless','http://www.hubworld.com/hubworld/img/thumbnail/tswift-video-promo-thumb-112x82.jpg'],
        ['The Twisted Whiskers Show','/twisted-whiskers/shows/twisted-whiskers-show','http://www.hubworld.com/hubworld/img/shows/twisted-whiskers/twhisk-show-thumb-112x82.jpg'],
        ['Transformers Prime','/transformers/shows/prime','http://www.hubworld.com/hubworld/img/shows/transformers-prime/tprime-show-thumb-112x82.jpg'],
        ['Transformers: Energon', '', ''],
        ['Transformers: Generation 1','/transformers/shows/generation-1','http://www.hubworld.com/hubworld/images/transformers/generation1/show-page/TSG1-112x82-Thumb-Bumblebee_01.jpg'],
        ['Truth or Scare','/truth-or-scare/shows/truth-or-scare','http://www.hubworld.com/hubworld/img/shows/truth-or-scare/tos-show-thumb-112x82.jpg'],
        ['Tutenstein','/tutenstein/shows/tutenstein','http://www.hubworld.com/hubworld/img/shows/tutenstein/gallery/Tutenstein_Gallery_112x82_01.jpg'],
        ['Where on Earth is Carmen Sandiego?','/where-on-earth-is-carmen-sandiego/shows/where-on-earth-is-carmen-sandiego','http://www.hubworld.com/hubworld/img/shows/where-on-earth-is-carmen-sandiego/Gallery/Carmen_Gallery_112x82_01.jpg']
    ]

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
