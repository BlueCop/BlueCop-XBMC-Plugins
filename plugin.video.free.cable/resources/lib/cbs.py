import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import MinimalSoup
import resources.lib._common as common

pluginhandle = int (sys.argv[1])

BASE_URL = "http://www.cbs.com/video/"
BASE = "http://www.cbs.com"

def masterlist():
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id' : 'videoContent'})
    categories=menu.findAll('div', attrs={'id' : True}, recursive=False)
    db_shows = []
    for item in categories:
        shows = item.findAll(attrs={'id' : 'show_block_interior'})
        for show in shows:
            name = show.find('img')['alt'].encode('utf-8')
            thumb = BASE_URL + show.find('img')['src']
            url = BASE + show.find('a')['href']
            db_shows.append((name,'cbs','showcats',url))
    return db_shows

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
                if 'MacGyver' in name:
                    url += '?vs=Full%20Episodes'
                common.addDirectory(name, 'cbs', 'showcats', url, thumb=thumbnail)
            break
    if catid == 'classics':
        stShows('http://startrek.com/videos')
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)

def stShows(url = common.args.url):
    stbase = 'http://www.startrek.com'
    data = common.getURL(url)
    remove = re.compile('<!.*?">')
    data = re.sub(remove, '', data)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    stshows=tree.find('div',attrs={'id' : 'channels'}).findAll('li', attrs={'class' : True})       
    for show in stshows:
        name = show['class'].replace('-',' ').title()
        thumb = stbase+show.find('img')['src']
        url = stbase+show.find('a')['href']
        common.addDirectory(name+' (startrek.com)', 'cbs', 'stshowcats', url, thumb=thumb)
 
def stshowcats(url = common.args.url):
    stbase = 'http://www.startrek.com'
    data = common.getURL(url)
    remove = re.compile('<!.*?">')
    data = re.sub(remove, '', data)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    stcats=tree.find('div',attrs={'id' : 'content'}).findAll('div', attrs={'class' : 'box_news'})       
    for cat in stcats:
        name = cat.find('h4').contents[1].strip()
        common.addDirectory(name, 'cbs', 'stvideos', url+'<name>'+name)

def stvideos(url = common.args.url):
    stbase = 'http://www.startrek.com'
    argname = url.split('<name>')[1]
    url = url.split('<name>')[0]
    stbase = 'http://www.startrek.com'
    data = common.getURL(url)
    remove = re.compile('<!.*?">')
    data = re.sub(remove, '', data)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    stcats=tree.find('div',attrs={'id' : 'content'}).findAll('div', attrs={'class' : 'box_news'})       
    for cat in stcats:
        name = cat.find('h4').contents[1].strip()
        if name == argname:
            titleUrl=stbase+cat.find('a',attrs={'class' : 'title '})['onclick'].split("url:'")[1].split("'}); return")[0]
            if 'Full Episodes' in argname:
                titleUrl += '/page_full/1'
            stprocessvideos(titleUrl)

def stprocessvideos(purl):
    stbase = 'http://www.startrek.com'
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    data = common.getURL(purl)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos=tree.find(attrs={'class' : 'videos_container'}).findAll('li')
    for video in videos:
        thumb = video.find('img')['src']
        url = stbase+video.find('a')['href']
        try:
            showname,name = video.findAll('a')[1].string.split('-')
        except:
            name = video.findAll('a')[1].string
            showname = ''
        try:
            seasonepisode, duration = video.findAll('p')
            seasonepisode = seasonepisode.string.replace('Season ','').split(' Ep. ')
            season = int(seasonepisode[0])
            episode = int(seasonepisode[1])
            duration = duration.string.split('(')[1].replace(')','')
        except:
            season = 0
            episode = 0
            duration = ''
        if season <> 0 or episode <> 0:
            displayname = '%sx%s - %s' % (str(season),str(episode),name)
        else:
            displayname = name
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="cbs"'
        u += '&sitemode="playST"'
        item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":displayname,
                                                 "Season":season,
                                                 "Episode":episode,
                                                 #"premiered":aired,
                                                 "Duration":duration,
                                                 "TVShowTitle":showname
                                                 }) 
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False)
    if len(videos) == 4:
        if '/page_full/' not in purl and '/page_other/' not in purl:
            nurl = purl+'/page_other/2'
        else:
            page = int(purl.split('/')[-1])
            nextpage = page + 1
            nurl = purl.replace('/'+str(page),'/'+str(nextpage))
        stprocessvideos(nurl)

