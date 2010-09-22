import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime,md5

################################ Common
def getURL( url ):
    try:
        print 'Cartoon Network Module --> getURL :: url = '+url
        txdata = None
        txheaders = {
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)'	
                    }
        req = urllib2.Request(url, txdata, txheaders)
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

def getServerTime(url):
    data = getURL(url)
    return re.compile('<time>(.+?)</time>').findall(data)[0]

def getPlaylist( pid, stime, referer, getVideoPlaylist, hostname):
    try:
        url = getVideoPlaylist + '?id=' + pid + '&r=' + stime
        print 'Adult Swim --> getplaylist :: url = '+url
        token = stime + '-' + md5.new(stime + pid + '-22rE=w@k4raNA').hexdigest()
        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14',
                   'Host': hostname,
                   'Referer':referer,
                   'x-prefect-token': token
                   }
        req = urllib2.Request(url,'',headers)    
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        print 'Error code: ', e.code
        return False
    else:
        return re.compile('<ref href="(.+?)" />').findall(link)[0]


################################ Get Video
                
def GETVIDEO(url):
    if 'adultswim.com' in url:
        configuration_url = 'http://asfix.adultswim.com/staged/configuration.xml'
        hostname = 'asfix.adultswim.com'
        referer = 'http://www.adultswim.com/video/ASFix.swf'
        network_name = 'AS'
        data = getURL(url)
        videoId = re.compile('<meta content="(.+?)" name="videoId"/>').findall(data)[0]
        #segIds = re.compile('<meta content="(.+?)" name="segIds"/>').findall(data)[0].split('#')
    elif 'cartoonnetwork.com' in url:
        configuration_url = 'http://www.cartoonnetwork.com/video/staged/CN2.configuration.xml'
        hostname = 'cnvideosvc2.cartoonnetwork.com'
        referer = 'http://www.cartoonnetwork.com/video/VideoBrowser.swf'
        network_name = 'CN2'
        videoId = url.split('episodeID=')[1]
    else:
        return False
    config = getURL(configuration_url)
    VideoPlaylist = re.compile('<getVideoPlaylist url="(.+?)"/>').findall(config)[0]
    ServerTime    = re.compile('<getServerTime url="(.+?)"/>').findall(config)[0]
    EpisodesByIDs = re.compile('<episodesByIDs url="(.+?)"/>').findall(config)[0]
    getsegments = EpisodesByIDs+'?ids='+videoId+'&networkName'+network_name
    data = getURL(getsegments)
    segIds = re.compile('<item name="segIds"><value>(.+?)</value>').findall(data)[0].split('#')
    stime = getServerTime(ServerTime)
    stacked_url = 'stack://'
    for segId in segIds:
        stacked_url += getPlaylist( segId, stime, referer, VideoPlaylist, hostname).replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    return stacked_url



