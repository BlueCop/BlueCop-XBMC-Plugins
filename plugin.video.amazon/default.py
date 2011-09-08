# -*- coding: utf_8 -*-
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
from datetime import datetime
import base64
import binascii
import cookielib
import demjson
import md5
import mechanize
import operator
import sys
import time
import urllib
import urllib2
import cookielib
import re
import os.path
import xbmcplugin
import xbmcgui
try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

pluginhandle = int(sys.argv[1])

COOKIEFILE = os.path.join(os.getcwd().replace(';', ''),'resources','cache','cookies.lwp')
cj = cookielib.LWPCookieJar()

BASE_URL = 'http://www.amazon.com'
NEW_MOVIE_URL = 'http://www.amazon.com/gp/search/ref=sr_nr_p_n_date_0?rh=n%3A2625373011%2Cn%3A!2644981011%2Cn%3A!2644982011%2Cn%3A2858778011%2Cn%3A2858905011%2Cp_85%3A2470955011%2Cp_n_date%3A2693527011&bbn=2858905011&ie=UTF8&qid=1315385409&rnid=2693522011'
MOVIE_URL = 'http://www.amazon.com/gp/search/ref=sr_st?qid=1314934213&rh=n%3A2625373011%2Cn%3A!2644981011%2Cn%3A!2644982011%2Cn%3A2858778011%2Cn%3A2858905011%2Cp_85%3A2470955011&sort=-releasedate'
TV_URL = 'http://www.amazon.com/gp/search/ref=sr_st?qid=1314982661&rh=n%3A2625373011%2Cn%3A!2644981011%2Cn%3A!2644982011%2Cn%3A2858778011%2Cn%3A2864549011%2Cp_85%3A2470955011&sort=-releasedate'
# 501-POSTER WRAP 503-MLIST3 504=MLIST2 508-FANARTPOSTER 
confluence_views = [500,501,502,503,504,508]

def getURL( url , host='www.amazon.com'):
    print 'getURL: '+url
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17'),
                         ('Host', host)]
    usock = opener.open(url)
    response = usock.read()
    usock.close()
    return response

def addDir(name,url,mode,poster='',fanart='',infoLabels=False,totalItems=0,cm=False):
    if not infoLabels:
        infoLabels={ "Title": name}
    u=sys.argv[0]
    u+="?url="+urllib.quote_plus(url)
    u+="&mode="+urllib.quote_plus(mode)
    u+="&name="+urllib.quote_plus(infoLabels['Title'])
    u+="&thumb="+urllib.quote_plus(poster)
    u+="&fanart="+urllib.quote_plus(fanart)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=poster)
    liz.setInfo( type="Video", infoLabels=infoLabels)
    liz.setProperty('fanart_image',fanart)
    if cm:
        liz.addContextMenuItems( cm )
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True,totalItems=totalItems)
    return ok

def addVideo(name,url,poster='',fanart='',infoLabels=False,totalItems=0,cm=False):
    if not infoLabels:
        infoLabels={ "Title": name}
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=PLAYVIDEO&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name, thumbnailImage=poster)
    utrailer=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=PLAYTRAILER&name="+urllib.quote_plus(name)
    infoLabels['Trailer']=utrailer
    liz.setInfo( type="Video", infoLabels=infoLabels)
    liz.setProperty('fanart_image',fanart)
    liz.setProperty('IsPlayable', 'true')
    if cm:
        liz.addContextMenuItems( cm )
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=False,totalItems=totalItems)     

def mechanizeLogin():
    if os.path.isfile(COOKIEFILE):
        os.remove(COOKIEFILE)
    br = mechanize.Browser()  
    br.set_handle_robots(False)
    br.set_cookiejar(cj)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17')]  
    sign_in = br.open("http://www.amazon.com/gp/flex/sign-out.html")   
    br.select_form(name="sign-in")  
    br["email"] = xbmcplugin.getSetting(pluginhandle,"login_name")
    br["password"] = xbmcplugin.getSetting(pluginhandle,"login_pass")
    logged_in = br.submit()  
    error_str = "The e-mail address and password you entered do not match any accounts on record."  
    if error_str in logged_in.read():
        xbmcgui.Dialog().ok('Login Error',error_str)
        print error_str
    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)

def oldlogin():
    if os.path.isfile(COOKIEFILE):
        os.remove(COOKIEFILE)
    data=getURL(BASE_URL)
    SIGNIN_URL = re.compile('<a href="(.+?)" rel="nofollow">Sign in</a>').findall(data)[0].replace('&amp;','&')
    data = getURL(SIGNIN_URL)
    form =  '<form name="signIn"' + re.compile('<form name="signIn"(.*?)</form>',re.DOTALL).findall(data)[0] + '</form>'
    tree = BeautifulSoup(form, convertEntities=BeautifulSoup.HTML_ENTITIES)
    action_url = tree.form['action']
    items = tree.findAll('input',attrs={'type' : 'hidden'})
    values = {}
    for item in items:
        values[item['name']] = item['value']
    values['create'] = '0'
    values['email'] =       xbmcplugin.getSetting(pluginhandle,"login_name")
    values['password'] =    xbmcplugin.getSetting(pluginhandle,"login_pass")
    postURL(action_url,values)
    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)


def GETTRAILERS(getstream):
    try:
        data = getURL(getstream,'atv-ps.amazon.com')
        print data
        rtmpdata = demjson.decode(data)
        print rtmpdata
        sessionId = rtmpdata['message']['body']['streamingURLInfoSet']['sessionId']
        cdn = rtmpdata['message']['body']['streamingURLInfoSet']['cdn']
        rtmpurls = rtmpdata['message']['body']['streamingURLInfoSet']['streamingURLInfo']
        return rtmpurls, sessionId, cdn
    except:
        return False, False, False

def PLAYTRAILER():
    videoname = params['name']
    swfUrl, values = GETFLASHVARS(params['url']) 
    values['deviceID'] = values['customerID'] + str(int(time.time() * 1000)) + values['asin']
    getstream  = 'https://atv-ps.amazon.com/cdp/catalog/GetStreamingTrailerUrls'
    getstream += '?asin='+values['asin']
    getstream += '&deviceTypeID='+values['deviceTypeID']
    getstream += '&deviceID='+values['deviceID']
    getstream += '&firmware=LNX%2010,3,181,14%20PlugIn'
    getstream += '&format=json'
    getstream += '&version=1'
    rtmpurls, streamSessionID, cdn = GETTRAILERS(getstream)
    if rtmpurls == False:
        xbmcgui.Dialog().ok('Trailer Not Available',videoname)
    elif cdn == 'limelight':
        xbmcgui.Dialog().ok('Limelight CDN','Limelight uses swfverfiy2. Playback may fail.')
    else:
        PLAY(rtmpurls,swfUrl=swfUrl,Trailer=videoname)
        
def GETSTREAMS(getstream):
    try:
        data = getURL(getstream,'atv-ps.amazon.com')
        print data
        rtmpdata = demjson.decode(data)
        print rtmpdata
        sessionId = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['sessionId']
        cdn = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['cdn']
        rtmpurls = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['streamingURLInfo']
        return rtmpurls, sessionId, cdn
    except:
        return False, False, False

