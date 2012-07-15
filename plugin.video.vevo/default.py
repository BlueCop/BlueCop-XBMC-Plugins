#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import string, os, re, time, datetime, math, time, unicodedata, types
import threading

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson

import facebook
from facebook import GraphAPIError, GraphWrapAuthError

import mechanize

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

pluginhandle = int(sys.argv[1])
#xbmcplugin.setContent(pluginhandle, 'musicvideos')

addon = xbmcaddon.Addon('plugin.video.vevo')
pluginpath = addon.getAddonInfo('path')
datapath = xbmc.translatePath('special://profile/addon_data/plugin.video.vevo/')
cachepath = xbmc.translatePath(addon.getSetting('cache-folder'))

BASE = 'http://www.vevo.com'
COOKIEFILE = os.path.join(pluginpath,'resources','vevo-cookies.lwp')
#USERFILE = os.path.join(pluginpath,'resources','userfile.js')
FAVFILE = os.path.join(datapath,'favs.json')
FAVFILESQL = os.path.join(datapath,'favs.sqlite')
CACHEDB = os.path.join(datapath,'cache.sqlite')

fanart = os.path.join(pluginpath,'fanart.jpg')
vicon = os.path.join(pluginpath,'icon.png')
maxperpage=(int(addon.getSetting('perpage'))+1)*25

# Root listing

def listCategories():
    addDir('Featured',    'http://api.vevo.com/mobile/v2/featured/carousel.json?',   'listFeatured')
    addDir('Premieres',   'http://api.vevo.com/mobile/v1/video/list.json?ispremiere=true',        'listVideos')
    addDir('Staff Picks',        '',                                                                'listStaffPicks')
    if (addon.getSetting('latitude') == 'Lookup by IP') and (addon.getSetting('latitude') == 'Lookup by IP'):
        setLocation()
    if (addon.getSetting('latitude') <> '') or (addon.getSetting('latitude') <> ''):
        cm = []
        u=sys.argv[0]+"?url="+urllib.quote_plus('')+"&mode="+urllib.quote_plus('setLocation')+'&page='+str(1)
        cm.append( ('Set Location by IP', "XBMC.RunPlugin(%s)" % u) )
        addDir('Trending',        '',                                                 'Trending', cm=cm)
        addDir('Touring',          '',                                               'toursRightNow', cm=cm)
    addDir('Videos',       'http://api.vevo.com/mobile/v1/video/list.json',                'rootVideos')
    addDir('Artists',            'http://api.vevo.com/mobile/v1/artist/list.json',         'rootArtists')
    addDir('Shows',               'http://api.vevo.com/mobile/v1/show/list.json?',                  'rootShows')
    cm = []
    u=sys.argv[0]+"?url="+urllib.quote_plus('')+"&mode="+urllib.quote_plus('rematchArtists')+'&page='+str(1)
    cm.append( ('Rematch Library Artists', "XBMC.RunPlugin(%s)" % u) )
    u=sys.argv[0]+"?url="+urllib.quote_plus('')+"&mode="+urllib.quote_plus('deletefavArtists')+'&page='+str(1)
    cm.append( ('Delete All Artists', "XBMC.RunPlugin(%s)" % u) )
    addDir('Favorite Artists',         '',                                                          'favArtists' , cm=cm)
    addDir('Playlists',        'http://api.vevo.com/mobile/v1/featured/staffpicks.json',            'rootPlaylists')
    addDir('Search',             '',                                                                'searchArtists')
    #addDir('Search Videos',      '',                                                                'searchVideos')
    #addDir('Search Artists',     '',                                                                'searchArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def listStaffPicks():
    addDir('Video Picks',        'http://api.vevo.com/mobile/v1/featured/TopVideos.json?',          'listVideos')
    addDir('Playlist Picks',     'http://api.vevo.com/mobile/v3/featured/TopPlaylists.json?',       'listPlaylists')
    xbmcplugin.endOfDirectory(pluginhandle)

def Trending():
    addDir('Being Watched',        '',                                                 'watchingRightNowIn')
    addDir('Trending Now',         '',                                                 'TrendingRightNowIn')
    xbmcplugin.endOfDirectory(pluginhandle)

def listFeatured(url=False):
    xbmcplugin.setContent(pluginhandle, 'musicvideos')
    if not url:
        url = params['url']
    max = maxperpage
    page = int(params['page'])
    offset = (page-1)*max
    fetch_url=url+'&offset='+str(offset)+'&max='+str(max)+'&extended=true'
    data = getURL(fetch_url)
    if data:
        items = demjson.decode(data)['result']
        for item in items:
            image_url = item['image_url']
            primary_text = item['primary_text'].encode('utf-8')
            secondary_text = item['secondary_text'].encode('utf-8')
            action_url = item['action_url']
            is_live_stream = item['is_live_stream']
            image_wide_url  = item['image_wide_url']
            cm=[]
            if 'vevo://playlist/' in action_url:
                mode = 'playlistRoot'
                videoid = action_url.replace('vevo://playlist/','')
            elif 'vevo://video/' in action_url:
                mode = 'playVideo'
                videoid = action_url.replace('vevo://video/','')
                if addon.getSetting('session_token'):
                    u=sys.argv[0]+"?url="+urllib.quote_plus(videoid)+"&mode="+urllib.quote_plus('addVideo2Playlist')+'&page='+str(1)
                    cm.append( ('Add to Playlist', "XBMC.RunPlugin(%s)" % u) )
                    u=sys.argv[0]+"?url="+urllib.quote_plus(videoid)+"&mode="+urllib.quote_plus('newVideoPlaylist')+'&page='+str(1)
                    cm.append( ('Start New Playlist', "XBMC.RunPlugin(%s)" % u) )   
            
            if ':' in primary_text:
                primary_split = primary_text.split(':')
                primary_text = primary_split[1].strip()
                text = primary_split[0].strip().title()
            else:
                text = ''
            
            u='plugin://plugin.video.youtube/?path=/root/search&feed=search&search='+urllib.quote_plus(primary_text)+'&'
            cm.append( ('YouTube %s' % primary_text, "Container.Update(%s)" % u) )
            
            displayname = primary_text+' - '+secondary_text
            if text <> '':
                displayname +=' ('+text+')'
            if mode == 'playVideo':
                overlay = checkIDdb(videoid)
                if overlay:
                    dcu=sys.argv[0]+"?url="+urllib.quote_plus(videoid)+"&mode="+urllib.quote_plus('deleteCachedFile')+'&page='+urllib.quote_plus('1')
                    cm.append( ('Delete Cached File', "XBMC.RunPlugin(%s)" % dcu) )
                else:
                    overlay=0
            else:
                overlay=0
            u = sys.argv[0]
            u += '?url='+urllib.quote_plus(videoid)
            u += '&mode='+urllib.quote_plus(mode)
            u += '&duration='+urllib.quote_plus('210')
            item=xbmcgui.ListItem(displayname, iconImage=image_url, thumbnailImage=image_url)
            item.setInfo( type="Video", infoLabels={ "Title":secondary_text,
                                                     "Artist":primary_text,
                                                     "Album":primary_text,
                                                     "Studio":text,
                                                     "overlay":overlay,
                                                     })
            item.setProperty('fanart_image',image_wide_url)
            item.addContextMenuItems( cm )
            if mode == 'playVideo':
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)
            else:
                u += '&page=1'
                xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=True)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView()

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
    
