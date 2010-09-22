import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime
from BeautifulSoup import BeautifulStoneSoup

################################ Common
def getURL( url ):
    try:
        print 'TNT & TNT Module --> getURL :: url = '+url
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

def getAUTH(aifp,window,tokentype,vid,filename,authUrl):
        if 'tnt.tv' in authUrl:
            profile = 'tnt' 
        elif 'tbs.com' in authUrl:
            profile = 'tbs'
        parameters = {'aifp' : aifp,
                      'window' : window,
                      'authTokenType' : tokentype,
                      'videoId' : vid,
                      'profile' : profile,
                      'path' : filename
                      }
        data = urllib.urlencode(parameters)
        request = urllib2.Request(authUrl, data)
        response = urllib2.urlopen(request)
        link = response.read(200000)
        response.close()
        return re.compile('<token>(.+?)</token>').findall(link)[0]

def GET_RTMP(url,vid,authUrl):
        html=getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        files = tree.findAll('file')
        #stream details
        filename = files[0].string
        if 'http://' in filename:
            filename = filename
            return filename
        else:
            filename = filename[1:len(filename)-4]
            serverDetails = tree.find('akamai')
            server = serverDetails.find('src').string.split('://')[1]
            #get auth
            tokentype = serverDetails.find('authtokentype').string
            window = serverDetails.find('window').string
            aifp = serverDetails.find('aifp').string
            auth=getAUTH(aifp,window,tokentype,vid,filename,authUrl)      
            swfUrl = 'http://www.tnt.tv/dramavision/tnt_video.swf'
            rtmp = 'rtmpe://'+server+'?'+auth+" swfurl="+swfUrl+" swfvfy=true"+' playpath='+filename
            return rtmp

################################ Play Video
                
def GETVIDEO(url):
        if 'tnt.tv' in url:
            VideoData = 'http://www.tnt.tv/video_cvp/cvp/videoData/?id='        
            EpisodeData = 'http://www.tnt.tv/dramavision/getVideoById/?id='
            authUrl = 'http://www.tnt.tv/processors/video_cvp/token.jsp'
        elif 'tbs.com' in url:
            VideoData = 'http://www.tbs.com/video/cvp/videoData.jsp?oid='
            EpisodeData = 'http://www.tbs.com/video/navigation/getVideoById/?id='
            authUrl = 'http://www.tbs.com/processors/cvp/token.jsp'
        vid = url.split('id=')[1]  
        url = EpisodeData + vid
        data=getURL(url)
        segments = re.compile("<segment id=['|\"](.+?)['|\"]>").findall(data)
        if len(segments) > 1:
            stacked_url = 'stack://'
            for segment in segments:
                url = VideoData+segment
                stacked_url += GET_RTMP(url,vid,authUrl).replace(',',',,')+' , '
            stacked_url = stacked_url[:-3]
            return stacked_url
        else:
            url = VideoData+vid
            return GET_RTMP(url,vid,authUrl)


