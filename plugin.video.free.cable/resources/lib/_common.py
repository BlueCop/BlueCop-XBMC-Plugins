import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import time
import md5
import tempfile
import addoncompat
from BeautifulSoup import BeautifulStoneSoup


try: from sqlite3 import dbapi2 as sqlite
except: from pysqlite2 import dbapi2 as sqlite
    

pluginhandle = int (sys.argv[1])
"""
    PARSE ARGV
"""

class _Info:
    def __init__( self, *args, **kwargs ):
        print "common.args"
        print kwargs
        self.__dict__.update( kwargs )

exec '''args = _Info(%s)''' % (urllib.unquote_plus(sys.argv[2][1:].replace("&", ", ").replace('"','\'')) , )

"""
    DEFINE
"""
site_dict= {'fox': 'FOX',
            'cbs': 'CBS',
            'nbc': 'NBC',
            'lifetime': 'Lifetime',
            'abc': 'ABC',
            'amc': 'AMC',
            'usa': 'USA',
            'nick': 'Nickelodeon',
            'abcfamily': 'ABC Family',
            'thecw': 'The CW',
            'vh1': 'VH1 Shows',
            'syfy': 'SyFy',
            'food': 'Food Network',
            'spike': 'Spike',
            'nicktoons': 'Nick Toons',
            'comedy': 'Comedy Central',
            'nickteen': 'Nick Teen',
            'aetv':'A&E',
            'bio': 'Biography',
            'hub':'The Hub',
            'fx': 'FX',
            'hgtv': 'HGTV',
            'tbs': 'TBS',
            'natgeo': 'National Geographic',
            'tvland': 'TV Land',
            'bravo': 'Bravo',
            'cartoon': 'Cartoon Network',
            'adultswim': 'Adult Swim',
            'tnt': 'TNT',
            'oxygen': 'Oxygen',
            'mtv': 'MTV Shows',
            'natgeowild': 'Nat Geo Wild',
            'thewb': 'The WB',
            'gsn': 'Game Show Network',
            'history': 'History Channel'
            }

addoncompat.get_revision()
pluginpath = addoncompat.get_path()

db_file = os.path.join(xbmc.translatePath(pluginpath),'resources','shows.db')
cachepath = os.path.join(xbmc.translatePath(pluginpath),'resources','cache')
imagepath = os.path.join(xbmc.translatePath(pluginpath),'resources','images')
fanartpath = os.path.join(xbmc.translatePath(pluginpath),'resources','FAimages')
plugin_icon = os.path.join(xbmc.translatePath(pluginpath),'icon.png')
plugin_fanart = os.path.join(xbmc.translatePath(pluginpath),'fanart.jpg')
fav_icon = os.path.join(xbmc.translatePath(pluginpath),'fav.png')
all_icon = os.path.join(xbmc.translatePath(pluginpath),'allshows.png')

"""
    GET SETTINGS
"""

settings={}
#settings general
quality = ['200', '400', '600', '800', '1000', '1200', '1400', '1600', '2000', '2500', '3000', '100000']
selectquality = int(addoncompat.get_setting('quality'))
settings['quality'] = quality[selectquality]
settings['enableproxy'] = addoncompat.get_setting('us_proxy_enable')
settings['enablesubtitles'] = addoncompat.get_setting('enablesubtitles')

