#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import string, os, re, time, datetime

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson

import unicodedata 

pluginhandle = int(sys.argv[1])
xbmcplugin.setContent(pluginhandle, 'musicvideos')

addon = xbmcaddon.Addon('plugin.video.vevo')
pluginpath = addon.getAddonInfo('path')

BASE = 'http://www.vevo.com'
COOKIEFILE = os.path.join(pluginpath,'resources','vevo-cookies.lwp')
USERFILE = os.path.join(pluginpath,'resources','userfile.js')

# Root listing

def listCategories():
    addDir('Video Premieres',    'http://api.vevo.com/mobile/v1/video/list.json?ispremiere=true',   'listVideos')
    addDir('Staff Picks',        'http://api.vevo.com/mobile/v1/featured/TopVideos.json?',          'listVideos')
    addDir('Music Videos',       'http://api.vevo.com/mobile/v1/video/list.json',                   'rootVideos')
    addDir('Search Videos',      '',                                                                'searchVideos')
    addDir('Artists',            'http://api.vevo.com/mobile/v1/artist/list.json',                  'rootArtists')
    addDir('Search Artists',     '',                                                                'searchArtists')
    #addDir('Favorite Artists',   '',                                                                '')
    #addDir('Favorite Videos',    '',                                                                '')
    addDir('Shows',               'http://api.vevo.com/mobile/v1/show/list.json?',                    'rootShows')
    xbmcplugin.endOfDirectory(pluginhandle)
    
# Video listings
def rootVideos():
    videos_url = params['url']
    addGenres(videos_url, 'sortByVideo')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def sortByVideo():
    url = params['url']
    addDir('Most Recent',   url+'&order=MostRecent',      'listVideos')
    addDir('Most Liked',    url+'&order=MostFavorited',   'sortWhenVideo')
    addDir('Most Viewed',   url+'&order=MostViewed',      'sortWhenVideo')
    addDir('Surprise Me',   url+'&order=Random',          'listVideos')
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
    max = 100
    page = int(params['page'])
    offset = (page-1)*max
    fetch_url=url+'&offset='+str(offset)+'&max='+str(max)+'&extended=true'
    data = getURL(fetch_url)
    print data
    videos = demjson.decode(data)['result']
    total = len(videos)
    if total >= max:
        addDir('*Next Page*', url,    'listVideos', page=str(page+1))
    for video in videos:
        video_id = video['isrc']
        title = video['title']
        video_image = video['image_url']
        duration = video['duration_in_seconds']

        if len(video['artists_main']) > 0:
            artistdata = video['artists_main'][0]
            artist_id = artistdata['id']
            artist_name = artistdata['name']
            artist_image = artistdata['image_url']
        else:
            artist_name = ''
    
        if len(video['artists_featured']) > 0:
            featuredartist = video['artists_featured'][0]
            featuredartist_id = featuredartist['id']
            featuredartist_name = featuredartist['name']
            featuredartist_image = featuredartist['image_url']
            artist = artist_name+' feat. '+featuredartist_name
        else:
            artist = artist_name
        u = sys.argv[0]
        u += '?url='+urllib.quote_plus(video_id)
        u += '&mode='+urllib.quote_plus('playVideo')
        displayname = artist+' - '+title
        item=xbmcgui.ListItem(displayname, iconImage=video_image, thumbnailImage=video_image)
        item.setInfo( type="Music", infoLabels={ "Title":title,
                                                 "Artist":artist,
                                                 "Duration":duration})
        item.setProperty('fanart_image',artist_image)
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False,totalItems=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# common genre listing for artists and videos
def addGenres(url,mode):
    data = getURL('http://api.vevo.com/mobile/v1/genre/list.json?culture=en_US')
    genres = demjson.decode(data)['result']
    addDir('All Genres', url+'?', mode)
    for genre in genres:
        name = genre['Value']
        furl = url+'?genres='+genre['Key']
        addDir(name, furl, mode)

