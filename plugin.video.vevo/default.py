import urllib, urllib2, re
import string, os, time, datetime
import xbmc, xbmcgui, xbmcplugin
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson

pluginhandle = int(sys.argv[1])

BASE = 'http://www.vevo.com'

def listCategories():
    addDir('Music Videos',  'http://www.vevo.com/videos',       'rootVideos')
    addDir('Artists',       'http://www.vevo.com/artists',      'rootArtists')
    #addDir('Playlists',     'http://www.vevo.com/playlists',    'rootPlaylists')
    #addDir('Shows',         'http://www.vevo.com/shows',        'rootShows')
    #addDir('Channels',      'http://www.vevo.com/channels',     'rootChannels')
    xbmcplugin.endOfDirectory(pluginhandle)

def rootVideos():
    videos_url = params['url']
    addGenres(videos_url, 'sortByVideo')
    xbmcplugin.endOfDirectory(pluginhandle)

def sortByVideo():
    url = params['url']
    if '?' in url:
        urlsplit = url.split('?')
        url = urlsplit[0]
        parameters = '?'+urlsplit[1]+'&'
    else:
        parameters = '?'
    addDir('Most Liked',    url+'/videosbrowse'+parameters+'order=MostViewed',      'sortWhenVideo')
    addDir('Most Viewed',   url+'/videosbrowse'+parameters+'order=MostFavorited',   'sortWhenVideo')
    addDir('Most Recent',   url+'/videosbrowse'+parameters+'order=MostViewed',      'listVideos')
    xbmcplugin.endOfDirectory(pluginhandle)

def sortWhenVideo():
    url = params['url']
    addDir('Today',         url+'Today',      'listVideos')
    addDir('This Week' ,    url+'ThisWeek',   'listVideos')
    addDir('This Month',    url+'ThisMonth',  'listVideos')
    addDir('All-Time',      url+'AllTime',    'listVideos')
    xbmcplugin.endOfDirectory(pluginhandle)

def listVideos():
    url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll(attrs={'class' : 'listThumb'})
    for video in videos:
            url = BASE+video.find(attrs={'class' : 'playOverlay'})['href']
            thumbnail = video.img['src'].split('?')[0]
            title = video.img['alt']
            addLink(title, url, 'getVideo', iconimage=thumbnail)
    xbmcplugin.endOfDirectory(pluginhandle)

def addGenres(url,mode):
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    genres = tree.find('ul', attrs={'class':'left-navigation-genres'}).findAll('li',recursive=False)
    for genre in genres:
        gclass = genre['class']
        if 'view_more_genres' not in gclass:
            subgenres = genre.findAll('a')
            for subgenre in subgenres:
                url = BASE + subgenre['href']
                name = subgenre.string
                if 'subgenre' in url:
                    name = ' - '+name
                addDir(name, url, mode)

def rootArtists():
    artist_url = params['url']
    addGenres(artist_url, 'sortByArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def sortByArtists():
    url = params['url']
    if '?' in url:
        urlsplit = url.split('?')
        url = urlsplit[0]
        parameters = '?'+urlsplit[1]+'&'
    else:
        parameters = '?'
    addDir('Most Liked',    url+'/artistsbrowse'+parameters+'order=MostViewed',      'sortWhenArtists')
    addDir('Most Viewed',   url+'/artistsbrowse'+parameters+'order=MostFavorited',   'sortWhenArtists')
    addDir('Most Recent',   url+'/artistsbrowse'+parameters+'order=MostViewed',      'listArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def sortWhenArtists():
    url = params['url']
    addDir('Today',         url+'Today',      'listArtists')
    addDir('This Week' ,    url+'ThisWeek',   'listArtists')
    addDir('This Month',    url+'ThisMonth',  'listArtists')
    addDir('All-Time',      url+'AllTime',    'listArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def listAZ(url):
    addDir('#', url+urllib.quote_plus('#'), 2)
    alphabet=set(string.ascii_uppercase)
    for letter in alphabet:
        print url
        newurl = url+str(letter)
        addDir(letter, newurl, 2)
    return

def listArtists():
    url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    artists = tree.findAll(attrs={'class' : 'playOverlay'})
    for artist in artists:
        url = BASE+artist['href']
        thumbnail = artist.find('img')['src'].split('?')[0]
        title = artist.find('img')['alt']
        addDir(title, url, 'listVideos', iconimage=thumbnail)
    xbmcplugin.endOfDirectory(pluginhandle)

def listArtistVideos():
    url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll(attrs={'class' : 'listThumb'})
    for video in videos:
            url = BASE+video.find(attrs={'class' : 'playOverlay'})['href']
            thumbnail = video.img['src'].split('?')[0]
            title = video.img['alt']
            addLink(title, url, 'getVideo', iconimage=thumbnail)
    xbmcplugin.endOfDirectory(pluginhandle)

def listArtistVideosOld():
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll(attrs={'class' : 'listThumb'})
    for video in videos:
        url = BASE_URL+video.find(attrs={'class' : 'playOverlay'})['href']
        thumbnail = video.img['src']
        title = video.img['alt']
        addLink(title, url, 'getVideo', iconimage=thumbnail)

def rootPlaylists():
    pass

def rootShows():
    pass
    
def rootChannels():
    pass        

def getVideo():
    pageurl = params['url']
    vevoID = pageurl.split('/')[-1]
    url = 'http://smilstream.vevo.com/HDFlash/v1/smil/%s/%s.smil' % (vevoID,vevoID.lower())
    data = getURL(url)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    videobase = tree.find(attrs={'name':'httpBase'})['content']
    videos = tree.findAll('video')
    filenames = ''
    select = len(videos) - 1
    for video in videos:
        filepath = video['src']
        path = filepath.split('_')[0]
        filename = filepath.replace(path,'').replace('.mp4','')
        filenames += filename+','
    finalUrl = videobase+path+','+filenames+'.mp4.csmil/bitrate='+str(select)#+'?v=2.1.20&fp=MAC%2010,2,152,33&r=KYLOY&g=CWOKVKGGUJPD&seek=0'
    item = xbmcgui.ListItem(path=finalUrl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)        
                
def getURL( url, data=None):
    print url
    headers =  {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'}
    if data:
        data = urllib.urlencode(data)
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    return data

def addLink(name, url, mode, plot='', iconimage='DefaultFolder.png'):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot } )
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
    return ok

def addDir(name, url, mode, plot='', iconimage='DefaultFolder.png'):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot } )
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

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
                param[splitparams[0]]=urllib.unquote_plus(splitparams[1])                                        
    return param

params=get_params()
mode=None
try:
    mode=params["mode"]
except:
    pass
print "Mode: "+str(mode)
print "Parameters:"+str(params)

if mode==None:
    listCategories()
else:
    exec '%s()' % mode
