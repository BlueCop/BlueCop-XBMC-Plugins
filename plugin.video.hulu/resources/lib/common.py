import xbmcplugin

import xbmc
import xbmcgui
import xbmcaddon

import urllib
import urllib2
import sys
import os
import cookielib

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
BASE_MENU_URL = "http://m.hulu.com/menu/hd_main_menu?show_id=0&dp_id=huludesktop&package_id=2&page=1"

#define etc.
login_url   = "https://secure.hulu.com/account/authenticate"
#define file locations
COOKIEFILE = 'special://temp/hulu-cookies.lwp'
imagepath   = os.path.join(os.getcwd().replace(';', ''),'resources','images')
addon = xbmcaddon.Addon(id='plugin.video.hulu')



"""
    GET SETTINGS
"""

settings={}
handle = int(sys.argv[1])

#settings general
settings['quality'] = xbmcplugin.getSetting( handle,"quality")
settings['enable_captions'] = xbmcplugin.getSetting( handle, "enable_captions" )
#per page settings
page = ['25','50','100','250','500','1000','2000']
perpage = int(xbmcplugin.getSetting(  handle,"perpage" ))
settings['perpage'] = page[perpage]
popperpage = int(xbmcplugin.getSetting(  handle,"popperpage" ))
settings['popperpage'] = page[popperpage]
allperpage = int(xbmcplugin.getSetting(  handle,"allperpage" ))
settings['allperpage'] = page[allperpage]
#settings login
settings['login_name'] = xbmcplugin.getSetting(  handle,"login_name" )
settings['login_pass'] = xbmcplugin.getSetting(  handle,"login_pass" )
settings['enable_login'] = xbmcplugin.getSetting(  handle,"enable_login" )
settings['enable_plus'] = xbmcplugin.getSetting( handle, "enable_plus" )

"""
    Clean Non-Ascii characters from names for XBMC
"""

def cleanNames(string):
    try:
        string = string.replace("'","").replace(unicode(u'\u201c'), '"').replace(unicode(u'\u201d'), '"').replace(unicode(u'\u2019'),'\'').replace(unicode(u'\u2026'),'...').replace(unicode(u'\u2018'),'\'').replace(unicode(u'\u2013'),'-')
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

def addDirectory(name, url='', mode='default', thumb='', icon='', fanart='http://assets.huluim.com/companies/key_art_hulu.jpg', plot='', genre='', showid='', season='', page = 1,perpage='',popular='false',updatelisting='false'):
    ok=True
    u = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+urllib.quote_plus(mode)+'"'
    u += '&name="'+urllib.quote_plus(name)+'"'
    u += '&page="'+urllib.quote_plus(page)+'"'
    u += '&perpage="'+urllib.quote_plus(perpage)+'"'
    u += '&popular="'+urllib.quote_plus(popular)+'"'
    u += '&updatelisting="'+urllib.quote_plus(updatelisting)+'"'
    liz=xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    liz.setInfo( type="Video", infoLabels={ "Title":name, "Plot":cleanNames(plot), "Genre":genre})
    liz.setProperty('fanart_image',fanart)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok


"""
    READ PAGE
"""

def getHTML( url ):
    print 'HULU --> common :: getHTML :: url = '+url
    cj = cookielib.LWPCookieJar()
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Referer', 'http://hulu.com'),
                         ('Content-Type', 'application/x-www-form-urlencoded'),
                         ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')]
    usock=opener.open(url)
    response=usock.read()
    usock.close()
    if os.path.isfile(COOKIEFILE):
        cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    return response

def getFEED( url ):
    try:
        print 'HULU --> common :: getFEED :: url = '+url
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('Referer', 'http://download.hulu.com/huludesktop.swf?ver=0.1.0'),
                             ('x-flash-version', '10,0,32,18'),
                             ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET CLR 1.1.4322; .NET4.0C)')]
        usock=opener.open(url)
        response=usock.read()
        usock.close()
        return response
    except:
        return False
        


"""
    ATTEMPT LOGIN
"""

def login():
    #don't do anything if they don't have a password or username entered
    if settings['login_name']=='' or settings['login_pass']=='':
        print "Hulu --> WARNING: Could not login.  Please enter a username and password in settings"
        return False

    cj = cookielib.LWPCookieJar()
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Referer', 'http://hulu.com'),
                         ('Content-Type', 'application/x-www-form-urlencoded'),
                         ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'),
                         ('Connection', 'keep-alive')]
    data =urllib.urlencode({"login":settings['login_name'],"password":settings['login_pass']})
    usock = opener.open(login_url, data)
    response = usock.read()
    usock.close()
    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    
    print 'HULU -- > These are the cookies we have received:'
    for index, cookie in enumerate(cj):
        print 'HULU--> '+str(index)+': '+str(cookie)
        
    print "HULU --> login_url response (we want 'ok=1'): " + response
    if response == 'ok=1':
        loggedIn = True
    else:
        loggedIn = False
    
    

    



