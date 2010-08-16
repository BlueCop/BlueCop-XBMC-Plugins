__plugin__ = "MTVN Plugin"
__authors__ = "BlueCop"
__credits__ = ""
__version__ = "0.74"

import urllib, urllib2
import os, re, sys, md5, string
import xbmc, xbmcgui, xbmcplugin

import mtvn as mtvn

pluginhandle = int (sys.argv[1])

MAXLISTING = (int(xbmcplugin.getSetting(pluginhandle,"maxlist")) + 1) * 5
if xbmcplugin.getSetting(pluginhandle,"sort") == '0':#Relevance
        SORTORDER = 'relevance'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '1':#Date Ascending
        SORTORDER = 'date_ascending'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '2':#Date Descending
        SORTORDER = 'date_descending'
        
def listCategories():
        addDir('Browse Artists A-Z', 'artists', 1)
        addDir('Browse Artists by Genre', 'artists', 2)
        addDir('Browse Videos by Genre', 'videos', 2)
        addDir('Search Artist', 'searchArtist', 5)
        addDir('Search Video', 'searchVideo', 5)
        addDir('MTV.com', 'mtvlist', 101)
        #addDir('Favorite Videos', 'favArtist', 1)
        #addDir('Favorite Artists', 'favVideo', 1)
        return

def listAZ():
        addDir('#', '-', 11)
        addDir('A', 'a', 11)
        addDir('B', 'b', 11)
        addDir('C', 'c', 11)
        addDir('D', 'd', 11)
        addDir('E', 'e', 11)
        addDir('F', 'f', 11)
        addDir('G', 'g', 11)
        addDir('H', 'h', 11)
        addDir('I', 'i', 11)
        addDir('J', 'j', 11)
        addDir('K', 'k', 11)
        addDir('L', 'l', 11)
        addDir('M', 'm', 11)
        addDir('N', 'n', 11)
        addDir('O', 'o', 11)
        addDir('P', 'p', 11)
        addDir('Q', 'q', 11)
        addDir('R', 'r', 11)
        addDir('S', 's', 11)
        addDir('T', 't', 11)
        addDir('U', 'u', 11)
        addDir('V', 'v', 11)
        addDir('W', 'w', 11)
        addDir('X', 'x', 11)
        addDir('Y', 'y', 11)
        addDir('Z', 'z', 11)
        return

def listGenres(mode):
        if mode == 'artists':
                linkmode = 22
        elif mode == 'videos':
                linkmode = 23
        #       Genre Name                      Genre Alias             Mode           
        addDir('World/Reggae',                  'world_reggae',         linkmode)
        addDir('Pop',                           'pop',                  linkmode)
        addDir('Metal',                         'metal',                linkmode)
        addDir('Environmental',                 'environmental',        linkmode)
        addDir('Latin',                         'latin',                linkmode)
        addDir('R&B',                           'randb',                linkmode)
        addDir('Rock',                          'rock',                 linkmode)
        addDir('Easy Listening',                'easy_listening',       linkmode)
        addDir('Jazz',                          'jazz',                 linkmode)
        addDir('Country',                       'country',              linkmode)
        addDir('Hip-Hop',                       'hip_hop',              linkmode)
        addDir('Classical',                     'classical',            linkmode)
        addDir('Electronic / Dance',            'electronic_dance',     linkmode)
        addDir('Blues / Folk',                  'blues_folk',           linkmode)
        addDir('Alternative',                   'alternative',          linkmode)
        addDir('Soundtracks / Musicals',        'soundtracks_musicals', linkmode)
        return

def ProcessResponse(response,mode): # Mode 3 Artist, Mode 4 Videos
        if response == False:
                return
        for url, name, thumbnail in response:
                name = name.replace('&amp;','&').replace('&#039;',"'")
                if mode == 4:
                        addLink(name.encode('utf-8'), url, mode, thumbnail)
                else:
                        addDir(name.encode('utf-8'), url, mode, thumbnail)
        return

