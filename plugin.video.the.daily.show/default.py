import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime
import demjson

DATELOOKUP = "http://www.thedailyshow.com/fragments/timeline/update?coords="
shownail = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),"icon.png"))
pluginhandle = int (sys.argv[1])

if xbmcplugin.getSetting(pluginhandle,"sort") == '0':#Relevance
        SORTORDER = 'date'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '1':#Date Ascending
        SORTORDER = 'views'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '2':#Date Descending
        SORTORDER = 'rating'

################################ Common
def getURL( url ):
    try:
        print 'The Daily Show --> getURL :: url = '+url
        req = urllib2.Request(url)
        req.addheaders = [('Referer', 'http://www.thedailyshow.com/videos'),
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

def addLink(name,url,iconimage='',plot=''):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot})
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage=shownail,plot=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot})
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def pageFragments(url):
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        pageNum = int(url[-1])
        nextPage = pageNum + 1
        nurl = url.replace('page='+str(pageNum),'page='+str(nextPage))
        if '/box' in nurl:
            nurl = nurl.replace('/box','')
        data = getURL(nurl)
        if 'Your search returned zero results' not in data:
            addDir('Next Page',nurl,7)
        LISTVIDEO(url) 

################################ Root listing
def ROOT():
        addDir('Full Episodes','full',5)
        addDir('Browse by Date','date',1)
        addDir('News Team','newsteam',2)
        addDir('Segments','segments',4)
        addDir('Guests','guests',3)

def FULLEPISODES():
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        for week in range(0,4):
            url = 'http://www.thedailyshow.com/feeds/full-episode/showcase/258329/'+str(week)+'/343079'
            data = getURL(url)
            episodes=re.compile('<span class="date"><a href="(.+?)">(.+?)</a></span>').findall(data)
            thumbnails=re.compile('<img width="156" height="86" src="(.+?)\?width=156" border="0"/>').findall(data)
            descriptions=re.compile('<span class="description">(.+?)</span>').findall(data)
            listings = []
            for link, name in episodes:
                listing = []
                listing.append(name)
                listing.append(link)
                listings.append(listing)
            for thumbnail in thumbnails:
                marker = thumbnails.index(thumbnail)
                listings[marker].append(thumbnail)
            for description in descriptions:
                marker = descriptions.index(description)
                listings[marker].append(description)
            for name, link, thumbnail, plot in listings:
                #addDir(name,link,10,thumbnail,plot)
                mode = 10
                u=sys.argv[0]+"?url="+urllib.quote_plus(link)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
                liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
                liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot})
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
   

def NEWS_TEAM():
        nurl= 'http://www.thedailyshow.com/news-team'
        data = getURL(nurl)
        people=re.compile('href="/news-team/(.+?)"').findall(data)
        names = []
        for name in people:
            name = name.replace('-',' ').title()
            if name not in names:
                names.append(name)
        for name in names:
            link = name.replace(' ','+')
            furl = 'http://www.thedailyshow.com/fragments/search/tags/'+link+'?sort='+SORTORDER+'&page=1'
            addDir(name,furl,7)

        
def GUESTS():
        gurl = "http://www.thedailyshow.com/guests"
        data = getURL(gurl)
        cats=re.compile('<option value="(.+?)">(.+?)</option>').findall(data)
        for link,name in cats:
            furl = 'http://www.thedailyshow.com/fragments/search/box/guests/'+link+'?page=1'
            addDir(name,furl,7)

def SEGMENTS():
        segments=[('Even Stevphen','Even+Stevphen'),
                  ('This Week in God','This+Week+in+God'),
                  ("Mess O'Potamia",'Mess+O%27Potamia'),
                  ('Clusterf#@k to the Poor House','Clusterf%23%40k+to+the+Poor+House'),
                  ('Moment of Zen','Moment+of+Zen'),
                  ('Back in Black','Back+in+Black')
                  ]
        for name, tag in segments:
                url = 'http://www.thedailyshow.com/fragments/search/tags/'+tag+'?sort='+SORTORDER+'&page=1'
                addDir(name,url,7)


################################ Browse by Date
        
def YEARS():
        now = datetime.datetime.now()
        maxyear = int(now.year)+1
        for year in range(1999,maxyear):
                year = str(year)
                ycode = str(int(year)- 1996)
                addDir(year,ycode,11)
                       
def MONTHES(ycode):
        MONTHES = ['January','February','March','April','May','June','July','August','September','October','November','December'] 
        year = str(int(ycode) + 1996)
        mcode = '11'
        dcode = '31'
        url = DATELOOKUP+ycode+','+mcode+','+dcode
        items = demjson.decode(getURL(url))
        #print items['label']
        mticks = items['ticks']['month']
        for tick in mticks:
                mcode = mticks.index(tick)
                if tick['on'] == True:
                        pname = MONTHES[mcode]+' '+year
                        pcode = ycode+','+str(mcode)
                        addDir(pname,pcode,12)