def listArtistVideos():
    listVideos(artistlist=True)
    
def listVideosNoPage(url=False):
    listVideos(url=url,paginate=False)
               
def listVideos(url = False,playlist=False,playall=False,queue=False,VEVOToken=False,artistlist=False,paginate=True):
    xbmcplugin.setContent(pluginhandle, 'musicvideos')
    if artistlist:
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_GENRE)
        #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    if not url:
        url = params['url']
    if paginate:
        max = maxperpage
        page = int(params['page'])
        offset = (page-1)*max
        fetch_url=url+'&offset='+str(offset)+'&max='+str(max)+'&extended=true'
    else:
        fetch_url=url+'&extended=true'
    data = getURL(fetch_url,VEVOToken=VEVOToken)
    if data:
        if playlist:
            videos = demjson.decode(data)['result']['videos']
        else:
            videos = demjson.decode(data)['result']
        total = len(videos)
        if playall or queue:
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            if playall:
                playlist.clear()   
        elif playlist is False:
            total = len(videos)
            if paginate:
                if total >= max:
                    addDir('*Next Page*', url,    'listVideos', page=str(page+1))
            cm=[]
            u=sys.argv[0]+"?url="+urllib.quote_plus(fetch_url)+"&mode="+urllib.quote_plus('queueAll')+'&page='+urllib.quote_plus('1')
            cm.append( ('Queue All', "XBMC.RunPlugin(%s)" % u) )
            if addon.getSetting('session_token'):
                #if VEVOToken:
                u=sys.argv[0]+"?url="+urllib.quote_plus(fetch_url)+"&mode="+urllib.quote_plus('addVideoPlaylistURL')+'&page='+urllib.quote_plus('1')
                #cm.append( ('Save to Playlist', "XBMC.RunPlugin(%s)" % u) )
                u=sys.argv[0]+"?url="+urllib.quote_plus(fetch_url)+"&mode="+urllib.quote_plus('newVideoPlaylistURL')+'&page='+urllib.quote_plus('1')
                cm.append( ('New Playlist', "XBMC.RunPlugin(%s)" % u) )
            addDir('*Play All*', url, 'playAll',folder=False,cm=cm)
        count = 0
        for video in videos:
            video_id = video['isrc']
            try:title = video['title'].encode('utf-8')
            except: title = ''                  
            video_image = video['image_url']
            duration = video['duration_in_seconds']
            try:year = int(video['video_year'])
            except:year = 0

            genre = ''
            recordlabel = ''
            director = ''
            producer = ''
            composer = ''
            plot = ''
            if video.has_key('credit'):
                credits = video['credit']
                if isinstance(credits, list):
                    metadict={}
                    for credit in credits:
                        if credit['Key'] == 'Credit':
                            value = credit['Value']
                            if '=>' in value:
                                valuesplit = value.split('=>')
                                metadict[valuesplit[0].strip()]=valuesplit[1].strip()
                            else:
                                metadict[credit['Key']]=credit['Value']
                        else:
                            metadict[credit['Key']]=credit['Value']
                else:
                    metadict=credits
                for item in metadict:
                    plot+=item+' : '+metadict[item]+'\n' 
                if metadict.has_key('Director'):
                    director = metadict['Director']    
                if metadict.has_key('Record Label'):
                    recordlabel = metadict['Record Label']
                if metadict.has_key('Genre'):
                    genre = metadict['Genre']           
                if metadict.has_key('Composer'):
                    composer = metadict['Composer'] 
                if metadict.has_key('Producer'):
                    producer = metadict['Producer']                                              
       
            if len(video['artists_main']) > 0:
                artistdata = video['artists_main'][0]
                artist_id = artistdata['id']
                artist_name = artistdata['name'].encode('utf-8')
                artist_image = artistdata['image_url']
            else:
                artist_name = ''
                artist_id = ''
                artist_image = ''
            artists = {artist_id:artist_name}
            if len(video['artists_featured']) > 0:
                feats=''
                for featuredartist in video['artists_featured']:
                    featuredartist_id = featuredartist['id']
                    #featuredartist_image = featuredartist['image_url']
                    featuredartist_name = featuredartist['name'].encode('utf-8')
                    feats+=featuredartist_name+', '
                    artists[featuredartist_id]=featuredartist_name
                feats=feats[:-2]
                title += ' (ft. '+feats+')'

            cm=[]
            if addon.getSetting('session_token'):
                if VEVOToken:
                    playlist_id = fetch_url.split('userplaylist/')[1].split('.')[0]
                    index=str(videos.index(video))
                    u=sys.argv[0]+"?url="+urllib.quote_plus(index)+"&mode="+urllib.quote_plus('removeVideo2Playlist')+'&page='+urllib.quote_plus(playlist_id)
                    cm.append( ('Remove from Playlist', "XBMC.RunPlugin(%s)" % u) )
                u=sys.argv[0]+"?url="+urllib.quote_plus(video_id)+"&mode="+urllib.quote_plus('addVideo2Playlist')+'&page='+str(1)
                cm.append( ('Add to Playlist', "XBMC.RunPlugin(%s)" % u) )
                u=sys.argv[0]+"?url="+urllib.quote_plus(video_id)+"&mode="+urllib.quote_plus('newVideoPlaylist')+'&page='+str(1)
                cm.append( ('Start New Playlist', "XBMC.RunPlugin(%s)" % u) )
            artist = artist_name
            for _artist in artists:
                if _artist <> '':
                    artist_name = artists[_artist]
                    artist_id = _artist
                    artist_url = 'http://api.vevo.com/mobile/v1/artist/%s/videos.json?order=MostRecent' % artist_id
                    u=sys.argv[0]+"?url="+urllib.quote_plus(artist_url)+"&mode="+urllib.quote_plus('listVideos')+'&page='+str(1)
                    cm.append( ('More %s' % artist_name, "Container.Update(%s)" % u) )
                    artist_url = 'http://api.vevo.com/mobile/v1/artist/%s.json' % artist_id
                    u='plugin://plugin.video.youtube/?path=/root/search&feed=search&search='+urllib.quote_plus(artist_name)+'&'
                    cm.append( ('YouTube %s' % artist_name, "Container.Update(%s)" % u) )
                    u=sys.argv[0]+"?url="+urllib.quote_plus(artist_url)+"&mode="+urllib.quote_plus('addfavArtists')+'&page='+str(1)
                    cm.append( ('Favorite %s' % artist_name, "XBMC.RunPlugin(%s)" % u) )
            u = sys.argv[0]
            u += '?url='+urllib.quote_plus(video_id)
            u += '&mode='+urllib.quote_plus('playVideo')
            u += '&duration='+urllib.quote_plus(str(duration))
            displayname = artist+' - '+title
            item=xbmcgui.ListItem(displayname, iconImage=video_image, thumbnailImage=video_image)
            infoLabels={ "Title":title,
                         "Artist":artist,
                         #Set album to artist because xbmc bug doesn't display artist value for video type
                         "Album":artist,
                         "Duration":str(duration/60)+':'+str(duration-(duration/60)*60),
                         "Studio":recordlabel,
                         "Director":director,
                         "Writer":composer,
                         "Producer":producer,
                         "Genre":genre,
                         "Plot":plot,
                         "Year":year,
                         "Count":count
                         }
            overlay = checkIDdb(video_id)
            if overlay:
                infoLabels['overlay']=overlay
                dcu=sys.argv[0]+"?url="+urllib.quote_plus(video_id)+"&mode="+urllib.quote_plus('deleteCachedFile')+'&page='+urllib.quote_plus('1')
                cm.append( ('Delete Cached File', "XBMC.RunPlugin(%s)" % dcu) )
            item.setInfo( type="Video",infoLabels=infoLabels)
            item.setProperty('Artist',artist)
            count +=1
            item.setProperty('fanart_image',artist_image)
            item.setProperty('IsPlayable', 'true')
            item.addContextMenuItems( cm )
            if playall or queue:
                playlist.add(url=u, listitem=item)
            else:
                xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False,totalItems=total)
        if playall:
            xbmc.Player().play(playlist)
        elif queue:
            pass
        else:
            xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
            setView()

