#!/usr/bin/python
#
#
# Written by Ksosez, with massive help from Bluecop
# Released under GPL(v2)

import urllib, urllib2, xbmcplugin, xbmcaddon, xbmcgui, string, htmllib, os, platform, random, calendar, re
import cookielib
import mechanize
import time
from datetime import datetime, timedelta
from BeautifulSoup import BeautifulStoneSoup

## Get the settings

selfAddon = xbmcaddon.Addon(id='plugin.video.espn3')
cbrowser=selfAddon.getSetting('browser')
if cbrowser is '' or cbrowser is None:
    # Default to Firefox
    cbrowser = "Firefox"
usexbmc = selfAddon.getSetting('watchinxbmc')
defaultimage = 'special://home/addons/plugin.video.espn3/icon.png'
defaultfanart = 'special://home/addons/plugin.video.espn3/fanart.jpg'
if usexbmc is '' or usexbmc is None:
    usexbmc = True

pluginpath = selfAddon.getAddonInfo('path')
pluginhandle = int(sys.argv[1])
ADDONDATA = xbmc.translatePath('special://profile/addon_data/plugin.video.espn3/')
COOKIEFILE = os.path.join(ADDONDATA,'cookies.lwp')
USERFILE = os.path.join(ADDONDATA,'userdata.xml')

cj = cookielib.LWPCookieJar()
confluence_views = [500,501,502,503,504,508]

channels = '&channel='
if selfAddon.getSetting('espn1') == 'true':
    channels += 'espn1,'
if selfAddon.getSetting('espn2') == 'true':
    channels += 'espn2,'
if selfAddon.getSetting('espn3') == 'true':
    channels += 'espn3,'
if selfAddon.getSetting('espnu') == 'true':
    channels += 'espnu,'
if selfAddon.getSetting('goalline') == 'true':
    channels += 'goalline,'
channels = channels[:-1]

def CATEGORIES():
    curdate = datetime.now()
    enddate = '&endDate='+ curdate.strftime("%Y%m%d")
    start10 = (curdate-timedelta(days=10)).strftime("%Y%m%d")
    start30 = (curdate-timedelta(days=30)).strftime("%Y%m%d")
    start60 = (curdate-timedelta(days=60)).strftime("%Y%m%d")
    start120 = (curdate-timedelta(days=120)).strftime("%Y%m%d")
    addDir('Live', 'http://espn.go.com/watchespn/feeds/startup?action=live'+channels, 1, defaultimage)
    addDir('Upcoming', 'http://espn.go.com/watchespn/feeds/startup?action=upcoming'+channels, 2,defaultimage)
    addDir('Replay 10 Days', 'http://espn.go.com/watchespn/feeds/startup?action=replay'+channels+enddate+'&startDate='+start10, 2, defaultimage)
    addDir('Replay 30 Days', 'http://espn.go.com/watchespn/feeds/startup?action=replay'+channels+enddate+'&startDate='+start30, 2, defaultimage)
    addDir('Replay 60 Days', 'http://espn.go.com/watchespn/feeds/startup?action=replay'+channels+enddate+'&startDate='+start60, 2, defaultimage)
    addDir('Replay 60-120 Days', 'http://espn.go.com/watchespn/feeds/startup?action=replay'+channels+'&endDate='+start60+'&startDate='+start120, 2, defaultimage)
    addDir('Replay All', 'http://espn.go.com/watchespn/feeds/startup?action=replay'+channels, 2, defaultimage)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def LISTSPORTS(url,name):
    if selfAddon.getSetting("enablelogin") == 'true':
        useCookie=True
    else:
        useCookie=False
    data = get_html(url,useCookie=useCookie)
    addDir('(All)', url, 1, defaultimage)
    SaveFile('videocache.xml', data, ADDONDATA)
    tree = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    sports = []
    for event in tree.findAll('sportdisplayvalue'):
        sport = event.string.title().encode('utf-8')
        if sport not in sports:
            sports.append(sport)
    for sport in sports:
        addDir(sport, url, 3, defaultimage)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)

def INDEXBYSPORT(url,name):
    INDEX(url,name,bysport=True)
    
