import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
import resources.lib._common as common

pluginhandle = int (sys.argv[1])

BASE_URL = "http://www.cbs.com/video/"
BASE = "http://www.cbs.com"

def masterlist():
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id' : 'videoContent'})
    categories=menu.findAll('div', attrs={'id' : True}, recursive=False)
    for item in categories:
        shows = item.findAll(attrs={'id' : 'show_block_interior'})
        for show in shows:
            name = show.find('img')['alt'].encode('utf-8')
            thumbnail = BASE_URL + show.find('img')['src']
            url = BASE + show.find('a')['href']
            common.addDirectory(name, 'cbs', 'showcats', url, thumb=thumbnail)
    
def play():
    pid = common.args.url
    url = "http://release.theplatform.com/content.select?format=SMIL&Tracking=true&balance=true&MBR=true&pid=" + pid
    data=common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('video',attrs={'profile': True})
    rtmps=[]
    https=[]
    for item in videos:
        url = item['src']
        if 'rtmp' in url:
            rtmps.append(item)
        elif 'http' in url:
            https.append(item)
    hbitrate = -1
    for item in rtmps:
        print item['profile']
        bitrate = int(item['system-bitrate'])
        if bitrate > hbitrate:
            hbitrate = bitrate
            url = item['src'].split('<break>')
            rtmp = url[0]
            playpath = url[1]
            if ".mp4" in playpath:
                    playpath = 'mp4:' + playpath
            else:
                    playpath = playpath.replace('.flv','')
            swfUrl = "http://www.cbs.com/thunder/player/1_0/chromeless/1_5_1/CAN.swf"
            finalurl = rtmp+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    '''
    for item in https:
        print item['profile']
        bitrate = int(item['system-bitrate'])
        if bitrate > hbitrate:
            hbitrate = bitrate
            finalurl = item['src']
    '''
    item = xbmcgui.ListItem(path=finalurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def rootlist():
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id' : 'daypart_nav'})
    categories=menu.findAll('a')
    for item in categories:
        catid = item['onclick'].replace("showDaypart('",'').replace("');",'')
        name = catid.title()
        common.addDirectory(name, 'cbs', 'shows', catid)

def shows(catid = common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id' : 'videoContent'})
    categories=menu.findAll('div', attrs={'id' : True}, recursive=False)
    for item in categories:
        if item['id'] == catid:
            shows = item.findAll(attrs={'id' : 'show_block_interior'})
            for show in shows:
                name = show.find('img')['alt'].encode('utf-8')
                thumbnail = BASE_URL + show.find('img')['src']
                url = BASE + show.find('a')['href']
                common.addDirectory(name, 'cbs', 'showcats', url, thumb=thumbnail)
            break
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)

def showcats(url = common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:
        options = tree.find(attrs={'id' : 'secondary-show-nav-wrapper'})
        options = options.findAll('a')
        for option in options:
            name = option.string.encode('utf-8')
            url = BASE + option['href']
            common.addDirectory(name, 'cbs', 'videos', url)
    except:
        print 'CBS: secondary-show-nav-wrapper failed'
        print 'CBS: trying vid_module'
        try:
            options = tree.findAll(attrs={'class' : 'vid_module'})
            for option in options:
                moduleid = option['id']
                name = option.find(attrs={'class' : 'hdr'}).string
                common.addDirectory(name, 'cbs', 'showsubcats', url+'<moduleid>'+moduleid)                                        
        except:
            print 'CBS: vid_module failed'

def showsubcats(url = common.args.url):
    moduleid = url.split('<moduleid>')[1]
    url      = url.split('<moduleid>')[0]
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    vid_module = tree.find(attrs={'id' : moduleid})
    PAGES(vid_module)

    
def videos(url = common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    print 'CBS: trying vid_module'
    try:
        options = tree.findAll(attrs={'class' : 'vid_module'})
        if len(options) == 1:
            PAGES(tree)
        else:
            for option in options:
                moduleid = option['id']
                name = option.find(attrs={'class' : 'hdr'}).string
                common.addDirectory(name, 'cbs', 'showsubcats', url+'<moduleid>'+moduleid)                                        
    except:
        PAGES(tree)
        

def PAGES( tree ):
        try:
            search_elements = tree.find(attrs={'name' : 'searchEl'})['value']
            return_elements = tree.find(attrs={'name' : 'returnEl'})['value']
        except:
            print 'CBS: search and return elements failed'
        try:
            last_page = tree.find(attrs={'id' : 'pagination0'}).findAll(attrs={'class' : 'vids_pag_off'})[-1].string
            last_page = int(last_page) + 1
        except:
            print 'CBS: last page failed reverting to default'
            last_page = 2
        for pageNum in range(1,last_page):
            values = {'pg' : str(pageNum),
                      'repub' : 'yes',
                      'displayType' : 'twoby',
                      'search_elements' : search_elements,
                      'return_elements' : return_elements,
                      'carouselId' : '0',
                      'vs' : 'Default',
                      'play' : 'true'
                      }
            url = 'http://www.cbs.com/sitecommon/includes/video/2009_carousel_data_multiple.php' 
            data = common.getURL(url, values)
            VIDEOLINKS(data)

def VIDEOLINKS( data ):
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    vidfeed=tree.find(attrs={'class' : 'vids_feed'})
    videos = vidfeed.findAll(attrs={'class' : 'floatLeft','style' : True})
    for video in videos:
        thumb = video.find('img')['src']
        vidtitle = video.find(attrs={'class' : 'vidtitle'})
        pid = vidtitle['href'].split('pid=')[1].split('&')[0]
        displayname = vidtitle.string.encode('utf-8')
        try:
            title = displayname.split('-')[1].strip()
            series = displayname.split('-')[0].strip()
        except:
            print 'title/series metadata failure'
            title = displayname
            series = ''

        metadata = video.find(attrs={'class' : 'season_episode'}).renderContents()
        try:
            duration = metadata.split('(')[1].replace(')','')
        except:
            print 'duration metadata failure'
            duration = ''
        try:
            aired = metadata.split('<')[0].split(':')[1].strip()
        except:
            print 'air date metadata failure'
            aired = ''
        try:
            seasonepisode = thumb.split('/')[-1].split('_')[2]
            if 3 == len(seasonepisode):
                season = int(seasonepisode[:1])
                episode = int(seasonepisode[-2:])
            elif 4 == len(seasonepisode):
                season = int(seasonepisode[:2])
                episode = int(seasonepisode[-2:])
            if season <> 0 or episode <> 0:
                displayname = '%sx%s - %s' % (str(season),str(episode),title)
        except:
            print 'season/episode metadata failed'
            season = 0
            episode = 0
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(pid)+'"'
        u += '&mode="cbs"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":title,
                                                 "Season":season,
                                                 "Episode":episode,
                                                 "premiered":aired,
                                                 "Duration":duration,
                                                 "TVShowTitle":series
                                                 }) 
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False)


