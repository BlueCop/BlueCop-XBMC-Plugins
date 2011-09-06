# -*- coding: utf_8 -*-
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

moviesDB = os.path.join(os.getcwd().replace(';', ''),'resources','cache','movies.db')
tvDB = os.path.join(os.getcwd().replace(';', ''),'resources','cache','tv.db')

BASE_URL = 'http://www.amazon.com'
MOVIE_URL = 'http://www.amazon.com/gp/search/ref=sr_st?qid=1314934213&rh=n%3A2625373011%2Cn%3A!2644981011%2Cn%3A!2644982011%2Cn%3A2858778011%2Cn%3A2858905011%2Cp_85%3A2470955011&sort=-releasedate'
TV_URL = 'http://www.amazon.com/gp/search/ref=sr_st?qid=1314982661&rh=n%3A2625373011%2Cn%3A!2644981011%2Cn%3A!2644982011%2Cn%3A2858778011%2Cn%3A2864549011%2Cp_85%3A2470955011&sort=-releasedate'

def getURL( url , host='www.amazon.com'):
    print 'getHTTP :: url = '+url
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17'),
                         ('Host', host)]
    usock = opener.open(url)
    response = usock.read()
    usock.close()
    return response


def addDir(name,url,mode,poster='',infoLabels=False,totalItems=0):
    if not infoLabels:
        infoLabels={ "Title": name}
    u=sys.argv[0]
    u+="?url="+urllib.quote_plus(url)
    u+="&mode="+urllib.quote_plus(mode)
    u+="&name="+urllib.quote_plus(infoLabels['Title'])
    u+="&thumb="+urllib.quote_plus(poster)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=poster)
    liz.setInfo( type="Video", infoLabels=infoLabels)
    liz.setProperty('fanart_image',poster)
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True,totalItems=totalItems)
    return ok

def addVideo(name,url,poster='',art='',infoLabels=False,totalItems=0):
    if not infoLabels:
        infoLabels={ "Title": name}
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=PLAYVIDEO&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name, thumbnailImage=poster)
    utrailer=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=PLAYTRAILER&name="+urllib.quote_plus(name)
    infoLabels['Trailer']=utrailer
    liz.setInfo( type="Video", infoLabels=infoLabels)
    liz.setProperty('fanart_image',art)
    liz.setProperty('IsPlayable', 'true')
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


################################ Movie db

def getMovieGenres():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    genreUnsplit = c.execute('select distinct genres from moviedata')
    genres = []
    for split in genreUnsplit:
        split = split[0].split(',')
        for genre in split:
            genre = genre.strip()
            if genre not in genres and genre <> '':
                genres.append(genre)
    c.close()
    return genres

def getMovieStudios():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    studios = c.execute('select distinct studio from moviedata')
    list = []
    for studio in studios:
        studio = studio[0].encode('utf-8')
        if studio not in list and studio <> '':
            list.append(studio)
    c.close()
    return list

def getMovieActors():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    actorsUnsplit = c.execute('select distinct actors from moviedata')
    actors = []
    for split in actorsUnsplit:
        split = split[0].split(',')
        for actor in split:
            actor = actor.strip().encode('utf-8')
            if actor not in actors and actor <> '':
                actors.append(actor)
    c.close()
    return actors

def getMovieDirectors():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    directors = c.execute('select distinct director from moviedata')
    list = []
    for director in directors:
        director = director[0].encode('utf-8')
        if director not in list and director <> '':
            list.append(director)
    c.close()
    return list

def getMovieYears():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    years = c.execute('select distinct year from moviedata')
    list = []
    for year in years:
        year = year[0]
        if year not in list and year <> 0:
            list.append(str(year))
    c.close()
    return list

def getMovieMPAA():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    mpaas = c.execute('select distinct mpaa from moviedata')
    list = []
    for mpaa in mpaas:
        mpaa = mpaa[0].split('for')[0].strip()
        if mpaa not in list and mpaa <> '':
            list.append(mpaa)
    c.close()
    return list

