import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re
import cookielib
import datetime
import time


import demjson
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import MinimalSoup
import resources.lib._common as common
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

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
            if 'MacGyver' in name:
                url += '?vs=Full%20Episodes'
            if 'daytime/lets_make_a_deal' in url:
                url = url.replace('daytime/lets_make_a_deal','shows/lets_make_a_deal')
            elif 'cbs_evening_news/video/' in url:
                url = 'http://www.cbs.com/shows/cbs_evening_news/video/'
            elif 'shows/dogs_in_the_city/' in url:
                url+='video/'
            elif '/shows/3/' in url:
                url+='video/'
            elif '/shows/nyc_22/' in url:
                name = 'NYC 22'
                url+='video/'
            db_shows.append((name,'cbs','showcats',url))
    for show in stShows('http://startrek.com/videos',db=True):
        db_shows.append(show)
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
    common.setView('seasons')

def shows(catid = common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    data = re.compile('<!-- SHOWS LIST -->(.*?)<!-- END SHOWS LIST -->',re.DOTALL).findall(data)[0]  
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    categories=tree.findAll('div', attrs={'id' : True}, recursive=False)
    for item in categories:
        if item['id'] == catid:
            shows = item.findAll(attrs={'id' : 'show_block_interior'})
            for show in shows:
                name = show.find('img')['alt'].encode('utf-8')
                thumbnail = BASE + show.find('img')['src']
                url = show.find('a')['href']
                if 'MacGyver' in name:
                    url += '?vs=Full%20Episodes'
                if 'daytime/lets_make_a_deal' in url:
                    url = url.replace('daytime/lets_make_a_deal','shows/lets_make_a_deal')
                elif 'cbs_evening_news/video/' in url:
                    url = 'http://www.cbs.com/shows/cbs_evening_news/video/'
                elif 'shows/dogs_in_the_city/' in url:
                    url+='video/'
                elif '/shows/3/' in url:
                    url+='video/'
                elif '/shows/nyc_22/' in url:
                    name = 'NYC 22'
                common.addShow(name, 'cbs', 'showcats', url)#, thumb=thumbnail)
            break
    if catid == 'classics':
        stShows('http://startrek.com/videos')
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    common.setView('tvshows')

def stShows(url = common.args.url,db=False):
    stbase = 'http://www.startrek.com'
    data = common.getURL(url)
    remove = re.compile('<!.*?">')
    data = re.sub(remove, '', data)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    stshows=tree.find('div',attrs={'id' : 'channels'}).findAll('li', attrs={'class' : True})
    st_shows = []      
    for show in stshows:
        name = show['class'].replace('-',' ').title()
        thumb = stbase+show.find('img')['src']
        url = stbase+show.find('a')['href']
        if 'Star Trek' not in name:
            name = 'Star Trek '+name
        if db:
            st_shows.append((name,'cbs','stshowcats',url))
        else:
            common.addShow(name, 'cbs', 'stshowcats', url)#, thumb=thumb)
    if db:
        return st_shows
 
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
    common.setView('seasons')

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
    common.setView('episodes')

def stprocessvideos(purl):
    print "enter stprocessvideos"
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
        infoLabels={ "Title":displayname,
                     "Season":season,
                     "Episode":episode,
                     #"premiered":aired,
                     "Duration":duration,
                     "TVShowTitle":showname
                     }
        common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
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
        print 'CBS: Trying New Carousel'
        carousels = re.compile("loadUpCarousel\('(.*?)','(.*?)', '(.*?)', (.*?), true, stored").findall(data)
        carousels[0][0]
        for name,dir1,dir2,dir3 in carousels:
            url = 'http://www.cbs.com/carousels/'+dir3+'/video/'+dir1+'/'+dir2+'/0/400/'
            common.addDirectory(name, 'cbs', 'newvideos', url)
    except:
        print 'CBS: Carousel Failed'
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        try:
            print 'CBS: trying secondary-show-nav-wrapper'
            options = tree.find(attrs={'id' : 'secondary-show-nav-wrapper'})
            options = options.findAll('a')
            for option in options:
                name = option.string.encode('utf-8')
                url = BASE + option['href']
                common.addDirectory(name, 'cbs', 'videos', url)
            print 'CBS: trying vid_module'
            options = tree.findAll(attrs={'class' : 'vid_module'})
            for option in options:
                moduleid = option['id']
                name = option.find(attrs={'class' : 'hdr'}).string
                common.addDirectory(name, 'cbs', 'showsubcats', url+'<moduleid>'+moduleid) 
        except:
            print 'CBS: secondary-show-nav-wrapper failed'
            print 'CBS: trying vid_module secondary'
            options = tree.findAll(attrs={'class' : 'vid_module'})
            for option in options:
                moduleid = option['id']
                name = option.find(attrs={'class' : 'hdr'}).string
                common.addDirectory(name, 'cbs', 'showsubcats', url+'<moduleid>'+moduleid) 
    common.setView('seasons')                                      

def showsubcats(url = common.args.url):
    moduleid = url.split('<moduleid>')[1]
    url      = url.split('<moduleid>')[0]
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    vid_module = tree.find(attrs={'id' : moduleid})
    PAGES(vid_module)
    common.setView('episodes')
    
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
    common.setView('episodes')
 
def newvideos(url = common.args.url):
    data = common.getURL(url)
    itemList = demjson.decode(data)['itemList']
    for video in itemList:
        url = video['pid']
        description = video['description']
        thumb = video['thumbnail']
        seriesTitle = video['seriesTitle']
        title = video['label']
        try:episodeNum = int(video['episodeNum'])
        except:episodeNum = 0 
        try:seasonNum = int(video['seasonNum'])
        except:seasonNum = 0
        duration = int(video['duration'])
        airDate = video['_airDate']
        rating = video['rating']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="cbs"'
        u += '&sitemode="play"'
        displayname = '%sx%s - %s' % (seasonNum,episodeNum,title)
        infoLabels={ "Title":title,
                     "Plot":description,
                     "Season":seasonNum,
                     "Episode":episodeNum,
                     "premiered":airDate,
                     "Duration":str(duration),
                     "mpaa":rating,
                     "TVShowTitle":seriesTitle
                     }
        common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')  
        
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
    print "Entering VIDEOLINKS function"
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
        infoLabels={ "Title":title,
                     "Season":season,
                     "Episode":episode,
                     "premiered":aired,
                     "Duration":duration,
                     "TVShowTitle":series
                     }
        common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')

        
def getHTML( url ):
    print 'HULU --> common :: getHTML :: url = '+url
    cj = cookielib.LWPCookieJar()
    #if os.path.isfile(COOKIEFILE):
    #    cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Referer', 'http://hulu.com'),
                         ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')]
    usock=opener.open(url)
    response=usock.read()
    usock.close()
    #if os.path.isfile(COOKIEFILE):
    #    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    return response

  
def clean_subs(data):
        br = re.compile(r'<br.*?>')
        br_2 = re.compile(r'\n')
        tag = re.compile(r'<.*?>')
        space = re.compile(r'\s\s\s+')
        sub = br.sub('\n', data)
        sub = tag.sub(' ', sub)
        sub = br_2.sub('<br/>', sub)
        sub = space.sub(' ', sub)
        return sub
    
        
def convert_subtitles(subtitles, output):
    subtitle_data = subtitles
    subtitle_data = subtitle_data.replace("\n","").replace("\r","")
    subtitle_data = BeautifulStoneSoup(subtitle_data)
    subtitle_array = []
    srt_output = ''

    print "CBS: --> Converting subtitles to SRT"
    #self.update_dialog('Converting Subtitles to SRT')
    lines = subtitle_data.findAll('p') #split the file into lines
    for line in lines:
        if line is not None:
            #print "LINE: " + str(line)
            #print "LINE BEGIN: " + str(line['begin'])
            
            sub=str(clean_subs(str(line)))
            try:
                newsub=sub
                sub = BeautifulStoneSoup(sub, convertEntities=BeautifulStoneSoup.ALL_ENTITIES)
            except:
                sub=newsub
            #print "CURRENT SUB: " + str(sub)
            begin_time = line['begin']
            end_time = line['end']
            start_split =begin_time.split(".")                        
            end_split =end_time.split(".")                        
            timestamp = "%s,%s" % (start_split[0], start_split[1])
            end_timestamp = "%s,%s" % (end_split[0], end_split[1])
            #print "TIMESTAMP " + str(timestamp) + " " + str(end_timestamp)
   
            temp_dict = {'start':timestamp, 'end':end_timestamp, 'text':sub}
            subtitle_array.append(temp_dict)
                
    for i, subtitle in enumerate(subtitle_array):
        line = str(i+1)+"\n"+str(subtitle['start'])+" --> "+str(subtitle['end'])+"\n"+str(subtitle['text'])+"\n\n"
        srt_output += line
                    
    file = open(os.path.join(common.pluginpath,'resources','cache',output+'.srt'), 'w')
    file.write(srt_output)
    file.close()
    print "CBS: --> Successfully converted subtitles to SRT"
    #self.update_dialog('Conversion Complete')
    return True
    
def playST(url = common.args.url):
    print "Entering playST function"

    if 'watch_episode' in url:
        pid=url.split('/')[-1]
        play(pid)
    else:
        data=common.getURL(url)
        url = re.compile("flowplayer\\('flow_player', '.*?', '(.*?)'\\)").findall(data)[0]
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)   

