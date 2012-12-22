import json
import datetime, time
from datetime import date
from datetime import datetime
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
        response, content = http.request(url, 'POST', headers=headers)
        xml = parseString(str(content))
        link = xml.getElementsByTagName("path")[0].childNodes[0].nodeValue
	pp = ' playpath=mp4:' + link.partition('mp4:')[2]
        app = ' app=ondemand?' + link.partition('?')[2]
        link = 'rtmp://cp118328.edgefcs.net/ondemand' + app + pp + ' swfUrl=http://neulionms.vo.llnwd.net/o37/nba/player/nbatv/console.swf swfVfy=1'
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

    try:
        date = ''
        h = ''
        v = ''
        gid =''
        st = ''
        vs = ''
        hs = ''
	idx = ''
	t = ''
	s = ''
        headers = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/2.0.0.13'}
        thisweek = 'http://smb.cdnak.neulion.com/fs/nba/feeds/schedule/' +fromDate +  '.js?t=' + "%d"  %time.time()
        req = urllib2.Request(thisweek, None, headers);
        response = str(urllib2.urlopen(req).read())
	js = json.loads(response[response.find("{"):])
	for game in js['games']:
		for details in game:
			try:
				h = details['h']
				v = details['v']
				gid = details['id']
				date = details['d']
				s = str(details['s'])
				t = str(details['t'])

				try:
					st = details['st']
					vs = str(details['vs'])
					hs = str(details['hs'])
				except:
					vs = ''
					hs = ''
				
				try:
					videos = details['video']
					full = videos['f']
					idx =  full['ipd']
				except:
					full = ''
					idx = ''

			except  Exception, e:
				continue

			if idx != '':
				name = date[:10] + ' ' + v + '@' + h
				if scores == '1':
					name = name + ' ' + vs + ':' + hs 	
				if highlight == True:
					url = 'http://nba.cdn.turner.com/nba/big/games/' + teams[h.lower()] + '/' + date[:10].replace('-','/') +'/' + gid + '-' + v.lower() 
					squality = '1280x720.mp4'
        				if quality == '0':
						squality = '576x324.flv'
				        elif quality == '1':
					        squality = '640x360.flv'

					url = url + '-' + h.lower() + '-recap.nba_nba_' + squality 
					addLink(name, url, name, '')
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
        liz.addLink(title, link, title, '')
	liz.select(true)
	xbmc.executebuiltin("PlayWith");
    else:
        xbmc.executebuiltin("XBMC.Notification("+'No Video'+"," + 'No video source available!' +")")

def mainMenu():
    addDir('Recaps', 'recaps', '1', '')
    addDir('Highlights', 'highlights', '1','')

def dateMenu(type):
    if (type == 'highlights'):
	getHighlights()
    else:
	addDir('This week',  type + 'this', '2' ,'')
    	addDir('Last week' , type + 'last', '3','')

def season2012(mode, url):
    d1 = date(2011, 12, 23)
    week = 1
    while week < 28:
    	gameLinks(mode,url, d1)
        d1 = d1 + timedelta(7)
	week = week + 1

def getHighlights():
 for index in ['1','2','3','4','5']:
    link = 'http://www.nba.com/feeds/mobile/xbox/video/league/news/highlights_' +index + '.xml'
    headers = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/2.0.0.13'}

    req = urllib2.Request(link, None, headers);
    response = str(urllib2.urlopen(req).read())
    xml = parseString(response)
    games = xml.getElementsByTagName("item")
    for game in games:
	t = None
	u = None
	i = None
	d = None
	date = None
	try:
		u = game.getElementsByTagName("link")[0].firstChild.nodeValue
	        t = game.getElementsByTagName("title")[0].firstChild.nodeValue
		i = game.getElementsByTagName("image")[0].firstChild.nodeValue
		d = game.getElementsByTagName("description")[0].firstChild.nodeValue
		date = game.getElementsByTagName("pubDate")[0].firstChild.nodeValue[:8]
		addLink(t, u, date + ' ' + d, i)
	except:
		continue

def gameLinks(mode, url, date2Use = None):
    try:
        isFull = url.find('archive') != -1
        isHighlight = url.find('recaps') != -1
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
        xbmcplugin.addSortMethod(handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
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
    liz=xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="video", infoLabels={ "Title": title, 'Genre' : 'Sports' } )
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
    return liz

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
