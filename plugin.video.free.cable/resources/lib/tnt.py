import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,sys,datetime
import resources.lib._common as common
from BeautifulSoup import BeautifulStoneSoup
pluginhandle = int(sys.argv[1])

BASE_URL = 'http://www.tnt.tv/video/content/services/getCollections.do?id=58127'
BASE = 'http://www.tnt.tv'

def masterlist():
        url = 'http://www.tnt.tv/content/services/getCollections.do?site=true&id=58127'
        html=common.getURL(BASE_URL)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                name = collection.find('name').string
                if name == 'Shows':
                        cid = collection['id']
                        return shows(cid,db=True)
def rootlist():
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        url = 'http://www.tnt.tv/content/services/getCollections.do?site=true&id=58127'
        html=common.getURL(BASE_URL)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                cid = collection['id']
                name = collection.find('name').string
                if name == 'Featured':
                        continue
                common.addDirectory(name, 'tnt', 'shows', cid)
        common.setView('seasons')

def shows(cid = common.args.url,db=False):
        name = common.args.name
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        if name == 'Full Episodes' or name == 'Web Exclusives':
            mode = 'episode' #EPISODE() Mode
        else:
            mode = 'show' #SHOW() Mode
        url = 'http://www.tnt.tv/content/services/getCollections.do?site=true&id=58127'
        html=common.getURL(BASE_URL)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        db_shows = []
        for collection in collections:
                if collection['id'] == cid:
                        subcollections = collection.findAll('subcollection')
                        for subcollection in subcollections:
                                scid = subcollection['id']
                                name = subcollection.find('name').string.split('-')[0].replace('Full Episodes','').strip()
                                if db==True:
                                        db_shows.append((name,'tnt',mode,scid))
                                else:
                                        common.addShow(name, 'tnt', mode, scid)
        if db==True:
                return db_shows
        else:
                common.setView('tvshows') 

def show():
        scid = common.args.url
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        url = 'http://www.tnt.tv/content/services/getCollections.do?site=true&id=58127'
        html=common.getURL(BASE_URL)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                subcollections = collection.findAll('subcollection')
                for subcollection in subcollections:
                        if subcollection['id'] == scid:
                                subsubcollections = subcollection.findAll('subsubcollection')
                                for subsubcollection in subsubcollections:
                                        sscid = subsubcollection['id']
                                        name = subsubcollection.find('name').string
                                        common.addDirectory(name, 'tnt', 'episode', sscid)
        common.setView('seasons')
        
def episode():
        cid = common.args.url
        showname = common.args.name
        #url = 'http://www.tnt.tv/processors/services/getCollectionByContentId.do?offset=0&sort=&limit=200&id='+cid
        #url = 'http://www.tnt.tv/content/services/getCollectionByContentId.do?site=true&offset=0&sort=&limit=200&id='+cid
        url = 'http://www.tnt.tv/video/content/services/getCollectionByContentId.do?offset=0&sort=&limit=200&id='+cid
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        episodes = tree.findAll('episode')
        for episode in episodes:
                episodeId = episode['id']
                name = episode.find('title').string
                thumbnail = episode.find('thumbnailurl').string
                plot = episode.find('description').string
                duration = episode.find('duration').string
                try:seasonNum = int(episode.find('seasonnumber').string)
                except:seasonNum = 0
                try:
                    episodeNum = episode.find('episodenumber').string
                    if len(episodeNum) > 2 and episodeNum.startswith(str(seasonNum)):
                        episodeNum = episodeNum[1:]
                    if len(episodeNum) > 2:
                        episodeNum = episodeNum[-2:]
                        print episodeNum
                    episodeNum = int(episodeNum)
                except:episodeNum = 0
                try:duration = episode.find('duration').string.strip()
                except: duration = ''
                try: mpaa = episode.find('tvratingcode').string.strip()
                except: mpaa = ''
                try: airdate = common.formatDate(episode.find('expirationdate').string,'%m/%d/%Y')
                except: airdate = ''
                displayname=name
                if episodeNum <> 0 or seasonNum <> 0:
                    displayname = str(seasonNum)+'x'+str(episodeNum)+' - '+name
                segments = episode.findAll('segment')
                if len(segments) == 0:
                    url = episodeId
                    mode = 'play'
                else:
                    url = ''
                    for segment in segments:
                            url += segment['id']+'<segment>'
                    mode = 'playepisode' #PLAYEPISODE
                u = sys.argv[0]
                u += '?url="'+urllib.quote_plus(url)+'"'
                u += '&mode="tnt"'
                u += '&sitemode="'+mode+'"'
                infoLabels={ "Title":name,
                             "Plot":plot,
                             "Season":seasonNum,
                             "Duration":duration,
                             "MPAA":mpaa,
                             "premiered":airdate,
                             "Episode":episodeNum,
                             "TVShowTitle":showname
                             }
                common.addVideo(u,displayname,thumbnail,infoLabels=infoLabels)
        common.setView('episodes')