def loadMoviedb(genrefilter=False,actorfilter=False,directorfilter=False,studiofilter=False,yearfilter=False,mpaafilter=False):
    if not os.path.exists(moviesDB):
        createMoviedb()
        addMoviesdb()
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    if genrefilter:
        genrefilter = '%'+genrefilter+'%'
        return c.execute('select distinct movies.asin,movietitle,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart from movies, moviedata where movies.asin=moviedata.asin and genres like (?)', (genrefilter,))
    elif mpaafilter:
        mpaafilter = '%'+mpaafilter+'%'
        return c.execute('select distinct movies.asin,movietitle,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart from movies, moviedata where movies.asin=moviedata.asin and mpaa like (?)', (mpaafilter,))
    elif actorfilter:
        actorfilter = '%'+actorfilter+'%'
        return c.execute('select distinct movies.asin,movietitle,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart from movies, moviedata where movies.asin=moviedata.asin and actors like (?)', (actorfilter,))
    elif directorfilter:
        return c.execute('select distinct movies.asin,movietitle,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart from movies, moviedata where movies.asin=moviedata.asin and director = (?)', (directorfilter,))
    elif studiofilter:
        return c.execute('select distinct movies.asin,movietitle,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart from movies, moviedata where movies.asin=moviedata.asin and studio = (?)', (studiofilter,))
    elif yearfilter:    
        return c.execute('select distinct movies.asin,movietitle,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart from movies, moviedata where movies.asin=moviedata.asin and year = (?)', (int(yearfilter),))
    else:
        return c.execute('select distinct movies.asin,movietitle,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart from movies, moviedata where movies.asin=moviedata.asin')  

def createMoviedb():
    conn = sqlite.connect(moviesDB)
    conn.text_factory = str
    c = conn.cursor()
    c.execute('''create table movies
                (asin PRIMARY KEY, movietitle text, url text, poster text)''')
    c.execute('''create table moviedata
                (asin PRIMARY KEY, plot text, director text, runtime text, year integer, premiered text, studio text, mpaa text, actors text, genres text, stars float, votes string, TMDBbanner string, TMDBposter string, TMDBfanart string)''')
    conn.commit()
    c.close()

def addMoviesdb(url=MOVIE_URL):
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    atf = tree.find(attrs={'id':'atfResults'}).findAll('div',recursive=False)
    btf = tree.find(attrs={'id':'btfResults'}).findAll('div',recursive=False)
    nextpage = tree.find(attrs={'title':'Next page','id':'pagnNextLink','class':'pagnNext'})
    del tree
    del data
    for movie in atf:
        asin = movie['name']
        link = movie.find('a', attrs={'class':'title'})
        name = link.string
        url = link['href']
        poster = movie.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        moviedata = [asin,name,url,poster]
        addMovie(moviedata)
        print moviedata
        print getMovieInfo(url,asin)
    for movie in btf:
        asin = movie['name']
        link = movie.find('a', attrs={'class':'title'})
        name = link.string
        url = link['href']
        poster = movie.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        moviedata = [asin,name,url,poster]
        addMovie(moviedata)
        print moviedata
        print getMovieInfo(url,asin)
    if nextpage:
        del atf
        del btf
        pagenext = BASE_URL + nextpage['href']
        del nextpage
        addMoviesdb(pagenext)

def addMovie(moviedata):
    conn = sqlite.connect(moviesDB)
    conn.text_factory = str
    c = conn.cursor()
    c.execute('insert or ignore into movies values (?,?,?,?)', moviedata)
    conn.commit()
    c.close()

def getMovieInfo(url,asin):
    conn = sqlite.connect(moviesDB)
    conn.text_factory = str
    c = conn.cursor()
    metadata = c.execute('select asin,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart string from moviedata where asin = (?)', (asin,))
    returndata = metadata.fetchone()
    if returndata:
        print 'AMAZON: Returning Cached Meta for ASIN: '+asin
        c.close()
        return returndata
    else:
        print 'AMAZON: Grabing Meta for ASIN: '+asin
        asin2,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes = scrapeMovieInfo(url,asin)
        moviemetadata = [asin,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,None,None,None]
        c.execute('insert or ignore into moviedata values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', moviemetadata)        
        conn.commit()
        c.close()
        print 'AMAZON: Meta Cached for ASIN: '+asin
        return moviemetadata