def INDEX(url,name,bysport=False):
    if 'action=live' in url:
        if selfAddon.getSetting("enablelogin") == 'true':
            useCookie=True
        else:
            useCookie=False
        data = get_html(url,useCookie=useCookie)
    else:
        data = ReadFile('videocache.xml', ADDONDATA)
    tree = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    for event in tree.findAll('event'):
        sport = event.find('sportdisplayvalue').string.title().encode('utf-8')
        if name <> sport and bysport == True:
            continue
        else:
            if 'action=upcoming' in url:
                mode = 5
            else:
                mode = 4
            ename = event.find('name').string.encode('utf-8')
            eventid = event['id']
            bamContentId = event['bamcontentid']
            bamEventId = event['bameventid']
            authurl = '&partnerContentId='+eventid
            authurl += '&eventId='+bamEventId
            authurl += '&contentId='+bamContentId
            sport2 = event.find('sport').string.title().encode('utf-8')
            if sport <> sport2:
                sport += ' ('+sport2+')'
            league = event.find('league').string
            location = event.find('site').string
            thumb = event.find('large').string
            starttime = int(event.find('starttimegmtms').string)/1000
            endtime = int(event.find('endtimegmtms').string)/1000
            start = time.strftime("%m/%d/%Y %I:%M %p",time.localtime(starttime))
            length = str((endtime - starttime)/60)
            rurl = "http://espn.go.com/espn3/player?id=%s" % eventid
            if league is not None:
                rurl += "&league=%s" % urllib.quote(league)
            try: plot = event.find('caption').string+'\n\n'
            except:
                try: plot = event.find('summary').string+'\n\n'
                except: plot = ''
            if sport is not None:
                plot += 'Sport: '+sport+'\n'
            else:
                sport = ''
            if league is not None:
                plot += 'League: '+league+'\n'
            if location is not None:
                plot += 'Location: '+location+'\n'
            infoLabels = {'title':ename,
                          'tvshowtitle':sport,
                          'plot':plot,
                          'aired':start,
                          'premiered':start,
                          'duration':length}
            addLink(ename, authurl, mode, thumb,infoLabels=infoLabels)
    xbmcplugin.setContent(pluginhandle, 'episodes')
    xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[3])+")")

def PLAY(url):
    #Make startupevent url from page url
    #startUrl = 'http://espn.go.com/espn3/feeds/startupEvent?'+url.split('?')[1]+'&gameId=null&sportCode=null'
    #Get eventid, bamContentId, and bamEventId from starturl data
    #html = get_html(startUrl,useCookie=useCookie)
    #if html == False:
    #    dialog = xbmcgui.Dialog()
    #    dialog.ok("Failure to Launch URL", "Unable to launch video feed most likely", "because you already requested this feed.", "Please wait a while and try again.")
    #else:
    #event = BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)('event')[1]
    #eventid = event['id']
    #bamContentId = event['bamcontentid']
    #bamEventId = event['bameventid']
    
    #Make identityPointId from userdata
    #userdata = 'http://broadband.espn.go.com/espn3/auth/userData'
    #html = get_html(userdata,useCookie=useCookie)

    if selfAddon.getSetting("enablelogin") == 'true':
        useCookie=True
    else:
        useCookie=False
    data = ReadFile('userdata.xml', ADDONDATA)
    soup = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print soup.prettify()
    affiliateid = soup('name')[0].string
    swid = soup('personalization')[0]['swid']
    identityPointId = affiliateid+':'+swid

    #Use eventid, bamContentId, bamEventId, and identityPointId to get smil url and auth data
    authurl = 'https://espn-ws.bamnetworks.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.1'
    authurl += '?platform=WEB_MEDIAPLAYER'
    authurl += '&playbackScenario=FMS_CLOUD'
    authurl += url
    #authurl += '&eventId='+bamEventId
    #authurl += '&contentId='+bamContentId
    #authurl += '&partnerContentId='+eventid
    authurl += '&rand='+str(random.random())+'0000'
    authurl += '&cdnName=PRIMARY_AKAMAI'
    authurl += '&identityPointId='+identityPointId
    authurl += '&playerId=domestic'
    html = get_html(authurl,useCookie=useCookie)
    smilurl = BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('url')[0].string
    auth = smilurl.split('?')[1]

    #Grab smil url to get rtmp url and playpath
    html = get_html(smilurl,useCookie=useCookie)
    soup = BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print soup.prettify()
    rtmp = soup.findAll('meta')[0]['base']
    # Live Qualities
    #     0,     1,     2,      3,      4
    # Replay Qualities
    #            0,     1,      2,      3
    # Lowest, Low,  Medium, High,  Highest
    # 200000,400000,800000,1200000,1800000
    if 'ondemand' in rtmp:
        replayquality = selfAddon.getSetting('replayquality')
        playpath = soup.findAll('video')[int(replayquality)]['src']
        finalurl = rtmp+'/?'+auth+' playpath='+playpath
    elif 'live' in rtmp:
        livequality = selfAddon.getSetting('livequality')
        playpath = soup.findAll('video')[int(livequality)]['src']
        finalurl = rtmp+' live=1 playlist=1 subscribe='+playpath+' playpath='+playpath+'?'+auth
    item = xbmcgui.ListItem(path=finalurl)
    return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def PLAYBROWSER(url):
    print "Play URL:%s" % url
    psystem = platform.system()
    if cbrowser == "Chrome":
        if psystem == "Darwin":
            cmd = 'open -a /Applications/Chrome.app %s' % url
        elif psystem == "Linux":
            cmd = "/usr/bin/google-chrome  %s" % url
        elif psystem == "Windows":
            cmd = "chrome.exe %s" % url
        else:
            print "Aint no browser here"
    else:
        if psystem == "Darwin":
            cmd = 'open -a /Applications/Firefox.app %s' % url
        elif psystem == "Linux":
            cmd = "/usr/bin/firefox %s" % url
        elif psystem == "Windows":
            cmd = '"C:\Program Files\Mozilla Firefox\firefox.exe" %s' % url
        else:
            print "Aint no browser here"

    os.system(cmd)