def PLAYVIDEO():
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    swfUrl, values = GETFLASHVARS(params['url'])            
    values['deviceID'] = values['customerID'] + str(int(time.time() * 1000)) + values['asin']
    getstream  = 'https://atv-ps.amazon.com/cdp/catalog/GetStreamingUrlSets'
    getstream += '?asin='+values['asin']
    getstream += '&deviceTypeID='+values['deviceTypeID']
    getstream += '&firmware=LNX%2010,3,181,14%20PlugIn'
    getstream += '&customerID='+values['customerID']
    getstream += '&deviceID='+values['deviceID']
    getstream += '&token='+values['token']
    getstream += '&xws-fa-ov=true'
    getstream += '&format=json'
    getstream += '&version=1'
    rtmpurls, streamSessionID, cdn = GETSTREAMS(getstream)
    if cdn == 'limelight':
        xbmcgui.Dialog().ok('Limelight CDN','Limelight uses swfverfiy2. Playback may fail.')
    if rtmpurls <> False:
        basertmp, ip = PLAY(rtmpurls,swfUrl=swfUrl)
    if streamSessionID <> False:
        epoch = str(int(time.mktime(time.gmtime()))*1000)
        USurl =  'https://atv-ps.amazon.com/cdp/usage/UpdateStream'
        USurl += '?device_type_id='+values['deviceTypeID']
        USurl += '&deviceTypeID='+values['deviceTypeID']
        USurl += '&streaming_session_id='+streamSessionID
        USurl += '&operating_system=Linux%202.6.35-28-generic'
        USurl += '&timecode=45.003'
        USurl += '&flash_version=LNX%2010,3,181,14%20PlugIn'
        USurl += '&asin='+values['asin']
        USurl += '&token='+values['token']
        USurl += '&browser='+urllib.quote_plus(values['userAgent'])
        USurl += '&server_id='+ip
        USurl += '&client_version='+swfUrl.split('/')[-1]
        USurl += '&unique_browser_id='+values['UBID']
        USurl += '&device_id='+values['deviceID']
        USurl += '&format=json'
        USurl += '&version=1'
        USurl += '&page_type='+values['pageType']
        USurl += '&start_state=Video'
        USurl += '&amazon_session_id='+values['sessionID']
        USurl += '&event=STOP'
        USurl += '&firmware=LNX%2010,3,181,14%20PlugIn'
        USurl += '&customerID='+values['customerID']
        USurl += '&deviceID='+values['deviceID']
        USurl += '&source_system=http://www.amazon.com'
        USurl += '&http_referer=ecx.images-amazon.com'
        USurl += '&event_timestamp='+epoch
        USurl += '&encrypted_customer_id='+values['customerID']
        print getURL(USurl,'atv-ps.amazon.com')

        epoch = str(int(time.mktime(time.gmtime()))*1000)
        surl =  'https://atv-ps.amazon.com/cdp/usage/ReportStopStreamEvent'
        surl += '?deviceID='+values['deviceID']
        surl += '&source_system=http://www.amazon.com'
        surl += '&format=json'
        surl += '&event_timestamp='+epoch
        surl += '&encrypted_customer_id='+values['customerID']
        surl += '&http_referer=ecx.images-amazon.com'
        surl += '&device_type_id='+values['deviceTypeID']
        surl += '&download_bandwidth=9926.295518207282'
        surl += '&device_id='+values['deviceTypeID']
        surl += '&from_mode=purchased'
        surl += '&operating_system=Linux%202.6.35-28-generic'
        surl += '&version=1'
        surl += '&flash_version=LNX%2010,3,181,14%20PlugIn'
        surl += '&url='+urllib.quote_plus(basertmp)
        surl += '&streaming_session_id='+streamSessionID
        surl += '&browser='+urllib.quote_plus(values['userAgent'])
        surl += '&server_id='+ip
        surl += '&client_version='+swfUrl.split('/')[-1]
        surl += '&unique_browser_id='+values['UBID']
        surl += '&amazon_session_id='+values['sessionID']
        surl += '&page_type='+values['pageType']
        surl += '&start_state=Video'
        surl += '&token='+values['token']
        surl += '&to_timecode=3883'
        surl += '&streaming_bit_rate=348'
        surl += '&new_streaming_bit_rate=2500'
        surl += '&asin='+values['asin']
        surl += '&deviceTypeID='+values['deviceTypeID']
        surl += '&firmware=LNX%2010,3,181,14%20PlugIn'
        surl += '&customerID='+values['customerID']
        print getURL(surl,'atv-ps.amazon.com')
        if values['pageType'] == 'movie':
            watchMoviedb(values['asin'])
        if values['pageType'] == 'tv':
            watchEpisodedb(values['asin'])

def GETFLASHVARS(pageurl):
    showpage = getURL(pageurl)
    flashVars = re.compile("'flashVars', '(.*?)' \+ new Date\(\)\.getTime\(\)\+ '(.*?)'",re.DOTALL).findall(showpage)
    flashVars =(flashVars[0][0] + flashVars[0][1]).split('&')
    swfUrl = re.compile("avodSwfUrl = '(.*?)'\;").findall(showpage)[0]
    values={'token'          :'',
            'deviceTypeID'   :'A13Q6A55DBZB7M',
            'version'        :'1',
            'firmware'       :'1',       
            'customerID'     :'',
            'format'         :'json',
            'deviceID'       :'',
            'asin'           :''      
            }
    for item in flashVars:
        item = item.split('=')
        if item[0]      == 'token':
            values[item[0]]         = item[1]
        elif item[0]    == 'customer':
            values['customerID']    = item[1]
        elif item[0]    == 'ASIN':
            values['asin']          = item[1]
        elif item[0]    == 'pageType':
            values['pageType']      = item[1]        
        elif item[0]    == 'UBID':
            values['UBID']          = item[1]
        elif item[0]    == 'sessionID':
            values['sessionID']     = item[1]
        elif item[0]    == 'userAgent':
            values['userAgent']     = item[1]
    return swfUrl, values
        