def playAll():
    listVideos(params['url'],playall=True)

def queueAll():
    listVideos(params['url'],queue=True)
    
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
    xbmcplugin.setContent(pluginhandle, 'artists')
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
        artist_name = artist['name'].encode('utf-8')
        artist_image = artist['image_url']
        video_count = artist['video_count']
        url = 'http://api.vevo.com/mobile/v1/artist/'+artist_id+'/videos.json?order=MostRecent'
        display_name=artist_name+' ('+str(video_count)+')'
        cm = []
        artist_url = 'http://api.vevo.com/mobile/v1/artist/%s.json' % artist_id
        u=sys.argv[0]+"?url="+urllib.quote_plus(artist_url)+"&mode="+urllib.quote_plus('addfavArtists')+'&page='+str(1)
        cm.append( ('Favorite %s' % artist_name, "XBMC.RunPlugin(%s)" % u) )
        u='plugin://plugin.video.youtube/?path=/root/search&feed=search&search='+urllib.quote_plus(artist_name)+'&'
        cm.append( ('YouTube %s' % artist_name, "Container.Update(%s)" % u) )
        tours_url = 'http://api.vevo.com/mobile/v1/artist/%s/tours.json?toDate=2020-12-31&extended=true' % artist_id
        u=sys.argv[0]+"?url="+urllib.quote_plus(tours_url)+"&mode="+urllib.quote_plus('listTours')+'&page='+str(1)
        cm.append( ('List Tours', "Container.Update(%s)" % u) )
        addDir(display_name, url, 'listArtistVideos', iconimage=artist_image, total=total, cm=cm)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView()

# Playlist listings
def rootPlaylists():
    addDir('Top Playlists',        'http://api.vevo.com/mobile/v1/featured/staffpicks.json',        'listPlaylists')
    if addon.getSetting('login_name') <> '' and addon.getSetting('login_pass') <> '':
        if addon.getSetting('getnewtoken') == 'true':
            if getFBAuth():
                getVEVOAccount()
                addon.setSetting(id='getnewtoken',value='false')
            else:
                xbmcgui.Dialog().ok('Error','Facebook Login Failed') 
        if addon.getSetting('session_token'):
            addDir('My Playlists',         'http://api.vevo.com/mobile/v1/userplaylists.json?',             'listPlaylistsToken')
            #friendPlaylists('http://api.vevo.com/mobile/v1/user/getfacebookfriends.json?')
            addDir('My Friends',           'http://api.vevo.com/mobile/v1/user/getfacebookfriends.json?',   'friendPlaylists')
    xbmcplugin.endOfDirectory(pluginhandle)

def removeVideo2Playlist(playlist_id=False,isrc=False):
    if not isrc:
        isrc = params['url']
    if not playlist_id:
        playlist_id = params['page']
    url = 'http://api.vevo.com/mobile/v1/userplaylist/%s.json'%(playlist_id)
    data = getURL(url,VEVOToken=True)
    playlist = demjson.decode(data)['result']
    title=playlist['title'].replace(' ','%20')
    videos = playlist['videos']
    ids=''
    videos.pop(int(isrc))
    for video in videos:
        id = video['isrc']
        #if isrc <> id:
        ids += id+','
    addurl = 'http://api.vevo.com/mobile/v1/userplaylist/%s.json?title=%s&description=&isrcs=%s&append=false'%(playlist_id,title,ids)
    getURL(addurl,postdata=':)',method='POST',VEVOToken=True)
    xbmc.executebuiltin("Container.Refresh()")
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Removed from Playlist', 5000) )

def addVideo2Playlist(isrc=False):
    if not isrc:
        isrc = params['url']
    url = 'http://api.vevo.com/mobile/v1/userplaylists.json?'
    data = getURL(url,VEVOToken=True)
    playlists = demjson.decode(data)['result']
    selected=xbmcgui.Dialog().select('Add Video to Playlist',
                            [playlist['title']+' ('+str(playlist['videocount'])+')' for playlist in playlists])
    playlist=playlists[selected]
    title=playlist['title'].replace(' ','%20')
    playlist_id=playlist['playlist_id']
    if ',' in isrc:
        isrcs=isrc
        isrcs=isrcs.strip(',').split(',')
        for isrc in isrcs:
            addurl = 'http://api.vevo.com/mobile/v1/userplaylist/%s.json?title=%s&description=&isrcs=%s&append=true'%(playlist_id,title,isrc)
            getURL(addurl,postdata=':)',method='POST',VEVOToken=True)
    else:
        addurl = 'http://api.vevo.com/mobile/v1/userplaylist/%s.json?title=%s&description=&isrcs=%s&append=true'%(playlist_id,title,isrc)
        getURL(addurl,postdata=':)',method='POST',VEVOToken=True)
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Added to Playlist', 5000) )

def newVideoPlaylistURLPLToken():
    newVideoPlaylistURL(playlist=True,VEVOToken=True)

def addVideoPlaylistURLPLToken():
    newVideoPlaylistURL(playlist=True,VEVOToken=True,Add=True)
   
def newVideoPlaylistURLPL():
    newVideoPlaylistURL(playlist=True)

def addVideoPlaylistURLPL():
    newVideoPlaylistURL(playlist=True,Add=True)
    
def addVideoPlaylistURL():
    newVideoPlaylistURL(Add=True)

def newVideoPlaylistURL(url=False,playlist=False,VEVOToken=False,Add=False):
    if not url:
        url = params['url']
    data = getURL(url,VEVOToken=VEVOToken)
    if data:
        if playlist:
            videos = demjson.decode(data)['result']['videos']
        else:
            videos = demjson.decode(data)['result']
        isrcs=''
        for video in videos:
            isrcs+=video['isrc']+','
    if Add:
        addVideo2Playlist(isrc=isrcs)
    else:
        newVideoPlaylist(isrc=isrcs)
    
    
