import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime
import demjson

DATELOOKUP = "http://www.thedailyshow.com/fragments/timeline/update?coords="

pluginhandle = int(sys.argv[1])
shownail = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),"icon.png"))
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(pluginhandle, fanart, color2='0xFFFF3300')


if xbmcplugin.getSetting(pluginhandle,"sort") == '0':
        SORTORDER = 'date'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '1':
        SORTORDER = 'views'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '2':
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
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot, "TVShowTitle":"The Daily Show"})
        liz.setProperty('fanart_image',fanart)
        ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage=shownail,plot=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot, "TVShowTitle":"The Daily Show"})
        liz.setProperty('fanart_image',fanart)
        ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
        return ok

def pageFragments(url):
        pageNum = int(url[-1])
        nextPage = pageNum + 1
        nurl = url.replace('page='+str(pageNum),'page='+str(nextPage))
        prevPage = pageNum - 1
        purl = url.replace('page='+str(pageNum),'page='+str(prevPage))
        if '/box' in nurl or '/box' in purl:
            nurl = nurl.replace('/box','')                
            purl = purl.replace('/box','')
        data = getURL(nurl)
        if 'Your search returned zero results' not in data:
            addDir('Next Page ('+str(nextPage)+')',nurl,7)
        if prevPage >= 1:
            addDir('Previous Page ('+str(prevPage)+')',purl,7)
        LISTVIDEOS(url)
        xbmcplugin.endOfDirectory(pluginhandle,updateListing=True)

################################ Root listing
def ROOT():
        addDir('Full Episodes','full',5)
        addDir('Browse by Date','date',1)
        addDir('News Team','newsteam',2)
        addDir('Segments','segments',4)
        addDir('Guests','guests',3)
        xbmcplugin.endOfDirectory(pluginhandle)

def FULLEPISODES():
        xbmcplugin.setContent(pluginhandle, 'episodes')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        full = 'http://www.thedailyshow.com/full-episodes/'
        data = getURL(full)
        weeks = re.compile('<a id="(.+?)" class="seaso.+?" href="#">(.+?)</a>').findall(data)
        for url, week in weeks:
            data = getURL(url)
            episodes=re.compile('<span class="date"><a href="(.+?)">(.+?)</a></span>').findall(data)
            thumbnails=re.compile('<img width="156" height="86" src="(.+?)\?width=156" border="0"/>').findall(data)
            descriptions=re.compile('<span class="description">(.+?)</span>').findall(data)
            airdates=re.compile('<span class="date">Aired: (.+?)</span>').findall(data)
            epNumbers=re.compile('<span class="id">Episode (.+?)</span>').findall(data)
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
            for airdate in airdates:
                marker = airdates.index(airdate)
                listings[marker].append(airdate)
            for epNumber in epNumbers:
                marker = epNumbers.index(epNumber)
                listings[marker].append(epNumber)
            for name, link, thumbnail, plot, date, seasonepisode in listings:
                mode = 10
                season = int(seasonepisode[:-3])
                episode = int(seasonepisode[-3:])
                u=sys.argv[0]+"?url="+urllib.quote_plus(link)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
                liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
                liz.setInfo( type="Video", infoLabels={ "Title": name,
                                                        "Plot":plot,
                                                        "Season":season,
                                                        "Episode": episode,
                                                        "premiered":date,
                                                        "TVShowTitle":"The Daily Show"})
                liz.setProperty('IsPlayable', 'true')
                liz.setProperty('fanart_image',fanart)
                xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)
        xbmcplugin.endOfDirectory(pluginhandle)
   

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
        xbmcplugin.endOfDirectory(pluginhandle)

        
def GUESTS():
        gurl = "http://www.thedailyshow.com/guests"
        data = getURL(gurl)
        cats=re.compile('<option value="(.+?)">(.+?)</option>').findall(data)
        for link,name in cats:
            furl = 'http://www.thedailyshow.com/fragments/search/box/guests/'+link+'?page=1'
            addDir(name,furl,7)
        xbmcplugin.endOfDirectory(pluginhandle)

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
        xbmcplugin.endOfDirectory(pluginhandle)


################################ Browse by Date
        
def YEARS():
        now = datetime.datetime.now()
        maxyear = int(now.year)+1
        for year in range(1999,maxyear):
                year = str(year)
                ycode = str(int(year)- 1996)
                addDir(year,ycode,11)
        xbmcplugin.endOfDirectory(pluginhandle)
                       
def MONTHES(ycode):
        MONTHES = ['January','February','March','April','May','June','July','August','September','October','November','December'] 
        year = str(int(ycode) + 1996)
        mcode = '11'
        dcode = '31'
        url = DATELOOKUP+ycode+','+mcode+','+dcode
        items = demjson.decode(getURL(url))
        mticks = items['ticks']['month']
        for tick in mticks:
                mcode = mticks.index(tick)
                if tick['on'] == True:
                        pname = MONTHES[mcode]+' '+year
                        pcode = ycode+','+str(mcode)
                        addDir(pname,pcode,12)
        xbmcplugin.endOfDirectory(pluginhandle)

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
        xbmcplugin.endOfDirectory(pluginhandle)
                        
