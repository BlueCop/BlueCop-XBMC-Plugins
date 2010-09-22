import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime

################################ Common
def getURL( url ):
    try:
        print 'Revision3 Module --> getURL :: url = '+url
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


################################ Get Video
                
def GETVIDEO(url):
        data = getURL( url )
        return re.compile('<a onmousedown="trackEvent.+?MP4 High Definition.+?" href="(.+?)">').findall(data)[0]