def newVideoPlaylist(name='',isrc=False):
    if not isrc:
        isrc = params['url']
    keyb = xbmc.Keyboard(name, 'Playlist Name')
    keyb.doModal()
    if keyb.isConfirmed():
        name = urllib.quote_plus(keyb.getText())
        addurl = 'http://api.vevo.com/mobile/v1/userplaylist.json?title=%s&description=&isrcs=%s' % (name,isrc)
        #require PUT
        getURL(addurl,postdata=':)',method='PUT',VEVOToken=True)
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'New Playlist', 5000) )

def deleteVideoPlaylist(id=False):
    if not id:
        id = params['url']
    url = 'http://api.vevo.com/mobile/v1/userplaylist/%s.json?' % id
    getURL(url,postdata=':)',method='DELETE',VEVOToken=True)
    xbmc.executebuiltin("Container.Refresh()")
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Deleted Playlist', 5000) )
    
def friendPlaylists(url = False):
    if not url:
        url = params['url']
    #if getFBAuth():
    sendtoken = 'accessToken='+addon.getSetting(id='fbtoken')
    data = getURL(url, postdata=sendtoken, VEVOToken=True)
    friends = demjson.decode(data)['result']['friends_on_vevo']
    total = len(friends)
    for friend in friends:
        url = 'http://api.vevo.com/mobile/v1/userplaylists/%s/list.json' % friend['vevo_id']
        name = friend['name']
        addDir(name, url, 'listPlaylistsToken', total=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    
def listPlaylistsToken():
    listPlaylists(VEVOToken=True)

def listPlaylists(url = False, VEVOToken=False):
    if not url:
        url = params['url']
    #max = maxperpage
    #page = int(params['page'])
    #offset = (page-1)*max1
    #fetch_url=url+'&offset='+str(offset)+'&max='+str(max)#+'&extended=true'
    #data = getURL(fetch_url)
    data = getURL(url,VEVOToken=VEVOToken)
    playlists = demjson.decode(data)['result']
    total = len(playlists)
    #if total >= max:
    #    addDir('*Next Page*', url,    'listPlaylists', page=str(page+1))
    for playlist in playlists:
        try:playlist_id = playlist['playlist_id']
        except:playlist_id = str(playlist['id'])
        cm=[]
        if addon.getSetting('session_token') and VEVOToken:
            u=sys.argv[0]+"?url="+urllib.quote_plus(playlist_id)+"&mode="+urllib.quote_plus('deleteVideoPlaylist')+'&page='+str(1)
            cm.append( ('Delete Playlist', "XBMC.RunPlugin(%s)" % u) )
        playlist_name = playlist['title']
        playlist_image = playlist['image_url']
        video_count = playlist['videocount']
        display_name=playlist_name+' ('+str(video_count)+')'
        if VEVOToken:
            mode = 'playlistUserRoot'
        else:
            mode = 'playlistRoot'
        addDir(display_name, playlist_id, mode, iconimage=playlist_image, total=total,cm=cm)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def playlistUserRoot():
    playlistRoot(VEVOToken=True)
  
def playlistRoot(VEVOToken=False):
    playlist_id = params['url']
    mode = 'playPlaylist'
    smode = 'newVideoPlaylistURLPL'
    amode = 'addVideoPlaylistURLPL'
    qmode = 'queuePlaylist'
    if VEVOToken:
        url = 'http://api.vevo.com/mobile/v1/userplaylist/%s.json?' % playlist_id
        mode = 'playUserPlaylist'
        smode = 'newVideoPlaylistURLPLToken'
        amode = 'addVideoPlaylistURLPLToken'
        qmode = 'queueUserPlaylist'
    elif playlist_id.isdigit():
        url = 'http://api.vevo.com/mobile/v1/playlist/%s.json?' % playlist_id
    else:
        url = 'http://api.vevo.com/mobile/v2/playlist/%s.json?' % playlist_id
    cm=[]
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(qmode)+'&page='+urllib.quote_plus('1')
    cm.append( ('Queue', "XBMC.RunPlugin(%s)" % u) )
    if addon.getSetting('session_token'):
        #if VEVOToken:
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(amode)+'&page='+urllib.quote_plus('1')
        #cm.append( ('Save to Playlist', "XBMC.RunPlugin(%s)" % u) )
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(smode)+'&page='+urllib.quote_plus('1')
        cm.append( ('New Playlist', "XBMC.RunPlugin(%s)" % u) )
    addDir('*Play*', url, mode,folder=False,cm=cm)
    listVideos(url,playlist=True,VEVOToken=VEVOToken)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def playUserPlaylist():
    listVideos(params['url'],playlist=True,playall=True,VEVOToken=True)
  
def playPlaylist():
    listVideos(params['url'],playlist=True,playall=True)

def queueUserPlaylist():
    listVideos(params['url'],playlist=True,queue=True,VEVOToken=True)

def queuePlaylist():
    listVideos(params['url'],playlist=True,queue=True)

# Show listings
def rootShows(url = False):
    xbmcplugin.setContent(pluginhandle, 'tvshows')
    if not url:
        url = params['url']
    data = getURL(url)
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
        url = 'http://api.vevo.com/mobile/v1/show/'+str(show_id)+'.json'
        display_name=show_name+' ('+str(video_count)+')'
        addDir(display_name, url, 'rootEpisodes', plot=description, iconimage=show_image, total=total)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView(override=504)

def rootEpisodes(url = False):
    if not url:
        url = params['url']
    data = getURL(url)
    result = demjson.decode(data)['result']
    show_id = result['id']
    show_name = result['name']
    show_image = result['image_url']
    description = result['description']
    if len(result['videos']) > 0:
        url = 'http://api.vevo.com/mobile/v1/show/'+str(show_id)+'/videos.json?order=MostRecent'
        listVideosNoPage(url)
    else:
        xbmcplugin.setContent(pluginhandle, 'episodes')
        episodes = result['episodes']
        total = len(episodes)
        for episode in episodes:
            episode_id = episode['episode_id']
            episode_title = episode['title']
            episode_image = episode['image_url']
            video_count = episode['video_count']
            url = 'http://api.vevo.com/mobile/v1/show/'+str(show_id)+'/videos.json?episode='+episode_id.replace(" ", "%20")
            display_name=episode_title +' ('+str(video_count)+')'
            u = sys.argv[0]
            u += '?url='+urllib.quote_plus(url)
            u += '&mode='+urllib.quote_plus('listVideosNoPage')
            u += '&page=1'
            item=xbmcgui.ListItem(display_name, iconImage=episode_image, thumbnailImage=episode_image)
            item.setInfo( type="Video", infoLabels={ "Title":episode_title,
                                                     "TVShowTitle":show_name,
                                                     "plot":description,
                                                     #"episode":video_count,
                                                     })
            item.setProperty('fanart_image',show_image)
            xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=True,totalItems=total)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
        setView(override=503)
    
# Search
def searchVideos():
    Search('Videos')

def searchArtists():
    Search('Artists')

def researchArtists():
    listArtists(params['url'])
    
