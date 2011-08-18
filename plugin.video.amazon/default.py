import xbmcplugin,xbmcgui
import urllib,urllib2,cookielib,re,os.path
import sys
import binascii
import md5
import base64
import operator
import cookielib
import time
import demjson
from BeautifulSoup import BeautifulSoup
try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite    

pluginhandle = int(sys.argv[1])
COOKIEFILE = os.path.join(os.getcwd().replace(';', ''),'resources','cache','cookies.lwp')
moviesDB = os.path.join(os.getcwd().replace(';', ''),'resources','cache','movies.db')
tvDB = os.path.join(os.getcwd().replace(';', ''),'resources','cache','tv.db')
cj = cookielib.LWPCookieJar()
BASE_URL = 'http://www.amazon.com'
MOVIE_URL = 'http://www.amazon.com/s/ref=sa_menu_piv_mov0/182-5606325-6863626?ie=UTF8&node=16386761&field-is_prime_benefit=1'
TV_URL = 'http://www.amazon.com/s/ref=sa_menu_piv_tv0/182-5606325-6863626?ie=UTF8&node=16262841&field-is_prime_benefit=1'

def getURL( url , host='www.amazon.com'):
    print 'getHTTP :: url = '+url
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17'),
                         ('Host', host)]
    usock = opener.open(url)
    response = usock.read()
    usock.close()
    return response

def postURL( url, values, host='www.amazon.com'):    
    print 'postHTTP :: url = '+url
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17'),
                         ('Host', host)]
    data = urllib.urlencode(values)
    usock = opener.open(url, data)
    response = usock.read()
    usock.close()
    return response

def login():
    if os.path.isfile(COOKIEFILE):
        os.remove(COOKIEFILE)
    SIGNIN_URL = re.compile('<a href="(.+?)" rel="nofollow">Sign in</a>').findall(getURL(BASE_URL))[0].replace('&amp;','&')
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


def GETSTREAMS(getstream):
    try:
        data = getURL(getstream,'atv-ps.amazon.com')
        rtmpdata = demjson.decode(data)
        print rtmpdata
        sessionId = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['sessionId']
        cdn = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['sessionId']
        rtmpurls = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['streamingURLInfo']
        return rtmpurls, sessionId, cdn
    except:
        return False, False, False

def PLAYVIDEO(pageurl):
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
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

    #if cdn = 'limelight' 
    if rtmpurls <> False:
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
        finalUrl += " pageurl=" + pageurl
        finalUrl += " swfurl=" + swfUrl + " swfvfy=true"
        item = xbmcgui.ListItem(path=finalUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
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


def addDir(name,url,mode,iconimage='',plot=''):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot})
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
    return ok

################################ Movie db

def loadMoviedb():
    #if os.path.exists(moviesDB):
    #    os.remove(moviesDB)
    if not os.path.exists(moviesDB):
        conn = sqlite.connect(moviesDB)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('''create table movies
                    (name text, url text, poster text)''')
        c.close()
        addMoviesdb()
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    return c.execute('select * from movies order by name')

def addMoviesdb(url=MOVIE_URL):
    conn = sqlite.connect(moviesDB)
    conn.text_factory = str
    c = conn.cursor()
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    atf = tree.find(attrs={'id':'atfResults'}).findAll('div',recursive=False)
    for movie in atf:
        link = movie.find('a', attrs={'class':'title'})
        name = link.string
        url = link['href']
        poster = movie.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        moviedata = [name,url,poster]
        c.execute('insert into movies values (?,?,?)', moviedata)
        conn.commit() 
    btf = tree.find(attrs={'id':'btfResults'}).findAll('div',recursive=False)
    for movie in btf:
        link = movie.find('a', attrs={'class':'title'})
        name = link.string
        url = link['href']
        poster = movie.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        moviedata = [name,url,poster]
        c.execute('insert into movies values (?,?,?)', moviedata)
        conn.commit() 
    c.close()
    try:
        pagenext = BASE_URL + re.compile('<a title="Next page" id="pagnNextLink" class="pagnNext" href="(.*?)">').findall(data)[0]
        addMoviesdb(pagenext)
    except:
        print 'No Next Page'

################################ TV db

def loadTVdb():
    #if os.path.exists(tvDB):
    #    os.remove(tvDB)
    if not os.path.exists(tvDB):
        conn = sqlite.connect(tvDB)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('''create table shows
                    (name text, url text, poster text)''')
        c.close()
        addTVdb()
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    return c.execute('select * from shows order by name')

def addTVdb(url=TV_URL):
    conn = sqlite.connect(tvDB)
    conn.text_factory = str
    c = conn.cursor()
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    atf = tree.find(attrs={'id':'atfResults'}).findAll('div',recursive=False)
    for show in atf:
        link = show.find('a', attrs={'class':'title'})
        name = link.string
        url = link['href']
        poster = show.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        showdata = [name,url,poster]
        c.execute('insert into shows values (?,?,?)', showdata)
        conn.commit()
    btf = tree.find(attrs={'id':'btfResults'}).findAll('div',recursive=False)
    for show in btf:
        link = show.find('a', attrs={'class':'title'})
        name = link.string
        url = link['href']
        poster = show.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        showdata = [name,url,poster]
        c.execute('insert into shows values (?,?,?)', showdata)
        conn.commit() 
    c.close()
    try:
        pagenext = BASE_URL + re.compile('<a title="Next page" id="pagnNextLink" class="pagnNext" href="(.*?)">').findall(data)[0]
        addTVdb(pagenext)
    except:
        print 'No Next Page'
    

################################ Root listing
def ROOT():
    login()
    addDir('Movies'     ,MOVIE_URL ,1)
    addDir('TV Shows'   ,TV_URL    ,2)
    addDir('HDTV Shows' ,TV_URL    ,4)
    xbmcplugin.endOfDirectory(pluginhandle)

################################ List Videos

def LIST_MOVIES():
    xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    movies = loadMoviedb()
    for name, url, poster in movies:
        poster = poster.replace('_AA160_','_SX500_')
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(10)+"&name="+urllib.quote_plus(name)
        liz=xbmcgui.ListItem(name,iconImage=poster, thumbnailImage=poster)
        liz.setInfo( type="Video", infoLabels={ "Title": name})
        liz.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_TVSHOWS(HDonly=False):
    shows = loadTVdb()
    for name, url, poster in shows:
        if HDonly==True:
            if '[HD]' not in name:
                continue
        addDir(name,url,3,poster)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_EPISODES(episode_url):
    data = getURL(episode_url)
    names = re.compile('<div style="width: 185px;">(.*?)</div>',re.DOTALL).findall(data)
    episodes = re.compile('<a href="(.*?)" style="text-decoration: none">').findall(data)
    mode = 10
    for name in names:
        marker = names.index(name)
        name = name.strip()
        if marker == 0:
            url = episode_url
        else:
            url = BASE_URL + episodes[marker - 1]
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        liz=xbmcgui.ListItem(name)
        liz.setInfo( type="Video", infoLabels={ "Title": name})
        liz.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)
    

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
    LIST_MOVIES()
elif mode==2:
    LIST_TVSHOWS()
elif mode==3:
    LIST_EPISODES(url)
elif mode==4:
    LIST_TVSHOWS(HDonly=True)
elif mode==10:
    PLAYVIDEO(url)