def PLAY(rtmpurls,swfUrl,Trailer=False):
    print rtmpurls
    quality = [0,2500,1328,996,664,348]
    lbitrate = quality[int(xbmcplugin.getSetting(pluginhandle,"bitrate"))]
    mbitrate = 0
    streams = []
    for data in rtmpurls:
        url = data['url']
        bitrate = int(data['bitrate'])
        if lbitrate == 0:
            streams.append([bitrate,url])
        elif bitrate >= mbitrate and bitrate <= lbitrate:
            mbitrate = bitrate
            rtmpurl = url
    if lbitrate == 0:        
        quality=xbmcgui.Dialog().select('Please select a quality level:', [str(stream[0])+'kbps' for stream in streams])
        print quality
        if quality!=-1:
            rtmpurl = streams[quality][1]
    protocolSplit = rtmpurl.split("://")
    pathSplit   = protocolSplit[1].split("/")
    hostname    = pathSplit[0]
    appName     = protocolSplit[1].split(hostname + "/")[1].split('/')[0]    
    streamAuth  = rtmpurl.split(appName+'/')[1].split('?')
    stream      = streamAuth[0].replace('.mp4','')
    auth        = streamAuth[1]
    identurl = 'http://'+hostname+'/fcs/ident'
    ident = getURL(identurl)
    ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
    basertmp = 'rtmpe://'+ip+':1935/'+appName+'?_fcs_vhost='+hostname+'&ovpfv=2.1.4&'+auth
    finalUrl = basertmp
    finalUrl += " playpath=" + stream 
    finalUrl += " pageurl=" + params['url']
    finalUrl += " swfurl=" + swfUrl + " swfvfy=true"
    if Trailer:
        finalname = Trailer+' Trailer'
        item = xbmcgui.ListItem(finalname,path=finalUrl)
        item.setInfo( type="Video", infoLabels={ "Title": finalname})
        item.setProperty('IsPlayable', 'true')
        xbmc.Player().play(finalUrl,item)
    else:
        item = xbmcgui.ListItem(path=finalUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    return basertmp, ip

################################ Root listing
def ROOT():
    try:
        mechanizeLogin()
    except:
        oldlogin()
    updatemovie = []  
    updatemovie.append( ('Full Movie Refresh', "XBMC.RunPlugin(%s?mode=addMoviesdb)" % ( sys.argv[0] ) ) )
    updatemovie.append( ('Update New Movies',  "XBMC.RunPlugin(%s?mode=addNewMoviesdb)" % ( sys.argv[0] ) ) )
    addNewMoviesdb
    addDir('Movies'     ,''                  ,'LIST_MOVIE_ROOT',cm=updatemovie)
    updatetv = [] 
    updatetv.append( ('Full Television Refresh', "XBMC.RunPlugin(%s?mode=addTVdb)" % ( sys.argv[0] ) ) )
    updatetv.append( ('Update New Television',   "XBMC.RunPlugin(%s?mode=addNewTVdb)" % ( sys.argv[0] ) ) )
    updatetv.append( ('Fix HD Shows',   "XBMC.RunPlugin(%s?mode=fixHDshows)" % ( sys.argv[0] ) ) )
    updatetv.append( ('Scan TVDB',   "XBMC.RunPlugin(%s?mode=scanTVDBshows)" % ( sys.argv[0] ) ) )
    addDir('Television' ,''                  ,'LIST_TV_ROOT',cm=updatetv)
    if xbmcplugin.getSetting(pluginhandle,'enablelibrary') == 'true':
        addDir('My Library' ,''              ,'LIBRARY_ROOT')
    xbmcplugin.endOfDirectory(pluginhandle)

################################ Library listing    
def LIBRARY_ROOT():
    addDir('Movie Library'      ,'https://www.amazon.com/gp/video/library/movie?show=all&sort=alpha'      ,'LIBRARY_LIST_MOVIES')
    addDir('Television Library' ,'https://www.amazon.com/gp/video/library/tv?show=all&sort=alpha'         ,'LIBRARY_LIST_TV')
    xbmcplugin.endOfDirectory(pluginhandle)

def LIBRARY_LIST_MOVIES():
    xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    url = params['url']
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('div',attrs={'class':'lib-item','asin':True})
    totalItems = len(videos)
    for video in videos:
        asin = video['asin']
        movietitle = video.find('',attrs={'class':'title'}).a.string
        url = BASE_URL+video.find('div',attrs={'class':'title'}).a['href']
        thumb = video.find('img')['src'].replace('._SS160_','')
        fanart = thumb.replace('.jpg','._BO354,0,0,0_CR177,354,708,500_.jpg')       
        #if xbmcplugin.getSetting(pluginhandle,'enablelibrarymeta') == 'true':
        #    asin2,movietitle,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart,isprime,watched,favor = getMovieInfo(asin,movietitle,url,poster,isPrime=False)
        #    actors = actors.split(',')
        #    infoLabels = { 'Title':movietitle,'Plot':plot,'Year':year,'premiered':premiered,
        #                   'rating':stars,'votes':votes,'Genre':genres,'director':director,
        #                   'studio':studio,'duration':runtime,'mpaa':mpaa,'cast':actors}
        #else:
        infoLabels = { 'Title':name}
        addVideo(name,url,thumb,fanart,infoLabels=infoLabels,totalItems=totalItems)
    view=int(xbmcplugin.getSetting(pluginhandle,"movieview"))
    xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle)

def LIBRARY_LIST_TV():
    url = params['url']
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('div',attrs={'class':'lib-item','asin':True})
    totalItems = len(videos)
    for video in videos:
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        asin = video['asin']
        name = video.find('',attrs={'class':'title'}).a.string
        thumb = video.find('img')['src'].replace('._SS160_','')
        if '[HD]' in name: isHD = True
        else: isHD = False
        url = BASE_URL+video.find('div',attrs={'class':'title'}).a['href']
        #if xbmcplugin.getSetting(pluginhandle,'enablelibrarymeta') == 'true':
        #    asin2,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart = getShowInfo(url,asin,isHD)
        #    actors = actors.split(',')
        #    infoLabels={'Title': name,'Plot':plot,'year':year,'rating':stars,'votes':votes,
        #                'Genre':genres,'Season':season,'episode':episodes,'studio':network,
        #                'duration':runtime,'cast':actors,'TVShowTitle':name,'credits':creator}
        #    if year <> 0: infoLabels['premiered'] = str(year)
        #else:
        infoLabels = { 'Title':name}
        addDir(name,url,'LIBRARY_EPISODES',thumb,thumb,infoLabels,totalItems)
    view=int(xbmcplugin.getSetting(pluginhandle,"showview"))
    xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle)

def LIBRARY_EPISODES():
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    LIST_EPISODES(owned=True)
    