def researchVideos():
    listVideos(params['url'])

def Search(mode):
    keyb = xbmc.Keyboard('', 'Search '+mode)
    keyb.doModal()
    if keyb.isConfirmed():
        search = urllib.quote_plus(keyb.getText())
        vurl = 'http://api.vevo.com/mobile/v1/search/videos.json?q='+search
        aurl = 'http://api.vevo.com/mobile/v1/search/artists.json?q='+search
        if mode == 'Videos':
            addDir('*Artist Results*',aurl,'researchArtists')
            listVideos(vurl)
        elif mode == 'Artists':
            addDir('*Video Results*',vurl,'researchVideos')
            listArtists(aurl)

def searchBox():
    latitude = float(addon.getSetting('latitude')) 
    longitude = float(addon.getSetting('longitude'))
    radius = (int(addon.getSetting('radius'))+1)*100
    lon_min = longitude - radius / abs(math.cos(math.radians(latitude)) * 69)
    lon_max = longitude + radius / abs(math.cos(math.radians(latitude)) * 69)
    lat_min = latitude - (radius / 69)
    lat_max = latitude + (radius / 69)
    parameters = '?s='+str(lat_min)
    parameters += '&w='+str(lon_min)
    parameters += '&n='+str(lat_max)
    parameters += '&e='+str(lon_max)
    return parameters

def TrendingRightNowIn():             
    url  = 'http://api.vevo.com/mobile/v1/video/TrendingRightNowIn.json'+searchBox()
    listVideos(url)

def watchingRightNowIn():             
    url  = 'http://api.vevo.com/mobile/v1/video/watchingRightNowIn.json'+searchBox()
    listVideos(url)  

def toursRightNow():    
    url = 'http://api.vevo.com/mobile/v1/geo/toursrightnow.json'+searchBox()
    max = maxperpage
    page = int(params['page'])
    offset = (page-1)*max
    fetch_url=url+'&offset='+str(offset)+'&max='+str(max)+'&extended=true'
    #if total >= max:
    #    addDir('*Next Page*', url,    'toursRightNow', page=str(page+1))
    listTours(fetch_url)

def listTours(url=False):
    if not url:
        url = params['url']
    data = getURL(url)
    artists = demjson.decode(data)['result']
    total = len(artists)
    for artist in artists:
        artist_id = artist['artistid']
        url = 'http://api.vevo.com/mobile/v1/artist/'+artist_id+'/videos.json?order=MostRecent'
        event_name = artist['eventname'].encode('utf-8')
        city = artist['city'].encode('utf-8')
        venuename = artist['venuename'].encode('utf-8')
        startdate = artist['startdate']
        type = artist['type']
        date = time.strftime("%B %d, %Y %I:%M%p", time.strptime(startdate[:-5], "%Y-%m-%dT%H:%M:%S") )
        if artist.has_key('artist'):
            artist_name = artist['artist']['name'].encode('utf-8')
            artist_image = artist['artist']['image_url']
        else:
            artist_name = event_name.split(' at ')[0].strip()
            artist_image = ''
        if type == 'Festival':
            if '@' in event_name:
                event_name = event_name.split('@')[1]
            if artist_name == event_name:
                final_name = date +' : '+city+' - '+event_name+' @ '+venuename
            else:    
                final_name = date +' : '+city+' - '+artist_name+' @ '+event_name
        elif type == 'Concert':
            final_name = date+' : '+city+' - '+artist_name+' @ '+venuename
        addDir(final_name, url, 'listArtistVideos', iconimage=artist_image, total=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView(override=51)

def createArtistdb():
    if not os.path.isfile(FAVFILESQL):
        db = sqlite.connect(FAVFILESQL)
        db.text_factory = str
        c = db.cursor()
        c.execute('''CREATE TABLE artists(
                     id TEXT,
                     name TEXT,
                     image TEXT,
                     count INTEGER,
                     PRIMARY KEY(id)
                     );''')
        db.commit()
        c.close()
        rematchArtists()
        try:convertJSONfavs()
        except:pass

def addArtistdb(artist):
    createArtistdb()
    db = sqlite.connect(FAVFILESQL)
    db.text_factory = str
    c = db.cursor()
    c.execute('insert or ignore into artists values (?,?,?,?)', [artist['id'],artist['name'],artist['image_url'],artist['video_count']])
    db.commit()
    c.close()

def addfavArtists():
    artist = demjson.decode(getURL(params['url']))['result']
    addArtistdb(artist)
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Added Artist', 5000) )

def removefavArtists():
    db = sqlite.connect(FAVFILESQL)
    db.text_factory = str
    c = db.cursor()
    c.execute('delete from artists where id = (?)', (params['url'],) )
    db.commit()
    c.close()
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Deleted Artist', 5000) )
    #xbmc.executebuiltin("Container.Refresh()")
    
def deletefavArtists():
    db = sqlite.connect(FAVFILESQL)
    db.text_factory = str
    c = db.cursor()
    c.execute('delete from artists')
    db.commit()
    c.close()
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Deleted Favorite Artists', 10000) )

def rematchArtists():
    for artist in matchedArtists():
        addArtistdb(artist)
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Library Artists Added', 10000) )

def convertJSONfavs():
    if os.path.isfile(FAVFILE): 
        for artist in demjson.decode(OpenFile(FAVFILE)):
            addArtistdb(artist)
        os.remove(FAVFILE)

def favArtists():
    xbmcplugin.setContent(pluginhandle, 'artists')
    createArtistdb()
    db = sqlite.connect(FAVFILESQL)
    db.text_factory = str
    c = db.cursor()
    for artist in c.execute('select distinct * from artists'):
        artist_id = artist[0]
        artist_name = artist[1]
        artist_image = artist[2]
        video_count = artist[3]
        url = 'http://api.vevo.com/mobile/v1/artist/'+artist_id+'/videos.json?order=MostRecent'
        display_name=artist_name+' ('+str(video_count)+')'
        cm = []
        tours_url = 'http://api.vevo.com/mobile/v1/artist/%s/tours.json?toDate=2020-12-31&extended=true' % artist_id
        u=sys.argv[0]+"?url="+urllib.quote_plus(tours_url)+"&mode="+urllib.quote_plus('listTours')+'&page='+str(1)
        cm.append( ('List Tours', "Container.Update(%s)" % u) )
        u='plugin://plugin.video.youtube/?path=/root/search&feed=search&search='+urllib.quote_plus(artist_name)+'&'
        cm.append( ('YouTube %s' % artist_name, "Container.Update(%s)" % u) )
        u=sys.argv[0]+"?url="+urllib.quote_plus(artist_id)+"&mode="+urllib.quote_plus('removefavArtists')+'&page='+str(1)
        cm.append( ('Remove %s' % artist_name, "XBMC.RunPlugin(%s)" % u) )
        addDir(display_name, url, 'listArtistVideos', iconimage=artist_image, cm=cm)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView()
    c.close()

def matchedArtists():
    url = 'http://api.vevo.com/mobile/v1/search/artistmatch.json'
    json_query = {}
    json_list = []
    for artist in getLibraryArtists():
        artistjson = {'songCount':1,
                      'query':artist}
        json_list.append(artistjson)
    json_query['query']=json_list 
    json_query['last_batch']='true'
    json_query = demjson.encode(json_query)
    data = getURL( url , postdata=json_query, extendTimeout=60)
    artists = demjson.decode(data)['result']
    #total = len(artists)
    returns = []
    for artist in artists:
        returns.append(artist['artist'])
    return returns
      
def getLibraryArtists():
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "id": 1}')
    json_response = demjson.decode(json_query)
    artistlist = []
    if json_response['result']:
        for item in json_response['result']['artists']:
            artistname = cleanartists(item['label'])
            artistlist.append(artistname)
    return artistlist
    
