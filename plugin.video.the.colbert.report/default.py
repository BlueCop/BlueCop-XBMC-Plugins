import urllib,urllib2,re,xbmcplugin,xbmcgui
import os

pluginhandle = int(sys.argv[1])
shownail = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),"icon.png"))
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(pluginhandle, fanart, color2='0xFFFF3300')
TVShowTitle = 'The Colbert Report' 

if xbmcplugin.getSetting(pluginhandle,"sort") == '0':
        SORTORDER = 'date'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '1':
        SORTORDER = 'views'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '2':
        SORTORDER = 'rating'

################################ Common
def getURL( url ):
    try:
        print 'The Colbert Report --> getURL :: url = '+url
        req = urllib2.Request(url)
        req.addheaders = [('Referer', 'http://www.colbertnation.com/video/'),
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
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot, "TVShowTitle":TVShowTitle})
        liz.setProperty('fanart_image',fanart)
        ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage=shownail,plot=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot, "TVShowTitle":TVShowTitle})
        liz.setProperty('fanart_image',fanart)
        ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
        return ok

def pageFragments(url):
        data = getURL(url)
        try:
                nextpage=re.compile('><span class="pageOff"><a href="(.+?)" class="nextprev" title="Go to Next Page">').findall(data)[0]
                nextpage = 'http://www.colbertnation.com'+nextpage
                addDir('Next Page',nextpage,7)
        except:
                print 'Last or Single page'
        try:
                prevpage=re.compile('\t<span class="pageOff"><a href="(.+?)" class="nextprev" title="Go to Previous Page">').findall(data)[0]
                prevpage = 'http://www.colbertnation.com'+prevpage
                addDir('Previous Page',prevpage,7)
        except:
                print 'No Previous page'
        LISTVIDEOS(url)
        xbmcplugin.endOfDirectory(pluginhandle,updateListing=True)

################################ Root listing
def ROOT():
        addDir('Full Episodes','full',5)
        addDir('Segments','segments',4)
        addDir('Guests','guests',3)
        xbmcplugin.endOfDirectory(pluginhandle)

def FULLEPISODES():
        xbmcplugin.setContent(pluginhandle, 'episodes')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        full = 'http://www.colbertnation.com/full-episodes/'
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
                listings[marker].append(thumbnail+'?width=400')
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
                                                        "TVShowTitle":TVShowTitle})
                liz.setProperty('IsPlayable', 'true')
                liz.setProperty('fanart_image',fanart)
                xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)
        xbmcplugin.endOfDirectory(pluginhandle)

 
def GUESTS():
        segurl = 'http://www.colbertnation.com/video/tag/'
        segments=[('Author','Author'),
                  ('Expert','Expert'),
                  ('Journalist','Journalist'),
                  ('Political Figure','Political+Figure')
                  ]
        for name,link in segments:
            furl = segurl+link
            addDir(name,furl,7)
        xbmcplugin.endOfDirectory(pluginhandle)

def SEGMENTS():
        exclude = ('Author','Expert','Journalist','Political Figure')
        url = 'http://www.colbertnation.com/alltags'
        data = getURL(url)
        tags=re.compile('<div class="navTags"><a href="(.+?)">(.+?)</a><span class="derivitiveTagsNumber">(.+?)</span></div>').findall(data)
        for url, name,count in tags:
                if name in exclude:
                        continue
                url = 'http://www.colbertnation.com'+url
                addDir(name+count,url,7)
        xbmcplugin.endOfDirectory(pluginhandle)


################################ List Videos

def LISTVIDEOS(url):
        xbmcplugin.setContent(pluginhandle, 'episodes')
        data = getURL(url)
        playbackUrls=re.compile('<div class="clipTitle"><a onclick="siteSearchReport\(\);"  href="http://www.colbertnation.com/the-colbert-report-videos/(.+?)"').findall(data)
        #playbackUrls=re.compile('href="http://www.colbertnation.com/the-colbert-report-videos/(.+?)"').findall(data)
        thumbnails=re.compile('<img src="(.+?)?width=.+?"  width=".+?"  height="71"').findall(data)
        names=re.compile('<div class="clipTitle"><a onclick="siteSearchReport\(\);"  href="http://www.colbertnation.com/the-colbert-report-videos/.+?">(.+?)</a></div>').findall(data)
        descriptions=re.compile('<div class="clipDescription">(.+?)\(.+?\)</div>').findall(data)
        durations=re.compile('<div class="clipDescription">.+?\((.+?)\)</div>').findall(data)
        epNumbers=re.compile('<span>Episode:</span> #(.+?)</div>').findall(data)
        airdates=re.compile('<div class="clipDate">Aired: (.+?)</div>').findall(data)
        for pb in playbackUrls:
                url = "http://www.colbertnation.com/the-colbert-report-videos/"+pb
                marker = playbackUrls.index(pb)
                thumbnail = thumbnails[marker]+'?width=400'
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
                u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(11)+"&name="+urllib.quote_plus(fname)
                liz=xbmcgui.ListItem(fname, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
                liz.setInfo( type="Video", infoLabels={ "Title": fname,
                                                        "Episode": episode,
                                                        "Season": season,
                                                        "Plot":description,
                                                        "premiered":date,
                                                        "Duration": duration,
                                                        "TVShowTitle":TVShowTitle})
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
            thumbnail = re.compile('<a rel="media:thumbnail" href="(.+?)">').findall(data)[0] + '?width=400'
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
                                                 "TVShowTitle":TVShowTitle})
        item.setProperty('fanart_image',fanart)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)


################################ Play Full Episode
        
def PLAYFULLEPISODE(name,url):
        data = getURL(url)
        uri=re.compile('<param name="movie" value="http://media.mtvnservices.com/(.+?)"').findall(data)[0]
        url = 'http://media.mtvnservices.com/player/config.jhtml?uri='+uri+'&group=entertainment&type=network&site=colbertnation.com'
        data = getURL(url)
        thumbnail = 'http://www.comedycentral.com/images/shows/'+re.compile('/images/shows/(.+?)\n').findall(data)[0]
        uris=re.compile('<guid isPermaLink="false">(.+?)</guid>').findall(data)
        stacked_url = 'stack://'
        for uri in uris:
            rtmp = GRAB_RTMP(uri)
            stacked_url += rtmp.replace(',',',,')+' , '
        item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail, path=stacked_url)
        item.setInfo( type="Video", infoLabels={ "Title": name,
                                                 "Season":0,
                                                 "Episode":0,
                                                 "TVShowTitle":TVShowTitle})
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
        furl=''
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
        if furl <> '':
                return furl
        else:
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
elif mode==3:
        GUESTS()
elif mode==4:
        SEGMENTS()
elif mode==5:
        FULLEPISODES()
elif mode==7:
        pageFragments(url)
elif mode==9:
        LISTVIDEOS(url)
        xbmcplugin.endOfDirectory(pluginhandle) 
elif mode==10:
        PLAYFULLEPISODE(name,url)
elif mode==11:
        PLAYVIDEO(name,url)