def LIST_EPISODES(owned=False):
    episode_url = params['url']
    showname = params['name']
    thumbnail = params['thumb']
    xbmcplugin.setContent(int(sys.argv[1]), 'Episodes') 
    data = getURL(episode_url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodebox = tree.find('div',attrs={'id':'avod-ep-list-rows'})
    episodes = episodebox.findAll('tr',attrs={'asin':True})
    try:season = int(tree.find('div',attrs={'class':'unbox_season_selected'}).string)
    except:
        try:season = int(tree.find('div',attrs={'style':'font-size: 120%;font-weight:bold; margin-top:15px;margin-bottom:10px;'}).contents[0].split('Season')[1].strip())
        except:season = 0
    del tree
    del episodebox
    for episode in episodes:
        if owned:
            purchasecheckbox = episode.find('input',attrs={'type':'checkbox'})
            if purchasecheckbox:
                continue
        asin = episode['asin']
        name = episode.find(attrs={'title':True})['title'].encode('utf-8')
        airDate = episode.find(attrs={'style':'width: 150px; overflow: hidden'}).string.strip()
        try: plot =  episode.findAll('div')[1].string.strip()
        except: plot = ''
        episodeNum = int(episode.find('div',attrs={'style':'width: 185px;'}).string.split('.')[0].strip())
        if season == 0: displayname =  str(episodeNum)+'. '+name
        else: displayname =  str(season)+'x'+str(episodeNum)+' - '+name
        url = BASE_URL+'/gp/product/'+asin
        infoLabels={'Title': name.replace('[HD]',''),'TVShowTitle':showname,
                    'Plot':plot,'Premiered':airDate,
                    'Season':season,'Episode':episodeNum}
        addVideo(displayname,url,thumbnail,thumbnail,infoLabels=infoLabels)
    view=int(xbmcplugin.getSetting(pluginhandle,"episodeview"))
    xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")  
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

################################ Movie db

def createMoviedb():
    c = MovieDB.cursor()
    c.execute('''create table movies
                (asin UNIQUE,movietitle PRIMARY KEY,url text,poster text,plot text,director text,writer text,runtime text,year integer,premiered text,studio text,mpaa text,actors text,genres text,stars float,votes string,TMDBbanner string,TMDBposter string,TMDBfanart string,isprime boolean,watched boolean,favor boolean)''')
    MovieDB.commit()
    c.close()

def loadMoviedb(genrefilter=False,actorfilter=False,directorfilter=False,studiofilter=False,yearfilter=False,mpaafilter=False,watchedfilter=False,favorfilter=False,isprime=True):
    c = MovieDB.cursor()
    if genrefilter:
        genrefilter = '%'+genrefilter+'%'
        return c.execute('select distinct * from movies where isprime = (?) and genres like (?)', (isprime,genrefilter))
    elif mpaafilter:
        mpaafilter = '%'+mpaafilter+'%'
        return c.execute('select distinct * from movies where isprime = (?) and mpaa like (?)', (isprime,mpaafilter))
    elif actorfilter:
        actorfilter = '%'+actorfilter+'%'
        return c.execute('select distinct * from movies where isprime = (?) and actors like (?)', (isprime,actorfilter))
    elif directorfilter:
        return c.execute('select distinct * from movies where isprime = (?) and director like (?)', (isprime,directorfilter))
    elif studiofilter:
        return c.execute('select distinct * from movies where isprime = (?) and studio = (?)', (isprime,studiofilter))
    elif yearfilter:    
        return c.execute('select distinct * from movies where isprime = (?) and year = (?)', (isprime,int(yearfilter)))
    elif watchedfilter:
        return c.execute('select distinct * from movies where isprime = (?) and watched = (?)', (isprime,watchedfilter))
    elif favorfilter:
        return c.execute('select distinct * from movies where isprime = (?) and favor = (?)', (isprime,favorfilter))        
    else:
        return c.execute('select distinct * from movies where isprime = (?)', (isprime,))

def getMovieTypes(col):
    c = MovieDB.cursor()
    items = c.execute('select distinct %s from movies' % col)
    list = []
    for data in items:
        data = data[0]
        if type(data) == type(str()):
            if 'Rated' in data:
                item = data.split('for')[0]
                if item not in list and item <> '' and item <> 0 and item <> 'Inc.' and item <> 'LLC.':
                    list.append(item)
            else:
                data = data.decode('utf-8').encode('utf-8').split(',')
                for item in data:
                    item = item.replace('& ','').strip()
                    if item not in list and item <> '' and item <> 0 and item <> 'Inc.' and item <> 'LLC.':
                        list.append(item)
        elif data <> 0:
            list.append(str(data))
    c.close()
    return list

def addNewMoviesdb():
    addMoviesdb(NEW_MOVIE_URL)

def addMoviesdb(url=MOVIE_URL):
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    atf = tree.find(attrs={'id':'atfResults'}).findAll('div',recursive=False)
    try:
        btf = tree.find(attrs={'id':'btfResults'}).findAll('div',recursive=False)
        atf.extend(btf)
        del btf
    except:
        print 'AMAZON: No btf found'
    nextpage = tree.find(attrs={'title':'Next page','id':'pagnNextLink','class':'pagnNext'})
    del tree
    del data  
    for movie in atf:
        asin = movie['name']
        movietitle = movie.find('a', attrs={'class':'title'}).string
        poster = movie.find(attrs={'class':'image'}).find('img')['src'].replace('._AA160_','')
        url = BASE_URL+'/gp/product/'+asin
        print getMovieInfo(asin,movietitle,url,poster,isPrime=True)
    del atf
    if nextpage:
        pagenext = BASE_URL + nextpage['href']
        del nextpage
        addMoviesdb(pagenext)

def getMovieInfo(asin,movietitle,url,poster,isPrime=False):
    c = MovieDB.cursor()
    returndata = c.execute('select asin,movietitle,url,poster,plot,director,writer,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart,isprime,watched,favor from movies where asin = (?) or movietitle = (?)', (asin,movietitle)).fetchone()
    c.close()
    if returndata:
        print 'AMAZON: Returning Cached Meta for ASIN: '+asin
        return returndata
    else:
        plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes = scrapeMovieInfo(asin)
        moviedata = [asin,movietitle,url,poster,plot,director,'',runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,'','','',isPrime,False,False]
        addMoviedb(moviedata)
        print 'AMAZON: Cached Meta for ASIN: '+asin
        return moviedata

def addMoviedb(moviedata):
    c = MovieDB.cursor()
    c.execute('insert or ignore into movies values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', moviedata)
    MovieDB.commit()
    c.close()

def deleteMoviedb(asin=False):
    if not asin:
        asin = params['url']
    c = MovieDB.cursor()
    shownamedata = c.execute('delete from movies where asin = (?)', (asin,))
    MovieDB.commit()
    c.close()

def watchMoviedb(asin=False):
    if not asin:
        asin = params['url']
    c = MovieDB.cursor()
    c.execute("update movies set watched=? where asin=?", (True,asin))
    MovieDB.commit()
    c.close()
    
def unwatchMoviedb(asin=False):
    if not asin:
        asin = params['url']
    c = MovieDB.cursor()
    c.execute("update movies set watched=? where asin=?", (False,asin))
    MovieDB.commit()
    c.close()

def favorMoviedb(asin=False):
    if not asin:
        asin = params['url']
    c = MovieDB.cursor()
    c.execute("update movies set favor=? where asin=?", (True,asin))
    MovieDB.commit()
    c.close()
    
def unfavorMoviedb(asin=False):
    if not asin:
        asin = params['url']
    c = MovieDB.cursor()
    c.execute("update movies set favor=? where asin=?", (False,asin))
    MovieDB.commit()
    c.close()

def scrapeMovieInfo(asin):
    url = BASE_URL+'/gp/product/'+asin
    tags = re.compile(r'<.*?>')
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    spaces = re.compile(r'\s+')
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:
        stardata = tree.find('span',attrs={'class':'crAvgStars'}).renderContents()
        stardata = scripts.sub('', stardata)
        stardata = tags.sub('', stardata)
        stardata = spaces.sub(' ', stardata).strip().split('out of ')
        stars = float(stardata[0])*2
        votes = stardata[1].split('customer reviews')[0].split('See all reviews')[1].replace('(','').strip()
    except:
        stars = None
        votes = None
    try:
        premieredpossible = tree.find('div', attrs={'class':'bucket','id':'stills'}).findAll('li')
        for item in premieredpossible:
            if item.contents[0].string == 'US Theatrical Release Date:':
                premiered = item.contents[1].strip()
                d = datetime.strptime(premiered, '%B %d, %Y')
                premiered = d.strftime('%Y-%m-%d')
        if not premiered:
            premiered = None
    except:
        premiered = None
    metadatas = tree.findAll('div', attrs={'style':'margin-top:7px;margin-bottom:7px;'})
    del tree, data
    metadict = {}
    for metadata in metadatas:
        mdata = metadata.renderContents()
        mdata = scripts.sub('', mdata)
        mdata = tags.sub('', mdata)
        mdata = spaces.sub(' ', mdata).strip().split(':')
        fd = ''
        for md in mdata[1:]:
            fd += ' '+md
        metadict[mdata[0].strip()] = fd.strip()
    try:plot = metadict['Synopsis']
    except: plot = None
    try:director = metadict['Directed by']
    except:director = None
    try:
        runtime = metadict['Runtime']
        if 'hours' in runtime:
            split = 'hours'
        elif 'hour' in runtime:
            split = 'hour'
        if 'minutes' in runtime:
            replace = 'minutes'
        elif 'minute' in runtime:
            replace = 'minute'
        if 'hour' not in runtime:
            runtime = runtime.replace(replace,'')
            minutes = int(runtime.strip())
        elif 'minute' not in runtime:
            runtime = runtime.replace(split,'')
            minutes = (int(runtime.strip())*60)     
        else:
            runtime = runtime.replace(replace,'').split(split)
            try:
                minutes = (int(runtime[0].strip())*60)+int(runtime[1].strip())
            except:
                minutes = (int(runtime[0].strip())*60)
        runtime = str(minutes)
    except: runtime = None
    try: year = int(metadict['Release year'])
    except: year = None
    try: studio = metadict['Studio']
    except: studio = None
    try: mpaa = metadict['MPAA Rating']
    except: mpaa = None
    try: actors = metadict['Starring']+', '+metadict['Supporting actors']
    except:
        try: actors = metadict['Starring']
        except: actors = None     
    try: genres = metadict['Genre']
    except: genres = None
    return plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes

################################ Movie listing   
def LIST_MOVIE_ROOT():
    addDir('Favorited'  ,''             ,'LIST_MOVIES_FAVOR_FILTERED')
    addDir('All Movies' ,''             ,'LIST_MOVIES')
    addDir('Genres'     ,'GENRE'        ,'LIST_MOVIE_TYPES')
    addDir('Years'      ,'YEARS'        ,'LIST_MOVIE_TYPES')
    addDir('Studios'    ,'STUDIOS'      ,'LIST_MOVIE_TYPES')
    addDir('MPAA Rating','MPAA'         ,'LIST_MOVIE_TYPES')
    addDir('Directors'  ,'DIRECTORS'    ,'LIST_MOVIE_TYPES')
    #addDir('Actors'     ,'ACTORS'       ,'LIST_MOVIE_TYPES')
    addDir('Watched History'    ,''     ,'LIST_MOVIES_WATCHED_FILTERED')
    xbmcplugin.endOfDirectory(pluginhandle)

def LIST_MOVIE_TYPES(type=False):
    if not type:
        type = params['url']
    if type=='GENRE':
        mode = 'LIST_MOVIES_GENRE_FILTERED'
        items = getMovieTypes('genres')
    elif type=='STUDIOS':
        mode =  'LIST_MOVIES_STUDIO_FILTERED'
        items = getMovieTypes('studio')
    elif type=='YEARS':
        mode = 'LIST_MOVIES_YEAR_FILTERED'
        items = getMovieTypes('year')
    elif type=='DIRECTORS':
        mode = 'LIST_MOVIES_DIRECTOR_FILTERED'
        items = getMovieTypes('director')
    elif type=='MPAA':
        mode = 'LIST_MOVIES_MPAA_FILTERED'
        items = getMovieTypes('mpaa')
    elif type=='ACTORS':        
        mode = 'LIST_MOVIES_ACTOR_FILTERED'
        items = getMovieTypes('actors')     
    for item in items:
        addDir(item,item,mode)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)   

