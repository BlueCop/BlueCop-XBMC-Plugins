import urllib,urllib2,re,sys
import xbmcplugin,xbmcgui
import demjson

playlistMode = True

def getURL( url ):
    try:
        print 'Southpark Studios --> getURL :: url = '+url
        req = urllib2.Request(url)
        req.addheaders = [('Referer', 'http://www.southparkstudios.com/episodes/'),
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

def seasons():
    xbmcplugin.setContent(int(sys.argv[1]), 'seasons')
    addDir('Random Episode','http://www.southparkstudios.com/episodes/random.php',3,'')
    for sn in range(1,15):
        sn = str(sn)
        #addDir('Season '+sn,sn,1,'')
        name = 'Season '+sn
        TVShowTitle='South Park'
        url = sn
        mode = 1
        iconimage = ''
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,
                                                "Season":int(sn),
                                                "TVShowTitle":TVShowTitle
                                                })
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def episodes(season):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    url = 'http://www.southparkstudios.com/includes/utils/proxy_feed.php?html=season_json.jhtml%3fseason=' + season
    json = getURL(url)
    episodes = demjson.decode(json)['season']['episode']
    for episode in episodes:
        title = episode['title']
        description = episode['description']
        thumbnail = episode['thumbnail'].replace('width=55','width=400')
        episodeid = episode['id']
        senumber = episode['episodenumber']
        date = episode['airdate'].replace('.','-')
        seasonnumber = senumber[:-2]
        episodenumber = senumber[len(seasonnumber):]
        itemname = seasonnumber+'x'+episodenumber+' - '+title
        TVShowTitle='South Park'
        mode = 2
        u=sys.argv[0]+"?url="+urllib.quote_plus(episodeid)+"&mode="+str(mode)+"&name="+urllib.quote_plus(itemname)
        liz=xbmcgui.ListItem(itemname, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": itemname,
                                                "Season":int(seasonnumber),
                                                "Episode":int(episodenumber),
                                                "premiered":date,
                                                "Plot":description,
                                                "TVShowTitle":TVShowTitle
                                                })
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def randomEpisode(url):
    data = getURL(url)
    randomEpisodeid=re.compile('swfobject.embedSWF\("http://media.mtvnservices.com/mgid:cms:content:southparkstudios.com:(.+?)"').findall(data)[0]
    rname=re.compile('<title>South Park Episode Player - South Park: (.+?)</title>').findall(data)[0]
    rname = rname.replace("&#039;","'")
    playVideo(randomEpisodeid,rname)

def playVideo(episodeid,rname=''):
    if rname <> '':
        dname = rname
    else:
        dname = name
    swfurl = 'http://media.mtvnservices.com/player/release/?v=4.5.3'
    url = 'http://media.mtvnservices.com/player/config.jhtml?uri=mgid%3Acms%3Acontent%3Asouthparkstudios.com%3A'+episodeid+'&group=entertainment&type=network'
    response = getURL(url)
    rtmp=re.compile('<media:content url="(.+?)" type="text/xml" medium="video" duration=".+?" isDefault=".+?" />').findall(response)
    playlist = xbmc.PlayList(1)
    playlist.clear() 
    counter = 0
    for url in rtmp:
        if counter == 0:
            iname = dname+' - Intro'
        else:
            iname = dname+' - Act '+str(counter)
        counter += 1
        response = getURL(url)
        rtmps=re.compile('<src>(.+?)</src>').findall(response)
        print str(rtmps)
        hbitrate = 0
        hwidth = 0
        h264 = False
        for rtmpbit in rtmps:
            filesplit = rtmpbit.split('/')[-1]
            brsplit  = filesplit.split('_')
            bitrate = int(brsplit[-1].split('.')[-2].replace('kbps',''))
            resolution = brsplit[-2].split('x')
            pixels = int(resolution[0]) * int(resolution[1])
            if bitrate > hbitrate or pixels > hpixels:
                hbitrate = bitrate
                hpixels = pixels
                fname = iname +' '+resolution[0]+'x'+resolution[1]+' '+str(bitrate)+'kbps'
                furl = rtmpbit + " swfurl=" + swfurl + " swfvfy=true"                        
        if playlistMode == False:
            addLink(fname,furl)
        elif playlistMode == True:
            item = xbmcgui.ListItem(iname)
            playlist.add(furl, item)
    if playlistMode == False:
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    elif playlistMode == True:
        xbmc.Player().play(playlist)
        xbmc.executebuiltin('XBMC.ActivateWindow(fullscreenvideo)')

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

       
def addLink(name,url):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok

def addDir(name,url,mode,iconimage=''):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name })
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
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
if mode==None or url==None or len(url)<1:
    print "categories"
    seasons()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==1:
    print "Get Eps"
    episodes(url)

elif mode==2:
    print "Get Rtmp"
    playVideo(url)
elif mode==3:
    print "Random Episode"
    randomEpisode(url)