def listArtistsAZ(letter):
        artists = mtvn.artistBrowse(letter)
        ProcessResponse(artists,3)
        return

def listGenreArtist(genre):
        if '<start>' in genre:
                breakgenre = genre.split('<start>')
                genre = breakgenre[0]
                start = int(breakgenre[1])
                nextpage = ' Next Page (' + str(start+MAXLISTING) + '-' + str(start+(MAXLISTING*2)-1) + ')'
                pagegenre = genre+"<start>"+str(start+MAXLISTING)
        else:
                start = 0
                nextpage = ' Next Page (' + str(MAXLISTING+1) + '-' + str(MAXLISTING*2) + ')'
                pagegenre = genre+"<start>"+str(MAXLISTING+1)
        artists = mtvn.genreArtists(genre,MAXLISTING,start,SORTORDER)
        if len(artists) == MAXLISTING:
                addDir(nextpage, pagegenre, 22)
        ProcessResponse(artists,3)
        return

def listGenreVideos(genre):
        if '<start>' in genre:
                breakgenre = genre.split('<start>')
                genre = breakgenre[0]
                start = int(breakgenre[1])
                nextpage = ' Next Page (' + str(start+MAXLISTING) + '-' + str(start+(MAXLISTING*2)-1) + ')'
                pagegenre = genre+"<start>"+str(start+MAXLISTING)
        else:
                start = 0
                nextpage = ' Next Page (' + str(MAXLISTING+1) + '-' + str(MAXLISTING*2) + ')'
                pagegenre = genre+"<start>"+str(MAXLISTING+1)
        videos = mtvn.genreVideos(genre,MAXLISTING,start,SORTORDER)
        if len(videos) == MAXLISTING:
                addDir(nextpage, pagegenre, 23)
        ProcessResponse(videos,4)
        return

def listSearch(searchtype):
        keyb = xbmc.Keyboard('', 'Search')
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = keyb.getText()
                if searchtype == 'searchArtist':
                        artists = mtvn.artistSearch(search)
                        ProcessResponse(artists,3)
                elif searchtype == 'searchVideo':
                        videos = mtvn.videoSearch(search)
                        ProcessResponse(videos,4)
                xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
        return

def listArtistVideos(artist):
        videos = mtvn.artistVideos(artist)
        addDir(' Related Artists', artist, 6, '')
        ProcessResponse(videos,4)
        return

def listRelatedArtists(artist):
        artists = mtvn.relatedArtists(artist)
        ProcessResponse(artists,3)
        return

def listMTV():
        addDir('Video Picks', 'videopicks', 101)
        addDir('Video Premieres', 'videopremieres', 101)
        #addDir('Most Popular', 'mostpopular', 101)
        return

def listMTVCOM(mode):
        if mode == 'mtvlist':
                listMTV()
                return
        elif mode == 'videopicks':
                videos = mtvn.VideoPicksMTV()
        elif mode == 'videopremieres':
                videos = mtvn.VideoPremieresMTV()
        elif mode == 'mostpopular':
                videos = mtvn.VideoPopularMTV()
        if videos == False:
                return False
        for artist, thumb, uri in videos:
                name = artist #+ ' - ' + song
                name = name.replace('&amp;','&').replace('&#039;',"'").replace('&#039;',"'")
                addLink(name, uri, 4, thumb)
        return
                