def scrapeMovieInfo(url,asin):
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
        stars = 0.0
        votes = ''
    try:
        premieredpossible = tree.find('div', attrs={'class':'bucket','id':'stills'}).findAll('li')
        for item in premieredpossible:
            if item.contents[0].string == 'US Theatrical Release Date:':
                premiered = item.contents[1].strip()
                d = datetime.strptime(premiered, '%B %d, %Y')
                premiered = d.strftime('%Y-%m-%d')
        if not premiered:
            premiered = ''
    except:
        premiered = ''
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
            fd += md
        metadict[mdata[0].strip()] = fd.strip()
    try:plot = metadict['Synopsis']
    except: plot = ''
    try:director = metadict['Directed by']
    except:director = ''
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
    except: runtime = ''
    try: year = int(metadict['Release year'])
    except: year = 0
    try: studio = metadict['Studio']
    except: studio = ''
    try: mpaa = metadict['MPAA Rating']
    except: mpaa = ''
    try: actors = metadict['Starring']+', '+metadict['Supporting actors']
    except:
        try: actors = metadict['Starring']
        except: actors = ''      
    try: genres = metadict['Genre']
    except: genres = ''
    return asin,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes

################################ TV db

def getShowsdb():
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    shownamedata = c.execute('select distinct seriestitle from shows')
    shownames = []
    for item in shownamedata:
        shownames.append(item[0])
    c.close()
    return shownames

def getShowGenres():
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    genreUnsplit = c.execute('select distinct genres from showdata')
    genres = []
    for split in genreUnsplit:
        split = split[0].split(',')
        for genre in split:
            genre = genre.strip()
            if genre not in genres and genre <> '':
                genres.append(genre)
    c.close()
    return genres

def getShowNetworks():
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    networks = c.execute('select distinct network from showdata')
    list = []
    for network in networks:
        network = network[0].encode('utf-8')
        if network not in list and network <> '':
            list.append(network)
    c.close()
    return list

def getShowCreators():
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    creators = c.execute('select distinct creator from showdata')
    list = []
    for creator in creators:
        creator = creator[0].encode('utf-8')
        if creator not in list and creator <> '':
            list.append(creator)
    c.close()
    return list

def getShowYears():
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    years = c.execute('select distinct year from showdata')
    list = []
    for year in years:
        year = year[0]
        if year not in list and year <> 0:
            list.append(str(year))
    c.close()
    return list

def loadTVdb(showname=False,HDonly=False,genrefilter=False,creatorfilter=False,networkfilter=False,yearfilter=False):
    if not os.path.exists(tvDB):
        createTVdb()
        addTVdb()
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    if HDonly and showname:
        return c.execute('select distinct shows.asin,seriestitle,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart from shows, showdata where shows.asin=showdata.asin and (seriestitle = (?) and HD = (?))', (showname,True))
    elif showname:
        return c.execute('select distinct shows.asin,seriestitle,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart from shows, showdata where shows.asin=showdata.asin and seriestitle = (?)', (showname,))
    elif HDonly:
        return c.execute('select distinct shows.asin,seriestitle,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart from shows, showdata where shows.asin=showdata.asin and HD = (?)', (True,))
    elif genrefilter:
        genrefilter = '%'+genrefilter+'%'
        return c.execute('select distinct shows.asin,seriestitle,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart from shows, showdata where shows.asin=showdata.asin and genres like (?)', (genrefilter,))
    elif creatorfilter:
        return c.execute('select distinct shows.asin,seriestitle,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart from shows, showdata where shows.asin=showdata.asin and creator = (?)', (creatorfilter,))
    elif networkfilter:
        return c.execute('select distinct shows.asin,seriestitle,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart from shows, showdata where shows.asin=showdata.asin and network = (?)', (networkfilter,))
    elif yearfilter:    
        return c.execute('select distinct shows.asin,seriestitle,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart from shows, showdata where shows.asin=showdata.asin and year = (?)', (int(yearfilter),))
    else:
        return c.execute('select distinct shows.asin,seriestitle,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart from shows, showdata where shows.asin=showdata.asin')  

def createTVdb():
    conn = sqlite.connect(tvDB)
    conn.text_factory = str
    c = conn.cursor()
    c.execute('''create table shows
                (asin PRIMARY KEY, seriestitle text, url text, poster text)''')
    c.execute('''create table showdata
                (asin PRIMARY KEY, season integer, episodes integer, plot text, creator text, runtime text, year integer, network text, actors text, genres text, stars float, votes string, HD boolean, TVDBbanner string, TVDBposter string, TVDBfanart string)''')
    c.close()

