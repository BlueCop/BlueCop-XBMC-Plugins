import xbmcplugin
import xbmc
import xbmcgui
#import xbmcaddon
import addoncompat
import urllib
import urllib2
import sys
import os
import cookielib
import operator
import sha
import re
import time
import md5
import tempfile
from BeautifulSoup import BeautifulStoneSoup


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
addoncompat.get_revision()
pluginpath = addoncompat.get_path()

COOKIEFILE = os.path.join(pluginpath,'resources','cache','hulu-cookies.lwp')
QUEUETOKEN = os.path.join(pluginpath,'resources','cache','token.xml')
ADCACHE = os.path.join(pluginpath,'resources','cache','ad.xml')
SMILCACHE = os.path.join(pluginpath,'resources','cache','smil.xml')
cachepath = os.path.join(pluginpath,'resources','cache')
imagepath  = os.path.join(pluginpath,'resources','images')
hulu_fanart = os.path.join(pluginpath,'fanart.jpg')

"""
    GET SETTINGS
"""

settings={}
handle = int(sys.argv[1])

#settings Advanced
settings['quality'] = addoncompat.get_setting("quality")
settings['adquality'] = int(addoncompat.get_setting("adquality"))
settings['prerollads'] = int(addoncompat.get_setting("prerollads"))
settings['trailads'] = int(addoncompat.get_setting("trailads"))
settings['adbreaks'] = int(addoncompat.get_setting("adbreaks"))
settings['segmentvideos'] = addoncompat.get_setting("segmentvideos")
settings['swfverify'] = addoncompat.get_setting("swfverify")
cdns = ['level3','limelight','akamai']
defualtcdn = int(addoncompat.get_setting("defaultcdn"))
settings['defaultcdn'] = cdns[defualtcdn]
#setting captions
settings['enable_captions'] = addoncompat.get_setting("enable_captions")
#per page settings
page = ['25','50','100','250','500','1000','2000']
perpage = int(addoncompat.get_setting("perpage"))
settings['perpage'] = page[perpage]
popperpage = int(addoncompat.get_setting("popperpage"))
settings['popperpage'] = page[popperpage]
allperpage = int(addoncompat.get_setting("allperpage" ))
settings['allperpage'] = page[allperpage]
searchperpage = int(addoncompat.get_setting("searchperpage" ))
settings['searchperpage'] = page[searchperpage]

settings['enablelibraryfolder'] = addoncompat.get_setting("enablelibraryfolder")
settings['customlibraryfolder'] = addoncompat.get_setting("customlibraryfolder")
settings['updatelibrary'] = addoncompat.get_setting("updatelibrary")

#settings login
settings['login_name'] = addoncompat.get_setting("login_name")
settings['login_pass'] = addoncompat.get_setting("login_pass")
settings['enable_login'] = addoncompat.get_setting("enable_login")
settings['enable_plus'] = addoncompat.get_setting("enable_plus")
if os.path.isfile(QUEUETOKEN):
    tokenfile = open(QUEUETOKEN, "r")
    tokenxml = tokenfile.read()
    tokenfile.close()
    tree=BeautifulStoneSoup(tokenxml)
    # "2011-08-13T19:44:02Z", "%Y-%m-%dT%H:%M:%SZ"
    settings['expiration'] = tree.find('token-expires-at').string
    settings['usertoken'] = tree.find('token').string

    
"""
    Clean Non-Ascii characters from names for XBMC
"""

def cleanNames(string):
    try:
        string = string.replace("'","").replace(unicode(u'\u201c'), '"').replace(unicode(u'\u201d'), '"').replace(unicode(u'\u2019'),'').replace(unicode(u'\u2026'),'...').replace(unicode(u'\u2018'),'').replace(unicode(u'\u2013'),'-')
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

def addDirectory(name, url='', mode='default', thumb='', icon='', fanart='', plot='', genre='', showid='', season='', page = '1',perpage='',popular='false',updatelisting='false',cm=False):
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
    if cm:
        liz.addContextMenuItems( cm )#,replaceItems=True)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