# Play Video
def playVideo():
    playlistVideo()

def playlistVideo():
    if addon.getSetting('rickroll') == 'true':
        params['url']='GB1108700010'
    subtitles = os.path.join(datapath,params['url']+'.srt')
    if addon.getSetting('lyricsubs') == 'true':
        if params['duration']:
            try:getLyrics(params['url'],params['duration'],subtitles)
            except: print "Subtitles Failed"

    if addon.getSetting('defaultyoutube') == 'true':
        try:YouTube()
        except:
            try:RTMP()
            except:HTTPDynamic()
    elif addon.getSetting('defaultrtmp') == 'true':
        try:RTMP()
        except:YouTube()
    elif addon.getSetting('enabled-cache') == 'true':
        HTTPDynamicCache()
    else:
        try:HTTPDynamic()
        except:YouTube()
    xbmc.sleep(5000)
    if addon.getSetting('lyricsubs') == 'true':
        if os.path.isfile(subtitles) and xbmc.Player().isPlaying():
            xbmc.Player().setSubtitles(subtitles)

class DownloadThread (threading.Thread):
    def __init__(self, url, dest, artist, title, id):
        self.url = url
        self.dest = dest
        self.artist = artist
        self.title = title
        self.id = id
        threading.Thread.__init__(self)
        
    def run(self):
        start_time = time.time()
        try:
            addCachedb(self.id,self.artist,self.title)
            urllib.urlretrieve(self.url, self.dest)
            statusUpdatedb(self.id,'completed')
        except:
            statusUpdatedb(self.id,'failed')

def createCachedb():
    if not os.path.isfile(CACHEDB):
        db = sqlite.connect(CACHEDB)
        db.text_factory = str
        c = db.cursor()
        c.execute('''CREATE TABLE videos(
                     id TEXT,
                     artist TEXT,
                     title TEXT,
                     status TEXT,
                     PRIMARY KEY(id)
                     );''')
        db.commit()
        c.close()

def checkIDdb(id): 
    if addon.getSetting('enabled-cache') == 'true':
        createCachedb()
        db = sqlite.connect(CACHEDB)
        db.text_factory = str
        c = db.cursor()
        video = c.execute('select distinct * from videos where id = (?)', (id,)).fetchone()
        c.close()
        if video:
            id,artist,title,status = video
            if status == 'failed':
                return False
            elif status == 'started':
                return 1
            elif status == 'completed':
                return 7
            else:
                return 3
        else:
            return False
    return False

def deleteCachedFile(id=False):
    if not id:
        id = params['url']
    db = sqlite.connect(CACHEDB)
    db.text_factory = str
    c = db.cursor()
    video = c.execute('select distinct * from videos where id = (?)', (id,)).fetchone()
    if video:
        id,artist,title,status = video
        filename=cleanfilename(artist+' - '+title)
        videofile = os.path.join(cachepath,filename+'.flv')
        jpgfile = os.path.join(cachepath,filename+'.jpg')
        nfofile = os.path.join(cachepath,filename+'.nfo')
        subfile = os.path.join(cachepath,filename+'.srt')
        for file in (videofile,jpgfile,nfofile,subfile):
            if os.path.exists(file):
                os.remove(file)
        deleteCachedb(id)
        #xbmc.executebuiltin("Container.Refresh()")

def statusUpdatedb(id,status):
    db = sqlite.connect(CACHEDB)
    db.text_factory = str
    c = db.cursor()
    c.execute("update videos set status=? where id=?", (status,id))
    db.commit()
    c.close()

def deleteCachedb(id):
    db = sqlite.connect(CACHEDB)
    db.text_factory = str
    c = db.cursor()
    c.execute("delete from videos where id=?", (id,))
    db.commit()
    c.close()

def addCachedb(id,artist,title,status='started'):
    db = sqlite.connect(CACHEDB)
    db.text_factory = str
    c = db.cursor()
    c.execute('insert or ignore into videos values (?,?,?,?)', [id,artist,title,status])
    db.commit()
    c.close()
    
def cleanfilename(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in name if c in valid_chars)    
  
def HTTPDynamicCache():
    vevoID = params['url'].split('/')[-1]
    createCachedb()
    db = sqlite.connect(CACHEDB)
    db.text_factory = str
    c = db.cursor()
    video = c.execute('select distinct * from videos where id = (?)', (vevoID,)).fetchone()
    if video:
        id,artist,title,status = video
        filename=cleanfilename(artist+' - '+title)
        videofile = os.path.join(cachepath,filename+'.flv')
        #jpgfile = os.path.join(cachepath,filename+'.jpg')
        #nfofile = os.path.join(cachepath,filename+'.nfo')
        #subfile = os.path.join(cachepath,filename+'.srt')
        if os.path.exists(videofile):
            if status == 'failed':
                os.remove(videofile)
                deleteCachedb(vevoID)
                HTTPDynamicCacheDownload(vevoID)
            else:
                print "Playing %s from Cache" % filename
                item = xbmcgui.ListItem(path=videofile)
                xbmcplugin.setResolvedUrl(pluginhandle, True, item)
                #if not os.path.exists(jpgfile):
                #    SaveFile(jpgfile, getURL(image_url))
                #if not os.path.exists(nfofile):
                #    url = 'http://videoplayer.vevo.com/VideoService/AuthenticateVideo?isrc=%s' % vevoID
                #    data = getURL(url)
                #    video = demjson.decode(data)['video']
                #    HTTPDynamicCacheNFO(video,nfofile)
                #if not os.path.exists(subfile):
                #    HTTPDynamicCacheSubtitles(subfile)
        else:
            deleteCachedb(vevoID)
            HTTPDynamicCacheDownload(vevoID)
    else:
        HTTPDynamicCacheDownload(vevoID)

def HTTPDynamicCacheSubtitles(filename):
    try:getLyrics(params['url'],params['duration'],filename)
    except:print 'subtitles failed'
    
