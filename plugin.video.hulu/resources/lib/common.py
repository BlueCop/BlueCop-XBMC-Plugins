import xbmcplugin
import xbmc
import xbmcgui
import addoncompat
import urllib
import urllib2
import sys
import os
import cookielib
import operator
import re
import time
import random

from crypto.cipher.cbc      import CBC
from crypto.cipher.base     import padWithPadLen
from crypto.cipher.rijndael import Rijndael

try:
    from xml.etree import ElementTree
except:
    from elementtree import ElementTree

"""
    PARSE ARGV
"""

class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )

exec "args = _Info(%s)" % (urllib.unquote_plus(sys.argv[2][1:].replace("&", ", ").replace('"','\'').replace('%5C', '%5C%5C')), )


"""
    DEFINE URLS
"""
BASE_MENU_URL = "http://m.hulu.com/menu/hd_main_menu?show_id=0&dp_id=huludesktop&package_id=2&page=1"

xmldeckeys = [
             ['4878B22E76379B55C962B18DDBC188D82299F8F52E3E698D0FAF29A40ED64B21', 'WA7hap7AGUkevuth'],
             ['246DB3463FC56FDBAD60148057CB9055A647C13C02C64A5ED4A68F81AE991BF5', 'vyf8PvpfXZPjc7B1'],
             ['8CE8829F908C2DFAB8B3407A551CB58EBC19B07F535651A37EBC30DEC33F76A2', 'O3r9EAcyEeWlm5yV'],
             ['852AEA267B737642F4AE37F5ADDF7BD93921B65FE0209E47217987468602F337', 'qZRiIfTjIGi3MuJA'],
             ['76A9FDA209D4C9DCDFDDD909623D1937F665D0270F4D3F5CA81AD2731996792F', 'd9af949851afde8c'],
             ['1F0FF021B7A04B96B4AB84CCFD7480DFA7A972C120554A25970F49B6BADD2F4F', 'tqo8cxuvpqc7irjw'],
             ['3484509D6B0B4816A6CFACB117A7F3C842268DF89FCC414F821B291B84B0CA71', 'SUxSFjNUavzKIWSh'],
             ['B7F67F4B985240FAB70FF1911FCBB48170F2C86645C0491F9B45DACFC188113F', 'uBFEvpZ00HobdcEo'],
             ['40A757F83B2348A7B5F7F41790FDFFA02F72FC8FFD844BA6B28FD5DFD8CFC82F', 'NnemTiVU0UA5jVl0'],
             ['d6dac049cc944519806ab9a1b5e29ccfe3e74dabb4fa42598a45c35d20abdd28', '27b9bedf75ccA2eC']
             ]

#define file locations
addoncompat.get_revision()
pluginpath = addoncompat.get_path()

COOKIEFILE = os.path.join(pluginpath,'resources','cache','hulu-cookies.lwp')
QUEUETOKEN = os.path.join(pluginpath,'resources','cache','token.xml')
ADCACHE = os.path.join(pluginpath,'resources','cache','ad.xml')
SMILCACHE = os.path.join(pluginpath,'resources','cache','smil.xml')
WARNING = os.path.join(pluginpath,'resources','cache','warning')
cachepath = os.path.join(pluginpath,'resources','cache')
imagepath  = os.path.join(pluginpath,'resources','images')
hulu_fanart = os.path.join(pluginpath,'fanart.jpg')
hulu_icon = os.path.join(imagepath,'icon.png')


if os.path.isfile(WARNING):
    xbmcgui.Dialog().ok('Attention','This is Free Software.','If you paid for the Hulu plug-in then you have','been defrauded and should request a refund.',)
    os.remove(WARNING)
"""
    GET SETTINGS
"""

settings={}
handle = int(sys.argv[1])

#settings Advanced
settings['quality'] = addoncompat.get_setting("quality")
settings['adquality'] = int(addoncompat.get_setting("adquality"))
settings['prerollads'] = int(addoncompat.get_setting("prerollads"))
settings['networkpreroll'] = addoncompat.get_setting("networkpreroll")
settings['trailads'] = int(addoncompat.get_setting("trailads"))
settings['adbreaks'] = int(addoncompat.get_setting("adbreaks"))
settings['segmentvideos'] = addoncompat.get_setting("segmentvideos")
settings['swfverify'] = addoncompat.get_setting("swfverify")
cdns = ['level3','limelight','akamai']
defualtcdn = int(addoncompat.get_setting("defaultcdn"))
settings['defaultcdn'] = cdns[defualtcdn]
#setting captions
settings['enable_captions'] = addoncompat.get_setting("enable_captions")
settings['queueremove'] = addoncompat.get_setting("queueremove")
settings['proxy_enable'] = addoncompat.get_setting('us_proxy_enable')
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

settings['viewenable'] = addoncompat.get_setting("viewenable")
settings['defaultview'] = addoncompat.get_setting("defaultview")

settings['enablelibraryfolder'] = addoncompat.get_setting("enablelibraryfolder")
settings['customlibraryfolder'] = addoncompat.get_setting("customlibraryfolder")
settings['updatelibrary'] = addoncompat.get_setting("updatelibrary")

#settings login
settings['login_name'] = addoncompat.get_setting("login_name")
settings['login_pass'] = addoncompat.get_setting("login_pass")
settings['enable_login'] = addoncompat.get_setting("enable_login")
settings['enable_plus'] = addoncompat.get_setting("enable_plus")

#Token settings
def setToken():       
    xml = OpenFile(QUEUETOKEN)
    tree = ElementTree.XML(xml)
    settings['expiration'] = tree.findtext('token-expires-at')
    settings['usertoken'] = tree.findtext('token')
    settings['planid'] = tree.findtext('plid')
    settings['userid'] = tree.findtext('id')