def LISTVIDEODATE(ymdcode):
        xbmcplugin.setContent(pluginhandle, 'episodes')
        url = DATELOOKUP+ymdcode
        items = demjson.decode(getURL(url))
        dataurl = items['data_url']
        LISTVIDEOS(dataurl)
        xbmcplugin.endOfDirectory(pluginhandle)
        

################################ List Videos

def LISTVIDEOS(url):
        xbmcplugin.setContent(pluginhandle, 'episodes')
        data = getURL(url)
        playbackUrls=re.compile('<a href="http://www.thedailyshow.com/watch/(.+?)">').findall(data)
        thumbnails=re.compile('<img src="(.+?)?width=.+?"').findall(data)
        names=re.compile('<span class="title"><a href=".+?">(.+?)</a></span>').findall(data)
        descriptions=re.compile('<span class="description">(.+?)\(.+?\)</span>').findall(data)
        durations=re.compile('<span class="description">.+?\((.+?)\)</span>').findall(data)
        epNumbers=re.compile('<span class="episode">Episode #(.+?)</span>').findall(data)
        airdates=re.compile('<span>Aired.+?</span>(.+?)</div>').findall(data)
        for pb in playbackUrls:
                url = "http://www.thedailyshow.com/watch/"+pb
                marker = playbackUrls.index(pb)
                thumbnail = thumbnails[marker]
                fname = names[marker]
                description = descriptions[marker]
                duration = durations[marker]
                try:
                        seasonepisode = epNumbers[marker]
                        season = int(seasonepisode[:-3])
                        episode = int(seasonepisode[-3:])
                except:
                        season = 0
                        episode = 0
                date = airdates[marker]
                u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(13)+"&name="+urllib.quote_plus(fname)
                liz=xbmcgui.ListItem(fname, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
                liz.setInfo( type="Video", infoLabels={ "Title": fname,
                                                        "Episode": episode,
                                                        "Season": season,
                                                        "Plot":description,
                                                        "premiered":date,
                                                        "Duration": duration,
                                                        "TVShowTitle":"The Daily Show"})
                liz.setProperty('IsPlayable', 'true')
                liz.setProperty('fanart_image',fanart)
                xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)
                


################################ Play Video
                
def PLAYVIDEO(name,url):
        data = getURL(url)
        #try:
        #        fname = re.compile('property="media:title" content="(.+?)">').findall(data)[0]
        #except:
        #        fname = re.compile('<meta name="title" content="(.+?)"').findall(data)[0]
        try:
            description = re.compile('<span property="dc:description" content="(.+?)">').findall(data)[0]
        except:
            description = ''
        try:
            thumbnail = re.compile('<a rel="media:thumbnail" href="(.+?)">').findall(data)[0]
        except:
            thumbnail = ''
        try:
            date = re.compile('<span property="dc:date" content="(.+?)"></span>').findall(data)[0]
        except:
            date = ''
        uri = re.compile('"http://media.mtvnservices.com/(.+?)"/>').findall(data)[0]
        rtmp = GRAB_RTMP(uri)
        item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail, path=rtmp)
        item.setInfo( type="Video", infoLabels={ "Title": name,
                                                 "Plot":description,
                                                 "premiered":date,
                                                 "Season":0,
                                                 "Episode":0,
                                                 "TVShowTitle":"The Daily Show"})
        item.setProperty('fanart_image',fanart)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)

################################ Play Full Episode
                
def PLAYFULLEPISODE(name,url):
        data = getURL(url)
        uri=re.compile('<param name="movie" value="http://media.mtvnservices.com/(.+?)"').findall(data)[0]
        url = 'http://media.mtvnservices.com/player/config.jhtml?uri='+uri+'&group=entertainment&type=network&site=thedailyshow.com'
        data = getURL(url)
        thumbnail = 'http://www.thedailyshow.com/images/shows/'+re.compile('/images/shows/(.+?)\n').findall(data)[0]
        uris=re.compile('<guid isPermaLink="false">(.+?)</guid>').findall(data)
        stacked_url = 'stack://'
        for uri in uris:
            rtmp = GRAB_RTMP(uri)
            stacked_url += rtmp.replace(',',',,')+' , '
        item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail, path=stacked_url)
        item.setInfo( type="Video", infoLabels={ "Title": name,
                                                 "Season":0,
                                                 "Episode":0,
                                                 "TVShowTitle":"The Daily Show"})
        item.setProperty('fanart_image',fanart)
        print stacked_url
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        
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
elif mode==1:
        YEARS()
elif mode==11:
        MONTHES(url)
elif mode==12:
        DATES(url)
elif mode==2:
        NEWS_TEAM()
elif mode==3:
        GUESTS()
elif mode==4:
        SEGMENTS()
elif mode==5:
        FULLEPISODES()
elif mode==7:
        pageFragments(url)
elif mode==8:
        LISTVIDEODATE(url)
elif mode==9:
        LISTVIDEOS(url)
elif mode==10:
        PLAYFULLEPISODE(name,url)
elif mode==13:
        PLAYVIDEO(name,url)
