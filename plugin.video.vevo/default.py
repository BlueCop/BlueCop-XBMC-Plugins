#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, re
import string, os, time, datetime

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import addoncompat

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson

pluginhandle = int(sys.argv[1])
xbmcplugin.setContent(pluginhandle, 'musicvideos')

BASE = 'http://www.vevo.com'

# Root listing
def listCategories():
    addDir('Music Videos',  'http://www.vevo.com/videos',       'rootVideos')
    addDir('Search Videos', '',                                 'searchVideos')
    addDir('Artists',       'http://www.vevo.com/artists',      'rootArtists')
    addDir('Search Artists','',                                 'searchArtists')
    addDir('Playlists',     '',                                 'rootPlaylists')
    addDir('Shows',         'http://www.vevo.com/shows',        'rootShows')
    addDir('Channels',      'http://www.vevo.com/channels',     'rootChannels')
    xbmcplugin.endOfDirectory(pluginhandle)

# Video listings
def rootVideos():
    videos_url = params['url']
    addGenres(videos_url, 'sortByVideo')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def sortByVideo():
    url = params['url']
    if '?' in url:
        urlsplit = url.split('?')
        url = urlsplit[0]
        parameters = '?'+urlsplit[1]+'&'
    else:
        parameters = '?'
    addDir('Most Recent',   url+'/videosbrowse'+parameters+'order=MostRecent',      'listVideos')
    addDir('Most Liked',    url+'/videosbrowse'+parameters+'order=MostFavorited',   'sortWhenVideo')
    addDir('Most Viewed',   url+'/videosbrowse'+parameters+'order=MostViewed',      'sortWhenVideo')
    xbmcplugin.endOfDirectory(pluginhandle)

def sortWhenVideo():
    url = params['url']
    if 'MostFavorited' in url:
        name = 'Most Liked'
    elif 'MostViewed' in url:
        name = 'Most Viewed'
    addDir(name+' Today',         url+'Today',      'listVideos')
    addDir(name+' This Week' ,    url+'ThisWeek',   'listVideos')
    addDir(name+' This Month',    url+'ThisMonth',  'listVideos')
    addDir(name+' All-Time',      url+'AllTime',    'listVideos')
    xbmcplugin.endOfDirectory(pluginhandle)

def listVideos(url = False):
    if not url:
        url = params['url']
    if '/videosbrowse' in url:
        addDir('*Next Page*',      url.replace('/videosbrowse?','/videos?page=2&'),    'listVideos')
    elif 'page=' in url:
        page = int(url.split('page=')[1].split('&')[0])
        nextpage = page + 1
        addDir('*Next Page*',      url.replace('page='+str(page),'page='+str(nextpage)),    'listVideos')
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    thumbs = tree.findAll(attrs={'class' : 'listThumb'})
    videos = tree.findAll(attrs={'class' : 'listContent'})
    for video,thumb in zip(videos,thumbs):
        url = BASE+thumb.find(attrs={'class' : 'playOverlay'})['href'].split('?')[0]
        thumbnail = thumb.img['src'].split('?')[0]
        tags = re.compile(r'<.*?>')
        spaces = re.compile(r'\s+')
        title = video.find('h4', attrs={'class' : 'ui-ellipsis'}).a.string.encode('utf-8')
        title = unicode(BeautifulSoup(title,convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0]).encode( "utf-8" )
        artist = str(video.find('h5')).decode('utf-8').encode('utf-8')
        artist = tags.sub('', artist)
        artist = spaces.sub(' ', artist)
        artist = unicode(BeautifulSoup(artist,convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0]).encode( "utf-8" )
        u = sys.argv[0]
        u += '?url='+urllib.quote_plus(url)
        u += '&mode='+urllib.quote_plus('playVideo')
        displayname = artist+' - '+title
        item=xbmcgui.ListItem(displayname, iconImage=thumbnail, thumbnailImage=thumbnail)
        item.setInfo( type="Music", infoLabels={ "Title":title,
                                                 "Artist":artist
                                                 })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# common genre listing for artists and videos
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
                if 'Video Premieres' in name:
                    url = 'http://www.vevo.com/videos/videosbrowse/is-premiere?order=MostRecent'
                    addDir(name, url, 'listVideos')
                    continue
                if 'subgenre' in url:
                    name = ' - '+name
                addDir(name, url, mode)