# Artist listings
def rootArtists():
    artist_url = params['url']
    addGenres(artist_url, 'sortByArtists')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def sortByArtists():
    url = params['url']
    #addDir('Alphabetical',  url+'&order=Alphabetic',      'listAZ')
    addDir('Most Recent',   url+'&order=MostRecent',      'listArtists')
    addDir('Most Liked',    url+'&order=MostFavorited',   'sortWhenArtists')
    addDir('Most Viewed',   url+'&order=MostViewed',      'sortWhenArtists')
    addDir('Surprise Me',   url+'&order=Random',          'listArtists')
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
    addDir('#', url+'&alpha='+urllib.quote_plus('#'), 'listVideos')
    alphabet=set(string.ascii_uppercase)
    for letter in alphabet:
        addDir(letter, url+'&alpha='+str(letter), 'listArtists')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle)

def listArtists(url = False):
    if not url:
        url = params['url']
    max = 100
    page = int(params['page'])
    offset = (page-1)*max
    fetch_url=url+'&offset='+str(offset)+'&max='+str(max)
    data = getURL(fetch_url)
    artists = demjson.decode(data)['result']
    total = len(artists)
    if total >= max:
        addDir('*Next Page*', url,    'listArtists', page=str(page+1))
    for artist in artists:
        artist_id = artist['id']
        artist_name = artist['name']
        artist_image = artist['image_url']
        video_count = artist['video_count']
        url = 'http://api.vevo.com/mobile/v1/artist/'+artist_id+'/videos.json?order=MostRecent'
        display_name=artist_name+' ('+str(video_count)+')'
        addDir(display_name, url, 'listVideos', iconimage=artist_image, total=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# Playlist listings
def rootPlaylists():
    url = params['url']
    addGenres(url, 'listPlaylists')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True) 
    
def myPlaylists():
    url = params['url']
    #userfile = open(USERFILE, "r")
    #userdata = userfile.read()
    #userfile.close()
    #userid = demjson.decode(userdata)['userId']
    #url += str(userid)
    listPlaylists(url,alloptions=True)

def listPlaylists(url = False,alloptions=False):
    if not url:
        url = params['url'].replace('/playlists','/playlists/playlistsbrowse')
    if alloptions:
        addDir('(Play All)', url, 'playAllPlaylists',folder=False)
        addDir('(Queue All)', url, 'queueAllPlaylists',folder=False)
        addDir('(Shuffle All)', url, 'shufflePlaylist',folder=False)
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    playlists = tree.findAll(attrs={'class' : 'listThumb'})
    for playlist in playlists:
        url = BASE+playlist.a['href']
        thumbnail = playlist.find('img')['src'].split('?')[0]
        title = playlist.find('img')['alt']
        addDir(title, url, 'playlistRoot', iconimage=thumbnail)
    if 'Show More Playlists' in data:
        url2 = params['url'].replace('/playlists','/playlists/playlists')+'?page=2' 
        listPlaylists(url2)
    else:
        xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def shufflePlaylist():
    queueAllPlaylists()
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.shuffle()
    xbmc.Player().play(playlist)

def playAllPlaylists():
    queueAllPlaylists(play=True)
    
def queueAllPlaylists(url = False,play=False):
    if not url:
        url = params['url']
    if play:
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    playlists = tree.findAll(attrs={'class' : 'listThumb'})
    for playlist in playlists:
        url = BASE+playlist.a['href']
        handlePlaylist(url=url)
    if 'Show More Playlists' in data:
        url2 = params['url'].replace('/playlists','/playlists/playlists')+'?page=2' 
        queueAllPlaylists(url=url2,play=play)
    else:
        if play:
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            xbmc.Player().play(playlist)


def playlistRoot():
    url = params['url']
    addDir('Play', url, 'playPlaylist',folder=False)
    addDir('Queue', url, 'queuePlaylist',folder=False)
    addDir('List', url, 'listPlaylist',folder=True)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    
def playPlaylist():
    handlePlaylist(play=True)
    
def queuePlaylist(url=False):
    handlePlaylist()

def listPlaylist():
    handlePlaylist(list=True)

