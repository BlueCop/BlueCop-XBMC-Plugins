import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os

pluginhandle = int (sys.argv[1])
"""
    PARSE ARGV
"""

class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )

exec "args = _Info(%s)" % (urllib.unquote_plus(sys.argv[2][1:].replace("&", ", ").replace('"','\'')) , )



"""
    DEFINE URLS
"""
BASE_URL = "http://www.cbs.com/video/"

imagepath = os.path.join(os.getcwd().replace(';', ''),'resources','images')

"""
    GET SETTINGS
"""

settings={}
#settings general
quality = ['DSI24FPS16x9-2064K', 'DSI24FPS16x9-1264K', 'DSI24FPS16x9-764K', 'DSI24FPS16x9-464K', 'DSI24FPS16x9-332K']
selectquality = int(xbmcplugin.getSetting(pluginhandle,'quality'))
settings['quality'] = quality[selectquality]



"""
    ADD DIRECTORY
"""

def addDirectory(name, url='', mode='', series='', page='undefined', updatelist='false'):
    ok=True
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+mode+'"'
    u += '&name="'+urllib.quote_plus(name.replace("'",''))+'"'
    u += '&series="'+urllib.quote_plus(series)+'"'
    u += '&page="'+urllib.quote_plus(page)+'"'
    u += '&updatelist="'+urllib.quote_plus(updatelist)+'"'
    liz=xbmcgui.ListItem(name)
    liz.setInfo( type="Video", infoLabels={ "Title":name })
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def getVIDEOS( s , series_title, b):
    try:
        url = 'http://www.cbs.com/video/_process.php'
        us_proxy = 'http://' + xbmcplugin.getSetting(pluginhandle,'us_proxy') + ':' + xbmcplugin.getSetting(pluginhandle,'us_proxy_port')

        if (xbmcplugin.getSetting(pluginhandle,'us_proxy_enable') == 'true'):
                 print 'Using proxy: ' + us_proxy
                 proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
                 opener = urllib2.build_opener(proxy_handler)
                 urllib2.install_opener(opener)
                 
        print 'CBS --> common :: postHTTP :: url = '+url
        values = {'_b':b,
                  '_s':s,
                  '_series_title':series_title}
        data = urllib.urlencode(values)
        req = urllib2.Request(url,data)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        print 'Error reason: ', e.reason
        return False
    else:
        return link

def getHTML( url ):
    try:
        us_proxy = 'http://' + xbmcplugin.getSetting(pluginhandle,'us_proxy') + ':' + xbmcplugin.getSetting(pluginhandle,'us_proxy_port')

        if (xbmcplugin.getSetting(pluginhandle,'us_proxy_enable') == 'true'):
                 print 'Using proxy: ' + us_proxy
                 proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
                 opener = urllib2.build_opener(proxy_handler)
                 urllib2.install_opener(opener)

        print 'CBS --> common :: getHTML :: url = '+url
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        print 'Error reason: ', e.reason
        return False
    else:
        return link
    



