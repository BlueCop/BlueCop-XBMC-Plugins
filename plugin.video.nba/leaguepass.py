import datetime, time
from datetime import date
from datetime import timedelta
import urllib,urllib2,re,time,xbmcplugin,xbmcgui, xbmcaddon, os, httplib2
from xml.dom.minidom import parse, parseString

############################################################################
# global variables
settings = xbmcaddon.Addon( id="plugin.video.nba")
quality = settings.getSetting( id="quality")
scores = settings.getSetting( id="scores")
cookies = ''
http = httplib2.Http()
http.disable_ssl_certificate_validation=True
############################################################################

def getDate( default= '', heading='Please enter date (YYYY/MM/DD)', hidden=False ):
    now = datetime.datetime.now()
    default = "%04d" % now.year + '/' + "%02d" % now.month + '/' + "%02d" % now.day
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    ret = date.today()
    if ( keyboard.isConfirmed() ):
        sDate = unicode( keyboard.getText(), "utf-8" )
        temp = sDate.split("/")
        ret = date(int(temp[0]),  int(temp[1]), int(temp[2]))
    return ret

def login():
    try:
        url = 'https://www.nba.tv/nbatv/secure/login?'
        body = {'username' : settings.getSetting( id="username"), 'password' : settings.getSetting( id="password")}
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        response, content = http.request(url+urllib.urlencode(body), 'POST', headers=headers)
        global cookies
        cookies  = response['set-cookie'].partition(';')[0] + '; locale=en_US'
        return cookies
    except:
        return ''

def encrypt(args):
    try:
        url = 'http://www.nba.tv/nbatv/servlets/encryptvideopath?'
        headers = { 'Host': 'www.nba.tv',
                    'User-Agent':'Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.1.18) Gecko/20110323 Iceweasel/3.5.18 (like Firefox/3.5.18)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Keep-Alive': '300',
                    'Connection': 'keep-alive',
                    'Cookie': cookies }
        url = url+ urllib.urlencode(args)
        response, content = http.request(url, 'POST', headers=headers)
        xml = parseString(str(content))
        link = xml.getElementsByTagName("path")[0].childNodes[0].nodeValue
        pp = ' playpath=mp4:u' + link.partition('mp4:u')[2]
        app = ' app=ondemand?' + link.partition('?')[2]
        link = 'rtmp://cp118328.edgefcs.net:1935/ondemand' + app + pp + ' swfUrl=http://neulionms.vo.llnwd.net/o37/nba/player/nbatv/console.swf swfVfy=1'
        return link
    except:
        return ''

teams = {
        "nyk" : "knicks",
        "njn" : "nets",
        "atl" : "hawks",
        "was" : "wizards",
        "phi" : "sixers",
        "bos" : "celtics",
        "chi" : "bulls",
        "min" : "timberwolves",
        "mil" : "bucks",
        "cha" : "bobcats",
        "dal" : "mavericks",
        "lac" : "clippers",
        "lal" : "lakers",
        "sas" : "spurs",
        "okc" : "thunder",
        "noh" : "hornets",
        "por" : "blazers",
        "mem" : "grizzlies",
        "mia" : "heat",
        "orl" : "magic",
        "sac" : "kings",
        "tor" : "raptors",
        "ind" : "pacers",
        "det" : "pistons",
        "cle" : "cavaliers",
        "den" : "nuggets",
        "uta" : "jazz",
        "phx" : "suns",
        "gsw" : "warriors",
        "hou" : "rockets"}