def play(url = common.args.url):
    print "DEBUG Entering play function"

    if 'http://' in url:
        data=common.getURL(url)
        try:
            pid = re.compile('var pid = "(.*?)";').findall(data)[0]
        except:
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
    #print "DEBUG TREEE "+str(tree)
    
    if (common.settings['enablesubtitles'] == 'true'):
        refs = tree.findAll('ref',attrs={'tp:closedcaptionurl': True})
        closedcaption = None
        for item in refs:
            try:
                closedcaption = item['tp:closedcaptionurl']
                guid = item['guid']
                print "closed caption: " + closedcaption + " GUID: " +str(guid)
            except:
                print "no key"
                
        if (closedcaption is not None):
            xml_closedcaption = getHTML(closedcaption)
            convert_subtitles(xml_closedcaption,guid)

    #print "DEBUG refs:" + str(refs)
        
    videos = tree.findAll('video',attrs={'profile': True})
    print "DEBUG videos:" + str(videos)
    rtmps=[]
    https=[]
    cccount=0
    for item in videos:
        print "VIDEO NUMBER " +str(cccount) + " " + str(item) + "      ENDDDD"
        cccount=cccount+1
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
    if (common.settings['enablesubtitles'] == 'true') and (closedcaption is not None):
        while not xbmc.Player().isPlaying():
            print 'CBS--> Not Playing'
            xbmc.sleep(100)
    
        subtitles = os.path.join(common.pluginpath,'resources','cache',guid+'.srt')
        print "HULU --> Setting subtitles"
        xbmc.Player().setSubtitles(subtitles)