def checkToken():
    if os.path.isfile(QUEUETOKEN):
        setToken()
        expires = time.strptime(settings['expiration'], "%Y-%m-%dT%H:%M:%SZ")
        now = time.localtime()
        if now > expires:
            print 'Expired Token'
            login_queue()
    elif settings['enable_login'] == 'true':
        login_queue()
        if os.path.isfile(QUEUETOKEN):
            setToken()
    else:
        print 'HULU -->  Login disabled'
        

    
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
    u += '&art=""'
    u += '&fanart=""'
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

def getFEED( url , postdata=None , proxy = False):
    try:
        print 'HULU --> common :: getFEED :: url = '+url
        if proxy == True:
            us_proxy = 'http://' + addoncompat.get_setting('us_proxy') + ':' + addoncompat.get_setting('us_proxy_port')
            proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
            if addoncompat.get_setting('us_proxy_pass') <> '' and addoncompat.get_setting('us_proxy_user') <> '':
                print 'Using authenticated proxy: ' + us_proxy
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, us_proxy, addoncompat.get_setting('us_proxy_user'), addoncompat.get_setting('us_proxy_pass'))
                proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
            else:
                print 'Using proxy: ' + us_proxy
                opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)
        if postdata == None:
            req = urllib2.Request(url)
        else:
            req = urllib2.Request(url,postdata)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)')
        req.add_header('Referer', 'http://download.hulu.com/hulu10.html')
        #req.add_header('x-flash-version', '11,1,102,55')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()

    except urllib2.URLError, e:
        print 'Error reason: ', e
        heading = 'Error'
        message = e
        duration = 10000
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
        return False
    else:
        return link

def postSTOP( type,content_id,position ):
    print 'HULU --> common :: postSTOP :: content_id = '+content_id
    opener = urllib2.build_opener()
    opener.addheaders = [('Referer', 'http://download.hulu.com/huludesktop.swf?ver=0.1.0'),
                         ('x-flash-version', '11,1,102,55'),
                         ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)')]
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

def SaveFile(path, data):
    file = open(path,'w')
    file.write(data)
    file.close()

def OpenFile(path):
    file = open(path, 'r')
    contents=file.read()
    file.close()
    return contents

def AES(key):
    return Rijndael(key, keySize=32, blockSize=16, padding=padWithPadLen())

def AES_CBC(key):
    return CBC(blockCipherInstance=AES(key))

def makeGUID():
    guid = ''
    for i in range(8):
        number = "%X" % (int( ( 1.0 + random.random() ) * 0x10000) | 0)
        guid += number[1:]
    return guid
    
"""
    Queue Token Login
"""
def login_queue():
    if settings['login_name']=='' or settings['login_pass']=='':
        print "Hulu --> WARNING: Could not login.  Please enter a username and password in settings"
        return False
    action = "authenticate"
    parameters = {'login'   : settings['login_name'],
                  'password': settings['login_pass'],
                  'nonce'   : NONCE()}
    data = postAPI(action,parameters,True)
    SaveFile(QUEUETOKEN, data)
    Notify('Success','User Queue Login Successful',4000)
    
def Notify(heading,message,duration):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )

def APIsignature(action,parameters):
    parameters['app'] = 'f8aa99ec5c28937cf3177087d149a96b5a5efeeb'
    sorted_parameters = sorted(parameters.iteritems(), key=operator.itemgetter(0))
    paramsString = ''
    for item1, item2 in sorted_parameters:
        paramsString += str(item1) + str(item2)
    secret = "mTGPli7doNEpGfaVB9fquWfuAis"
    data = secret + action + paramsString
    try:
        import hashlib
        return hashlib.sha1(data).hexdigest()
    except:
        import sha
        return sha.new(data).hexdigest()

def postAPI( action , parameters, secure):
    if secure == True:
        url = 'https://secure.'
        host = 'secure.hulu.com'
    elif secure == False:
        url = 'http://www.'
        host = 'www.hulu.com'
    url += 'hulu.com/api/1.0/'+action
    parameters['sig'] = APIsignature(action,parameters)
    data = urllib.urlencode(parameters)
    headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)',
               'Host': host,
               'Referer':'http://download.hulu.com/huludesktop.swf?ver=0.1.0'
               }
    req = urllib2.Request(url,data,headers)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

def NONCE():
    action = 'nonce'
    values = {}
    data = postAPI(action,values,True)
    return re.compile('<nonce>(.+?)</nonce>').findall(data)[0]

def userSettings():
    action = 'user'
    values = {'token'       : settings['usertoken'],
              'operation'   : 'config'}
    return postAPI(action , values, False)

def viewcomplete():
    action = "event"
    parameters = {'event_type':'view_complete',
                  'token':settings['usertoken'],
                  'target_type':'video',
                  'id':args.videoid}
    postAPI(action,parameters,False)
    print "HULU --> Posted View Complete"
    
def viewed(videoid):
    try:
        action = "event"
        parameters = {'event_type':'view',
                      'token':settings['usertoken'],
                      'target_type':'video',
                      'id':videoid}
        postAPI(action,parameters,False)
        print "HULU --> Posted view"
    except:
        print "HULU --> Post view failed"

def queueEdit():
    values = {'token':settings['usertoken'],
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
        Notify(heading,message,duration)
    except:
        Notify('Failure','Operation Failed',4000)


#Do token settings
checkToken()





"""
    Hulu+ Cookie Login
    NO LONGER USED
"""

def login_cookie():
    #don't do anything if they don't have a password or username entered
    login_url   = "https://secure.hulu.com/account/authenticate"
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