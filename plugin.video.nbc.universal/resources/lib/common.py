import xbmcplugin

import xbmc
import xbmcgui

import urllib
import urllib2
import sys
import os
import cookielib

pluginhandle = int (sys.argv[1])
"""
    PARSE ARGV
"""
class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )

exec "args = _Info(%s)" % (urllib.unquote_plus(sys.argv[2][1:].replace("&", ", ").replace('"','\'')), )


"""
    DEFINE URLS
"""
# NBC Universal et al.
NBC_BASE_URL   = "http://www.nbc.com"
NBC_FULL_URL   = "http://www.nbc.com/video/library/full-episodes/"
USA_BASE_URL   = "http://www.usanetwork.com"
USA_FULL_URL   = "http://www.usanetwork.com/globalNav.xml"
SCIFI_BASE_URL = "http://www.scifi.com/rewind/"
SCIFI_FULL_URL = "http://www.scifi.com/rewind/includes/playlist_new.xml"

#define file locations
COOKIEFILE  = "cookies.lwp"
imagepath   = os.path.join(os.getcwd().replace(';', ''),'resources','images')


"""
    GET SETTINGS
"""
settings={}

#settings general
settings['resolution_hack'] = (xbmcplugin.getSetting(pluginhandle,"resolution_hack") == "true")
settings['quality']         = xbmcplugin.getSetting(pluginhandle,"quality")

#settings TV
settings['flat_season']        = int(xbmcplugin.getSetting(pluginhandle,"flat_season"))
settings['flat_channels']      = (xbmcplugin.getSetting(pluginhandle,"flat_channels") == "true")
settings['flat_tv_cats']       = (xbmcplugin.getSetting(pluginhandle,"flat_tv_cats") == "true")
settings['only_full_episodes'] = (xbmcplugin.getSetting(pluginhandle,"only_full_episodes") == "true")    
settings['show_epi_labels']    = (xbmcplugin.getSetting(pluginhandle,"show_epi_labels") == "true")    
settings['get_show_plot']      = (xbmcplugin.getSetting(pluginhandle,"get_show_plot") == "true")    
settings['get_episode_plot']   = (xbmcplugin.getSetting(pluginhandle,"get_episode_plot") == "true")


"""
    Clean Non-Ascii characters from names for XBMC
"""
def cleanNames(string):
    try:
        string = string.replace("'","").replace(unicode(u'\u201c'), '"').replace(unicode(u'\u201d'), '"').replace(unicode(u'\u2019'), '\'').replace('&amp;', '&').replace('&quot;', '"').replace('&#039;',"'")
        return string
    except:
        return string


"""
    ADD DIRECTORY
"""
try:
    args.fanart
except:
    args.fanart=''

def addDirectory(name, url='', mode='default', thumb='', icon='', fanart=args.fanart, plot='', genre=''):
    ok=True
    u = sys.argv[0]+'?url="'+urllib.quote_plus(url)+'"&mode="'+mode+'"&name="'+urllib.quote_plus(cleanNames(name))+'"&fanart="'+urllib.quote_plus(fanart)+'"&plot="'+urllib.quote_plus(cleanNames(plot))+'"&genre="'+cleanNames(genre)+'"'
    liz=xbmcgui.ListItem(cleanNames(name), iconImage=icon, thumbnailImage=thumb)
    liz.setInfo( type="Video", infoLabels={ "Title":cleanNames(name), "Plot":cleanNames(plot), "Genre":genre})
    liz.setProperty('fanart_image',fanart)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok


"""
    READ PAGE
"""
def getHTML( url ):
    print 'NBC Universal --> common :: getHTML :: url = '+url
    cj = cookielib.LWPCookieJar()
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Referer', 'http://nbc.com'),
                         ('Content-Type', 'application/x-www-form-urlencoded'),
                         ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')]
    usock=opener.open(url)
    response=usock.read()
    usock.close()
    if os.path.isfile(COOKIEFILE):
        cj.save(COOKIEFILE)
    return response


"""
    make a list unique; credit to http://www.peterbe.com/plog/uniqifiers-benchmark, variant f5
"""

def unique(seq, idfun=None):  
    # order preserving 
    if idfun is None: 
        def idfun(x): return x 
    seen = {} 
    result = [] 
    for item in seq: 
        marker = idfun(item) 
        # in old Python versions: 
        # if seen.has_key(marker) 
        # but in new ones: 
        if marker in seen: continue 
        seen[marker] = 1 
        result.append(item) 
    return result