#	subprocess.call(['open -a /Applications/Firefox.app'])
def saveUserdata(useCookie=False):
    userdata = 'http://broadband.espn.go.com/espn3/auth/userData'
    data = get_html(userdata,useCookie=useCookie)
    SaveFile('userdata.xml', data, ADDONDATA)
    soup = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print soup.prettify()
    
def login():
    if selfAddon.getSetting("enablelogin") == 'false':
        if os.path.isfile(USERFILE):
            if selfAddon.getSetting("clearcookies") == 'true':
                saveUserdata()
        else: saveUserdata()
    elif selfAddon.getSetting("enablelogin") == 'true':
        if os.path.isfile(COOKIEFILE):
            if selfAddon.getSetting("clearcookies") == 'true':
                os.remove(COOKIEFILE)
            else:
                return
        types = ['comcast','att','verizon','twc','bhn','insight','cox']
        logintype = types[int(selfAddon.getSetting("logintype"))]
        url = 'http://a.espncdn.com/combiner/c?v=201110050400&js=/espn/espn360/watchespn/format/design11/shell/js/auth'
        data = get_html(url)
        p_AUTH = 'http://broadband.espn.go.com/espn3/auth'
    
        br = mechanize.Browser()  
        br.set_handle_robots(False)
        br.set_cookiejar(cj)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17')]  
    
        if logintype == 'comcast':
            comcastLogin = re.compile('function comcastLogin\(\){(.*?)}').findall(data)[0]
            Cookie = re.compile('set_cookie2\("(.*?)","(.*?)",').findall(comcastLogin)[0]
            LoginUrl = re.compile('var A="(.*?)";').findall(comcastLogin)[0]
            sign_in = br.open(LoginUrl)
            br.select_form(nr=0)
            response = br.submit()
            print response.read()
            br.select_form(name='signin')
            br["user"] = selfAddon.getSetting("login_name")
            br["password"] = selfAddon.getSetting("login_pass")
        elif logintype == 'att':
            attLogin = re.compile('function attLogin\(\){(.*?)}').findall(data)[0]
            Cookie = re.compile('set_cookie2\("(.*?)","(.*?)",').findall(attLogin)
            LoginUrl = re.compile('var A="(.*?)";').findall(attLogin)[0]
            sign_in = br.open(LoginUrl)
            br.select_form(nr=0)
            response = br.submit()
            print response.read()
            br.select_form(name='LoginForm')
            br["userid"] = selfAddon.getSetting("login_name")
            br["password"] = selfAddon.getSetting("login_pass")
        elif logintype == 'twc':    
            twcLogin = re.compile('function twcLogin\(\){(.*?)}').findall(data)[0]
            LoginUrl = p_AUTH + re.compile('p_AUTH\+"(.*?)";').findall(twcLogin)[0]
            sign_in = br.open(LoginUrl)
            br.select_form(nr=0)
            response = br.submit()
            print response.read()
            br.select_form(name='IDPLogin')
            br["Ecom_User_ID"] = selfAddon.getSetting("login_name")
            br["Ecom_Password"] = selfAddon.getSetting("login_pass")
        elif logintype == 'bhn':    
            bhnLogin = re.compile('function bhnLogin\(\){(.*?)}').findall(data)[0]
            LoginUrl = p_AUTH + re.compile('p_AUTH\+"(.*?)";').findall(bhnLogin)[0]
            sign_in = br.open(LoginUrl)
            br.select_form(nr=0)
            response = br.submit()
            print response.read()
            br.select_form(name='IDPLogin')
            br["j_username"] = selfAddon.getSetting("login_name")
            br["j_password"] = selfAddon.getSetting("login_pass")
        elif logintype == 'insight':
            insightLogin = re.compile('function insightLogin\(\){(.*?)}').findall(data)[0]
            LoginUrl = re.compile('open\("(.*?)","').findall(insightLogin)[0]
            LoginUrl = 'http://www.insightbb.com/Auth/Login.aspx?ContentType=ESPN360'
            sign_in = br.open(LoginUrl)
            br.select_form(name="aspnetForm")
            br["ctl00$ContentPlaceHolder1$UL_login1$txtUserID"] = selfAddon.getSetting("login_name")
            br["ctl00$ContentPlaceHolder1$UL_login1$txtpwd"] = selfAddon.getSetting("login_pass")
            #ctl00$ContentPlaceHolder1$UL_login1$chkrememberme
        elif logintype == 'verizon':
            verizonLogin = re.compile('function verizonLogin\(A\){(.*?)}').findall(data)[0]
            LoginUrl = re.compile('open\("(.*?)","').findall(verizonLogin)[0]
            sign_in = br.open(LoginUrl)
            br.select_form(name="loginpage")
            br["IDToken1"] = selfAddon.getSetting("login_name")
            br["IDToken2"] = selfAddon.getSetting("login_pass")
        elif logintype == 'cox':
            coxLogin = re.compile('function coxLogin\(\){(.*?)}').findall(data)[0]
            Cookie = re.compile('set_cookie2\("(.*?)","(.*?)",').findall(coxLogin)[0]
            LoginUrl = re.compile('var A="(.*?)";').findall(coxLogin)[0]
            sign_in = br.open(LoginUrl)
            br.select_form(name="LoginPage")  
            br["username"] = addon.getSetting("login_name")
            br["password"] = addon.getSetting("login_pass")
        response = br.submit()
        print response.read()
        br.select_form(nr=0)
        response = br.submit()
        print response.read()
        saveUserdata()
        cj.save(COOKIEFILE, ignore_discard=False, ignore_expires=False)

