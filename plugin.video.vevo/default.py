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

fanart = os.path.join(pluginpath,'fanart.jpg')
vicon = os.path.join(pluginpath,'icon.png')
maxperpage=(int(addon.getSetting('perpage'))+1)*25


# Root listing

def listCategories():
    addDir('Video Premieres',    'http://api.vevo.com/mobile/v1/video/list.json?ispremiere=true',   'listVideos')
    addDir('Music Videos',       'http://api.vevo.com/mobile/v1/video/list.json',                   'rootVideos')
    addDir('Search Videos',      '',                                                                'searchVideos')
    addDir('Artists',            'http://api.vevo.com/mobile/v1/artist/list.json',                  'rootArtists')
    addDir('Search Artists',     '',                                                                'searchArtists')
    #addDir('My Artists',         ' ',   ' ')
    addDir('Shows',               'http://api.vevo.com/mobile/v1/show/list.json?',                  'rootShows')
    addDir('Staff Picks',        '',                                                                'listStaffPicks')
    addDir('Top Playlists',        'http://api.vevo.com/mobile/v1/featured/staffpicks.json',        'listPlaylists')
    xbmcplugin.endOfDirectory(pluginhandle)

def listStaffPicks():
    addDir('Video Picks',        'http://api.vevo.com/mobile/v1/featured/TopVideos.json?',          'listVideos')
    addDir('Playlist Picks',     'http://api.vevo.com/mobile/v3/featured/TopPlaylists.json?',       'listPlaylists')
    xbmcplugin.endOfDirectory(pluginhandle)

# Video listings
def rootVideos():
    videos_url = params['url']
    addGenres(videos_url, 'sortByVideo')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def sortByVideo():
    url = params['url']
    addDir('Most Viewed',   url+'&order=MostViewed',      'sortWhenVideo')
    addDir('Most Liked',    url+'&order=MostFavorited',   'sortWhenVideo')
    addDir('Most Recent',   url+'&order=MostRecent',      'listVideos')
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
    
