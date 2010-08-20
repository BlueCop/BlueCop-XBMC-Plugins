__plugin__ = "Yahoo Music Videos Plugin"
__authors__ = "BlueCop"
__credits__ = ""
__version__ = "0.1"

import urllib, urllib2
import os, re, sys, md5, string
import xbmc, xbmcgui, xbmcplugin


pluginhandle = int (sys.argv[1])

#MAXLISTING = (int(xbmcplugin.getSetting(pluginhandle,"maxlist")) + 1) * 5
#if xbmcplugin.getSetting(pluginhandle,"sort") == '0':#Relevance
#        SORTORDER = 'relevance'
#elif xbmcplugin.getSetting(pluginhandle,"sort") == '1':#Date Ascending
#        SORTORDER = 'date_ascending'
#elif xbmcplugin.getSetting(pluginhandle,"sort") == '2':#Date Descending
#        SORTORDER = 'date_descending'

################################ Common
def getURL( url ):
    try:
        print 'Yahoo Music Videos --> getURL :: url = '+url
        req = urllib2.Request(url)
        req.addheaders = [('Referer', 'http://new.music.yahoo.com/videos/'),
                          ('Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)')]
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

     
def listCategories():
        addDir('Top Videos', 'artists', 1)
        addDir('New Videos', 'artists', 2)
        addDir('Reccomended Videos', 'artists', 3)
        return

def addVideos(datatype, results, start):
        url = 'http://new.music.yahoo.com/playlistMgrGetContents?datatype='+datatype+'&results='+results+'&start='+start
        data=getURL(url)
        videos=re.compile('<div class="ymusic_mediaInfo" img73=".+?" img130="(.+?)" aname="(.+?)" aid="(.+?)" vname="(.+?)" vid="(.+?)">').findall(data)
        for thumbnail, artistName, artistID, videoName, videoID in videos:
                thumbnail = thumbnail.replace('size=146x88','size=438x264')
                addLink(artistName+' - '+videoName, videoID, 10, thumbnail)       


def topVideos():
        addVideos('popular', '100', '1')
        addVideos('popular', '100', '101')
        addVideos('popular', '100', '201')
        addVideos('popular', '100', '301')
        addVideos('popular', '100', '401')
def newVideos():
        addVideos('new', '100', '1')
        addVideos('new', '100', '101')
        addVideos('new', '100', '201')
        addVideos('new', '100', '301')
        addVideos('new', '100', '401')
        
def reccomendedVideos():
        addVideos('recommended', '100', '1')
        addVideos('recommended', '100', '101')


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
                
#Get SMIL url and play video
def playRTMP(url, name):
        url = 'http://video.music.yahoo.com/up/music_e/process/getPlaylistFOP.php?node_id=v'+ url + '&tech=flash&bitrate=20000&mode=&vidH=720&vidW=1280'
        swfUrl = 'http://d.yimg.com/m/up/fop/embedflv/swf/fop.swf'
        data=getURL(url)
        rtmpParts=re.compile('STREAM APP="(.+?)" FULLPATH="(.+?)" CLIPID').findall(data)
        for app, fullpath in rtmpParts:
                playpath = fullpath.replace('.flv','')
                rtmpurl = app+fullpath+" playpath="+playpath+" swfurl="+swfUrl+" swfvfy=true"
        item=xbmcgui.ListItem(name, iconImage='', thumbnailImage='', path=rtmpurl)
        item.setInfo( type="Video",infoLabels={ "Title": name})
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)

   
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

#List Root
if mode==None or url==None or len(url)<1:
        print ""
        listCategories()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)

elif mode==1:
        print ""+url
        topVideos()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==2:
        print ""+url
        newVideos()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==3:
        print ""+url
        reccomendedVideos()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)

#SEARCH ARTISTS or VIDEOS
elif mode==5:
        print ""+url
        listSearch(url)

#Play Video
elif mode==10:
        print ""+url
        playRTMP(url, name)
