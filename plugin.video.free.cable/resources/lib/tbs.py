import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,sys,datetime
import resources.lib._common as common
from BeautifulSoup import BeautifulStoneSoup
pluginhandle = int(sys.argv[1])

#getCollections = 'http://www.tbs.com/video/navigation/getCollections.jsp'
#getCollectionById = 'http://www.tbs.com/video/navigation/getCollectionById/'

getCollections = 'http://www.tbs.com/video/content/services/getCollections.do'
getCollectionById = 'http://www.tbs.com/video/content/services/getCollectionByContentId.do?offset=0&sort=&cTest=2&limit=200'

def masterlist():
        url = getCollections + '?id=185669'
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                name = collection.find('name').string
                if name == 'shows':
                        cid = collection['id']
                        return shows(cid,db=True)
                        
def rootlist(): # No mode - Root Listing
        url = getCollections + '?id=185669'
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                cid = collection['id']
                name = collection.find('name').string
                if name == 'feature - not show in nav':
                        continue
                common.addDirectory(name.title(), 'tbs', 'shows', cid)
        common.setView('seasons')

def shows(cid = common.args.url,db=False):
        name = common.args.name
        xbmcplugin.setContent(pluginhandle, 'shows')
        if name == 'Full Episodes':
                mode = 'episode'
        else:
                mode = 'show'
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        url = getCollections + '?id=' + cid
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        db_shows = []
        for collection in collections:
                cid = collection['id']
                name = collection.find('name').string.replace(': Full Episodes','')
                if db==True:
                        db_shows.append((name,'tbs', mode,cid))
                else:
                        common.addShow(name, 'tbs', mode, cid)
        if db==True:
                return db_shows
        else:
                common.setView('tvshows')

def show(cid = common.args.url): 
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        url = getCollections + '?id=' + cid
        html=common.getURL(url)
        if '<collections total_collections="0">' in html:
            episode(cid=cid)
            return
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                cid = collection['id']
                name = collection.find('name').string
                mode = episode
                common.addDirectory(name, 'tbs', 'episode', cid)
        common.setView('seasons')
        
def episode(cid = common.args.url):
        showname = common.args.name
        url = getCollectionById + '&id=' + cid
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        episodes = tree.findAll('episode')
        for episode in episodes:
                episodeId = episode['id']
                name = episode.find('title').string.encode( "utf-8" )
                thumbnail = episode.find('thumbnailurl').string.encode( "utf-8" )
                plot = episode.find('description').string.encode( "utf-8" )
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
                u += '&mode="tbs"'
                u += '&sitemode="'+mode+'"'
                infoLabels={ "Title":name,
                             "Plot":plot,
                             "Season":seasonNum,
                             "Episode":episodeNum,
                             "MPAA":mpaa,
                             "premiered":airdate,
                             "Episode":episodeNum,
                             "TVShowTitle":showname
                             }
                common.addVideo(u,displayname,thumbnail,infoLabels=infoLabels)
        common.setView('episodes')

def getAUTH(aifp,window,tokentype,vid,filename):
        authUrl = 'http://www.tbs.com/processors/cvp/token.jsp'
        parameters = {'aifp' : aifp,
                      'window' : window,
                      'authTokenType' : tokentype,
                      'videoId' : vid,
                      'profile' : 'tbs',
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
        #url = 'http://www.tbs.com/video/cvp/videoData.jsp?oid='+vid
        url = 'http://www.tbs.com/tveverywhere/content/services/cvpXML.do?titleId='+vid
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        #print tree.prettify()
        files = tree.findAll('file')
        if not files:
            url = 'http://www.tbs.com/tveverywhere/content/services/cvpXML.do?titleId=&id='+vid
            html=common.getURL(url)
            tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
            #print tree.prettify()
            files = tree.findAll('file')
        if files:
            html=common.getURL(url)
            tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
            print tree.prettify()
            sbitrate = int(common.settings['quality'])
            hbitrate = -1
            files = tree.findAll('file')
            for filenames in files:
                    try: bitrate = int(filenames['bitrate'])
                    except: bitrate = 1
                    if bitrate > hbitrate and bitrate <= sbitrate:
                            hbitrate = bitrate
                            filename = filenames.string            
            serverDetails = tree.find('akamai')
            if serverDetails:
                filename = filename[1:len(filename)-4]
                serverDetails = tree.find('akamai')
                server = serverDetails.find('src').string.split('://')[1]
                #get auth
                tokentype = serverDetails.find('authtokentype').string
                window = serverDetails.find('window').string
                aifp = serverDetails.find('aifp').string
                auth=getAUTH(aifp,window,tokentype,vid,filename.replace('mp4:',''))      
                swfUrl = 'http://www.tbs.com/cvp/tbs_video.swf'
                link = 'rtmpe://'+server+'?'+auth+" swfurl="+swfUrl+" swfvfy=true"+' playpath='+filename
            elif 'http://' in filename:
                link = filename
            else:
                link = 'http://ht.cdn.turner.com/tbs/big'+filename
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

