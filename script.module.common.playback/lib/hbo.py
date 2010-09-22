import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime
from BeautifulSoup import BeautifulStoneSoup

################################ Common
def getURL( url ):
    try:
        print 'HBO Module --> getURL :: url = '+url
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

################################ Play Video
                
def GETVIDEO(url):
        path = url.split('.com')[1]
        url = 'http://render.cdn.hbo.com'+path+'/index.xml?g=u'
        data=getURL(url)
        vid = re.compile('<videoId><\!\[CDATA\[(.+?)\]\]></videoId>').findall(data)[0]
        url = 'http://render.cdn.hbo.com/data/content/global/videos/data/'+vid+'.xml'
        data=getURL(url)
        #<path><![CDATA[rtmp://stream.cdn.hbo.com/a2267/d1/mp4:av/streaming/series/real-time-with-bill-maher/season-08/season-8-rant-f-230173-10-hi.mov]]></path>
        link = re.compile('<path><\!\[CDATA\[(.+?)\]\]></path>').findall(data)[1]
        return link