#Get SMIL url and play video
def playRTMP(url, name):
        rtmps = mtvn.getrtmp(url)
        if rtmps == False:
                return
        swfUrl = mtvn.getswfUrl()
        options = []
        for _url,_playpath in rtmps:
                filesplit = _playpath.split('/')[-1].split('_')
                if 'mp4:' in _playpath:
                        option = filesplit[-2] + ' ' + filesplit[-1] + 'kbps (h264/aac)'
                elif 'full' == filesplit[-2] or 'ALL' == filesplit[-2]:
                        if '320' == filesplit[-1]:
                                option = filesplit[-1] + 'x240 700kbps (vp6/mp3)'
                        elif '240' == filesplit[-1]:
                                option = filesplit[-1] + 'x180 300kbps (vp6/mp3)'
                else:
                        option = filesplit[-2] + ' ' + filesplit[-1] + 'kbps (vp6/mp3)'
                options.append(option) 
        options.append(xbmc.getLocalizedString(30007))
        if (xbmcplugin.getSetting(pluginhandle,"askquality") == 'true'):
                dia = xbmcgui.Dialog()
                ret = dia.select(xbmc.getLocalizedString(30006), options)
                if (ret == (len(options)-1)):
                        return
        else:
                hbitrate = 0
                hpixels = 0
                finalret = 0
                for quality in options:
                        finalret += 1
                        if quality == xbmc.getLocalizedString(30007):
                                continue
                        quality = quality.split(' ')
                        resolution = quality[0].split('x')
                        w = int(resolution[0])
                        h = int(resolution[1])
                        pixels = w * h
                        bitrate = int(quality[1].replace('kbps',''))
                        codec = quality[2].replace('(','').replace(')','')
                        if xbmcplugin.getSetting(pluginhandle,"codec") == '1':
                                dcodec = 'h264/aac'
                        elif xbmcplugin.getSetting(pluginhandle,"codec") == '0':
                                dcodec = 'vp6/mp3'
                        if codec <> dcodec:
                                if hbitrate == 0 or hpixels == 0:
                                        if bitrate > hbitrate:
                                                hbitrate = bitrate
                                                ret = finalret - 1
                                        if pixels > hpixels:
                                                hpixels = pixels
                                                ret = finalret - 1     
                        else:
                                if bitrate > hbitrate:
                                        hbitrate = bitrate
                                        ret = finalret - 1
                                if pixels > hpixels:
                                        hpixels = pixels
                                        ret = finalret - 1

        for _url,_playpath in rtmps:
                optsplit = options[ret].replace('x240','').replace('x180','').replace('kbps','').split(' ')
                if optsplit[2] == '(vp6/mp3)' and 'mp4:' in _playpath:
                        continue
                elif optsplit[0] in _playpath and optsplit[1] in _playpath:
                        rtmpurl = _url + " playpath=" + _playpath + " swfurl=" + swfUrl + " swfvfy=true"
                        item=xbmcgui.ListItem(name, iconImage='', thumbnailImage='', path=rtmpurl)
                        item.setInfo( type="Video",infoLabels={ "Title": name})
                elif optsplit[0] in _playpath:
                        rtmpurl = _url + " playpath=" + _playpath + " swfurl=" + swfUrl + " swfvfy=true"
                        item=xbmcgui.ListItem(name, iconImage='', thumbnailImage='', path=rtmpurl)
                        item.setInfo( type="Video",infoLabels={ "Title": name})
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        #xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(rtmpurl, item)

   
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


def addLink(name, url, mode, iconimage='', plot=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,
                                                "plot": plot} )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok


def addDir(name, url, mode, iconimage='', plot=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,
                                                "plot": plot} )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

              
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

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "\n\n\n\n\n\n\nstart of MTVN plugin\n\n\n\n\n\n"

#List Categories
if mode==None or url==None or len(url)<1:
        print ""
        listCategories()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
#ARTISTS
elif mode==1:
        print ""+url
        listAZ()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==11:
        print ""+url
        listArtistsAZ(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)

#GENRES
elif mode==2:
        print ""+url
        listGenres(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==22:
        print ""+url
        listGenreArtist(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==23:
        print ""+url
        listGenreVideos(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)


#ARTISTS VIDEOS
elif mode==3:
        print ""+url
        listArtistVideos(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)


#RELATED ARTISTS
elif mode==6:
        print ""+url
        listRelatedArtists(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)

#SEARCH ARTISTS or VIDEOS
elif mode==5:
        print ""+url
        listSearch(url)

#Video Picks
elif mode==101:
        print ""+url
        listMTVCOM(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)   

#Play Video
elif mode==4:
        print ""+url
        playRTMP(url, name)