def get_series_id(seriesdata,seriesname):
    shows = BeautifulStoneSoup(seriesdata, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('series')
    names = list(BeautifulStoneSoup(seriesdata, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('seriesname'))
    if len(names) > 1:
        select = xbmcgui.Dialog()
        ret = select.select(seriesname, [name.string for name in names])
        if ret <> -1:
            seriesid = shows[ret].find('seriesid').string
    else:
        seriesid = shows[0].find('seriesid').string
    return seriesid

def tv_db_series_lookup(seriesname,manualSearch=False):
    tv_api_key = '03B8C17597ECBD64'
    mirror = 'http://thetvdb.com'
    banners = 'http://thetvdb.com/banners/'
    series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(seriesname)
    seriesdata = getURL(series_lookup)
    try: seriesid = get_series_id(seriesdata,seriesname)
    except:
        if manualSearch:
            keyb = xbmc.Keyboard(seriesname, 'Manual Search')
            keyb.doModal()
            if (keyb.isConfirmed()):
                    series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(keyb.getText())
                    seriesid = getURL(series_lookup)
                    try: seriesid = get_series_id(seriesid,seriesname)
                    except:
                        print 'manual search failed'
                        return False
        else:
            return False
    series_xml = mirror+('/api/%s/series/%s/en.xml' % (tv_api_key, seriesid))
    series_xml = getURL(series_xml)
    tree = BeautifulStoneSoup(series_xml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    #print tree.prettify()
    try:
        first_aired = tree.find('firstaired').string
        date = first_aired
        year = int(first_aired.split('-')[0])
    except:
        print '%s - Air Date Failed' % seriesname
        first_aired = None
        date = None
        year = None
    try: genres = tree.find('genre').string
    except:
        print '%s - Genre Failed' % seriesname
        genres = None
    try: plot = tree.find('overview').string
    except:
        print '%s - Plot Failed' % seriesname
        plot = None
    try: actors = tree.find('actors').string
    except:
        print '%s - Actors Failed' % seriesname
        actors = None
    try: rating = float(tree.find('rating').string)
    except:
        print '%s - Rating Failed' % seriesname
        rating = None
    try: TVDBbanner = banners + tree.find('banner').string
    except:
        print '%s - Banner Failed' % seriesname
        TVDBbanner = None
    try: TVDBfanart = banners + tree.find('fanart').string
    except:
        print '%s - Fanart Failed' % seriesname
        TVDBfanart = None
    try: TVDBposter = banners + tree.find('poster').string
    except:
        print '%s - Poster Failed' % seriesname
        TVDBposter = None
    try: IMDB_ID = tree.find('imdb_id').string
    except:
        print '%s - IMDB_ID Failed' % seriesname
        IMDB_ID = None
    try: runtime = tree.find('runtime').string
    except:
        print '%s - Runtime Failed' % seriesname
        runtime = None
    try: Airs_DayOfWeek = tree.find('airs_dayofweek').string
    except:
        print '%s - Airs_DayOfWeek Failed' % seriesname
        Airs_DayOfWeek = None
    try: Airs_Time = tree.find('airs_time').string
    except:
        print '%s - Airs_Time Failed' % seriesname
        Airs_Time = None
    try: status = tree.find('status').string
    except:
        print '%s - status Failed' % seriesname
        status = None
    try: network = tree.find('network').string
    except:
        print '%s - Network Failed' % seriesname
        network = None
    return [seriesid,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status]

def load_db():
    #if os.path.exists(db_file):
    #    os.remove(db_file)
    if not os.path.exists(db_file):
        create_db()
        refresh_db()
    #else:
    #    refresh_db()
    conn = sqlite.connect(db_file)
    c = conn.cursor()
    return c.execute('select * from shows order by series_title')

def load_showlist(favored=False):
    shows = load_db()
    for series_title,mode,sitemode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,has_full_episodes,favor,hide in shows:
        if addoncompat.get_setting(mode) == 'false':
            continue
        elif hide:
            continue
        elif favored and not favor:
            continue
        thumb=os.path.join(imagepath,mode+'.png')
        fanart=''
        infoLabels={}
        if TVDBfanart:
            fanart=TVDBfanart
        else:
            if args.__dict__.has_key('fanart'): fanart = args.fanart
            else: fanart=''
        if TVDBbanner:
            thumb=TVDBbanner
        infoLabels['Title']=series_title.encode('utf-8', 'ignore')
        infoLabels['TVShowTitle']=series_title.encode('utf-8', 'ignore')
        prefixplot=''
        if network<>None:
            prefixplot+='Station: %s' % network
            prefixplot+='\n'
        if Airs_DayOfWeek<>None and Airs_Time<>None:
            prefixplot+='Airs: %s @ %s' % (Airs_DayOfWeek,Airs_Time)
            prefixplot+='\n'
        if status<>None:
            prefixplot+='Status: %s' % status
            prefixplot+='\n'
        if prefixplot <> '':
            prefixplot+='\n'
        if plot<>None:
            infoLabels['Plot']=prefixplot.encode('utf-8', 'ignore')+plot.encode('utf-8', 'ignore')
        else:
            infoLabels['Plot']=prefixplot
        #if date: infoLabels['date']=date
        if first_aired<>None: infoLabels['aired']=first_aired
        if year<>None: infoLabels['Year']=year
        if actors<>None:
            actors = actors.encode('utf-8', 'ignore').strip('|').split('|')
            if actors[0] <> '':
                infoLabels['cast']=actors
        if genres<>None: infoLabels['genre']=genres.encode('utf-8', 'ignore').replace('|',',').strip(',')
        if network<>None: infoLabels['studio']=network.encode('utf-8', 'ignore')
        if runtime<>None: infoLabels['duration']=runtime
        if rating<>None: infoLabels['rating']=rating
        addShow(series_title, mode, sitemode, url, thumb, fanart,TVDBposter, infoLabels,favor=favor,hide=hide)

def lookup_db(series_title,mode,submode,url,forceRefresh=False):
    print 'Looking Up: %s for %s' % (series_title,mode)
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    checkdata = c.execute('select * from shows where series_title=? and mode=? and submode =?', (series_title,mode,submode)).fetchone()
    if checkdata and not forceRefresh:
        if checkdata[3] <> url:
            c.execute("update shows set url=? where series_title=? and mode=? and submode =?", (url,series_title,mode,submode))
            conn.commit()
            return c.execute('select * from shows where series_title=? and mode=? and submode =?', (series_title,mode,submode)).fetchone()
        else:
            return checkdata
    else:
        tvdb_data = tv_db_series_lookup(series_title,manualSearch=forceRefresh)
        if tvdb_data:
            TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status = tvdb_data
            #           series_title,mode,submode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,has_full_episodes,favor
            showdata = [series_title,mode,submode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,True,False,False]
        else:
            showdata = [series_title,mode,submode,url,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,True,False,False]
        c.execute('insert or replace into shows values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', showdata)
        conn.commit()
        return c.execute('select * from shows where series_title=? and mode=? and submode =?', (series_title,mode,submode)).fetchone()
        
def refreshShow():
    series_title,mode,submode,url = args.url.split('<join>')
    lookup_db(series_title,mode,submode,url,forceRefresh=True)

def favorShow():
    series_title,mode,submode,url = args.url.split('<join>')
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("update shows set favor=? where series_title=? and mode=? and submode =?", (True,series_title,mode,submode))
    conn.commit()
    c.close()

def unfavorShow():
    series_title,mode,submode,url = args.url.split('<join>')
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("update shows set favor=? where series_title=? and mode=? and submode =?", (False,series_title,mode,submode))
    conn.commit()
    c.close()

def hideShow():
    series_title,mode,submode,url = args.url.split('<join>')
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("update shows set hide=? where series_title=? and mode=? and submode =?", (True,series_title,mode,submode))
    conn.commit()
    c.close()

def unhideShow():
    series_title,mode,submode,url = args.url.split('<join>')
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("update shows set hide=? where series_title=? and mode=? and submode =?", (False,series_title,mode,submode))
    conn.commit()
    c.close()
    
def create_db():
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute('''CREATE TABLE shows(
                 series_title TEXT,
                 mode TEXT,
                 submode TEXT,
                 url TEXT,
                 TVDB_ID TEXT,
                 IMDB_ID TEXT,
                 TVDBbanner TEXT,
                 TVDBposter TEXT,
                 TVDBfanart TEXT,
                 first_aired TEXT,
                 date TEXT,
                 year INTEGER,
                 actors TEXT,
                 genres TEXT,
                 network TEXT,
                 plot TEXT,
                 runtime TEXT,
                 rating float,
                 Airs_DayOfWeek TEXT,
                 Airs_Time TEXT,
                 status TEXT,
                 has_full_episodes BOOLEAN,
                 favor BOOLEAN,
                 hide BOOLEAN,
                 PRIMARY KEY(series_title,mode,submode)
                 );''')
    conn.commit()
    c.close()

def refresh_db():
    dialog = xbmcgui.DialogProgress()
    dialog.create('Caching')
    total_stations = len(site_dict)
    current = 0
    increment = 100.0 / total_stations
    for network, name in site_dict.iteritems():
        if addoncompat.get_setting(network) == 'true':
            percent = int(increment*current)
            dialog.update(percent,'Scanning %s' % name,'Grabbing Show list')
            exec 'import %s' % network
            exec 'showdata = %s.masterlist()' % network
            total_shows = len(showdata)
            current_show = 0
            for show in showdata:
                percent = int((increment*current)+(float(current_show)/total_shows)*increment)
                dialog.update(percent,'Scanning %s' % name,'Looking up %s' % show[0] )
                lookup_db(show[0],show[1],show[2],show[3])
                current_show += 1
                if (dialog.iscanceled()):
                    return False
        current += 1

def setView(type='root'):
    confluence_views = [500,501,502,503,504,508]
    #types: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
    if type <> 'root':
        xbmcplugin.setContent(pluginhandle, type)
    #xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)
    viewenable=addoncompat.get_setting("viewenable")
    if viewenable == 'true':
        view=int(addoncompat.get_setting(type+'view'))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")  

def addVideo(u,displayname,thumb=False,fanart=False,infoLabels=False):
    if not fanart:
        if args.__dict__.has_key('fanart'): fanart = args.fanart
        else: fanart = ''
    if not thumb:
        if args.__dict__.has_key('thumb'): thumb = args.thumb
        else: thumb = ''
    item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
    item.setInfo( type="Video", infoLabels=infoLabels)
    item.setProperty('fanart_image',fanart)
    item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

"""
    ADD DIRECTORY
"""

def addDirectory(name, mode='', sitemode='', url='', thumb=False, fanart=False, description='', aired='', genre=''):
    if not fanart:
        if args.__dict__.has_key('fanart'): fanart = args.fanart
        else: fanart = plugin_fanart
    if not thumb:
        if args.__dict__.has_key('poster'): thumb = args.poster
        elif args.__dict__.has_key('thumb'): thumb = args.thumb
        else: thumb = ''
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+mode+'"'
    u += '&sitemode="'+sitemode+'"'
    u += '&thumb="'+urllib.quote_plus(thumb)+'"'
    u += '&fanart="'+urllib.quote_plus(fanart)+'"'
    u += '&name="'+urllib.quote_plus(name.replace("'",''))+'"'
    item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
    item.setProperty('fanart_image',fanart)
    item.setInfo( type="Video", infoLabels={ "Title":name,
                                             "Genre":genre,
                                             "premiered":aired,
                                             "Plot":description})
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=item,isFolder=True)
    
def addShow(series_title, mode='', sitemode='', url='', thumb='', fanart='', TVDBposter=False, infoLabels=False, favor=False, hide=False):
    if not os.path.exists(db_file):
        create_db()
    #           series_title,mode,submode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,has_full_episodes,favor
    if not infoLabels:
        infoLabels={}
        showdata = lookup_db(series_title,mode,sitemode,url)
        #series_title,mode,submode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,has_full_episodes,favor
        series_title,mode,sitemode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,has_full_episodes,favor,hide = showdata
        if TVDBfanart:
            fanart=TVDBfanart
        else:
            if args.__dict__.has_key('fanart'): fanart = args.fanart
            else: fanart=''
        if TVDBbanner:
            thumb=TVDBbanner
        else:
            thumb=os.path.join(imagepath,mode+'.png')
        series_title = series_title.decode("utf-8")
        infoLabels['Title']=series_title.encode('utf-8', 'ignore')
        infoLabels['TVShowTitle']=series_title.encode('utf-8', 'ignore')
        prefixplot=''
        if network<>None:
            prefixplot+='Station: %s' % network
            prefixplot+='\n'
        if Airs_DayOfWeek<>None and Airs_Time<>None:
            prefixplot+='Airs: %s @ %s' % (Airs_DayOfWeek,Airs_Time)
            prefixplot+='\n'
        if status<>None:
            prefixplot+='Status: %s' % status
            prefixplot+='\n'
        if prefixplot <> '':
            prefixplot+='\n'
        if plot<>None:
            infoLabels['Plot']=prefixplot.encode('utf-8', 'ignore')+plot.decode("utf-8").encode('utf-8', 'ignore')
        else:
            infoLabels['Plot']=prefixplot
        #if date: infoLabels['date']=date
        if first_aired<>None: infoLabels['aired']=first_aired
        if year<>None: infoLabels['Year']=year
        if actors<>None:
            actors = actors.decode("utf-8").encode('utf-8', 'ignore').strip('|').split('|')
            if actors[0] <> '':
                infoLabels['cast']=actors
        if genres<>None: infoLabels['genre']=genres.encode('utf-8', 'ignore').replace('|',',').strip(',')
        if network<>None: infoLabels['studio']=network.encode('utf-8', 'ignore')
        if runtime<>None: infoLabels['duration']=runtime
        if rating<>None: infoLabels['rating']=rating
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+mode+'"'
    u += '&sitemode="'+sitemode+'"'
    u += '&thumb="'+urllib.quote_plus(thumb)+'"'
    u += '&fanart="'+urllib.quote_plus(fanart)+'"'
    if TVDBposter:
        u += '&poster="'+urllib.quote_plus(TVDBposter)+'"'
    u += '&name="'+urllib.quote_plus(series_title.encode('ascii', 'ignore').replace("'",""))+'"'
    
    cm=[]
    if favor:
        fav_u=sys.argv[0]+"?url='"+urllib.quote_plus('<join>'.join([series_title.encode('ascii', 'ignore').replace("'",""),mode,sitemode,url]))+"'&mode='common'"+"&sitemode='unfavorShow'"
        cm.append( ('Remove Favorite %s' % series_title.encode('ascii', 'ignore'), "XBMC.RunPlugin(%s)" % fav_u) )
    else:
        fav_u=sys.argv[0]+"?url='"+urllib.quote_plus('<join>'.join([series_title.encode('ascii', 'ignore').replace("'",""),mode,sitemode,url]))+"'&mode='common'"+"&sitemode='favorShow'"
        cm.append( ('Favorite %s' % series_title.encode('ascii', 'ignore'), "XBMC.RunPlugin(%s)" % fav_u) )
    refresh_u=sys.argv[0]+"?url='"+urllib.quote_plus('<join>'.join([series_title.encode('ascii', 'ignore').replace("'",""),mode,sitemode,url]))+"'&mode='common'"+"&sitemode='refreshShow'"
    cm.append( ('Refresh TVDB Data', "XBMC.RunPlugin(%s)" % refresh_u) )
    if hide:
        hide_u=sys.argv[0]+"?url='"+urllib.quote_plus('<join>'.join([series_title.encode('ascii', 'ignore').replace("'",""),mode,sitemode,url]))+"'&mode='common'"+"&sitemode='unhideShow'"
        cm.append( ('UnHide Show', "XBMC.RunPlugin(%s)" % hide_u) )
    else:  
        hide_u=sys.argv[0]+"?url='"+urllib.quote_plus('<join>'.join([series_title.encode('ascii', 'ignore').replace("'",""),mode,sitemode,url]))+"'&mode='common'"+"&sitemode='hideShow'"
        cm.append( ('Hide Show', "XBMC.RunPlugin(%s)" % hide_u) )

    item=xbmcgui.ListItem(series_title, iconImage=thumb, thumbnailImage=thumb)
    item.addContextMenuItems( cm )
    item.setProperty('fanart_image',fanart)
    item.setInfo( type="Video", infoLabels=infoLabels)
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=item,isFolder=True)

def getURL( url , values = None ,proxy = False, referer=False):
    try:
        if proxy == True:
            us_proxy = 'http://' + addoncompat.get_setting('us_proxy') + ':' + addoncompat.get_setting('us_proxy_port')
            print 'Using proxy: ' + us_proxy
            proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        print 'FREE CABLE --> common :: getURL :: url = '+url
        if values == None:
            req = urllib2.Request(url)
        else:
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data)
        if referer:
            req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:13.0) Gecko/20100101 Firefox/13.0.1')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.HTTPError, error:
        print 'Error reason: ', error
        return error.read()
    else:
        return link
    
def getRedirect( url , values = None ,proxy = False, referer=False):
    try:
        if proxy == True:
            us_proxy = 'http://' + addoncompat.get_setting('us_proxy') + ':' + addoncompat.get_setting('us_proxy_port')
            print 'Using proxy: ' + us_proxy
            proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        print 'FREE CABLE --> common :: getRedirect :: url = '+url
        if values == None:
            req = urllib2.Request(url)
        else:
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data)
        if referer:
            req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:13.0) Gecko/20100101 Firefox/13.0.1')
        response = urllib2.urlopen(req)
        finalurl=response.geturl()
        response.close()
    except urllib2.HTTPError, error:
        print 'Error reason: ', error
        return error.read()
    else:
        return finalurl