"""
    READ PAGE
"""

def getHTML( url ):
    print 'HULU --> common :: getHTML :: url = '+url
    cj = cookielib.LWPCookieJar()
    #if os.path.isfile(COOKIEFILE):
    #    cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Referer', 'http://hulu.com'),
                         ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')]
    usock=opener.open(url)
    response=usock.read()
    usock.close()
    #if os.path.isfile(COOKIEFILE):
    #    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    return response

def getFEED( url, max_age=0 , postdata=False):
    try:
        print 'HULU --> common :: getFEED :: url = '+url
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('Referer', 'http://download.hulu.com/hulu10.html'),
                             ('x-flash-version', '11,1,102,55'),
                             ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET CLR 1.1.4322; .NET4.0C)')]
        if postdata:
            usock=opener.open(url,postdata)
        else:
            usock=opener.open(url)
        response=usock.read()
        usock.close()
        return response
    except:
        return False

def postSTOP( type,content_id,position ):
    print 'HULU --> common :: postSTOP :: content_id = '+content_id
    opener = urllib2.build_opener()
    opener.addheaders = [('Referer', 'http://download.hulu.com/huludesktop.swf?ver=0.1.0'),
                         ('x-flash-version', '11,1,102,55'),
                         ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET CLR 1.1.4322; .NET4.0C)')]
    url = 'http://www.hulu.com/pt/position'
    strposition = "%.2f" % position
    values = {'type':type,
              'position':strposition,
              'token':settings['usertoken'],
              'content_id':content_id,
              'device_name':'huludesktop'}
    data = urllib.urlencode(values)
    usock=opener.open(url,data)
    response=usock.read()
    usock.close()
    return response


def cacheFEED( url, max_age=0,cache_dir=cachepath):
    print 'HULU --> common :: cacheFEED :: url = '+url
    filename = md5.new(url).hexdigest()
    filepath = os.path.join(cache_dir, filename)
    if os.path.exists(filepath):
        if int(time.time()) - os.path.getmtime(filepath) < max_age:
            print 'Returned from Cache'
            return open(filepath).read()
        else:
            os.remove(filepath)
    
    opener = urllib2.build_opener(urllib2.HTTPHandler())
    opener.addheaders = [('Referer', 'http://download.hulu.com/huludesktop.swf?ver=0.1.0'),
                         ('x-flash-version', '11,1,102,55'),
                         ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET CLR 1.1.4322; .NET4.0C)')]
    usock=opener.open(url)
    data=usock.read()
    usock.close()
        
    fd, temppath = tempfile.mkstemp()
    fp = os.fdopen(fd, 'w')
    fp.write(data)
    fp.close()
    os.rename(temppath, filepath)
    print 'Returned from web'
    return data       

def SaveFile(path, data):
    file = open(path,'w')
    file.write(data)
    file.close()

def OpenFile(path):
    file = open(path, 'r')
    contents=file.read()
    file.close()
    return contents


"""
    Hulu+ Cookie Login
    NO LONGER USED
"""

def login_cookie():
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
    
    print 'HULU -- > These are the cookies we have received:'
    for index, cookie in enumerate(cj):
        print 'HULU--> '+str(index)+': '+str(cookie)
        
    print "HULU --> login_url response (we want 'ok=1'): " + response
    if response == 'ok=1':
        cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)
        loggedIn = True
        heading = 'Success'
        message = 'Hulu Login Successful'
        duration = 1500
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
    else:
        loggedIn = False
        heading = 'Failure'
        message = 'Hulu Login Failed'
        duration = 1500
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
    
