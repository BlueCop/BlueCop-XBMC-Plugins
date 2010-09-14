import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime
from BeautifulSoup import BeautifulStoneSoup
pluginhandle = int(sys.argv[1])

getCollections = 'http://www.tbs.com/video/navigation/getCollections.jsp?oid=185669'

################################ Common
def getURL( url ):
    try:
        print 'TBS--> getURL :: url = '+url
        txdata = None
        txheaders = {
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)'	
                    }
        req = urllib2.Request(url, txdata, txheaders)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        error = 'Error code: '+ str(e.code)
        xbmcgui.Dialog().ok(error,error)
        print 'Error code: ', e.code
        return False
    else:
        return link

def addLink(name,url,mode,iconimage='',plot='',season=0,episode=0,showname=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        if season == 0 and episode == 0:
            list_name = name
        else:
            list_name = str(season)+'x'+str(episode)+' - '+name
        liz=xbmcgui.ListItem(list_name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,
                                                "Plot":plot,
                                                "Season":season,
                                                "Episode":episode,
                                                "TVShowTitle":showname})
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage='',plot=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot})
        ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
        return ok

################################ Root listing
def ROOT():
        #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        url = getCollections
        html=getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                cid = collection['id']
                name = collection.find('name').string
                if name == 'feature - not show in nav' or name == 'shows' or name == 'exclusives':
                        continue
                else:
                        SHOWS(name.title(), cid)
                #mode = 1 #SHOWS() Mode
                #addDir(name.title(),cid,mode)
        #xbmcplugin.endOfDirectory(pluginhandle)

def SHOWS(name, cid):
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        if name == 'Full Episodes':
            mode = 3 #EPISODE() Mode
            url = getCollections
            html=getURL(url)
            tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
            collections = tree.findAll('collection')
            for collection in collections:
                    if collection['id'] == cid:
                            subcollections = collection.findAll('subcollection')
                            for subcollection in subcollections:
                                    scid = subcollection['id']
                                    name = subcollection.find('name').string.title()
                                    addDir(name,scid,mode)
        else:
            mode = 2 #EPISODE() Mode
            url = getCollections
            html=getURL(url)
            tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
            collections = tree.findAll('collection')
            for collection in collections:
                    if collection['id'] == cid:
                            subcollections = collection.findAll('subcollection',recursive=False)
                            for subcollection in subcollections:
                                    scid = subcollection['id']
                                    name = subcollection.find('name').string.title()
                                    addDir(name,scid,mode)
        xbmcplugin.endOfDirectory(pluginhandle)  

def SHOW(scid):
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        url = getCollections
        html=getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                subcollections = collection.findAll('subcollection')
                for subcollection in subcollections:
                        if subcollection['id'] == scid:
                                subsubcollections = subcollection.findAll('subcollection',recursive=False)
                                for subsubcollection in subsubcollections:
                                        sscid = subsubcollection['id']
                                        name = subsubcollection.find('name').string
                                        mode = 3 #EPISODE() Mode
                                        addDir(name,sscid,mode)
        xbmcplugin.endOfDirectory(pluginhandle)
        
def EPISODE(name, cid):
        showname = name
        xbmcplugin.setContent(pluginhandle, 'episodes')
        url = 'http://www.tbs.com/video/navigation/getCollectionById/?oid='+cid
        html=getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        episodes = tree.findAll('episode')
        for episode in episodes:
                episodeId = episode['id']
                name = episode.find('title').string
                thumbnail = episode.find('thumbnailurl').string
                plot = episode.find('description').string
                try:
                    season_episode = thumbnail.split('_')[1]
                    seasonNum = int(season_episode[:-2])
                    episodeNum = int(season_episode[-2:])
                except:
                    seasonNum = 0
                    episodeNum = 0
                segments = episode.findAll('segment')
                if len(segments) == 0:
                    url = episodeId
                    mode = 4
                    addLink(name,url,mode,thumbnail,plot,seasonNum,episodeNum,showname)
                else:
                    url = ''
                    for segment in segments:
                            url += segment['id']+'<segment>'
                    mode = 5 #PLAYEPISODE
                    addLink(name,url,mode,thumbnail,plot,seasonNum,episodeNum,showname)
        xbmcplugin.endOfDirectory(pluginhandle)

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
        response = urllib2.urlopen(request)
        link = response.read(200000)
        response.close()
        return re.compile('<token>(.+?)</token>').findall(link)[0]

def GET_RTMP(vid):
        url = 'http://www.tbs.com/video/cvp/videoData.jsp?oid='+vid
        html=getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        files = tree.findAll('file')
        #stream details
        filename = files[0].string
        if 'http://' in filename:
            filename = filename
            return filename
        else:
            filename = filename[1:len(filename)-4]
            serverDetails = tree.find('akamai')
            server = serverDetails.find('src').string.split('://')[1]
            #get auth
            tokentype = serverDetails.find('authtokentype').string
            window = serverDetails.find('window').string
            aifp = serverDetails.find('aifp').string
            auth=getAUTH(aifp,window,tokentype,vid,filename)      
            swfUrl = 'http://www.tbs.com/cvp/tbs_video.swf'
            rtmp = 'rtmpe://'+server+'?'+auth+" swfurl="+swfUrl+" swfvfy=true"+' playpath='+filename
            return rtmp

def PLAYEPISODE(vids):
        vids = vids.split('<segment>')
        url = 'stack://'
        for vid in vids:
            if vid <> '':
                url += GET_RTMP(vid).replace(',',',,')+' , '
        url = url[:-3]
        item = xbmcgui.ListItem(path=url)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def PLAY(vid):
        url = GET_RTMP(vid)
        item = xbmcgui.ListItem(path=url)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, item)


def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

              
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        thumbnail=urllib.unquote_plus(params["thumbnail"])
except:
        thumbnail=''

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)


if mode==None or url==None or len(url)<1:
        ROOT()
elif mode==1:
        SHOWS(name,url)
elif mode==2:
        SHOW(url)
elif mode==3:
        EPISODE(name,url)
elif mode==4:
        PLAY(url)
elif mode==5:
        PLAYEPISODE(url)