# Artist listings
def rootArtists():
    artist_url = params['url']
    addGenres(artist_url, 'sortByArtists')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def sortByArtists():
    url = params['url']
    if '?' in url:
        urlsplit = url.split('?')
        url = urlsplit[0]
        parameters = '?'+urlsplit[1]+'&'
    else:
        parameters = '?'
    addDir('Alphabetical',  url+'/artistsbrowse'+parameters+'order=Alphabetic',      'listAZ')
    addDir('Most Recent',   url+'/artistsbrowse'+parameters+'order=MostRecent',      'listArtists')
    addDir('Most Liked',    url+'/artistsbrowse'+parameters+'order=MostFavorited',   'sortWhenArtists')
    addDir('Most Viewed',   url+'/artistsbrowse'+parameters+'order=MostViewed',      'sortWhenArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def sortWhenArtists():
    url = params['url']
    if 'MostFavorited' in url:
        name = 'Most Liked'
    elif 'MostViewed' in url:
        name = 'Most Viewed'
    addDir(name+' Today',         url+'Today',      'listArtists')
    addDir(name+' This Week' ,    url+'ThisWeek',   'listArtists')
    addDir(name+' This Month',    url+'ThisMonth',  'listArtists')
    addDir(name+' All-Time',      url+'AllTime',    'listArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def listAZ():
    url = params['url']
    #addDir('#', url+'&alpha='+urllib.quote_plus('#'), 'listVideos')
    alphabet=set(string.ascii_uppercase)
    for letter in alphabet:
        addDir(letter, url+'&alpha='+str(letter), 'listArtists')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle)

def listArtists(url = False):
    if not url:
        url = params['url']
    if '/artistsbrowse' in url:
        addDir('*Next Page*',      url.replace('/artistsbrowse?','/artists?page=2&'),    'listArtists')
    elif 'page=' in url:
        page = int(url.split('page=')[1].split('&')[0])
        nextpage = page + 1
        addDir('*Next Page*',      url.replace('page='+str(page),'page='+str(nextpage)),    'listArtists')
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    artists = tree.findAll(attrs={'class' : 'playOverlay'})
    for artist in artists:
        print artist
        url = BASE+artist['href']
        thumbnail = artist.find('img')['src'].split('?')[0]
        try:title = artist.find('img')['title'].encode('utf-8')
        except:title = artist.find('img')['alt'].encode('utf-8')
        addDir(title, url, 'listVideos', iconimage=thumbnail)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# Playlist listings
def rootPlaylists():
    listPlaylists('http://www.vevo.com/playlists/playlistsbrowse')
    listPlaylists('http://www.vevo.com/playlists/playlists?page=2')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True) 

def listPlaylists(url):
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    playlists = tree.findAll(attrs={'class' : 'listThumb'})
    for playlist in playlists:
        url = BASE+playlist.a['href']
        thumbnail = playlist.find('img')['src'].split('?')[0]
        title = playlist.find('img')['alt']
        addDir(title, url, 'playPlaylists', iconimage=thumbnail,isplayable=True)

def playPlaylists():
    url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('meta',attrs={'property' : 'og:song','content':True})
    stacked_url = 'stack://'
    for video in videos:
        url = getVideo(video['content'])
        stacked_url += url.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(path=stacked_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item) 

# Show listings
def rootShows():
    url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows = tree.findAll(attrs={'class' : 'listThumb'})
    for show in shows:
        url = BASE+show.a['href'].replace('/show/','/show/detailcontentlist/')+'?page=1'
        thumbnail = show.find('img')['src'].split('?')[0]
        title = show.find('img')['title']
        addDir(title, url, 'listVideos', iconimage=thumbnail)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# Channel listings    
def rootChannels(url = False):
    if not url:
        url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows = tree.findAll(attrs={'class' : 'listThumb'})
    for show in shows:
        url = BASE+show.a['href']+'?page=1'
        thumbnail = show.find('img')['src'].split('?')[0]
        title = show.find('img')['title']
        addDir(title, url, 'listVideos', iconimage=thumbnail)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# Search
def searchVideos():
    Search('Videos')

def searchArtists():
    Search('Artists')    
    
def Search(mode):
        keyb = xbmc.Keyboard('', 'Search '+mode)
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = urllib.quote_plus(keyb.getText())
                url = 'http://www.vevo.com/search?q='+search+'&content='+mode+'&page=1'
                if mode == 'Videos':
                    listVideos(url)
                elif mode == 'Artists':
                    rootChannels(url)
    
# Play Video
def playVideo():
    item = xbmcgui.ListItem(path=getVideo(params['url']))
    xbmcplugin.setResolvedUrl(pluginhandle, True, item) 
    import time
    time.sleep(4)
    xbmc.Player().pause()

def getVideo(pageurl):
    quality = [564000, 864000, 1328000, 1728000, 2528000, 3328000, 4392000, 5392000]
    select = int(addoncompat.get_setting('bitrate'))
    maxbitrate = quality[select]
    vevoID = pageurl.split('/')[-1]
    url = 'http://smilstream.vevo.com/HDFlash/v1/smil/%s/%s.smil' % (vevoID,vevoID.lower())
    data = getURL(url)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    videobase = tree.find(attrs={'name':'httpBase'})['content']
    videos = tree.findAll('video')
    filenames = ''
    number = len(videos) - 1
    if number < select:
        select = number
    if '_' in videos[number]:
        for video in videos:
            filepath = video['src']
            path = filepath.split('_')[0]
            filename = filepath.replace(path,'').replace('.mp4','')
            filenames += filename+','
    else:
        for video in videos:
            filepath = video['src']
            filename = filepath.split('/')[-1]
            path = filepath.replace(filename,'')
            filenames += filename.replace('.mp4','')+','              
    finalUrl = videobase+path+','+filenames+'.mp4.csmil/bitrate='+str(select)+'?seek=0'
    return finalUrl

# Common                
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

def addDir(name, url, mode, plot='', iconimage='DefaultFolder.png' ,isplayable=False):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)
    item=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if isplayable:
        item.setProperty('IsPlayable', 'true')
        folder = False
    else:
        folder = True
    return xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=folder)

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
try:
    mode=params["mode"]
except:
    mode=None
print "Mode: "+str(mode)
print "Parameters: "+str(params)

if mode==None:
    listCategories()
else:
    exec '%s()' % mode