def get_html( url , useCookie=False):
    try:
        print 'ESPN3:  get_html: '+url
        if useCookie and os.path.isfile(COOKIEFILE):
            cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17')]
        usock = opener.open(url)
        response = usock.read()
        usock.close()
        #cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)
        return response
    except: return False

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

def SaveFile(filename, data, dir):
    path = os.path.join(dir, filename)
    file = open(path,'w')
    file.write(data)
    file.close()

def ReadFile(filename, dir):
    path = os.path.join(dir, filename)
    file = open(path,'r')
    return file.read()

def addLink(name, url, mode, iconimage, infoLabels=False):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    if not infoLabels:
        infoLabels={"Title": name}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    liz.setProperty('IsPlayable', 'true')
    liz.setProperty('fanart_image',defaultfanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('fanart_image',defaultfanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = get_params()
url = None
name = None
mode = None
cookie = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)

if mode == None or url == None or len(url) < 1:
    login()
    print "Generate Main Menu"
    CATEGORIES()
elif mode == 1:
    print "Indexing Videos"
    INDEX(url,name)
elif mode == 2:
    print "List sports"
    LISTSPORTS(url,name)
elif mode == 3:
    print "Index by sport"
    INDEXBYSPORT(url,name)
elif mode == 5:
    print "Upcoming"

elif mode == 4:
    print "Play Video"
    if usexbmc == True or usexbmc == "true":
        PLAY(url)
    else:
        PLAYBROWSER(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