def DATES(ymcode):
        dcode = '31'
        url = DATELOOKUP+ymcode+','+dcode
        items = demjson.decode(getURL(url))
        dticks = items['ticks']['day']
        namesplit = name.split(' ')
        month = namesplit[0]
        year = namesplit[1]
        for tick in dticks:
                if tick['on'] == True:
                        d = dticks.index(tick)
                        if d == 31:
                                continue
                        day = str(d+1)
                        dcode = str(d)
                        addDir((month+' '+day+', '+year),(ymcode+','+dcode),8)
                        
def LISTVIDEODATE(ymdcode):
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        url = DATELOOKUP+ymdcode
        items = demjson.decode(getURL(url))
        dataurl = items['data_url']
        LISTVIDEO(dataurl)
        

################################ List Videos

def LISTVIDEO(url):
        data = getURL(url)
        playbackUrls=re.compile('<a href="http://www.thedailyshow.com/watch/(.+?)">').findall(data)
        for pb in playbackUrls:
                url = "http://www.thedailyshow.com/watch/"+pb
                data = getURL(url)
                fname = re.compile('<span property="media:title" content="(.+?)">').findall(data)[0]
                try:
                    description = re.compile('<span property="dc:description" content="(.+?)">').findall(data)[0]
                except:
                    description = ''
                thumbnail = re.compile('<a rel="media:thumbnail" href="(.+?)">').findall(data)[0]
                uri = re.compile('"http://media.mtvnservices.com/(.+?)"/>').findall(data)[0]
                furl = GRAB_RTMP(uri)
                addLink(fname,furl,thumbnail,description)


################################ Play Full Episode
                
def PLAYVIDEO(name,url):
        data = getURL(url)
        uri=re.compile('<param name="movie" value="http://media.mtvnservices.com/(.+?)"').findall(data)[0]
        url = 'http://media.mtvnservices.com/player/config.jhtml?uri='+uri+'&group=entertainment&type=network&site=thedailyshow.com'
        data = getURL(url)
        uris=re.compile('<guid isPermaLink="false">(.+?)</guid>').findall(data)
        playlist = xbmc.PlayList(1)
        playlist.clear() 
        for uri in uris:
            rtmp = GRAB_RTMP(uri)
            item = xbmcgui.ListItem(name)
            playlist.add(rtmp, item)
        xbmc.Player().play(playlist)
        xbmc.executebuiltin('XBMC.ActivateWindow(fullscreenvideo)')
        
################################ Grab rtmp        

def GRAB_RTMP(uri):
        swfurl = 'http://media.mtvnservices.com/player/release/?v=4.5.3'
        url = 'http://www.comedycentral.com/global/feeds/entertainment/media/mediaGenEntertainment.jhtml?uri='+uri+'&showTicker=true'
        data = getURL(url)
        widths = re.compile('width="(.+?)"').findall(data)
        heights = re.compile('height="(.+?)"').findall(data)
        bitrates = re.compile('bitrate="(.+?)"').findall(data)
        rtmps = re.compile('<src>rtmp(.+?)</src>').findall(data)
        mpixels = 0
        mbitrate = 0
        lbitrate = 0
        if xbmcplugin.getSetting(pluginhandle,"bitrate") == '0':
                lbitrate = 0
        elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '1':
                lbitrate = 1720
        elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '2':
                lbitrate = 1300
        elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '3':
                lbitrate = 960
        elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '4':
                lbitrate = 640
        elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '5':
                lbitrate = 450
        for rtmp in rtmps:
                marker = rtmps.index(rtmp)
                print marker
                w = int(widths[marker])
                h = int(heights[marker])
                bitrate = int(bitrates[marker])
                if bitrate == 0:
                    continue
                elif bitrate > lbitrate and lbitrate <> 0:
                    continue
                elif lbitrate <= bitrate or lbitrate == 0:
                    pixels = w * h
                    if pixels > mpixels or bitrate > mbitrate:
                            mpixels = pixels
                            mbitrate = bitrate
                            #rtmpsplit = rtmp.split('/ondemand')
                            #server = rtmpsplit[0]
                            #path = rtmpsplit[1].replace('.flv','')
                            #if '.mp4' in path:
                            #    path = 'mp4:' + path
                            #port = ':1935'
                            #app = '/ondemand?ovpfv=2.1.4'
                            #furl = 'rtmp'+server+port+app+path+" playpath="+path+" swfurl="+swfurl+" swfvfy=true"
                            furl = 'rtmp'+ rtmp + " swfurl=" + swfurl + " swfvfy=true"
        return furl


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
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)


if mode==None or url==None or len(url)<1:
        ROOT()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==1:
        YEARS()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==11:
        MONTHES(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==12:
        DATES(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==2:
        NEWS_TEAM()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==3:
        GUESTS()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==4:
        SEGMENTS()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==5:
        FULLEPISODES()
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==7:
        pageFragments(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==8:
        LISTVIDEODATE(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==9:
        LISTVIDEO(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]),updateListing=False,cacheToDisc=True)
elif mode==10:
        PLAYVIDEO(name,url)