"""
    Queue Token Login
"""
def login_queue():
    if settings['login_name']=='' or settings['login_pass']=='':
        print "Hulu --> WARNING: Could not login.  Please enter a username and password in settings"
        return False
    action = "authenticate"
    app = "f8aa99ec5c28937cf3177087d149a96b5a5efeeb"
    nonce = NONCE()
    username = settings['login_name']
    password = settings['login_pass']
    parameters = {'login'   : username,
                  'password': password,
                  'app'     : app,
                  'nonce'   : nonce}
    data = postAPI(action,parameters,True)
    file = open(QUEUETOKEN, 'w')
    file.write(data)
    file.close()
    heading = 'Success'
    message = 'User Queue Login Successful'
    duration = 1500
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )

def check_expiration(expiration):
    expires = time.strptime(expiration, "%Y-%m-%dT%H:%M:%SZ")
    now = time.localtime()
    if now > expires:
        print 'Expired Token'
        login_queue()


def postAPI( action , parameters, secure):
    if secure == True:
        url = 'https://secure.'
        host = 'secure.hulu.com'
    elif secure == False:
        url = 'http://www.'
        host = 'www.hulu.com'
    url += 'hulu.com/api/1.0/'+action
    sorted_parameters = sorted(parameters.iteritems(), key=operator.itemgetter(0))
    paramsString = ''
    for item1, item2 in sorted_parameters:
        paramsString += str(item1) + str(item2)
    secret = "mTGPli7doNEpGfaVB9fquWfuAis"
    sig = sha.new(secret + action + paramsString).hexdigest()
    parameters['sig'] = sig
    data = urllib.urlencode(parameters)
    headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET CLR 1.1.4322; .NET4.0C)',
               'Host': host,
               'Referer':'http://download.hulu.com/huludesktop.swf?ver=0.1.0',
               'x-flash-version':'10,1,51,66'
               }
    req = urllib2.Request(url,data,headers)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

def NONCE():
    action = 'nonce'
    values = {'app':'f8aa99ec5c28937cf3177087d149a96b5a5efeeb'}
    data = postAPI(action,values,True)
    return re.compile('<nonce>(.+?)</nonce>').findall(data)[0]

def userSettings():
    action = 'user'
    values = {'app'         : 'f8aa99ec5c28937cf3177087d149a96b5a5efeeb',
              'token'       : settings['usertoken'],
              'operation'   : 'config'}
    return postAPI(action , values, False)


def queueEdit():
    values = {'app':'f8aa99ec5c28937cf3177087d149a96b5a5efeeb',
              'token':settings['usertoken'],
              'id':args.url}
    try:
        if args.mode == 'addqueue':
            values['operation'] = 'add'
            action = 'queue'
            data=postAPI(action,values,False)
            message = 'Added to Queue'
        elif args.mode == 'removequeue':
            values['operation'] = 'remove'
            action = 'queue'
            data=postAPI(action,values,False)
            message = 'Removed from Queue'
        elif args.mode == 'addsub':
            values['operation'] = 'add'
            values['type'] = 'episodes'
            action = 'subscription'
            data=postAPI(action,values,False)
            message = 'Added Subscription'
        elif args.mode == 'removesub':
            values['operation'] = 'remove'
            values['type'] = 'episodes'
            action = 'subscription'
            message = 'Removed Subscription'
            data=postAPI(action,values,False)
        elif args.mode == 'removehistory':
            values['operation'] = 'remove'
            action = 'history'
            data=postAPI(action,values,False)
            message = 'Removed from History'
        elif args.mode == 'vote':
            star = unicode(u'\u2605')
            rating = xbmcgui.Dialog().select('Vote for Video', [star, star+star, star+star+star, star+star+star+star, star+star+star+star+star])
            if rating!=-1:
                rating += 1
                values['target_type'] = 'video'
                values['rating'] = rating
                action = 'vote'
                data=postAPI(action,values,False)
                message = 'Vote Succeeded'
            else:
                return
        if 'ok' in data:
            heading = 'Success'
            duration = 3000
        else:
            heading = 'Failure'
            message = 'Operation Failed'
            duration = 4000
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
    except:
        heading = 'Failure'
        message = 'Operation Failed'
        duration = 4000
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
try:
    check_expiration(settings['expiration'])
except:
    print 'no expiration'