def getGames(fromDate = '', full = True, highlight = False):
    pattern = 'c:{ipd:'
    postfix = 'condensed_'
    squality = 'hd'

    if quality == '0':
        squality = 'sd'

    if full == True:
        pattern = 'f:{ipd:'
        postfix ='whole_'

    try:
        date = ''
        h = ''
        v = ''
        gid =''
        idx = ''
        st = ''
        vs = ''
        hs = ''
        headers = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/2.0.0.13'}
        thisweek = 'http://smb.cdnak.neulion.com/fs/nba/feeds/schedule/' +fromDate +  '.js?t=' + "%d"  %time.time()
        req = urllib2.Request(thisweek, None, headers);
        response = str(urllib2.urlopen(req).read())
        tmp = response.split('}}}')
        isFirst = True

        for x in tmp:
            date = ''
            h = ''
            v = ''
            gid =''
            idx = ''
            vs = ''
            hs = ''
            if isFirst:
                tmp2 = x.partition('games":[[{')
                isFirst = False
                tmp3 = tmp2[2]
            else:
                tmp3 = x

            tmp4 = tmp3.split(',')
            for y in tmp4:
                y = y.replace('"', '').replace(" ", "").replace("[", "")
                y = y.replace('{h' , 'h')

                if y[:2] == 'h:':
                    h = y[2:]
                elif y[:2] == 'v:':
                    v = y[2:]
                elif y[:3] == 'vs:':
                    vs = y[3:]
                elif y[:3] == 'hs:':
                    hs = y[3:]
                elif y[:3] == 'id:':
                    gid = y[5:]
                elif y[:2] == 'd:':
                    date = y[2:].partition('T')[0].replace('-','/')
                else:
                    pos = y.find(pattern)
                    if pos != -1:
                        idx = y[pos+8:pos+9]

            if date != '' and idx in ['1', '2', '3', '4', '5']:
                name = date  + ' '  + v + '@' + h

                if scores == '1' and vs != '':
                    name = name + " " + vs + ":" + hs

                if highlight == False:
                    url = 'rtmp://cp117939.edgefcs.net/ondemand/mp4:u/nbamobile/vod/nba/' + date + '/' + gid + '/pc/2_' + gid
                    url = url + '_' + v.lower() + '_' + h.lower() + '_2011_h_'  + postfix+ idx + '_'  + squality + '.mp4'
                    addDir(name, url, '5', '')
                else:
                    url = 'http://nba.cdn.turner.com/nba/big/games/' + teams[h.lower()] + '/' + date + '/00' + gid + '_' + v.lower() + '_' + h.lower() + '_recap.nba_nba_'
                    if quality == '0':
                        url = url + '576x324.flv'
                    else:
                        url = url + '1280x720.mp4'
                    thumb = 'http://nba.cdn.turner.com/nba/nba/video/games/' + teams[h.lower()] + '/' + date + '/00' + gid + '_' + v.lower() + '_' + h.lower() + '_recap.nba.400x300.jpg'
                    addLink(name, url, '', thumb)
    except:
        return None

def playGame(title, url):
    global cookies
    if cookies == '':
        cookies  = login()
    values = { 'path' : url , 'isFlex' : 'true', 'type': 'fvod'}
    link = encrypt(values)
    if link != '':
        addLink(title, link, '', '')
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='')
        liz.setInfo( type="Video", infoLabels={ "Title": title } )
        xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(link,liz)

def mainMenu():
    addDir('Archive', 'archive', '1','')
    addDir('Condensed', 'condensed', '1','')
    addDir('Highlights', 'highlights', '1', '')

def dateMenu(type):
    addDir('This week',  type + 'this', '2' ,'')
    addDir('Last week' , type + 'last', '3','')
    addDir('Select date' , type + 'date', '4','')

def gameLinks(mode, url):
    try:
        isFull = url.find('archive') != -1
        isHighlight = url.find('highlights') != -1
        if mode == 4:
            tday = getDate()
        else:
            tday = date.today()

        day = tday.isoweekday()
        # starts on mondays
        tday = tday - timedelta(day -1)
        now = tday
        default = "%04d" % now.year
        default = default + '/' + "%d" % now.month
        default = default + '_' + "%d" % now.day
        if mode == 2 or mode ==4:
            getGames(default, isFull, isHighlight)
        elif mode == 3:
            tday = tday - timedelta(7)
            now = tday
            default = "%04d" % now.year
            default = default + '/' + "%d" % now.month
            default = default + '_' + "%d" % now.day
            getGames(default, isFull, isHighlight)
        else:
                getGames(default, False, isHighlight)
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
    except:
        xbmcplugin.endOfDirectory(handle = int(sys.argv[1]),succeeded=False)
        return None

def getParams():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
    return param

def addLink(name,url,title,iconimage):
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": title } )
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)

def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

params=getParams()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass

if mode==None or url==None or len(url)<1:
    mainMenu()

elif mode==1:
    dateMenu(url)

elif mode==5:
    playGame(name, url)

else:
    gameLinks(mode, url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