def addTVdb(url=TV_URL):
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    atf = tree.find(attrs={'id':'atfResults'}).findAll('div',recursive=False)
    btf = tree.find(attrs={'id':'btfResults'}).findAll('div',recursive=False)
    nextpage = tree.find(attrs={'title':'Next page','id':'pagnNextLink','class':'pagnNext'})
    del tree
    del data
    for show in atf:
        asin = show['name']
        link = show.find('a', attrs={'class':'title'})
        name = link.string
        if '[HD]' in name: isHD = True
        else: isHD = False
        name = name.split('Season ')[0].split('season ')[0].split('Volume ')[0].split('Series ')[0].split('Year ')[0].split(' The Complete')[0].replace('[HD]','').strip()
        if name.endswith('-') or name.endswith(',') or name.endswith(':'):
            name = name[:-1].strip()
        url = link['href']
        poster = show.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        asin2,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart = getShowInfo(url,asin,isHD)
        strseason = str(season)
        if len(strseason)>2 and strseason in name:
            name = name.replace(strseason,'').strip()
        showdata = [asin,name,url,poster]
        addShow(showdata)
        print showdata
    for show in btf:
        asin = show['name']
        link = show.find('a', attrs={'class':'title'})
        name = link.string
        if '[HD]' in name: isHD = True
        else: isHD = False
        name = name.split('Season ')[0].split('season ')[0].split('Volume ')[0].split('Series ')[0].split('Year ')[0].split(' The Complete')[0].replace('[HD]','').strip()
        if name.endswith('-') or name.endswith(',') or name.endswith(':'):
            name = name[:-1].strip()
        url = link['href']
        poster = show.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        asin2,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart = getShowInfo(url,asin,isHD)
        strseason = str(season)
        if len(strseason)>2 and strseason in name:
            name = name.replace(strseason,'').strip()
        showdata = [asin,name,url,poster]
        addShow(showdata)
        print showdata
    if nextpage:
        del atf
        del btf
        pagenext = BASE_URL + nextpage['href']
        del nextpage
        addTVdb(pagenext)

def addShow(showdata):
    conn = sqlite.connect(tvDB)
    conn.text_factory = str
    c = conn.cursor()
    c.execute('insert or ignore into shows values (?,?,?,?)', showdata)
    conn.commit()
    c.close()

def getShowInfo(url,asin,HD=False):
    conn = sqlite.connect(tvDB)
    conn.text_factory = str
    c = conn.cursor()
    metadata = c.execute('select asin,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart from showdata where asin = (?)', (asin,))
    returndata = metadata.fetchone()
    if returndata:
        print 'AMAZON: Returning Cached Meta for ASIN: '+asin
        c.close()
        return returndata
    else:
        print 'AMAZON: Grabing Meta for ASIN: '+asin
        asin2,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes = scrapeShowInfo(url,asin)
        showmetadata = [asin,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,None,None,None]
        c.execute('insert or ignore into showdata values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', showmetadata)     
        conn.commit()
        c.close()
        print 'AMAZON: Meta Cached for ASIN: '+asin
        return showmetadata

def scrapeShowInfo(url,asin):
    tags = re.compile(r'<.*?>')
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    spaces = re.compile(r'\s+')
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:season = int(tree.find('div',attrs={'class':'unbox_season_selected'}).string)
    except:
        try:season = int(tree.find('div',attrs={'style':'font-size: 120%;font-weight:bold; margin-top:15px;margin-bottom:10px;'}).contents[0].split('Season')[1].strip())
        except:season = 0
    try:
        episodebox = tree.find('div',attrs={'id':'avod-ep-list-rows'}).findAll('tr',attrs={'asin':True})
        episodes = len(episodebox)
        del episodebox
    except:
        episodes = 1
    try:
        stardata = tree.find('span',attrs={'class':'crAvgStars'}).renderContents()
        stardata = scripts.sub('', stardata)
        stardata = tags.sub('', stardata)
        stardata = spaces.sub(' ', stardata).strip().split('out of ')
        stars = float(stardata[0])*2
        votes = stardata[1].split('customer reviews')[0].split('See all reviews')[1].replace('(','').strip()
    except:
        stars = 0.0
        votes = ''
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
            fd += md
        metadict[mdata[0].strip()] = fd.strip()
    try:plot = metadict['Synopsis']
    except: plot = ''
    try:creator = metadict['Creator']
    except:creator = ''
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
    except: runtime = ''
    try: year = int(metadict['Season year'])
    except: year = 0
    try: network = metadict['Network']
    except: network = ''
    try: actors = metadict['Starring']+', '+metadict['Supporting actors']
    except:
        try: actors = metadict['Starring']
        except: actors = ''      
    try: genres = metadict['Genre']
    except: genres = ''
    return asin,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes    