def HTTPDynamicCacheNFO(video,nfofile):
    try:
        title = video['title'].encode('utf-8')
        image_url = video['imageUrl']
        artist = video['mainArtists'][0]['artistName'].encode('utf-8')
        duration = str(video['duration'])
        genre=''
        for item in video['genres']:
            genre+=item+','
        genre=genre[:-1]
        releaseDate=int(video['releaseDate'].replace('/Date(','').replace(')/','')[:-3])
        year = time.strftime("%Y",time.localtime(releaseDate))
        metadict={}
        plot=''
        for meta in video['metadata']:
            metadict[meta['keyType']]=meta['keyValue']
            if meta['keyType'] == 'Credit':
                plot+=meta['keyValue'].replace('=>',':')+'\n'
            else:
                plot+=meta['keyType']+' : '+meta['keyValue']+'\n'
        nfo ='<musicvideo>'+'\n'
        nfo+='<title>'+title+'</title>'+'\n'
        nfo+='<artist>'+artist+'</artist>'+'\n'
        nfo+='<album>'+'Music Video'+'</album>'
        nfo+='<genre>'+genre+'</genre>'+'\n'
        nfo+='<runtime>'+duration+'</runtime>'+'\n'
        nfo+='<thumb>'+image_url+'</thumb>'+'\n'
        nfo+='<plot>'+plot+'</plot>'+'\n'
        nfo+='<year>'+year+'</year>'+'\n'
        try:director = metadict['Director'].encode('utf-8')
        except:director = ''
        nfo+='<director>'+director+'</director>'+'\n'
        try:studio = metadict['Label'].encode('utf-8')
        except:studio = ''
        nfo+='<studio>'+studio+'</studio>'+'\n'
        nfo+='</musicvideo>'
        SaveFile(nfofile, nfo)
    except: print 'nfo failed'

def HTTPDynamicCacheDownload(vevoID):
    print "Cacheing %s" % vevoID
    url = 'http://videoplayer.vevo.com/VideoService/AuthenticateVideo?isrc=%s' % vevoID
    data = getURL(url)
    video = demjson.decode(data)['video']
    title = video['title'].encode('utf-8')
    image_url = video['imageUrl']
    artist = video['mainArtists'][0]['artistName'].encode('utf-8')
    filename=cleanfilename(artist+' - '+title)
    videofile = os.path.join(cachepath,filename+'.flv')
    jpgfile = os.path.join(cachepath,filename+'.jpg')
    nfofile = os.path.join(cachepath,filename+'.nfo')
    subfile = os.path.join(cachepath,filename+'.srt')
    if os.path.exists(videofile):
        print "Found %s in cache, Adding to savedDB and resolving" % filename
        item = xbmcgui.ListItem(path=videofile) 
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        addCachedb(vevoID,artist,title,'completed')
        if not os.path.exists(jpgfile):
            SaveFile(jpgfile, getURL(image_url))
        if not os.path.exists(nfofile):
            HTTPDynamicCacheNFO(video,nfofile)
        if not os.path.exists(subfile):
            HTTPDynamicCacheSubtitles(subfile)
    else:
        type5=False
        youtube=False
        for version in video['videoVersions']:
            if version['sourceType'] == 5:
                type5=True
            elif version['sourceType'] == 0:
                youtubeID = version['id']
                youtube=True
        
        video_url=False
        if type5:
            print "VEVO - Saving from VEVO"
            video_url = getVideo(params['url'])
        elif youtube:
            print "VEVO - Saving from Youtube"
            video_url = getYouTubeLink(youtubeID)
        else:
            try:video_url = getVideo(params['url'])
            except: pass
        if video_url:
            print "VEVO Downloading : %s" % video_url
            dlThread = DownloadThread(video_url, videofile, artist, title, vevoID)
            dlThread.start()
            HTTPDynamicCacheSubtitles(subfile)
            HTTPDynamicCacheNFO(video,nfofile)
            try:SaveFile(jpgfile, getURL(image_url))
            except: print 'Saving screenshot failed'
            count=0
            while not os.path.exists(videofile):
                count+=1
                if count > 6:
                    break
                xbmc.sleep(2500)
            if os.path.exists(videofile):
                if dlThread.isAlive():
                    sleeptime = (int(addon.getSetting('unpausetime'))+1)*1000
                    xbmc.sleep(sleeptime+5000)
                    print "Playing %s while downloading" % filename
                    item = xbmcgui.ListItem(path=videofile) 
                    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        else:
            print "No Link Found"

def getYouTubeLink(youtubeID):
    data = getURL('http://www.youtube.com/watch?v=%s&safeSearch=none' % youtubeID, browser=True)
    data = re.compile('yt.playerConfig = (.*?)};',re.DOTALL).findall(data)[0].replace("\\/", "/")
    json = demjson.decode('{ "PLAYER_CONFIG" : ' + data + "}}" )
    fmt_stream_map = json['PLAYER_CONFIG']['args']['url_encoded_fmt_stream_map']
    links = urllib.unquote(fmt_stream_map[4:]).split(',url=')
    qualities = (5,33,18,26,43,34,78,44,59,35,22,45,38,37)
    index= -1
    for link in links:
        for quality in qualities:
            tag = '&itag='+str(quality)
            if tag in link:
                vindex = qualities.index(quality)
                if vindex > index:
                    index=vindex
                    video_url=link
    return video_url.replace(" ", "%20").split('&type')[0]

def HTTPDynamic():
    item = xbmcgui.ListItem(path=getVideo(params['url']))
    xbmcplugin.setResolvedUrl(pluginhandle, True, item) 
    if addon.getSetting('unpause') == 'true':
        sleeptime = (int(addon.getSetting('unpausetime'))+1)*1000
        xbmc.sleep(sleeptime)
        xbmc.Player().pause()

def convert_time(milliseconds):
    seconds = int(float(milliseconds)/1000)
    milliseconds -= (seconds*1000)
    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    seconds -= 60*minutes
    return "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, milliseconds)

def getLyrics(vevoID,duration,subtitles):
    if not os.path.isfile(subtitles):
        url = 'http://www.vevo.com/data/VideoLyrics/'+vevoID
        data = getURL(url,browser=True,alert=False)
        if data:
            json = demjson.decode(data)
            lyrics = json['Text'].replace('\r','').split('\n')
            sets = []
            set=''
            setlength = 0
            for lyric in lyrics:
                sub = lyric.strip().encode('utf-8')
                if setlength > 7 and set <> '':
                    sets.append(set)
                    set=''
                    setlength = 0
                if sub == '' and set <> '':
                    sets.append(set)
                    set=''
                    setlength = 0
                elif sub <> '':
                    set += sub+'\n'
                    setlength += 1 
            if set <> '':
                sets.append(set)
            lines = len(sets)
            duration = float(duration)*1000
            offset = duration*0.025
            rate = (duration*0.95)/lines
            count = 0
            srt_output = ''      
            for set in sets:
                start = convert_time( (count*rate)+offset )
                end = convert_time( ( (count+1)*rate ) + offset)
                count += 1
                line = str(count)+"\n"+start+" --> "+end+"\n"+set+"\n"
                srt_output += line
            if srt_output <> '':
                SaveFile(subtitles, srt_output)

