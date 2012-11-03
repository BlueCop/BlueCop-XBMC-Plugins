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
        url = 'https://watch.nba.com/nba/secure/login?'
        body = {'username' : settings.getSetting( id="username"), 'password' : settings.getSetting( id="password")}
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        response, content = http.request(url+urllib.urlencode(body), 'POST', headers=headers)
        global cookies
        cookies  = response['set-cookie'].partition(';')[0]
        if cookies == '' or str(content).find('loginsuccess') <= 0:
		xbmc.executebuiltin("XBMC.Notification("+'Login Failure'+"," + 'Please check Your credentials!' +")")
		return ''
	return cookies
    except:
        xbmc.executebuiltin("XBMC.Notification("+'Login Failure'+"," + 'Please check Your credentials!' +")")
	return ''

def encrypt2012(args):
    try:
        url = 'http://watch.nba.com/nba/servlets/publishpoint?'
        headers = { 'Host': 'www.nba.tv',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip,deflate',
                    'Keep-Alive': '300',
                    'Connection': 'keep-alive',
                    'Cookie': cookies }
        url = url+ urllib.urlencode(args)
        print 'url--> ' + url + ' headers ' + str(headers)
        response, content = http.request(url, 'POST', headers=headers)
        xml = parseString(str(content))
        link = xml.getElementsByTagName("path")[0].childNodes[0].nodeValue
	pp = ' playpath=mp4:' + link.partition('mp4:')[2]
        app = ' app=ondemand?' + link.partition('?')[2]
        link = 'rtmp://cp118328.edgefcs.net/ondemand' + app + pp + ' swfUrl=http://neulionms.vo.llnwd.net/o37/nba/player/nbatv/console.swf swfVfy=1'
        print 'encrypt--> ' + str(response) + ' content ' + str(content)
        return link
    except:
        return ''



def encrypt(args):
    try:
        url = 'http://watch.nba.com/nba/servlets/encryptvideopath?'
        headers = { 'Host': 'www.nba.tv',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip,deflate',
                    'Keep-Alive': '300',
                    'Connection': 'keep-alive',
                    'Cookie': cookies }
        url = url+ urllib.urlencode(args)
	print 'url--> ' + url + ' headers ' + str(headers)
        response, content = http.request(url, 'POST', headers=headers)
        xml = parseString(str(content))
        link = xml.getElementsByTagName("path")[0].childNodes[0].nodeValue
        pp = ' playpath=mp4:u' + link.partition('mp4:u')[2]
        app = ' app=ondemand?' + link.partition('?')[2]
        link = 'rtmp://cp118328.edgefcs.net:1935/ondemand' + app + pp + ' swfUrl=http://neulionms.vo.llnwd.net/o37/nba/player/nbatv/console.swf swfVfy=1'
	print 'encrypt--> ' + str(response) + ' content ' + str(content)
        return link
    except:
        return ''

teams = {
	"bkn" : "nets",
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
                tmp2 = x.partition('games":[[')
                isFirst = False
                tmp3 = tmp2[2][tmp2[2].find('{"h'):]
            else:
                tmp3 = x

            tmp4 = tmp3.split(',')
            for y in tmp4:
                y = y.replace('"', '').replace(" ", "").replace("[", "").replace("]","").replace("}","")
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
                    year = '2011'
                    playoffidx = '2'
                    if date > '2012/04/27' and date < '2012/10/01':
                        playoffidx = '3'
		    elif date < '2012/10/30' and date > '2012/10/01':
			playoffidx = '1'
			year = '2012'
		    elif date > '2012/10/29':
			year = '2012'

                    url = 'rtmp://cp117939.edgefcs.net/ondemand/mp4:u/nbamobile/vod/nba/' + date + '/' + gid + '/pc/' + playoffidx + '_' + gid
                    url = url + '_' + v.lower() + '_' + h.lower() + '_' + year + '_h_'  + postfix+ idx + '_'  + squality + '.mp4'
                    addDir(name, url, '5', '')
                else:
                    if date < '2012/04/27':
                        url = 'http://nba.cdn.turner.com/nba/big/games/' + teams[h.lower()] + '/' + date + '/00' + gid + '_' + v.lower() + '_' + h.lower() + '_recap.nba_nba_'
                        if quality == '0':
                            url = url + '576x324.flv'
                        else:
                            url = url + '1280x720.mp4'
                        thumb = 'http://nba.cdn.turner.com/nba/nba/video/games/' + teams[h.lower()] + '/' + date + '/00' + gid + '_' + v.lower() + '_' + h.lower() + '_recap.nba.400x300.jpg'
                    elif date < '2012/10/30':
                        url = 'http://nba.cdn.turner.com/nba/big/channels/playoffs/' + date + '/00' + gid + '_' + v.lower() + '_' + h.lower() + '_recap.nba_nba_'
                        if quality == '0':
                            url = url + '576x324.flv'
                        else:
                            url = url + '1280x720.mp4'
                        thumb = 'http://i2.cdn.turner.com/nba/nba/video/channels/playoffs/' + date + '/00' + gid + '_' + v.lower() + '_' + h.lower() + '_recap.nba.576x324.jpg'
		    else:
			url = '00' + gid
			thumb = ''
			addDir(name, url, '5', thumb)
			continue
                    addLink(name, url, '', thumb)
    except:
        return None

def playGame(title, url):
    global cookies
    values = { 'path' : url , 'isFlex' : 'true', 'type': 'fvod'}
 
    if url.find('00') == 0:
	squality = '3000'

	if quality == '0':
	  squality = '800'
	elif quality == '1':
	  squality = '1600'
	
    	values = { 'id' :  url, 'isFlex':'true','bitrate': squality,'gt':'recapf', 'type':'game' }
    	link = encrypt2012(values)
    else:
	if cookies == '':
          cookies  = login()
	link = encrypt(values)
    if link != '':
	addLink(title, link,'','')
	info = xbmcgui.ListItem(name)
        playlist = xbmc.PlayList(1)
        playlist.clear()
        playlist.add(link, info)
        xbmc.executebuiltin('playlist.playoffset(video,0)')
    else:
	xbmc.executebuiltin("XBMC.Notification("+'No Video'+"," + 'No video source available!' +")")	

def mainMenu():
    addDir('Archive', 'archive', '1','')
    addDir('Condensed', 'condensed', '1','')
    addDir('Highlights', 'highlights', '1', '')

def dateMenu(type):
    if type != 'archive' and type != 'condensed': 
      addDir('This week',  type + 'this', '2' ,'')
      addDir('Last week' , type + 'last', '3','')
      addDir('Select date' , type + 'date', '4','')
    addDir('2011-2012', type +'s12', '6','')

def season2012(mode, url):
    d1 = date(2011, 12, 23)
    week = 1
    while week < 28:
    	gameLinks(mode,url, d1)
        d1 = d1 + timedelta(7)
	week = week + 1

def gameLinks(mode, url, date2Use = None):
    try:
        isFull = url.find('archive') != -1
        isHighlight = url.find('highlights') != -1
        if mode == 4:
            tday = getDate()
	elif mode == 6:
	    tday = date2Use
        else:
            tday = date.today()

        day = tday.isoweekday()
        # starts on mondays
        tday = tday - timedelta(day -1)
        now = tday
        default = "%04d" % now.year
        default = default + '/' + "%d" % now.month
        default = default + '_' + "%d" % now.day
        if mode == 2 or mode ==4 or mode ==6:
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
elif mode==6:
    season2012(mode, url)
else:
    gameLinks(mode, url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
