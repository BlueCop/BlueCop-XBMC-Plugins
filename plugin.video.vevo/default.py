import urllib, urllib2, re, md5
import string, os, time, datetime
import xbmc, xbmcgui, xbmcplugin
from BeautifulSoup import BeautifulSoup
import demjson

pluginhandle = int(sys.argv[1])

BASE_URL = 'http://www.vevo.com'

def listCategories():
    addDir('Music Videos',  'http://www.vevo.com/videos',       'rootVideos')
    addDir('Playlists',     'http://www.vevo.com/playlists',    'rootPlaylists')
    addDir('Artists',       'http://www.vevo.com/artists',      'rootArtists')
    addDir('Shows',         'http://www.vevo.com/shows',        'rootShows')
    addDir('Channels',      'http://www.vevo.com/channels',     'rootChannels')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def rootVideos():
    addDir('Test', 'http://www.vevo.com/videos', 1)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
def rootPlaylists():
    pass
    
def rootArtists():
    pass

def rootShows():
    pass
    
def rootChannels():
    pass

def mostViewed(mode,genre = 'none'):
        if mode == 'artist':
                name = 'Artists'
                mode = 2
                urlname = 'artists'
        elif mode == 'video':
                name = 'Video'
                mode = 4
                urlname = 'videos'
        if genre <> 'none':
                genreparam = '&genre='+genre
        else:
                genreparam = ''
        addDir('Most Viewed '+name+' Today',            'http://www.vevo.com/'+urlname+'?order=MostViewedToday'+genreparam,     mode)
        addDir('Most Viewed '+name+' This Week',        'http://www.vevo.com/'+urlname+'?order=MostViewedThisWeek'+genreparam,  mode)
        addDir('Most Viewed '+name+' This Month',       'http://www.vevo.com/'+urlname+'?order=MostViewedThisMonth'+genreparam, mode)
        addDir('Most Viewed '+name+' All Time',         'http://www.vevo.com/'+urlname+'?order=MostViewedAllTime'+genreparam,   mode)
        
def mostLiked(mode,genre = 'none'):
        if mode == 'artist':
                name = 'Artists'
                mode = 2
                urlname = 'artists'
        elif mode == 'video':
                name = 'Video'
                mode = 4
                urlname = 'videos'
        if genre <> 'none':
                genreparam = '&genre='+genre
        else:
                genreparam = ''
        addDir('Most Liked '+name+' Today',            'http://www.vevo.com/'+urlname+'?order=MostFavoritedToday'+genreparam,     mode)
        addDir('Most Liked '+name+' This Week',        'http://www.vevo.com/'+urlname+'?order=MostFavoritedThisWeek'+genreparam,  mode)
        addDir('Most Liked '+name+' This Month',       'http://www.vevo.com/'+urlname+'?order=MostFavoritedThisMonth'+genreparam, mode)
        addDir('Most Liked '+name+' All Time',         'http://www.vevo.com/'+urlname+'?order=MostFavoritedAllTime'+genreparam,   mode)

def choiceGenres(url, mode):
        if mode == 8:
                urlname = 'artists'
                mode = 11
                rmode = 2
        elif mode == 9:
                urlname = 'videos'
                mode = 13
                rmode= 4
        addDir('Most Liked',url, mode)
        addDir('Most Viewed',url, mode+1)
        addDir('Most Recent', 'http://www.vevo.com/'+urlname+'?order=MostRecent&genre='+url, rmode)
        
def listGenres(mode):
        if mode == 'artist':
                mode = 8
                urlname = 'artists'
        elif mode == 'video':
                mode = 9
                urlname = 'videos'    
        addDir('Alternative','alternative',mode)
        addDir('Blues','blues',mode)
        addDir("Children's Music",'childrens-music',mode)
        addDir('Classical','classical',mode)
        addDir('Comedy/Humor','comedyhumor',mode)
        addDir('Country','country',mode)
        addDir('Electronic/Dance','electronicdance',mode)
        addDir('Christian & Gospel','christian-gospel',mode)
        addDir('Holiday','holiday',mode)
        addDir('Jazz','jazz',mode)
        addDir('Latino','latino',mode)
        addDir('Rock','rock',mode)
        addDir('Pop','pop',mode)
        addDir('R&B/Soul','rbsoul',mode)
        addDir('Reggae','reggae',mode)
        addDir('Rap/Hip-Hop','raphip-hop',mode)
        addDir('Soundtrack','soundtrack',mode)
        addDir('Spoken Word','spoken-word',mode)
        addDir('World','world',mode)
        addDir('Easy Listening','easy-listening',mode)
        addDir('Other','other',mode)

def listAZ(url):
        addDir('#', url+urllib.quote_plus('#'), 2)
        alphabet=set(string.ascii_uppercase)
        for letter in alphabet:
                print url
                newurl = url+str(letter)
                addDir(letter, newurl, 2)
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

def listVideos(url):
        data = getURL(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        try:
                pagenext = tree.find(attrs={'class' : 'next'})
                addDir(pagenext.string+' Page', BASE_URL+pagenext['href'], 4)
        except:
                print 'No Next Page'
        try:
                pageprev = tree.find(attrs={'class' : 'prev'})
                addDir(pageprev.string+' Page', BASE_URL+pageprev['href'], 4)
        except:
                print 'No Previous Page'
        videos = tree.findAll(attrs={'class' : 'listThumb'})
        for video in videos:
                url = BASE_URL+video.find(attrs={'class' : 'playOverlay'})['href']
                thumbnail = video.img['src']
                title = video.img['alt']
                addLink(title, url, 10, iconimage=thumbnail)

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

#===============================================================================
# if mode==None or url==None:
#        print "CATEGORY INDEX : "
#        listCategories()
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==1:
#        listAZ(url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==2:
#        listArtist(url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==3:
#        listArtistVideos(url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==4:
#        listVideos(url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==5:
#        mostViewed(url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==6:
#        mostLiked(url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==7:
#        listGenres(url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==8:
#        choiceGenres(url, mode)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==9:
#        choiceGenres(url, mode)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==11:
#        mostLiked('artist',url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==12:
#        mostViewed('artist',url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==13:
#        mostLiked('video',url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1]))
# elif mode==14:
#        mostViewed('video',url)
#        xbmcplugin.endOfDirectory(int(sys.argv[1])) 
# elif mode==10:
#        getVideo(url)
#===============================================================================