def YouTube():
    vevoID = params['url'].split('/')[-1]
    url = 'http://videoplayer.vevo.com/VideoService/AuthenticateVideo?isrc=%s' % vevoID
    data = getURL(url)
    youtubeID = demjson.decode(data)['video']['videoVersions'][0]['id']
    youtubeurl = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % youtubeID
    item = xbmcgui.ListItem(path=youtubeurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def RTMP():
    item = xbmcgui.ListItem(path=getVideoRTMP(params['url']))
    xbmcplugin.setResolvedUrl(pluginhandle, True, item) 

def getVideoRTMP(pageurl):
    quality = [564000, 864000, 1328000, 1728000, 2528000, 3328000, 4392000, 5392000]
    select = int(addon.getSetting('bitrate'))
    maxbitrate = quality[select]
    vevoID = pageurl.split('/')[-1]
    url = 'http://vevoodfs.fplive.net/Video/V2/VFILE/%s/%sr.smil' % (vevoID,vevoID.lower())
    data = getURL(url,alert=False)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print tree.prettify()
    rtmp = tree.find('meta')['base']
    videos = tree.findAll('video')
    number = len(videos)-1
    if number < select:
        select = number
    playpath = videos[select]['src']
    final = rtmp+' playpath='+playpath
    return final

def getVideo(pageurl):
    quality = [564000, 864000, 1328000, 1728000, 2528000, 3328000, 4392000, 5392000]
    select = int(addon.getSetting('bitrate'))
    maxbitrate = quality[select]
    vevoID = pageurl.split('/')[-1]
    url = 'http://smilstream.vevo.com/HDFlash/v1/smil/%s/%s.smil' % (vevoID,vevoID.lower())
    data = getURL(url,alert=False)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print tree.prettify()
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
def addDir(name, url, mode, plot='', iconimage=vicon ,folder=True,total=0,page=1,cm=False):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+'&page='+str(page)
    item=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if iconimage <> vicon:
        item.setProperty('fanart_image',iconimage)
    else:
        item.setProperty('fanart_image',fanart)
    item.setInfo( type="Video", infoLabels={ "Title":name,
                                             "plot":plot
                                           })
    if cm:
        item.addContextMenuItems( cm )
    return xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=folder,totalItems=total)

def setView(override=False):
    confluence_views = [50,500,511]
    if addon.getSetting('viewenable') == 'true':
        if override:
            view = str(override)
        else:
            view=int(addon.getSetting('defaultview'))
            view = str(confluence_views[view])
        xbmc.executebuiltin("Container.SetViewMode("+view+")")

def setLocation():
    try:
        url = 'http://www.geobytes.com/IpLocator.htm?GetLocation&template=json.txt'
        data = getURL(url)
        locationdata = demjson.decode(data)['geobytes']
        latitude=str(locationdata['latitude'])
        longitude=str(locationdata['longitude'])
        addon.setSetting(id='latitude',value=latitude)
        addon.setSetting(id='longitude',value=longitude)
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Set Location', '%s , %s' % (latitude, longitude), 8000) )
    except:
        addon.setSetting(id='latitude',value='')
        addon.setSetting(id='longitude',value='')
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Failed', 'No Location Set', 10000) )

def newGraph(email,password,uid=None,token=None,new_token_callback=None):
    graph = facebook.GraphWrap(token,new_token_callback=new_token_callback)
    graph.setAppData('184548202936',scope='email,user_birthday,user_likes,user_interests,publish_actions')
    graph.setLogin(email,password,uid)
    return graph

def getFBAuth():
    email = addon.getSetting("login_name")
    password = addon.getSetting("login_pass")
    cj = cookielib.LWPCookieJar()
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.set_cookiejar(cj)
    user = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0'
    #user = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Mobile/9A405'
    br.addheaders = [('User-agent', user)]
    #redirect = urllib.quote('fbconnect://success')
    redirect = urllib.quote('https://www.vevo.com')
    #scope = urllib.quote('email,user_birthday,user_likes,user_interests,publish_actions')
    scope = urllib.quote('email')
    url = 'https://graph.facebook.com/oauth/authorize?client_id=184548202936&local_client_id=vevo&redirect_uri=%s&type=user_agent&scope=%s&sdk=ios&display=touch' % (redirect,scope)
    br.open(url)
    response = br.response()
    headers = response.info()
    headers["Content-type"] = "text/html; charset=utf-8"
    response.set_data(response.get_data().replace('<?xml version="1.0" encoding="utf-8"?>',''))
    br.set_response(response)
    br.select_form(nr=0)  
    br["email"] = email
    br["pass"] = password
    logged_in = br.submit()
    data = logged_in.read()
    url = logged_in.geturl()
    graph = newGraph(email, password)
    token = graph.extractTokenFromURL(url)
    if graph.tokenIsValid(token):
        addon.setSetting(id='fbtoken',value=token)
        return True
    else:
        return False
        
def getVEVOAccount():
    url = 'http://api.vevo.com/mobile/v1/user/facebookauth.json'
    sendtoken = {}
    sendtoken['accessToken'] = addon.getSetting(id='fbtoken')
    data = getURL( url , postdata=demjson.encode(sendtoken), VEVOKey=True)
    json = demjson.decode(data)
    addon.setSetting(id='vevo_user_id',value=json['user_id'])
    addon.setSetting(id='session_token',value=json['session_token'])

def getURL( url , postdata=False, method=False, extendTimeout=False, VEVOToken=False, VEVOKey=False, browser=False, alert=True):
    try:
        print 'VEVO --> common :: getURL :: url = '+url
        #proxy = 'http://localhost:8888'
        #proxy_handler = urllib2.ProxyHandler({'http':proxy})
        #opener = urllib2.build_opener(proxy_handler)
        opener = urllib2.build_opener()
        if browser:
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0')]
        else:
            opener.addheaders = [('User-Agent', 'VEVO 1.5 rv:5529 (iPad; iPhone OS 5.0.1; en_US)')]
        if VEVOToken:
            opener.addheaders = [('X-VEVO-Session-Token', addon.getSetting('session_token') )]
        if VEVOKey:
            opener.addheaders = [('X-VEVO-Private-Key', 'G05bmz9x--_6-J-qpR4_' )]
        if postdata:
            if method:
                request = urllib2.Request(url, data=postdata)
                #request.add_header('Content-Type', 'your/contenttype')
                request.get_method = lambda: method
                usock=opener.open(request)
            elif extendTimeout <> False:
                try:usock=opener.open(url,postdata,extendTimeout)
                except:usock=opener.open(url,postdata)
            else:
                usock=opener.open(url,postdata)
        else:
            usock=opener.open(url)
        response=usock.read()
        usock.close()
        return response
    except urllib2.URLError, e:
        print 'Error reason: ', e
        heading = 'Error'
        message = e
        duration = 10000
        if alert:
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
        return False

def _unicode( text, encoding='utf-8' ):
    try: text = unicode( text, encoding )
    except: pass
    return text

def cleanartists(name):    
    try: name = unicodedata.normalize( 'NFKD', _unicode( name ) ).encode( 'ascii', 'ignore' )
    except: pass
    return name.replace('"','').replace("'",'').replace('<','').replace('>','').replace('(','').replace(')','').replace('\n',' ').replace('-',' ')

def SaveFile(path, data):
    file = open(path,'w')
    file.write(data)
    file.close()

def OpenFile(path):
    file = open(path, 'r')
    contents=file.read()
    file.close()
    return contents

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