def showcats(url = common.args.url):
    data = common.getURL(url)
    try:
        carousel = re.compile('var myCarousel\s+=\s+{(.*?)};',re.DOTALL).findall(data)[1].split(',')
        carouselDicts = []
        carouselDict = {}
        for car in carousel:
            itemsplit = car.replace('"','').split(':')
            carouselDict[itemsplit[0]] = itemsplit[1]
        carouselDicts.append(carouselDict) 
        carousel1 = re.compile('var myCarousel_1\s+=\s+{(.*?)\s+}',re.DOTALL).findall(data)[0].replace('}]','').split('[{')[1].split('},{')
        for car in carousel1:
            newdict = {}
            carsplit = car.split(',')
            for sub in carsplit:
                itemsplit = sub.replace('"','').split(':')
                newdict[itemsplit[0]] = itemsplit[1]
            carouselDicts.append(newdict)  
        for item in carouselDicts:
            url = 'http://www.cbs.com/carousel/initialize_carousel.php'
            url += '?jsObjName='+item['obj']#t_0
            url += '&xz='+item['xz']
            url += '&section='+item['section']
            url += '&k='+item['key']
            url += '&i='+item['i']
            url += '&begin=0'
            url += '&size=500'
            url += '&itemCount=12'
            common.addDirectory(item['title'], 'cbs', 'newvideos', url)
    except:
        print 'CBS: Carousel Failed'
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
 
def newvideos(url = common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll(attrs={'class' : 'cbs-video-item'})
    for video in videos:
        thumb = video.find('img')['src']
        displayname = video.find(attrs={'class' : 'cbs-video-thumbnail-link'})['title'].encode('utf-8')
        url = BASE+video.find('a')['href']
        try:
            title = displayname.split(' - ')[1].strip()
            series = displayname.split(' - ')[0].strip()
        except:
            print 'title/series metadata failure'
            title = displayname
            series = ''
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
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="cbs"'
        u += '&sitemode="play"'
        item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type="Video", infoLabels={ "Title":title,
                                                 "Season":season,
                                                 "Episode":episode,
                                                 #"premiered":aired,
                                                 #"Duration":duration,
                                                 "TVShowTitle":series
                                                 }) 
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False)        
        
def PAGES( tree ):
    try:
        print 'starting PAGES'
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
    except:
        print 'Pages Failed'

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

def playST(url = common.args.url):
    if 'watch_episode' in url:
        pid=url.split('/')[-1]
        play(pid)
    else:
        data=common.getURL(url)
        url = re.compile("flowplayer\\('flow_player', '.*?', '(.*?)'\\)").findall(data)[0]
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)   

def play(url = common.args.url):
    if 'http://' in url:
        data=common.getURL(url)
        pid = re.compile("var pid = '(.*?)';").findall(data)[0]
    else:
        pid = url  
    url = "http://release.theplatform.com/content.select?format=SMIL&Tracking=true&balance=true&MBR=true&pid=" + pid
    if (common.settings['enableproxy'] == 'true'):
        proxy = True
    else:
        proxy = False
    data=common.getURL(url,proxy=proxy)
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
    sbitrate = int(common.settings['quality']) * 1024
    for item in rtmps:
        bitrate = int(item['system-bitrate'])
        if bitrate > hbitrate and bitrate <= sbitrate:
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