################################ Root listing
def ROOT():
    mechanizeLogin()
    addDir('Movies'      ,''                 ,'LIST_MOVIE_ROOT')
    addDir('Television' ,''                  ,'LIST_TV_ROOT')
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
        name = video.find('',attrs={'class':'title'}).a.string
        url = BASE_URL+video.find('div',attrs={'class':'title'}).a['href']
        thumb = video.find('img')['src'].replace('._SS160_','')
        fanart = video.find('img')['src'].replace('._SS160_','._BO354,0,0,0_CR177,354,708,500_')       
        if xbmcplugin.getSetting(pluginhandle,'enablelibrarymeta') == 'true':
            asin2,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart = getMovieInfo(url,asin)
            actors = actors.split(',')
            infoLabels = { 'Title':name,'Plot':plot,'Year':year,'premiered':premiered,
                           'rating':stars,'votes':votes,'Genre':genres,'director':director,
                           'studio':studio,'duration':runtime,'mpaa':mpaa,'cast':actors}
        else:
            infoLabels = { 'Title':name}
        addVideo(name,url,thumb,fanart,infoLabels=infoLabels,totalItems=totalItems)
    xbmc.executebuiltin("Container.SetViewMode(504)")
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
        if '[HD]' in name:
            isHD = True
        else:
            isHD = False           
        url = BASE_URL+video.find('div',attrs={'class':'title'}).a['href']
        if xbmcplugin.getSetting(pluginhandle,'enablelibrarymeta') == 'true':
            asin2,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart = getShowInfo(url,asin,isHD)
            actors = actors.split(',')
            infoLabels={'Title': name,'Plot':plot,'year':year,'rating':stars,'votes':votes,
                        'Genre':genres,'Season':season,'episode':episodes,'studio':network,
                        'duration':runtime,'cast':actors,'TVShowTitle':name,'credits':creator}
            if year <> 0:
                infoLabels['premiered'] = str(year)
        else:
            infoLabels = { 'Title':name}  
        thumb = video.find('img')['src'].replace('._SS160_','')
        addDir(name,url,'LIBRARY_EPISODES',thumb,infoLabels,totalItems)
    xbmc.executebuiltin("Container.SetViewMode(504)")
    xbmcplugin.endOfDirectory(pluginhandle)

def LIBRARY_EPISODES():
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    LIST_EPISODES(owned=True)

################################ Movie listing   
def LIST_MOVIE_ROOT():
    addDir('All Movies' ,''             ,'LIST_MOVIES')
    addDir('Genres'     ,'GENRE'        ,'LIST_MOVIE_TYPES')
    addDir('Years'      ,'YEARS'        ,'LIST_MOVIE_TYPES')
    #addDir('Actors'     ,'ACTORS' ,'LIST_MOVIE_TYPES')
    addDir('Directors'  ,'DIRECTORS'    ,'LIST_MOVIE_TYPES')
    addDir('Studios'    ,'STUDIOS'      ,'LIST_MOVIE_TYPES')
    addDir('MPAA Rating','MPAA'         ,'LIST_MOVIE_TYPES')
    xbmcplugin.endOfDirectory(pluginhandle)

def LIST_MOVIE_TYPES(type=False):
    if not type:
        type = params['url']
    if type=='GENRE':
        mode = 'LIST_MOVIES_GENRE_FILTERED'
        items = getMovieGenres()
    elif type=='STUDIOS':
        mode =  'LIST_MOVIES_STUDIO_FILTERED'
        items = getMovieStudios() 
    elif type=='YEARS':
        mode = 'LIST_MOVIES_YEAR_FILTERED'
        items = getMovieYears()     
    elif type=='DIRECTORS':
        mode = 'LIST_MOVIES_DIRECTOR_FILTERED'
        items = getMovieDirectors()
    elif type=='MPAA':
        mode = 'LIST_MOVIES_MPAA_FILTERED'
        items = getMovieMPAA()
    elif type=='ACTORS':        
        mode = 'LIST_MOVIES_ACTOR_FILTERED'
        items = getMovieActors()
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

