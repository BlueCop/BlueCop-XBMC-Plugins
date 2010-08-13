import urllib,urllib2,re,sys,os
import xbmcplugin,xbmcgui
import demjson

fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(int(sys.argv[1]), fanart, color2='0xFFFF3300')
TVShowTitle='South Park'

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
    addRandom('Random Episode','http://www.southparkstudios.com/episodes/random.php',3)
    for sn in range(1,15):
        sn = str(sn)
        name = 'Season '+sn
        url = sn
        mode = 1
        iconimage = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'resources','images','season'+sn+'.jpg'))
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,
                                                "Season":int(sn),
                                                "TVShowTitle":TVShowTitle
                                                })
        liz.setProperty('fanart_image',fanart)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def addRandom(name,url,mode):
    iconimage = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name })
    liz.setProperty('IsPlayable', 'true')
    liz.setProperty('fanart_image',fanart)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
    return ok

def randomEpisode(url):
    data = getURL(url)
    randomEpisodeid=re.compile('swfobject.embedSWF\("http://media.mtvnservices.com/mgid:cms:content:southparkstudios.com:(.+?)"').findall(data)[0]
    name = re.compile('<title>South Park Episode Player - South Park: (.+?)</title>').findall(data)[0]
    name = name.replace("&#039;","'")
    thumbnail = re.compile('<link rel="image_src" href="(.+?)?width=90&quality=100"').findall(data)[0]
    playVideo(randomEpisodeid,name,thumbnail)

def episodes(season):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_EPISODE)
    url = 'http://www.southparkstudios.com/includes/utils/proxy_feed.php?html=season_json.jhtml%3fseason=' + season
    json = getURL(url)
    episodes = demjson.decode(json)['season']['episode']
    for episode in episodes:
        title = episode['title']
        description = episode['description']
        thumbnail = episode['thumbnail'].replace('width=55','')
        episodeid = episode['id']
        senumber = episode['episodenumber']
        date = episode['airdate'].replace('.','-')
        seasonnumber = senumber[:-2]
        episodenumber = senumber[len(seasonnumber):]
        mode = 2
        u=sys.argv[0]+"?url="+urllib.quote_plus(episodeid)+"&mode="+str(mode)+"&name="+urllib.quote_plus(title)
        u += "&season="+urllib.quote_plus(seasonnumber)
        u += "&episode="+urllib.quote_plus(episodenumber)
        u += "&premiered="+urllib.quote_plus(date)
        u += "&plot="+urllib.quote_plus(description)
        u += "&thumbnail="+urllib.quote_plus(thumbnail)
        ok=True
        liz=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": title,
                                                "Season":int(seasonnumber),
                                                "Episode":int(episodenumber),
                                                "premiered":date,
                                                "Plot":description,
                                                "TVShowTitle":TVShowTitle
                                                })
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image',fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def playVideo(episodeid,name,thumbnail):
    dname = name
    swfurl = 'http://media.mtvnservices.com/player/release/?v=4.5.3'
    url = 'http://media.mtvnservices.com/player/config.jhtml?uri=mgid%3Acms%3Acontent%3Asouthparkstudios.com%3A'+episodeid+'&group=entertainment&type=network'
    response = getURL(url)
    rtmp=re.compile('<media:content url="(.+?)" type="text/xml" medium="video" duration=".+?" isDefault=".+?" />').findall(response)
    final_urls = []
    for url in rtmp:
        response = getURL(url)
        rtmps=re.compile('<src>(.+?)</src>').findall(response)
        hbitrate = 0
        hwidth = 0
        for rtmpbit in rtmps:
            filesplit = rtmpbit.split('/')[-1]
            brsplit  = filesplit.split('_')
            bitrate = int(brsplit[-1].split('.')[-2].replace('kbps',''))
            resolution = brsplit[-2].split('x')
            pixels = int(resolution[0]) * int(resolution[1])
            if bitrate > hbitrate or pixels > hpixels:
                hbitrate = bitrate
                hpixels = pixels
                furl = rtmpbit + " swfurl=" + swfurl + " swfvfy=true"
        final_urls.append(furl)
    stacked_url = 'stack://'
    for stack in final_urls:
        if len(final_urls) == final_urls.index(stack):
            stacked_url += stack.replace(',',',,')
        else:
            stacked_url += stack.replace(',',',,')+' , '
    item=xbmcgui.ListItem(dname, thumbnailImage=thumbnail, path=stacked_url)
    item.setInfo( type="Video", infoLabels={"Title": dname,
                                            "Season":season,
                                            "Episode":episode,
                                            "premiered":premiered,
                                            "Plot":plot,
                                            "TVShowTitle":TVShowTitle
                                            })
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)  

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
    name=''
try:
    mode=int(params["mode"])
except:
    pass
try:
    thumbnail=urllib.unquote_plus(params["thumbnail"])
except:
    thumbnail=''
try:
    season=int(params["season"])
except:
    season=0
try:
    episode=int(params["episode"])
except:
    episode=0
try:
    premiered=urllib.unquote_plus(params["premiered"])
except:
    premiered=''
try:
    plot=urllib.unquote_plus(params["plot"])
except:
    plot=''

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
    playVideo(url,name,thumbnail)
elif mode==3:
    print "Random Episode"
    randomEpisode(url)