def handlePlaylist(url=False,play=False,list=False):
    if not url:
        url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('meta',attrs={'property' : 'og:song','content':True})
    vids = ''
    for video in videos:
        vids += video['content'].split('/')[-1]+','
    vids = vids[:-1]
    infourl = 'http://www.vevo.com/Proxy/Video/GetData.ashx?isrc='+urllib.quote_plus(vids)
    data = getURL(infourl)
    playlistvideos = demjson.decode(data)
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    if play:
        playlist.clear()
    total = len(videos)
    for video in videos:
        video = playlistvideos[video['content'].split('/')[-1]]
        artist = video['byline_text']
        title = video['video_name']
        thumbnail = video['image']
        url = BASE+video['video_url']
        u = sys.argv[0]
        u += '?url='+urllib.quote_plus(url)
        u += '&mode='+urllib.quote_plus('playlistVideo')
        displayname = artist+' - '+title
        item=xbmcgui.ListItem(displayname, iconImage=thumbnail, thumbnailImage=thumbnail)
        item.setInfo( type="Video", infoLabels={ "Title":displayname
                                                 #"Artist":artist
                                                 })
        item.setProperty('IsPlayable', 'true')
        if list:
            xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False,totalItems=total)
        else:
            playlist.add(url=u, listitem=item)
    if play:
        xbmc.Player().play(playlist)
    elif list:
        xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    
# Show listings
def rootShows(url = False):
    xbmcplugin.setContent(pluginhandle, 'shows')
    if not url:
        url = params['url']
    max = 100
    page = int(params['page'])
    offset = (page-1)*max
    fetch_url=url+'&offset='+str(offset)+'&max='+str(max)
    data = getURL(fetch_url)
    shows = demjson.decode(data)['result']
    total = len(shows)
    if total >= max:
        addDir('*Next Page*', url,    'listArtists', page=str(page+1))
    for show in shows:
        show_id = show['id']
        show_name = show['name']
        show_image = show['image_url']
        #video_count = show['video_count']
        description = show['description']
        url = 'http://api.vevo.com/mobile/v1/show/'+str(show_id)+'/videos.json?order=MostRecent'
        display_name=show_name
        addDir(display_name, url, 'listVideos', plot=description, iconimage=show_image, total=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# Search
def searchVideos():
    url = 'http://api.vevo.com/mobile/v1/search/videos.json?extended=false'
    Search('Videos',url)

def searchArtists():
    url = 'http://api.vevo.com/mobile/v1/search/artists.json?extended=false'
    Search('Artists',url)

def Search(mode,url):
        keyb = xbmc.Keyboard('', 'Search '+mode)
        keyb.doModal()
        if keyb.isConfirmed():
                search = urllib.quote_plus(keyb.getText())
                url += '&q='+search
                if mode == 'Videos':
                    listVideos(url)
                elif mode == 'Artists':
                    listArtists(url)
    
# Play Video
def playVideo():
    playlistVideo()

def playlistVideo():
    try:
        item = xbmcgui.ListItem(path=getVideo(params['url']))
        xbmcplugin.setResolvedUrl(pluginhandle, True, item) 
        if addon.getSetting('unpause') == 'true':
            import time
            sleeptime = int(addon.getSetting('unpausetime'))+1
            time.sleep(sleeptime)
            xbmc.Player().pause()
    except:
        vevoID = params['url'].split('/')[-1]
        url = 'http://videoplayer.vevo.com/VideoService/AuthenticateVideo?isrc=%s' % vevoID
        data = getURL(url)
        youtubeID = demjson.decode(data)['video']['videoVersions'][0]['id']
        youtubeurl = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % youtubeID
        item = xbmcgui.ListItem(path=youtubeurl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        
def getVideo(pageurl):
    quality = [564000, 864000, 1328000, 1728000, 2528000, 3328000, 4392000, 5392000]
    select = int(addon.getSetting('bitrate'))
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
def addDir(name, url, mode, plot='', iconimage='DefaultFolder.png' ,folder=True,total=0,page=1):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+'&page='+str(page)
    item=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if iconimage <> 'DefaultFolder.png':
        item.setProperty('fanart_image',iconimage)
    item.setInfo( type="Video", infoLabels={ "Title":name,
                                             "plot":plot
                                           })
    return xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=folder,totalItems=total)

def getURL( url , extraheader=True):
    print 'VEVO --> common :: getURL :: url = '+url
    cj = cookielib.LWPCookieJar()
    #if os.path.isfile(COOKIEFILE):
    #    cj.load(COOKIEFILE, ignore_discard=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Referer', 'http://www.vevo.com'),
                         ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)')]
    if extraheader:
        opener.addheaders = [('X-Requested-With', 'XMLHttpRequest')]
    usock=opener.open(url)
    response=usock.read()
    usock.close()
    #if os.path.isfile(COOKIEFILE):
    #    cj.save(COOKIEFILE, ignore_discard=True)
    return response

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