def getAUTH(aifp,window,tokentype,vid,filename):
        authUrl = 'http://www.tnt.tv/processors/services/token.do'
        authUrl = 'http://www.tbs.com/processors/cvp/token.jsp'
        #authUrl = 'http://www.tnt.tv/tveverywhere/processors/services/token.do'
        parameters = {'aifp' : aifp,
                      'window' : window,
                      'authTokenType' : tokentype,
                      'videoId' : vid,
                      'profile' : 'tnt',
                      'path' : filename
                      }
        data = urllib.urlencode(parameters)
        request = urllib2.Request(authUrl, data)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1')
        response = urllib2.urlopen(request)
        link = response.read(200000)
        response.close()
        return re.compile('<token>(.+?)</token>').findall(link)[0]

def GET_RTMP(vid):
        #url = 'http://www.tnt.tv/video_cvp/cvp/videoData/?id='+vid
        #http://www.tnt.tv/video/content/services/cvpXML.do?titleId=828441
        url = 'http://www.tnt.tv/video/content/services/cvpXML.do?titleId='+vid
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        #print tree.prettify()
        files = tree.findAll('file')
        if not files:
            url = 'http://www.tnt.tv/video/content/services/cvpXML.do?titleId=&id='+vid
            html=common.getURL(url)
            tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
            #print tree.prettify()
            files = tree.findAll('file')
        sbitrate = int(common.settings['quality'])
        hbitrate = -1
        for filenames in files:
                try: bitrate = int(filenames['bitrate'])
                except: bitrate = 1
                if bitrate > hbitrate and bitrate <= sbitrate:
                        hbitrate = bitrate
                        filename = filenames.string
        serverDetails = tree.find('akamai')
        if serverDetails:
            filename = filename[1:len(filename)-4]#.replace('mp4:','')
            #serverDetails = tree.find('akamai')
            server = serverDetails.find('src').string.split('://')[1]
            #get auth
            tokentype = serverDetails.find('authtokentype').string
            window = serverDetails.find('window').string
            aifp = serverDetails.find('aifp').string
            
            auth=getAUTH(aifp,window,tokentype,vid,filename.replace('mp4:',''))      
            swfUrl = 'http://www.tnt.tv/dramavision/tnt_video.swf'
            link = 'rtmpe://'+server+'?'+auth+" swfurl="+swfUrl+" swfvfy=true"+' playpath='+filename
        elif 'http://' in filename:
            link = filename
        else:
            link = 'http://ht.cdn.turner.com/tnt/big/'+filename
        return link

def playepisode():
        vids = common.args.url.split('<segment>')
        url = 'stack://'
        for vid in vids:
            if vid <> '':
                url += GET_RTMP(vid).replace(',',',,')+' , '
        url = url[:-3]
        item = xbmcgui.ListItem(path=url)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    
def play():
        url = GET_RTMP(common.args.url)
        item = xbmcgui.ListItem(path=url)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

