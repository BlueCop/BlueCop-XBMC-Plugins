import urllib, urllib2, re, md5
import string, os, time, datetime
import xbmc, xbmcgui, xbmcplugin
from BeautifulSoup import BeautifulSoup
import demjson

pluginhandle = int(sys.argv[1])

BASE_URL = 'http://www.vevo.com'

def listCategories():
        addDir('A-Z', 'http://www.vevo.com/artists/index/a-z?alpha=', 1)
        addDir('On Tour', 'http://www.vevo.com/artists/on-tour', 2)
        addDir('Most Recent', 'http://www.vevo.com/artists?order=MostRecent', 2)
        addDir('Most Viewed Artists', 'http://www.vevo.com/artists?order=MostViewedToday', 2)
        addDir('Most Liked Artists', 'http://www.vevo.com/artists?order=MostFavoritedToday', 2)

def listAZ(url):
        addDir('#', url+urllib.quote_plus('#'), 2)
        alphabet=set(string.ascii_uppercase)
        for letter in alphabet:
                url = url+letter
                addDir(letter, url, 2)
        return

def listArtist(url):
        data = getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        try:
                pagenext = tree.find(attrs={'class' : 'next'})
                addDir(pagenext.string+' Page', BASE_URL+pagenext['href'], 2)
        except:
                print 'No Next Page'
        try:
                pageprev = tree.find(attrs={'class' : 'prev'})
                addDir(pageprev.string+' Page', BASE_URL+pageprev['href'], 2)
        except:
                print 'No Previous Page'
        artists = tree.findAll(attrs={'class' : 'listThumb'})
        for artist in artists:
                url = BASE_URL+artist.a['href']
                thumbnail = artist.a.img['src']
                title = artist.a.img['alt']
                addDir(title, url, 3, iconimage=thumbnail)

def listArtistVideos(url):
        data = getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        videos = tree.findAll(attrs={'class' : 'listThumb'})
        for video in videos:
                url = BASE_URL+video.find(attrs={'class' : 'playOverlay'})['href']
                thumbnail = video.img['src']
                title = video.img['alt']
                addLink(title, url, 10, iconimage=thumbnail)
                

def getVideo(page):
        pageurl = page.split('?')[0]
        isrc = pageurl.split('/')[-1]
        authUrl = 'http://videoplayer.vevo.com/VideoService/AuthenticateVideo'
        authUrl += '?isrc='+isrc
        authUrl += '&domain='+page
        authUrl += '&authToken=123456'
        data = getURL(authUrl)
        tree = demjson.decode(data)
        for item in tree['video']['videoVersions']:
            if item['sourceType'] == 0:
                video_id = item['id']       
        apiUrl = 'http://www.youtube.com/api_video_info'
        apiUrl += '?video_id='+video_id
        apiUrl += '&hl=en'
        apiUrl += '&el=embedded'
        apiUrl += '&ps=vevo'
        apiUrl += '&asv=3'
        data = getURL(apiUrl).split('&')
        for item in data:
                if 'fmt_stream_map' in item:
                        urls = urllib.unquote(item.split('=')[1]).split(',')
                        for url in urls:
                                urlsplit = url.split('|')
                                if urlsplit[0] == '35':
                                        item = xbmcgui.ListItem(path=urlsplit[1])
                                        xbmcplugin.setResolvedUrl(pluginhandle, True, item)       
                
	
def getURL( url, data=None):
        print url
        headers = { 
                'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14',
                #'Referer':''
        }
        if data:
                data = urllib.urlencode(data)
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        return data


"""
        addDir()
"""
def addLink(name, url, mode, plot='', iconimage='DefaultFolder.png'):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addDir(name, url, mode, plot='', iconimage='DefaultFolder.png'):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok



"""
        getParams()
        grab parameters passed by the available functions in this script
"""
def getParams():
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

def qs2dict(qs):
    try:
        params = dict([part.split('=') for part in qs.split('&')])
    except:
        params = {}
    return params


#grab params and assign them if found
params=getParams()
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

#print params to the debug log
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None:
        print "CATEGORY INDEX : "
        listCategories()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==1:
        listAZ()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==2:
        listArtist(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==3:
        listArtistVideos(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==10:
        getVideo(url)