def listVideos(url = False,playlist=False,playall=False):
    if not url:
        url = params['url']
    max = maxperpage
    page = int(params['page'])
    offset = (page-1)*max
    fetch_url=url+'&offset='+str(offset)+'&max='+str(max)+'&extended=true'
    data = getURL(fetch_url)
    if data:
        if playlist:
            videos = demjson.decode(data)['result']['videos']
        else:
            videos = demjson.decode(data)['result']
        total = len(videos)
        if playall:
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()        
        elif playlist is False:
            total = len(videos)
            if total >= max:
                addDir('*Next Page*', url,    'listVideos', page=str(page+1))
            addDir('*Play All*', url, 'playAll',folder=False)
        for video in videos:
            video_id = video['isrc']
            try:title = video['title'].encode('utf-8')
            except: title = ''
            video_image = video['image_url']
            duration = video['duration_in_seconds']
            try:year = int(video['video_year'])
            except:year = 0
            
            credits = video['credit']
            try:
                for credit in credits:
                    if credit['Key'] == 'Genre':
                        genre = credit['Value']
                    #elif credit['Key'] == 'Producer':
                    #    pass
                    #elif credit['Key'] == 'Director':
                    #    pass
                    #elif credit['Key'] == 'Composer':
                    #    pass
                    elif credit['Key'] == 'Record Label':
                        recordlabel = credit['Value']
            except:
                  genre = credits['Genre']
                  recordlabel = credits['Record Label']      
    
            if len(video['artists_main']) > 0:
                artistdata = video['artists_main'][0]
                artist_id = artistdata['id']
                artist_name = artistdata['name'].encode('utf-8')
                artist_image = artistdata['image_url']
            else:
                artist_name = ''
                artist_image = ''
        
            if len(video['artists_featured']) > 0:
                feats=''
                for featuredartist in video['artists_featured']:
                    #featuredartist_id = featuredartist['id']
                    #featuredartist_image = featuredartist['image_url']
                    featuredartist_name = featuredartist['name'].encode('utf-8')
                    feats= featuredartist_name+', '
                feats=feats[:-2]
                artist = artist_name+' feat. '+feats
            else:
                artist = artist_name
            u = sys.argv[0]
            u += '?url='+urllib.quote_plus(video_id)
            u += '&mode='+urllib.quote_plus('playVideo')
            displayname = artist+' - '+title
            item=xbmcgui.ListItem(displayname, iconImage=video_image, thumbnailImage=video_image)
            item.setInfo( type="Music", infoLabels={ "Title":title,
                                                     "Artist":artist,
                                                     "Duration":duration,
                                                     "Album":recordlabel,
                                                     "Genre":genre,
                                                     "Year":year})
            item.setProperty('fanart_image',artist_image)
            item.setProperty('IsPlayable', 'true')
            if playall:
                playlist.add(url=u, listitem=item)
            else:
                xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)#,totalItems=total)
        if playall:
            xbmc.Player().play(playlist)
        else:
            xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def playAll():
    listVideos(params['url'],playall=True)
    
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
    addDir('Most Viewed',   url+'&order=MostViewed',      'sortWhenArtists')
    addDir('Most Liked',    url+'&order=MostFavorited',   'sortWhenArtists')
    addDir('Most Recent',   url+'&order=MostRecent',      'listArtists')
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
    max = maxperpage
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
def listPlaylists(url = False):
    if not url:
        url = params['url']
    #max = maxperpage
    #page = int(params['page'])
    #offset = (page-1)*max
    #fetch_url=url+'&offset='+str(offset)+'&max='+str(max)#+'&extended=true'
    #data = getURL(fetch_url)
    data = getURL(url)
    playlists = demjson.decode(data)['result']
    total = len(playlists)
    #if total >= max:
    #    addDir('*Next Page*', url,    'listPlaylists', page=str(page+1))
    for playlist in playlists:
        try:playlist_id = playlist['playlist_id']
        except:playlist_id = str(playlist['id'])
        playlist_name = playlist['title']
        playlist_image = playlist['image_url']
        video_count = playlist['videocount']
        display_name=playlist_name+' ('+str(video_count)+')'
        addDir(display_name, playlist_id, 'playlistRoot', iconimage=playlist_image, total=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def playlistRoot():
    playlist_id = params['url']
    if playlist_id.isdigit():
        url = 'http://api.vevo.com/mobile/v1/playlist/'+playlist_id+'.json?'
    else:
        url = 'http://api.vevo.com/mobile/v2/playlist/'+playlist_id+'.json?'
    addDir('*Play*', url, 'playPlaylist',folder=False)
    listVideos(url,playlist=True)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def playPlaylist():
    listVideos(params['url'],playlist=True,playall=True)

# Show listings
def rootShows(url = False):
    xbmcplugin.setContent(pluginhandle, 'shows')
    if not url:
        url = params['url']
    max = maxperpage
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
        video_count = show['total_videos_count']
        description = show['description']
        url = 'http://api.vevo.com/mobile/v1/show/'+str(show_id)+'/videos.json?order=MostRecent'
        display_name=show_name+' ('+str(video_count)+')'
        addDir(display_name, url, 'listVideos', plot=description, iconimage=show_image, total=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# Search
def searchVideos():
    url = 'http://api.vevo.com/mobile/v1/search/videos.json?'
    Search('Videos',url)

def searchArtists():
    url = 'http://api.vevo.com/mobile/v1/search/artists.json?'
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
    if addon.getSetting('defaultyoutube') == 'true':
        try:YouTube()
        except:HTTPDynamic()
    else:  
        try:HTTPDynamic()
        except:YouTube()

def HTTPDynamic():
    item = xbmcgui.ListItem(path=getVideo(params['url']))
    xbmcplugin.setResolvedUrl(pluginhandle, True, item) 
    if addon.getSetting('unpause') == 'true':
        import time
        sleeptime = int(addon.getSetting('unpausetime'))+1
        time.sleep(sleeptime)
        xbmc.Player().pause()

def YouTube():
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
def addDir(name, url, mode, plot='', iconimage=vicon ,folder=True,total=0,page=1):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+'&page='+str(page)
    item=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if iconimage <> vicon:
        item.setProperty('fanart_image',iconimage)
    else:
        item.setProperty('fanart_image',fanart)
    item.setInfo( type="Video", infoLabels={ "Title":name,
                                             "plot":plot
                                           })
    return xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=folder,totalItems=total)

def getURL( url , extraheader=True):
    try:
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
    except urllib2.URLError, e:
        print 'Error reason: ', e
        heading = 'Error'
        message = e
        duration = 10000
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
        return False

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