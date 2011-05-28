import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,sys,datetime
import resources.lib._common as common
from BeautifulSoup import BeautifulStoneSoup
pluginhandle = int(sys.argv[1])



def masterlist():
        url = 'http://www.tnt.tv/content/services/getCollections.do?site=true&id=58127'
        html=common.getURL(url)
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
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                cid = collection['id']
                name = collection.find('name').string
                if name == 'Featured':
                        continue
                common.addDirectory(name, 'tnt', 'shows', cid)

def shows(cid = common.args.url,db=False):
        name = common.args.name
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        if name == 'Full Episodes' or name == 'Web Exclusives':
            mode = 'episode' #EPISODE() Mode
        else:
            mode = 'show' #SHOW() Mode
        url = 'http://www.tnt.tv/content/services/getCollections.do?site=true&id=58127'
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        db_shows = []
        for collection in collections:
                if collection['id'] == cid:
                        subcollections = collection.findAll('subcollection')
                        for subcollection in subcollections:
                                scid = subcollection['id']
                                name = subcollection.find('name').string.replace('- Full Episodes','')
                                if db==True:
                                        db_shows.append((name,'tnt',mode,scid,None,None,None))
                                else:
                                        common.addDirectory(name, 'tnt', mode, scid)
        if db==True:
                return db_shows  

def show():
        scid = common.args.url
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        url = 'http://www.tnt.tv/content/services/getCollections.do?site=true&id=58127'
        html=common.getURL(url)
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
        
def episode():
        cid = common.args.url
        showname = common.args.name
        xbmcplugin.setContent(pluginhandle, 'episodes')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        url = 'http://www.tnt.tv/processors/services/getCollectionByContentId.do?offset=0&sort=&limit=200&id='+cid
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        episodes = tree.findAll('episode')
        for episode in episodes:
                episodeId = episode['id']
                name = episode.find('title').string
                thumbnail = episode.find('thumbnailurl').string
                plot = episode.find('description').string
                duration = episode.find('duration').string
                try:
                    seasonNum = int(episode.find('seasonnumber').string)
                    print seasonNum
                except:
                    seasonNum = 0
                try:
                    episodeNum = int(episode.find('episodenumber').string)
                    print episodeNum
                except:
                    episodeNum = 0
                if episodeNum == 0 or seasonNum == 0:
                    print 'bad season or episode value'
                else:
                    name = str(seasonNum)+'x'+str(episodeNum)+' - '+name
                segments = episode.findAll('segment')
                if len(segments) == 0:
                    url = episodeId
                    mode = 'play'
                    addLink(name,url,mode,thumbnail,plot,seasonNum,episodeNum,showname,duration)
                else:
                    url = ''
                    for segment in segments:
                            url += segment['id']+'<segment>'
                    mode = 'playepisode' #PLAYEPISODE
                    addLink(name,url,mode,thumbnail,plot,seasonNum,episodeNum,showname,duration)

def addLink(name,url,mode,iconimage='',plot='',season=0,episode=0,showname='',duration=''):
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="tnt"'
        u += '&sitemode="'+mode+'"'
        item=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        item.setInfo( type="Video", infoLabels={ "Title":name,
                                                 "Plot":plot,
                                                 "Season":season,
                                                 "Episode":episode,
                                                 "Duration":duration,
                                                 "TVShowTitle":showname
                                                 }) 
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False)


def getAUTH(aifp,window,tokentype,vid,filename):
        authUrl = 'http://www.tnt.tv/processors/services/token.do'
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
        url = 'http://www.tnt.tv/video_cvp/cvp/videoData/?id='+vid
        html=common.getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        files = tree.findAll('file')
        #stream details
        filename = files[0].string
        if 'http://' in filename:
            filename = filename
            return filename
        else:
            filename = filename[1:len(filename)-4]#.replace('mp4:','')
            serverDetails = tree.find('akamai')
            server = serverDetails.find('src').string.split('://')[1]
            #get auth
            tokentype = serverDetails.find('authtokentype').string
            window = serverDetails.find('window').string
            aifp = serverDetails.find('aifp').string
            auth=getAUTH(aifp,window,tokentype,vid,filename.replace('mp4:',''))      
            swfUrl = 'http://www.tnt.tv/dramavision/tnt_video.swf'
            rtmp = 'rtmpe://'+server+'?'+auth+" swfurl="+swfUrl+" swfvfy=true"+' playpath='+filename
            return rtmp

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