def LIST_MOVIES(genrefilter=False,actorfilter=False,directorfilter=False,studiofilter=False,yearfilter=False,mpaafilter=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    movies = loadMoviedb(genrefilter=genrefilter,actorfilter=actorfilter,directorfilter=directorfilter,studiofilter=studiofilter,yearfilter=yearfilter,mpaafilter=mpaafilter)
    for asin,name,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart in movies:
        actors = actors.split(',')
        fanart = poster.replace('_SX500_','_BO354,0,0,0_CR177,354,708,500_')
        infoLabels={'Title':name,'Plot':plot,'Year':year,'Premiered':premiered,
                    'Rating':stars,'Votes':votes,'Genre':genres,'Director':director,
                    'Studio':studio,'Duration':runtime,'mpaa':mpaa,'Cast':actors}
        addVideo(name,url,poster,fanart,infoLabels=infoLabels)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_DURATION)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
    xbmc.executebuiltin("Container.SetViewMode(504)")
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)


###################### Television

def LIST_TV_ROOT():
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
        items = getShowGenres()
    elif type=='NETWORKS':
        mode =  'LIST_TVSHOWS_NETWORKS_FILTERED'
        items = getShowNetworks()  
    elif type=='YEARS':
        mode = 'LIST_TVSHOWS_YEARS_FILTERED'
        items = getShowYears()      
    elif type=='CREATORS':
        mode = 'LIST_TVSHOWS_CREATORS_FILTERED'
        items = getShowCreators()
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
    
def LIST_HDTVSHOWS():
    LIST_TVSHOWS(HDonly=True)

def LIST_TVSHOWS(HDonly=False,genrefilter=False,creatorfilter=False,networkfilter=False,yearfilter=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    shows = loadTVdb(HDonly=HDonly,genrefilter=genrefilter,creatorfilter=creatorfilter,networkfilter=networkfilter,yearfilter=yearfilter)
    shownames = getShowsdb()
    for id,name,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,isHD,TVDBbanner,TVDBposter,TVDBfanart in shows:
        if name in shownames:
            shownames.remove(name)
        else:
            continue
        actors = actors.split(',')
        infoLabels={'Title': name,'Plot':plot,'Year':year,'Rating':stars,'Votes':votes,
                    'Genre':genres,'Season':season,'Episode':episodes,'Studio':network,
                    'Duration':runtime,'Cast':actors,'TVShowTitle':name,'Credits':creator}
        if year <> 0:
            infoLabels['Premiered'] = str(year)
        if HDonly==True:
            listmode = 'LIST_HDTV_SEASONS'
        else:
            listmode = 'LIST_TV_SEASONS'
        addDir(name,url,listmode,poster,infoLabels)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
    xbmc.executebuiltin("Container.SetViewMode(504)")
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_HDTV_SEASONS():
    LIST_TV_SEASONS(HDonly=True)
   
def LIST_TV_SEASONS(HDonly=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    namefilter = params['name']
    shows = loadTVdb(showname=namefilter,HDonly=HDonly)
    for id,name,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,isHD,TVDBbanner,TVDBposter,TVDBfanart in shows:
        actors = actors.split(',')
        infoLabels={'Title': name,'Plot':plot,'Year':year,'Rating':stars,'Votes':votes,
                    'Genre':genres,'Season':season,'Episode':episodes,'Studio':network,
                    'Duration':runtime,'Cast':actors,'TVShowTitle':name,'Credits':creator}
        if year <> 0:
            infoLabels['Premiered'] = str(year) 
        if season <> 0 and len(str(season)) < 3:
            displayname = 'Season '+str(season)
        elif len(str(season)) > 2:
            displayname = 'Year '+str(season)
        else:
            displayname = name
        if isHD:
            displayname += ' [HD]'
        addDir(displayname,url,'LIST_EPISODES',poster,infoLabels)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmc.executebuiltin("Container.SetViewMode(504)")
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)    

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
    episodeNum = 0
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
        episodeNum += 1
        if season == 0:
            displayname =  str(episodeNum)+'. '+name
        else:
            displayname =  str(season)+'x'+str(episodeNum)+' - '+name
        url = BASE_URL+'/gp/product/'+asin
        infoLabels={'Title': name.replace('[HD]',''),'TVShowTitle':showname,
                    'Plot':plot,'Premiered':airDate,
                    'Season':season,'Episode':episodeNum}
        addVideo(displayname,url,thumbnail,thumbnail,infoLabels=infoLabels)
    xbmc.executebuiltin("Container.SetViewMode(504)")   
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

if mode==None:
    ROOT()
else:
    exec '%s()' % mode