def LIST_MOVIES_GENRE_FILTERED():
    LIST_MOVIES(genrefilter=params['url'])

def LIST_MOVIES_YEAR_FILTERED():
    LIST_MOVIES(yearfilter=params['url'])

def LIST_MOVIES_MPAA_FILTERED():
    LIST_MOVIES(mpaafilter=params['url'])
    
def LIST_MOVIES_STUDIO_FILTERED():
    LIST_MOVIES(studiofilter=params['url'])

def LIST_MOVIES_DIRECTOR_FILTERED():
    LIST_MOVIES(directorfilter=params['url'])

def LIST_MOVIES_ACTOR_FILTERED():
    LIST_MOVIES(actorfilter=params['url'])
    
def LIST_MOVIES_WATCHED_FILTERED():
    LIST_MOVIES(watchedfilter=True)
  
def LIST_MOVIES_FAVOR_FILTERED():
    LIST_MOVIES(favorfilter=True)

def LIST_MOVIES(genrefilter=False,actorfilter=False,directorfilter=False,studiofilter=False,yearfilter=False,mpaafilter=False,watchedfilter=False,favorfilter=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    movies = loadMoviedb(genrefilter=genrefilter,actorfilter=actorfilter,directorfilter=directorfilter,studiofilter=studiofilter,yearfilter=yearfilter,mpaafilter=mpaafilter,watchedfilter=watchedfilter,favorfilter=favorfilter)
    for asin,movietitle,url,poster,plot,director,writer,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart,isprime,watched,favor in movies:
        actors = actors.split(',')
        fanart = poster.replace('.jpg','._BO354,0,0,0_CR177,354,708,500_.jpg')
        infoLabels={'Title':movietitle,'Plot':plot,'Year':year,'Premiered':premiered,
                    'Rating':stars,'Votes':votes,'Genre':genres,'Director':director,
                    'Studio':studio,'Duration':runtime,'mpaa':mpaa,'Cast':actors}
        cm = []
        if watched:
            infoLabels['overlay']=7
            cm.append( ('Unwatch', "XBMC.RunPlugin(%s?mode=unwatchMoviedb&url=%s)" % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        else: cm.append( ('Mark Watched', "XBMC.RunPlugin(%s?mode=watchMoviedb&url=%s)" % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        if favor: cm.append( ('Remove from Favorites', "XBMC.RunPlugin(%s?mode=unfavorMoviedb&url=%s)" % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        else: cm.append( ('Add to Favorites', "XBMC.RunPlugin(%s?mode=favorMoviedb&url=%s)" % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        #cm.append( ('Remove from Movies', "XBMC.RunPlugin(%s?mode=deleteMoviedb&url=%s)" % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        addVideo(movietitle,url,poster,fanart,infoLabels=infoLabels,cm=cm)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_DURATION)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
    view=int(xbmcplugin.getSetting(pluginhandle,"movieview"))
    xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

################################ TV db

def createTVdb():
    c = tvDB.cursor()
    c.execute('''CREATE TABLE shows(
                 seriestitle TEXT,
                 plot TEXT,
                 creator TEXT,
                 network TEXT,
                 genres TEXT,
                 actors TEXT,
                 year INTEGER,
                 stars float,
                 votes TEXT,
                 episodetotal INTEGER,
                 watched INTEGER,
                 unwatched INTEGER,
                 isHD BOOLEAN,
                 isprime BOOLEAN,
                 favor BOOLEAN,
                 TVDBbanner TEXT,
                 TVDBposter TEXT,
                 TVDBfanart TEXT,
                 PRIMARY KEY(seriestitle)
                 );''')
    c.execute('''CREATE TABLE seasons(
                 url TEXT,
                 poster TEXT,
                 season INTEGER,
                 seriestitle TEXT,
                 plot TEXT,
                 creator TEXT,
                 network TEXT,
                 genres TEXT,
                 actors TEXT,
                 year INTEGER,
                 stars float,
                 votes TEXT,
                 episodetotal INTEGER,
                 watched INTEGER,
                 unwatched INTEGER,
                 isHD BOOLEAN,
                 isprime BOOLEAN,
                 PRIMARY KEY(seriestitle,season,isHD),
                 FOREIGN KEY(seriestitle) REFERENCES shows(seriestitle)
                 );''')
    c.execute('''create table episodes(
                 asin TEXT,
                 seriestitle TEXT,
                 season INTEGER,
                 episode INTEGER,
                 episodetitle TEXT,
                 url TEXT,
                 plot TEXT,
                 airdate TEXT,
                 runtime TEXT,
                 isHD BOOLEAN,
                 isprime BOOLEAN,
                 watched BOOLEAN,
                 PRIMARY KEY(seriestitle,season,episode,episodetitle),
                 FOREIGN KEY(seriestitle,season) REFERENCES seasons(seriestitle,season)
                 );''')
    tvDB.commit()
    c.close()

def loadTVShowdb(HDonly=False,genrefilter=False,creatorfilter=False,networkfilter=False,yearfilter=False,watchedfilter=False,favorfilter=False,isprime=True):
    c = tvDB.cursor()
    if HDonly:
        return c.execute('select distinct * from shows where isprime = (?) and isHD = (?)', (isprime,HDonly))
    elif genrefilter:
        genrefilter = '%'+genrefilter+'%'
        return c.execute('select distinct * from shows where isprime = (?) and genres like (?)', (isprime,genrefilter))
    elif creatorfilter:
        return c.execute('select distinct * from shows where isprime = (?) and creator = (?)', (isprime,creatorfilter))
    elif networkfilter:
        return c.execute('select distinct * from shows where isprime = (?) and network = (?)', (isprime,networkfilter))
    elif yearfilter:    
        return c.execute('select distinct * from shows where isprime = (?) and year = (?)', (isprime,int(yearfilter)))
    elif favorfilter:
        return c.execute('select distinct * from shows where isprime = (?) and favor = (?)', (isprime,favorfilter)) 
    else:
        return c.execute('select distinct * from shows where isprime = (?)', (isprime,))

def loadTVSeasonsdb(showname,HDonly=False,isprime=True):
    c = tvDB.cursor()
    if HDonly:
        return c.execute('select distinct * from seasons where isprime = (?) and (seriestitle = (?) and isHD = (?))', (isprime,showname,HDonly))
    else:
        return c.execute('select distinct * from seasons where isprime = (?) and seriestitle = (?)', (isprime,showname))

def loadTVEpisodesdb(showname,season,HDonly=False,isprime=True):
    c = tvDB.cursor()
    if HDonly:
        return c.execute('select distinct * from episodes where isprime = (?) and (seriestitle = (?) and season = (?) and isHD = (?)) order by episode', (isprime,showname,season,HDonly))
    else:
        return c.execute('select distinct * from episodes where isprime = (?) and (seriestitle = (?) and season = (?) and isHD = (?)) order by episode', (isprime,showname,season,HDonly))

def getShowTypes(col):
    c = tvDB.cursor()
    items = c.execute('select distinct %s from seasons' % col)
    list = []
    for data in items:
        if data and data[0] <> None:
            data = data[0]
            if type(data) == type(str()):
                data = data.decode('utf-8').encode('utf-8').split(',')
                for item in data:
                    item = item.replace('& ','').strip()
                    if item not in list and item <> ' Inc':
                        list.append(item)
            else:
                list.append(str(data))
    c.close()
    return list

def getPoster(seriestitle):
    c = tvDB.cursor()
    data = c.execute('select distinct poster from seasons where seriestitle = (?)', (seriestitle,)).fetchone()
    return data[0]

    
def deleteShowdb(seriestitle=False):
    if not seriestitle:
        seriestitle = params['title']
    c = tvDB.cursor()
    c.execute('delete from shows where seriestitle = (?)', (seriestitle,))
    c.execute('delete from seasons where seriestitle = (?)', (seriestitle,))
    tvDB.commit()
    c.close()

def deleteSeasondb(seriestitle=False,season=False):
    if not seriestitle and not season:
        seriestitle = params['title']
        season = int(params['season'])
    c = tvDB.cursor()
    c.execute('delete from seasons where seriestitle = (?) and season = (?)', (seriestitle,season))
    c.execute('delete from episodes where seriestitle = (?) and season = (?)', (seriestitle,season))
    tvDB.commit()
    c.close()
    
def fixHDshows():
    c = tvDB.cursor()
    HDseasons = c.execute('select distinct seriestitle from seasons where isHD = (?)', (True,)).fetchall()
    for series in HDseasons:
        c.execute("update shows set isHD=? where seriestitle=?", (True,series[0]))
    tvDB.commit()
    c.close() 

def favorShowdb(seriestitle=False):
    if not seriestitle:
        seriestitle = params['title']
    c = tvDB.cursor()
    c.execute("update shows set favor=? where seriestitle=?", (True,seriestitle))
    tvDB.commit()
    c.close()
    
def unfavorShowdb(seriestitle=False):
    if not seriestitle:
        seriestitle = params['title']
    c = tvDB.cursor()
    c.execute("update shows set favor=? where seriestitle=?", (False,seriestitle))
    tvDB.commit()
    c.close()
    
def watchEpisodedb(asin=False):
    if not asin:
        asin = params['url']
    c = tvDB.cursor()
    c.execute("update episodes set watched=? where asin=?", (True,asin))
    tvDB.commit()
    c.close()
    
def unwatchEpisodedb(asin=False):
    if not asin:
        asin = params['url']
    c = tvDB.cursor()
    c.execute("update episodes set watched=? where asin=?", (False,asin))
    tvDB.commit()
    c.close()

def addEpisodedb(episodedata):
    print 'AMAZON: addEpisodedb'
    print episodedata
    c = tvDB.cursor()
    c.execute('insert or ignore into episodes values (?,?,?,?,?,?,?,?,?,?,?,?)', episodedata)
    tvDB.commit()
    c.close()
    
def addSeasondb(seasondata):
    print 'AMAZON: addSeasondb'
    print seasondata
    c = tvDB.cursor()
    c.execute('insert or ignore into seasons values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', seasondata)
    tvDB.commit()
    c.close()

def addShowdb(showdata):
    print 'AMAZON: addShowdb'
    print showdata
    seriestitle = showdata[0]
    #seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime,favor,TVDBbanner,TVDBposter,TVDBfanart
    c = tvDB.cursor()
    c.execute('insert or ignore into shows values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', showdata)
    tvDB.commit()
    c.close()

def addTVdb(url=TV_URL,isprime=True):
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    atf = tree.find(attrs={'id':'atfResults'}).findAll('div',recursive=False)
    try:
        btf = tree.find(attrs={'id':'btfResults'}).findAll('div',recursive=False)
        atf.extend(btf)
        del btf
    except:
        print 'AMAZON: No btf found'
    nextpage = tree.find(attrs={'title':'Next page','id':'pagnNextLink','class':'pagnNext'})
    del tree
    del data
    for show in atf:
        showasin = show['name']
        url = BASE_URL+'/gp/product/'+showasin
        name = show.find('a', attrs={'class':'title'}).string
        poster = show.find(attrs={'class':'image'}).find('img')['src'].replace('._AA160_','')
        if '[HD]' in name: isHD = True
        else: isHD = False
        seriestitle = name.split('Season ')[0].split('season ')[0].split('Volume ')[0].split('Series ')[0].split('Year ')[0].split(' The Complete')[0].replace('[HD]','').strip('-').strip(',').strip(':').strip()
        try:
            if 'Season' in name:
                seasonGuess = int(name.split('Season')[1].replace('[HD]','').strip('-').strip(',').strip(':').strip())
            elif 'Volume' in name:
                seasonGuess = int(name.split('Volume')[1].replace('[HD]','').strip('-').strip(',').strip(':').strip())
            elif 'Series' in name:
                seasonGuess = int(name.split('Series')[1].replace('[HD]','').strip('-').strip(',').strip(':').strip())
            elif 'Year' in name:
                seasonGuess = int(name.split('Year')[1].replace('[HD]','').strip('-').strip(',').strip(':').strip())
            elif 'season' in name:
                seasonGuess = int(name.split('season')[1].replace('[HD]','').strip('-').strip(',').strip(':').strip())
            else:
                seasonGuess = False
        except:
            seasonGuess = False
        if seasonGuess:
            strseason = str(seasonGuess)
            if len(strseason)>2 and strseason in name:
                seriesnamecheck = seriestitle.replace(strseason,'').strip()
            else:
                seriesnamecheck = seriestitle
            seasondata = checkSeasonInfo(seriesnamecheck,seasonGuess,isHD)
            if seasondata:
                print 'AMAZON: Returning Cached Meta for SEASON: '+str(seasonGuess)+' SERIES: '+seriestitle
                print seasondata
                continue
        showdata, episodes = scrapeShowInfo(url,owned=False)
        season,episodetotal,plot,creator,runtime,year,network,actors,genres,stars,votes = showdata
        strseason = str(season)
        if len(strseason)>2 and strseason in name:
            seriestitle = seriestitle.replace(strseason,'').strip()
        seasondata = checkSeasonInfo(seriestitle,season,isHD)
        if seasondata:
            print 'AMAZON: Returning Cached Meta for SEASON: '+str(season)+' SERIES: '+seriestitle
            print seasondata
            continue
        #          seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime,favor,TVDBbanner,TVDBposter,TVDBfanart
        addShowdb([seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,0,episodetotal,isHD,isprime,False,None,None,None])
        for episodeASIN,Eseason,episodeNum,episodetitle,eurl,eplot,eairDate,eisHD in episodes:
            #                    asin,seriestitle,season,episode,episodetitle,url,plot,airdate,runtime,isHD,isprime,watched
            addEpisodedb([episodeASIN,seriestitle,Eseason,episodeNum,episodetitle,eurl,eplot,eairDate,runtime,eisHD,isprime,False])
        #            url,poster,season,seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime
        addSeasondb([url,poster,season,seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,0,episodetotal,isHD,isprime])
    del atf
    if nextpage:
        pagenext = BASE_URL + nextpage['href']
        del nextpage
        addTVdb(pagenext)

def checkSeasonInfo(seriestitle,season,isHD):
    c = tvDB.cursor()
    metadata = c.execute('select * from seasons where seriestitle = (?) and season = (?) and isHD = (?)', (seriestitle,season,isHD))
    returndata = metadata.fetchone()
    c.close()
    return returndata

def scrapeShowInfo(url,owned=False):
    tags = re.compile(r'<.*?>')
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    spaces = re.compile(r'\s+')
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:season = int(tree.find('div',attrs={'class':'unbox_season_selected'}).string)
    except:
        try:season = int(tree.find('div',attrs={'style':'font-size: 120%;font-weight:bold; margin-top:15px;margin-bottom:10px;'}).contents[0].split('Season')[1].strip())
        except:season = None
    episodes = []
    try:
        episodebox = tree.find('div',attrs={'id':'avod-ep-list-rows'}).findAll('tr',attrs={'asin':True})
        episodecount = len(episodebox)
        for episode in episodebox:
            if owned:
                purchasecheckbox = episode.find('input',attrs={'type':'checkbox'})
                if purchasecheckbox:
                    continue
            episodeASIN = episode['asin']
            episodetitle = episode.find(attrs={'title':True})['title'].encode('utf-8')
            if '[HD]' in episodetitle:
                episodetitle.replace('[HD]','').strip()
                isHD = True
            else:
                isHD = False
            airDate = episode.find(attrs={'style':'width: 150px; overflow: hidden'}).string.strip()
            try: plot =  episode.findAll('div')[1].string.strip()
            except: plot = ''
            episodeNum = int(episode.find('div',attrs={'style':'width: 185px;'}).string.split('.')[0].strip())
            url = BASE_URL+'/gp/product/'+episodeASIN
            episodedata = [episodeASIN,season,episodeNum,episodetitle,url,plot,airDate,isHD]
            episodes.append(episodedata)
        del episodebox
    except:
        episodecount = None
    try:
        stardata = tree.find('span',attrs={'class':'crAvgStars'}).renderContents()
        stardata = scripts.sub('', stardata)
        stardata = tags.sub('', stardata)
        stardata = spaces.sub(' ', stardata).strip().split('out of ')
        stars = float(stardata[0])*2
        votes = stardata[1].split('customer reviews')[0].split('See all reviews')[1].replace('(','').strip()
    except:
        stars = None
        votes = None
    metadatas = tree.findAll('div', attrs={'style':'margin-top:7px;margin-bottom:7px;'})
    del tree, data
    metadict = {}
    for metadata in metadatas:
        mdata = metadata.renderContents()
        mdata = scripts.sub('', mdata)
        mdata = tags.sub('', mdata)
        mdata = spaces.sub(' ', mdata).strip().split(': ')
        fd = ''
        for md in mdata[1:]:
            fd += md+' '
        metadict[mdata[0].strip()] = fd.strip()
    try:plot = metadict['Synopsis']
    except: plot = None
    try:creator = metadict['Creator']
    except:creator = None
    try:
        runtime = metadict['Runtime']
        if 'hours' in runtime:
            split = 'hours'
        elif 'hour' in runtime:
            split = 'hour'
        if 'minutes' in runtime:
            replace = 'minutes'
        elif 'minute' in runtime:
            replace = 'minute'
        if 'hour' not in runtime:
            runtime = runtime.replace(replace,'')
            minutes = int(runtime.strip())
        elif 'minute' not in runtime:
            runtime = runtime.replace(split,'')
            minutes = (int(runtime.strip())*60)     
        else:
            runtime = runtime.replace(replace,'').split(split)
            try:
                minutes = (int(runtime[0].strip())*60)+int(runtime[1].strip())
            except:
                minutes = (int(runtime[0].strip())*60)
        runtime = str(minutes)
    except: runtime = None
    try: year = int(metadict['Season year'])
    except: year = None
    try: network = metadict['Network']
    except: network = None
    try: actors = metadict['Starring']+', '+metadict['Supporting actors']
    except:
        try: actors = metadict['Starring']
        except: actors = None     
    try: genres = metadict['Genre']
    except: genres = None
    showdata = [season,episodecount,plot,creator,runtime,year,network,actors,genres,stars,votes]
    return showdata, episodes

def scanTVDBshows():
    c = tvDB.cursor()
    shows = c.execute('select distinct seriestitle,genres from shows order by seriestitle').fetchall()
    for seriestitle,genre in shows:
        TVDBbanner,TVDBposter,TVDBfanart,genre2 = tv_db_series_lookup(seriestitle)
        if genre:
            genre = genre
        else:
            genre = genre2
        c.execute("update shows set TVDBbanner=?,TVDBposter=?,TVDBfanart=?,genres=? where seriestitle=?", (TVDBbanner,TVDBposter,TVDBfanart,genre,seriestitle))
        tvDB.commit()
    c.close()


def tv_db_series_lookup(seriesname):
    tv_api_key = '03B8C17597ECBD64'
    mirror = 'http://thetvdb.com'
    banners = 'http://thetvdb.com/banners/'
    try:
        print 'intial search'
        series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(seriesname)
        seriesid = getURL(series_lookup)
        seriesid = get_series_id(seriesid,seriesname)
    except:
        try:
            print 'strip search'
            series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(seriesname.split('(')[0].split(':')[0].strip())
            seriesid = getURL(series_lookup)
            seriesid = get_series_id(seriesid,seriesname)
        except:
            #return None,None,None,None
            print 'manual search'
            keyb = xbmc.Keyboard(seriesname, 'Manual Search')
            keyb.doModal()
            if (keyb.isConfirmed()):
                try:
                    series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(keyb.getText())
                    seriesid = getURL(series_lookup)
                    seriesid = get_series_id(seriesid,seriesname)
                except:
                    print 'manual search failed'
                    return None,None,None,None
    if seriesid:
        series_xml = mirror+('/api/%s/series/%s/en.xml' % (tv_api_key, seriesid))
        series_xml = getURL(series_xml)
        tree = BeautifulStoneSoup(series_xml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        try:
            genre = tree.find('genre').string
            genre = genre.replace("|",",")
            genre = genre.strip(",")
        except:
            print '%s - Genre Failed' % seriesname
            genre = None
        try: banner = banners + tree.find('banner').string
        except:
            print '%s - Banner Failed' % seriesname
            banner = None
        try: fanart = banners + tree.find('fanart').string
        except:
            print '%s - Fanart Failed' % seriesname
            fanart = None
        try: poster = banners + tree.find('poster').string
        except:
            print '%s - Poster Failed' % seriesname
            poster = None
        return banner, poster, fanart, genre
    else:
        return None,None,None,None

def get_series_id(seriesid,seriesname):
    shows = BeautifulStoneSoup(seriesid, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('series')
    names = list(BeautifulStoneSoup(seriesid, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('seriesname'))
    if len(names) > 1:
        select = xbmcgui.Dialog()
        ret = select.select(seriesname, [name.string for name in names])
        if ret <> -1:
            seriesid = shows[ret].find('seriesid').string
        else:
            seriesid = False
    else:
        seriesid = shows[0].find('seriesid').string
    return seriesid  

###################### Television

def LIST_TV_ROOT():
    addDir('Favorited'  ,''                 ,'LIST_TVSHOWS_FAVOR_FILTERED')
    addDir('All Shows'  ,''                 ,'LIST_TVSHOWS')
    addDir('HDTV Shows' ,''                 ,'LIST_HDTVSHOWS')
    addDir('Genres'     ,'GENRE'            ,'LIST_TVSHOWS_TYPES')
    addDir('Years   '   ,'YEARS'            ,'LIST_TVSHOWS_TYPES')
    addDir('Networks'   ,'NETWORKS'         ,'LIST_TVSHOWS_TYPES')
    #addDir('Creators'   ,'CREATORS'        ,'LIST_TVSHOWS_TYPES')
    xbmcplugin.endOfDirectory(pluginhandle)
    
def LIST_TVSHOWS_TYPES(type=False):
    if not type:
        type = params['url']
    if type=='GENRE':
        mode = 'LIST_TVSHOWS_GENRE_FILTERED'
        items = getShowTypes('genres')
    elif type=='NETWORKS':
        mode =  'LIST_TVSHOWS_NETWORKS_FILTERED'
        items = getShowTypes('network')  
    elif type=='YEARS':
        mode = 'LIST_TVSHOWS_YEARS_FILTERED'
        items = getShowTypes('year')     
    elif type=='CREATORS':
        mode = 'LIST_TVSHOWS_CREATORS_FILTERED'
        items = getShowTypes('creator')
    for item in items:
        addDir(item,item,mode)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)   

def LIST_TVSHOWS_GENRE_FILTERED():
    LIST_TVSHOWS(genrefilter=params['url'])

def LIST_TVSHOWS_NETWORKS_FILTERED():
    LIST_TVSHOWS(networkfilter=params['url'])
    
def LIST_TVSHOWS_YEARS_FILTERED():
    LIST_TVSHOWS(yearfilter=params['url'])

def LIST_TVSHOWS_CREATORS_FILTERED():
    LIST_TVSHOWS(creatorfilter=params['url'])
  
def LIST_TVSHOWS_FAVOR_FILTERED():
    LIST_TVSHOWS(favorfilter=True)
    
def LIST_HDTVSHOWS():
    LIST_TVSHOWS(HDonly=True)

def LIST_TVSHOWS(HDonly=False,genrefilter=False,creatorfilter=False,networkfilter=False,yearfilter=False,favorfilter=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    shows = loadTVShowdb(HDonly=HDonly,genrefilter=genrefilter,creatorfilter=creatorfilter,networkfilter=networkfilter,yearfilter=yearfilter,favorfilter=favorfilter)
    for seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime,favor,TVDBbanner,TVDBposter,TVDBfanart in shows:
        infoLabels={'Title': seriestitle,'TVShowTitle':seriestitle}
        if plot:
            infoLabels['Plot'] = plot
        if actors:
            infoLabels['Cast'] = actors.split(',')
        if year:
            infoLabels['Year'] = year
            infoLabels['Premiered'] = str(year)
        if stars:
            infoLabels['Rating'] = stars           
        if votes:
            infoLabels['Votes'] = votes  
        if genres:
            infoLabels['Genre'] = genres 
        if episodetotal:
            infoLabels['Episode'] = episodetotal
        if network:
            infoLabels['Studio'] = network
        if creator:
            infoLabels['Credits'] = creator
        if HDonly==True: listmode = 'LIST_HDTV_SEASONS'
        else: listmode = 'LIST_TV_SEASONS'
        #TVDBbanner,TVDBposter,TVDBfanart
        artOptions = ['Poster','Banner','Amazon']
        tvart=int(xbmcplugin.getSetting(pluginhandle,"tvart"))
        option = artOptions[tvart]
        if TVDBposter and option == 'Poster':
            poster = TVDBposter
        elif TVDBbanner and option == 'Banner':
            poster = TVDBbanner
        else:
            seriesposter = getPoster(seriestitle)
            poster = seriesposter
        if TVDBfanart:
            fanart = TVDBfanart
        elif seriesposter:
            fanart = seriesposter
        else:
            fanart = getPoster(seriestitle)
        cm = []
        if favor: cm.append( ('Remove from Favorites', "XBMC.RunPlugin(%s?mode=unfavorShowdb&title=%s)" % ( sys.argv[0], urllib.quote_plus(seriestitle) ) ) )
        else: cm.append( ('Add to Favorites', "XBMC.RunPlugin(%s?mode=favorShowdb&title=%s)" % ( sys.argv[0], urllib.quote_plus(seriestitle) ) ) )
        #cm.append( ('Remove from Shows', "XBMC.RunPlugin(%s?mode=deleteShowdb&title=%s)" % ( sys.argv[0], urllib.quote_plus(seriestitle) ) ) )
        addDir(seriestitle,seriestitle,listmode,poster,fanart,infoLabels,cm=cm)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
    view=int(xbmcplugin.getSetting(pluginhandle,"showview"))
    xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_HDTV_SEASONS():
    LIST_TV_SEASONS(HDonly=True)
   
def LIST_TV_SEASONS(HDonly=False):
    namefilter = params['url']
    seasons = loadTVSeasonsdb(showname=namefilter,HDonly=HDonly)
    for url,poster,season,seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime in seasons:
        infoLabels={'Title': seriestitle,'TVShowTitle':seriestitle}
        if plot:
            infoLabels['Plot'] = plot
        if actors:
            infoLabels['Cast'] = actors.split(',')
        if year:
            infoLabels['Year'] = year
            infoLabels['Premiered'] = str(year)
        if stars:
            infoLabels['Rating'] = stars           
        if votes:
            infoLabels['Votes'] = votes  
        if genres:
            infoLabels['Genre'] = genres 
        if episodetotal:
            infoLabels['Episode'] = episodetotal
        if season:
            infoLabels['Season'] = season
        if network:
            infoLabels['Studio'] = network
        if creator:
            infoLabels['Credits'] = creator
        if isHD:
            mode = 'LIST_HDEPISODES_DB'
        else:
            mode = 'LIST_EPISODES_DB'
        if season <> 0 and len(str(season)) < 3: displayname = 'Season '+str(season)
        elif len(str(season)) > 2: displayname = 'Year '+str(season)
        else: displayname = seriestitle
        if isHD: displayname += ' [HD]'
        cm = []  
        #cm.append( ('Remove Season', "XBMC.RunPlugin(%s?mode=deleteSeasondb&title=%s&season=%s)" % ( sys.argv[0], urllib.quote_plus(seriestitle), str(season) ) ) )
        if params["fanart"] and params["fanart"] <>'': fanart = params["fanart"]
        else: fanart=poster
        addDir(displayname,seriestitle+'<split>'+str(season),mode,poster,fanart,infoLabels,cm=cm)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    view=int(xbmcplugin.getSetting(pluginhandle,"seasonview"))
    xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_HDEPISODES_DB():
    LIST_EPISODES_DB(HDonly=True)

def LIST_EPISODES_DB(HDonly=False,owned=False):
    split = params['url'].split('<split>')
    seriestitle = split[0]
    season = int(split[1])
    episodes = loadTVEpisodesdb(seriestitle,season,HDonly)
    #asin,seriestitle,season,episode,episodetitle,url,plot,airdate,runtime,isHD,isprime,watched
    for asin,seriestitle,season,episode,episodetitle,url,plot,airdate,runtime,isHD,isprime,watched in episodes:
        infoLabels={'Title': episodetitle,'TVShowTitle':seriestitle,
                    'Episode': episode,'Season':season}
        if plot:
            infoLabels['Plot'] = plot
        if airdate:
            infoLabels['Premiered'] = airdate 
        if runtime:
            infoLabels['Duration'] = runtime
        if season == 0: displayname =  str(episode)+'. '+episodetitle
        else: displayname =  str(season)+'x'+str(episode)+' - '+episodetitle

        if params['thumb']: poster = params["thumb"]
        if params["fanart"] and params["fanart"] <>'': fanart = params["fanart"]
        else: fanart=poster

        cm = []
        if watched:
            infoLabels['overlay']=7
            cm.append( ('Unwatch', "XBMC.RunPlugin(%s?mode=unwatchEpisodedb&url=%s)" % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        else: cm.append( ('Mark Watched', "XBMC.RunPlugin(%s?mode=watchEpisodedb&url=%s)" % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        addVideo(displayname,url,poster,fanart,infoLabels=infoLabels,cm=cm)
    #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setContent(int(sys.argv[1]), 'Episodes') 
    view=int(xbmcplugin.getSetting(pluginhandle,"episodeview"))
    xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")  
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

############ SET PARAMETERS AND INIT
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

MovieDBfile = os.path.join(os.getcwd().replace(';', ''),'resources','cache','movies.db')
if not os.path.exists(MovieDBfile):
    MovieDB = sqlite.connect(MovieDBfile)
    MovieDB.text_factory = str
    createMoviedb()
else:
    MovieDB = sqlite.connect(MovieDBfile)
    MovieDB.text_factory = str

tvDBfile = os.path.join(os.getcwd().replace(';', ''),'resources','cache','tv.db')
if not os.path.exists(tvDBfile):
    tvDB = sqlite.connect(tvDBfile)
    tvDB.text_factory = str
    createTVdb()
else:
    tvDB = sqlite.connect(tvDBfile)
    tvDB.text_factory = str

if mode==None:
    ROOT()
else:
    exec '%s()' % mode